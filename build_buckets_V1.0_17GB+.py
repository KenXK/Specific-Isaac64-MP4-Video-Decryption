#!/usr/bin/env python3
"""
彩虹表桶化排序构建器 V1.0
============================
三级流水线架构，SSD 全速读取：
  [读线程] → buffer → [分发(numpy)] → 桶缓冲 → [写线程]

输出：buckets/bucket_0000.bin ~ bucket_FFFF.bin

用法：
  python build_buckets_V1.0.py
  python build_buckets_V1.0.py --rainbow-dir D:/table --output-dir D:/buckets
  python build_buckets_V1.0.py --workers 12 --force

依赖：numpy
"""

import os
import sys
import struct
import time
import argparse
import threading
import queue
import logging
import signal
from pathlib import Path
from collections import OrderedDict
from multiprocessing import Pool

try:
    import numpy as np
except ImportError:
    print("❌ 需要 numpy: pip install numpy")
    sys.exit(1)

# ============================================================
#  日志 & Ctrl+C
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger('build_buckets')

_stop_event = threading.Event()

def _sigint_handler(sig, frame):
    log.warning("收到 Ctrl+C，正在停止...")
    _stop_event.set()

signal.signal(signal.SIGINT, _sigint_handler)

# ============================================================
#  配置项
# ============================================================
SCRIPT_DIR = Path(__file__).parent.resolve()

RECORD_SIZE = 16
NUM_BUCKETS = 65536

DEFAULT_RAINBOW_DIR = SCRIPT_DIR
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "buckets"

RAINBOW_FOLDERS = ["0-20亿", "20亿-40亿", "40亿-80亿", "80亿-100亿"]
PART_COUNT = 19

DTYPE = np.dtype([('prefix', 'u8'), ('key', 'u8')])

READ_BUF_SIZE = 64 * 1024 * 1024       # 64MB per chunk
BUCKET_BUF_SIZE = 240 * 1024            # 240KB/bucket（~15.0GB，减少 flush 次数）
FLUSH_QUEUE_MAX = 2048                  # 写队列（省内存）
MAX_OPEN_FILES = 8100

# ============================================================
#  LRU 文件句柄池
# ============================================================

class FileHandlePool:
    def __init__(self, directory: str, max_size: int = MAX_OPEN_FILES):
        self.directory = directory
        self.max_size = max_size
        self.pool = OrderedDict()
        self.open_count = 0
        self.close_count = 0

    def get_handle(self, bid: int):
        if bid in self.pool:
            self.pool.move_to_end(bid)
            return self.pool[bid]
        while len(self.pool) >= self.max_size:
            _, old_f = self.pool.popitem(last=False)
            old_f.close()
            self.close_count += 1
        path = os.path.join(self.directory, f"bucket_{bid:04X}.bin")
        f = open(path, 'ab')  # Python open()，支持更多文件句柄
        self.pool[bid] = f
        self.open_count += 1
        return f

    def close_all(self):
        for f in self.pool.values():
            f.close()
        self.pool.clear()


# ============================================================
#  读线程
# ============================================================

def reader_thread(part_files: list, filled_queue: queue.Queue,
                  stop_event: threading.Event):
    total_bytes = 0
    t_start = time.time()

    for pf in part_files:
        if stop_event.is_set():
            break
        fsize = os.path.getsize(pf)
        if fsize == 0:
            continue
        log.info(f"读取: {Path(pf).name} ({fsize/1024**3:.2f} GB)")

        with open(pf, 'rb') as fin:
            import mmap as mmap_mod
            mm = mmap_mod.mmap(fin.fileno(), 0, access=mmap_mod.ACCESS_READ)
            offset = 0
            while offset < fsize:
                if stop_event.is_set():
                    break
                n = min(READ_BUF_SIZE, fsize - offset)
                filled_queue.put((mm[offset:offset + n], n))
                total_bytes += n
                offset += n
            mm.close()

    filled_queue.put(None)
    elapsed = time.time() - t_start
    log.info(f"读线程完成: {total_bytes/1024**3:.1f} GB, "
             f"{elapsed:.0f}s, {total_bytes/1024**2/elapsed:.0f} MB/s")


# ============================================================
#  分发线程
# ============================================================

def distributor_thread(filled_queue: queue.Queue,
                       flush_queue: queue.Queue,
                       stop_event: threading.Event):
    # 用 list 存储 numpy 视图，避免 bytearray.extend 的反复拷贝
    bucket_chunks = {}   # bid_int -> list of numpy views
    bucket_sizes = {}    # bid_int -> 累计字节数
    flush_threshold = BUCKET_BUF_SIZE

    total_records = 0
    total_chunks = 0
    t_start = time.time()
    numpy_time = 0
    copy_time = 0
    last_log = time.time()

    while True:
        item = filled_queue.get()
        if item is None:
            break
        if stop_event.is_set():
            break

        buf, length = item
        n_records = length // RECORD_SIZE

        # ---- numpy 计算 ----
        t0 = time.time()

        data = np.frombuffer(buf, dtype=np.uint8)[:length]
        records = data.reshape(n_records, RECORD_SIZE)

        byte4 = records[:, 4].astype(np.uint16)
        byte5 = records[:, 5].astype(np.uint16)
        bucket_ids = (byte4 << 8) | byte5

        sort_order = np.argsort(bucket_ids, kind='stable')
        sorted_ids = bucket_ids[sort_order]

        # structured dtype 重排（比 2D fancy indexing 略快）
        records_st = data.view(np.dtype([('prefix', 'u8'), ('key', 'u8')]))
        sorted_records = records_st[sort_order]

        t1 = time.time()
        numpy_time += (t1 - t0)

        # ---- 按桶切片发送 ----
        boundaries = np.flatnonzero(np.diff(sorted_ids)) + 1
        boundaries = np.concatenate([[0], boundaries, [n_records]])

        for k in range(len(boundaries) - 1):
            start = boundaries[k]
            end = boundaries[k + 1]
            bid_int = int(sorted_ids[start])

            if bid_int not in bucket_chunks:
                bucket_chunks[bid_int] = []
                bucket_sizes[bid_int] = 0

            chunk_bytes = sorted_records[start:end].view(np.uint8).tobytes()
            bucket_chunks[bid_int].append(chunk_bytes)
            bucket_sizes[bid_int] += len(chunk_bytes)

            if bucket_sizes[bid_int] >= flush_threshold:
                data_to_flush = b''.join(bucket_chunks[bid_int])
                flush_queue.put((bid_int, data_to_flush))
                bucket_chunks[bid_int] = []
                bucket_sizes[bid_int] = 0

        t2 = time.time()
        copy_time += (t2 - t1)

        total_records += n_records
        total_chunks += 1

        now = time.time()
        if now - last_log >= 10:
            log.info(
                f"分发: {total_chunks} chunks, "
                f"{total_records/1e6:.0f}M 条, "
                f"numpy {numpy_time/total_chunks*1000:.0f}ms/ch, "
                f"copy {copy_time/total_chunks*1000:.0f}ms/ch, "
                f"flushQ {flush_queue.qsize()}"
            )
            last_log = now

    # 刷剩余
    remaining_flushes = []
    for bid_int, chunks in bucket_chunks.items():
        if chunks:
            remaining_flushes.append((bid_int, b''.join(chunks)))
    if remaining_flushes:
        # 按 bid 排序后发送
        remaining_flushes.sort(key=lambda x: x[0])
        for bid_int, data in remaining_flushes:
            flush_queue.put((bid_int, data))
    flush_queue.put(None)

    elapsed = time.time() - t_start
    log.info(f"分发完成: {total_chunks} chunks, {total_records/1e6:.0f}M 条, {elapsed:.0f}s")
    log.info(f"  numpy均值: {numpy_time/max(total_chunks,1)*1000:.0f}ms/chunk")
    log.info(f"  copy均值: {copy_time/max(total_chunks,1)*1000:.0f}ms/chunk")


# ============================================================
#  写线程
# ============================================================

def writer_thread(flush_queue: queue.Queue, output_dir: str,
                  counters: dict, stop_event: threading.Event):
    pool = FileHandlePool(output_dir, MAX_OPEN_FILES)

    flush_count = 0
    flush_bytes = 0
    t_start = time.time()
    last_log = time.time()

    while True:
        item = flush_queue.get()
        if item is None:
            break
        if stop_event.is_set():
            break

        bid, data = item
        f = pool.get_handle(bid)
        f.write(data)

        flush_count += 1
        flush_bytes += len(data)
        counters['flushed'] = flush_count
        counters['bytes'] = flush_bytes

        now = time.time()
        if now - last_log >= 10:
            elapsed = now - t_start
            log.info(
                f"写入: {flush_count} flush, "
                f"{flush_bytes/1024**3:.1f} GB, "
                f"{flush_bytes/1024**2/elapsed:.0f} MB/s, "
                f"FD {len(pool.pool)}/{pool.max_size}, "
                f"open {pool.open_count} close {pool.close_count}"
            )
            last_log = now

    pool.close_all()

    elapsed = time.time() - t_start
    log.info(f"写入完成: {flush_count} flush, "
             f"{flush_bytes/1024**3:.1f} GB, {elapsed:.0f}s, "
             f"{flush_bytes/1024**2/elapsed:.0f} MB/s, "
             f"open {pool.open_count} close {pool.close_count}")


# ============================================================
#  流水线
# ============================================================

def run_pipeline(part_files: list, output_dir: Path):
    filled_queue = queue.Queue(maxsize=18)
    flush_queue = queue.Queue(maxsize=FLUSH_QUEUE_MAX)
    stop_event = _stop_event

    counters = {'flushed': 0, 'bytes': 0}

    reader = threading.Thread(target=reader_thread,
                              args=(part_files, filled_queue, stop_event),
                              name='Reader')
    distributor = threading.Thread(target=distributor_thread,
                                   args=(filled_queue, flush_queue, stop_event),
                                   name='Distributor')
    writer = threading.Thread(target=writer_thread,
                              args=(flush_queue, str(output_dir),
                                    counters, stop_event),
                              name='Writer')

    t_start = time.time()

    reader.start()
    distributor.start()
    writer.start()

    # 用 timeout join 让主线程定期唤醒，处理 Ctrl+C 信号
    while reader.is_alive() or distributor.is_alive() or writer.is_alive():
        reader.join(timeout=1)
        distributor.join(timeout=1)
        writer.join(timeout=1)
        if _stop_event.is_set():
            log.warning("等待线程退出...")
            break

    reader.join(timeout=5)
    distributor.join(timeout=5)
    writer.join(timeout=5)

    elapsed = time.time() - t_start
    log.info(f"散列完成: {counters['flushed']:,} 次flush, "
             f"{counters['bytes']/1024**3:.1f} GB, {elapsed:.0f}s")

    non_empty = 0
    for i in range(NUM_BUCKETS):
        path = os.path.join(str(output_dir), f"bucket_{i:04X}.bin")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            non_empty += 1
    log.info(f"非空桶: {non_empty}/{NUM_BUCKETS}")

    return counters['bytes'] // RECORD_SIZE


# ============================================================
#  Phase 2: 排序
# ============================================================

def _sort_one_bucket(args):
    bucket_path, bucket_id = args
    fsize = os.path.getsize(bucket_path)
    if fsize == 0:
        return bucket_id, 0
    n_records = fsize // RECORD_SIZE
    with open(bucket_path, 'r+b') as f:
        import mmap as mmap_mod
        mm = mmap_mod.mmap(f.fileno(), 0)
        data = mm[:]
        arr = np.frombuffer(data, dtype=DTYPE, count=n_records).copy()
        mm.close()
    order = arr['prefix'].byteswap().argsort()
    arr = arr[order]
    with open(bucket_path, 'wb') as f:
        f.write(arr.tobytes())
    return bucket_id, n_records


def sort_all_buckets(output_dir: Path, workers: int):
    tasks = []
    for i in range(NUM_BUCKETS):
        path = str(output_dir / f"bucket_{i:04X}.bin")
        if os.path.exists(path):
            tasks.append((path, i))
    total = len(tasks)
    log.info(f"排序: {workers} 进程, {total} 个桶")

    t_start = time.time()
    completed = 0
    total_records = 0

    with Pool(workers) as pool:
        for bucket_id, n_records in pool.imap_unordered(_sort_one_bucket, tasks):
            completed += 1
            total_records += n_records
            if completed % 5000 == 0 or completed == total:
                elapsed = time.time() - t_start
                rate = completed / elapsed if elapsed > 0 else 0
                eta = (total - completed) / rate if rate > 0 else 0
                log.info(f"排序: [{completed}/{total}] "
                         f"{elapsed:.0f}s, ETA {eta:.0f}s")

    elapsed = time.time() - t_start
    log.info(f"排序完成: {total_records:,} 条, {elapsed:.0f}s")


# ============================================================
#  主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="彩虹表桶化排序构建器 V1.0（三级流水线）"
    )
    parser.add_argument('--rainbow-dir', type=str, default=None)
    parser.add_argument('--output-dir', type=str, default=None)
    parser.add_argument('--workers', type=int, default=None)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    rainbow_dir = Path(args.rainbow_dir).resolve() if args.rainbow_dir else DEFAULT_RAINBOW_DIR
    output_dir = Path(args.output_dir).resolve() if args.output_dir else DEFAULT_OUTPUT_DIR
    sort_workers = args.workers or max((os.cpu_count() or 4) - 2, 1)

    # 扫描输入
    part_files = []
    total_input_bytes = 0
    for folder_name in RAINBOW_FOLDERS:
        folder = rainbow_dir / folder_name
        if not folder.exists():
            continue
        for i in range(PART_COUNT):
            pf = folder / f"part_{i:03d}.bin"
            if pf.exists():
                part_files.append(str(pf))
                total_input_bytes += pf.stat().st_size

    if not part_files:
        print("❌ 未找到任何彩虹表文件！")
        sys.exit(1)

    total_input_gb = total_input_bytes / 1024**3

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║      彩虹表桶化排序构建器 V1.0（三级流水线）             ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print(f"║  彩虹表:   {str(rainbow_dir)[:46]}".ljust(59) + "║")
    print(f"║  输入:     {len(part_files)} 个文件 ({total_input_gb:.1f} GB)".ljust(59) + "║")
    print(f"║  输出:     {str(output_dir)[:46]}".ljust(59) + "║")
    print(f"║  桶:       {NUM_BUCKETS} (prefix[4:6])".ljust(59) + "║")
    print(f"║  排序进程: {sort_workers}".ljust(59) + "║")
    print(f"║  读缓冲:   {READ_BUF_SIZE//1024//1024}MB/chunk".ljust(59) + "║")
    print(f"║  桶缓冲:   {BUCKET_BUF_SIZE//1024}KB/bucket".ljust(59) + "║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print("║  [Reader] → queue → [Distributor(numpy)] → flush_q → [Writer] ║")
    print("║    全速SSD读     向量化分桶(不做I/O)      LRU句柄池刷盘       ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    if not args.force:
        resp = input("确认开始？(y/N): ").strip().lower()
        if resp != 'y':
            print("已取消")
            return
        print()

    if output_dir.exists():
        existing = list(output_dir.glob("bucket_*.bin"))
        if existing and not args.force:
            print(f"⚠️ 已有 {len(existing)} 个桶文件")
            resp = input("覆盖？(y/N): ").strip().lower()
            if resp != 'y':
                print("已取消")
                return
            for bf in existing:
                bf.unlink()
            print()

    os.makedirs(output_dir, exist_ok=True)

    t_total = time.time()

    log.info("=== Phase 1: 流水线散列 ===")
    total_records = run_pipeline(part_files, output_dir)
    t_p1 = time.time()

    if _stop_event.is_set():
        log.warning("已中断，跳过排序")
        return

    log.info("=== Phase 2: 排序 ===")
    sort_all_buckets(output_dir, sort_workers)
    t_p2 = time.time()

    t_elapsed = time.time() - t_total
    log.info(f"=== 完成 ===")
    log.info(f"记录: {total_records:,}")
    log.info(f"桶:   {NUM_BUCKETS}")
    log.info(f"Phase 1: {t_p1-t_total:.0f}s")
    log.info(f"Phase 2: {t_p2-t_p1:.0f}s")
    log.info(f"总计:    {t_elapsed:.0f}s ({t_elapsed/60:.1f}分钟)")


if __name__ == '__main__':
    main()
