#!/usr/bin/env python3
"""
彩虹表索引构建器
================
将彩虹表按 reversed keystream 前缀（前8字节）排序，生成单一排序文件。
后续查找可用二分搜索，从36秒全量扫描降到毫秒级。

排序后文件格式与原彩虹表相同：
  每条记录 16 字节 = 8 字节 prefix + 8 字节 decode_key (uint64 BE)
  按 prefix 字典序升序排列

用法：
  python build_index.py                        # 默认路径
  python build_index.py --rainbow-dir D:/table # 指定彩虹表目录
  python build_index.py --output sorted.bin    # 指定输出文件名
  python build_index.py --memory 16            # 指定排序用内存(GB)
  python build_index.py --tmpdir E:/tmp        # 指定临时文件目录

依赖：numpy（用于内存高效的排序）
"""

import os
import sys
import struct
import heapq
import time
import argparse
import tempfile
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("❌ 需要 numpy: pip install numpy")
    sys.exit(1)

# ============================================================
#  配置
# ============================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
RECORD_SIZE = 16
PREFIX_SIZE = 8

RAINBOW_FOLDERS = ["0-20亿", "20亿-40亿", "40亿-80亿", "80亿-100亿"]
PART_COUNT = 19

# numpy 结构化 dtype
DTYPE = np.dtype([('prefix', 'u8'), ('key', 'u8')])

# 归并写入缓冲区大小（记录数），约 16MB
MERGE_WRITE_BUF_RECORDS = 1_000_000


# ============================================================
#  第一阶段：分块排序（多进程并行）
# ============================================================

def sort_chunk_file(chunk_path: str, sorted_path: str):
    """排序单个 chunk 文件（供 multiprocessing 调用）"""
    raw = open(chunk_path, 'rb').read()
    n = len(raw) // RECORD_SIZE
    arr = np.frombuffer(raw, dtype=DTYPE, count=n).copy()
    order = arr['prefix'].byteswap().argsort()
    arr = arr[order]
    with open(sorted_path, 'wb') as f:
        f.write(arr.tobytes())
    del arr, order, raw
    return sorted_path


def create_sorted_chunks(rainbow_dir: Path, chunk_records: int,
                          tmpdir: Path, read_buffer_mb: int,
                          workers: int) -> list:
    """
    读取彩虹表写入未排序 chunk，然后多进程并行排序。
    返回已排序的临时文件路径列表。
    """
    import mmap

    # 收集所有 part 文件
    part_files = []
    for folder_name in RAINBOW_FOLDERS:
        folder = rainbow_dir / folder_name
        if not folder.exists():
            print(f"  ⚠️ 跳过不存在的文件夹: {folder}")
            continue
        for i in range(PART_COUNT):
            pf = folder / f"part_{i:03d}.bin"
            if pf.exists():
                part_files.append(str(pf))

    if not part_files:
        print("❌ 未找到彩虹表文件！")
        sys.exit(1)

    print(f"  📂 找到 {len(part_files)} 个彩虹表文件")

    chunk_bytes = chunk_records * RECORD_SIZE
    read_buf_bytes = read_buffer_mb * 1024 * 1024

    # ---- Pass 1: 写未排序 chunk ----
    print(f"\n  📝 Pass 1: 写入未排序 chunk...")
    unsorted_dir = tmpdir / "unsorted"
    unsorted_dir.mkdir()

    buffer = bytearray()
    total_records = 0
    chunk_id = 0
    unsorted_files = []

    def flush_buffer():
        nonlocal buffer, chunk_id
        if not buffer:
            return
        n_rec = len(buffer) // RECORD_SIZE
        chunk_path = str(unsorted_dir / f"chunk_{chunk_id:04d}.bin")
        with open(chunk_path, 'wb') as f:
            f.write(buffer)
        unsorted_files.append((chunk_id, n_rec, chunk_path))
        print(f"  📦 chunk {chunk_id}: {n_rec:,} 条 ({len(buffer)/1024**3:.2f} GB)")
        chunk_id += 1
        buffer = bytearray()

    for pf_idx, pf in enumerate(part_files):
        fsize = os.path.getsize(pf)
        if fsize == 0:
            continue
        print(f"  📖 [{pf_idx+1}/{len(part_files)}] {Path(pf).name} ({fsize/1024**3:.2f} GB)")

        with open(pf, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            offset = 0
            while offset < fsize:
                remaining = chunk_bytes - len(buffer)
                if remaining <= 0:
                    flush_buffer()
                    remaining = chunk_bytes
                read_size = min(remaining, read_buf_bytes, fsize - offset)
                mm.seek(offset)
                data = mm.read(read_size)
                buffer.extend(data)
                offset += read_size
                total_records += read_size // RECORD_SIZE
            mm.close()

    flush_buffer()
    print(f"  ✅ 共 {total_records:,} 条记录，{len(unsorted_files)} 个 chunk")

    # ---- Pass 2: 多进程并行排序 ----
    print(f"\n  🔧 Pass 2: {workers} 进程并行排序...")
    sorted_dir = tmpdir / "sorted"
    sorted_dir.mkdir()

    sort_tasks = []
    for cid, n_rec, unsorted_path in unsorted_files:
        sorted_path = str(sorted_dir / f"chunk_{cid:04d}.bin")
        sort_tasks.append((unsorted_path, sorted_path))

    chunk_files = []
    total_tmp_bytes = 0
    t_sort_start = time.time()

    from multiprocessing import Pool
    with Pool(workers) as pool:
        results = []
        for unsorted_path, sorted_path in sort_tasks:
            r = pool.apply_async(sort_chunk_file, (unsorted_path, sorted_path))
            results.append(r)

        done = 0
        for r in results:
            sorted_path = r.get(timeout=3600)
            chunk_files.append(sorted_path)
            total_tmp_bytes += os.path.getsize(sorted_path)
            done += 1
            elapsed = time.time() - t_sort_start
            print(f"  ✅ [{done}/{len(sort_tasks)}] 排序完成 ({elapsed:.1f}s)")

    t_sort_end = time.time()
    print(f"  ⏱️ 排序耗时: {t_sort_end - t_sort_start:.1f}s")
    print(f"  📁 临时文件总量: {total_tmp_bytes/1024**3:.2f} GB")

    return chunk_files


# ============================================================
#  第二阶段：归并（批量读写优化）
# ============================================================

class ChunkReader:
    """
    从排序后的 chunk 文件中批量读取记录。
    完全基于 raw bytes 操作，避免 numpy per-record 开销。
    """

    def __init__(self, filepath: str, block_records: int):
        self.f = open(filepath, 'rb')
        self.fsize = os.path.getsize(filepath)
        self.block_bytes = block_records * RECORD_SIZE
        self.buf = b''       # 当前缓冲区（原始字节）
        self.pos = 0         # 当前记录在 buf 中的字节偏移
        self._load_block()

    def _load_block(self):
        remaining = self.fsize - self.f.tell()
        if remaining <= 0:
            self.buf = b''
            return
        read_size = min(self.block_bytes, remaining)
        self.buf = self.f.read(read_size)
        self.pos = 0

    def peek_prefix_bytes(self):
        """返回当前记录前缀的原始字节（8字节，大端序），到末尾返回 None"""
        if self.pos + RECORD_SIZE > len(self.buf):
            if self.f.tell() >= self.fsize and self.pos >= len(self.buf):
                return None
            self._load_block()
            if len(self.buf) < RECORD_SIZE:
                return None
        return self.buf[self.pos:self.pos + PREFIX_SIZE]

    def pop_record(self) -> bytes:
        """取出当前记录（16字节原始字节），并推进位置"""
        if self.pos + RECORD_SIZE > len(self.buf):
            self._load_block()
            if len(self.buf) < RECORD_SIZE:
                return None
        end = self.pos + RECORD_SIZE
        rec = self.buf[self.pos:end]
        self.pos = end
        return rec

    def close(self):
        self.f.close()

    def __lt__(self, other):
        a = self.peek_prefix_bytes()
        b = other.peek_prefix_bytes()
        if a is None: return False
        if b is None: return True
        return a < b


def merge_pass(chunk_files: list, output_path: str,
               block_records: int, label: str) -> int:
    """
    一轮归并：将多个 chunk 文件归并为一个输出文件。
    优化：
    - 批量写入（1MB buffer）
    - 纯字节操作，避免 numpy per-record 开销
    - 预取 prefix 减少函数调用
    """
    readers = []
    for cf in chunk_files:
        r = ChunkReader(cf, block_records)
        if r.peek_prefix_bytes() is not None:
            readers.append(r)

    if not readers:
        return 0

    # 初始化堆：(prefix_bytes, reader_index)
    # bytes 比较在 Python 中是 C 级别的，比 tuple 快
    heap = []
    for idx, reader in enumerate(readers):
        pfx = reader.peek_prefix_bytes()
        if pfx is not None:
            heap.append((pfx, idx))
    heapq.heapify(heap)

    # 批量写入缓冲
    write_buf = bytearray(MERGE_WRITE_BUF_RECORDS * RECORD_SIZE)
    write_pos = 0
    buf_capacity = len(write_buf)

    out = open(output_path, 'wb', buffering=4 * 1024 * 1024)  # 4MB OS buffer
    written = 0
    last_progress = time.time()

    while heap:
        pfx, idx = heapq.heappop(heap)
        reader = readers[idx]
        record = reader.pop_record()
        if record is None:
            reader.close()
            continue

        # 写入缓冲
        write_buf[write_pos:write_pos + RECORD_SIZE] = record
        write_pos += RECORD_SIZE

        # 缓冲满则刷盘
        if write_pos >= buf_capacity:
            out.write(write_buf)
            write_pos = 0

        written += 1

        # 推进该 reader，预取下一个 prefix
        next_pfx = reader.peek_prefix_bytes()
        if next_pfx is not None:
            heapq.heappush(heap, (next_pfx, idx))
        else:
            reader.close()

        now = time.time()
        if now - last_progress >= 5:
            gb = written * RECORD_SIZE / 1024**3
            print(f"     {label}: 已写入 {written:,} 条 ({gb:.2f} GB)")
            last_progress = now

    # 刷出剩余
    if write_pos > 0:
        out.write(write_buf[:write_pos])
    out.close()

    for r in readers:
        try: r.close()
        except: pass

    return written


def merge_sorted_chunks(chunk_files: list, output_path: str,
                         merge_block_records: int, tmpdir: Path,
                         max_open_files: int = 50):
    """
    两轮归并，控制同时打开的文件数。
    """
    if len(chunk_files) <= max_open_files:
        print(f"\n  🔀 一轮归并 {len(chunk_files)} 个 chunk...")
        total = merge_pass(chunk_files, output_path, merge_block_records, "归并")
    else:
        groups = [chunk_files[i:i+max_open_files]
                  for i in range(0, len(chunk_files), max_open_files)]
        print(f"\n  🔀 第一轮归并: {len(chunk_files)} 个 chunk → {len(groups)} 个中间文件")

        intermediates = []
        for gi, group in enumerate(groups):
            mid_path = str(tmpdir / f"merge_pass1_{gi:04d}.bin")
            print(f"  📦 归并组 {gi+1}/{len(groups)} ({len(group)} 个 chunk)...")
            merge_pass(group, mid_path, merge_block_records, f"组{gi+1}")
            intermediates.append(mid_path)

        print(f"\n  🔀 第二轮归并: {len(intermediates)} 个中间文件 → 最终输出")
        total = merge_pass(intermediates, output_path, merge_block_records, "最终")

    print(f"  ✅ 归并完成：{total:,} 条记录，文件大小 {total * RECORD_SIZE / 1024**3:.2f} GB")
    return total


# ============================================================
#  主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="彩虹表索引构建器 - 按 prefix 排序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python build_index.py
  python build_index.py --rainbow-dir D:/table --memory 32
  python build_index.py --tmpdir E:/tmp --output D:/sorted.bin

注意:
  - 内存用于: chunk 数据(~40%) + numpy argsort 索引(~25%) + 开销(~35%)
  - 建议 --memory 设为实际可用内存的 80%（如 32GB 机器用 --memory 24）
  - 临时文件总大小约等于彩虹表大小，存放在 --tmpdir
  - 最终输出文件大小也约等于彩虹表大小
  - 建议把 --tmpdir 和 --output 放在最快的 SSD 上
        """
    )
    parser.add_argument('--rainbow-dir', type=str, default=None,
                        help='彩虹表父目录（默认：脚本同目录）')
    parser.add_argument('--output', type=str, default=None,
                        help='输出文件路径（默认：rainbow_dir/rainbow_sorted.bin）')
    parser.add_argument('--memory', type=float, default=8,
                        help='可用内存上限(GB)，默认 8。排序时实际 chunk 约占 40%%（其余留给 numpy）')
    parser.add_argument('--tmpdir', type=str, default=None,
                        help='临时文件目录（默认：彩虹表同目录）')
    parser.add_argument('--chunk-records', type=int, default=None,
                        help='每个排序 chunk 的记录数（覆盖 --memory）')
    parser.add_argument('--merge-block', type=int, default=500_000,
                        help='归并阶段每个 reader 的读取块大小（记录数），默认 50万')
    parser.add_argument('--read-buffer', type=int, default=64,
                        help='读取彩虹表的缓冲区大小(MB)，默认 64')
    parser.add_argument('--force', action='store_true',
                        help='覆盖已有输出文件，不询问')

    args = parser.parse_args()

    if args.rainbow_dir:
        rainbow_dir = Path(args.rainbow_dir).resolve()
    else:
        rainbow_dir = SCRIPT_DIR

    if args.output:
        output_path = args.output
    else:
        output_path = str(rainbow_dir / "rainbow_sorted.bin")

    if args.tmpdir:
        tmpdir_base = args.tmpdir
    else:
        tmpdir_base = str(rainbow_dir)

    os.makedirs(tmpdir_base, exist_ok=True)

    workers = max((os.cpu_count() or 4) - 2, 1)

    if args.chunk_records:
        chunk_records = args.chunk_records
    else:
        per_worker_bytes = int((args.memory - 2) * 0.4 / workers * 1024**3)
        chunk_records = max(per_worker_bytes // RECORD_SIZE, 1_000_000)

    chunk_gb = chunk_records * RECORD_SIZE / 1024**3
    peak_mem_est = chunk_gb * 2.5 * workers

    total_input_bytes = 0
    for folder_name in RAINBOW_FOLDERS:
        folder = rainbow_dir / folder_name
        if not folder.exists():
            continue
        for i in range(PART_COUNT):
            pf = folder / f"part_{i:03d}.bin"
            if pf.exists():
                total_input_bytes += pf.stat().st_size
    total_input_gb = total_input_bytes / 1024**3

    n_chunks_est = max(total_input_bytes / (chunk_records * RECORD_SIZE), 1) if chunk_records > 0 else 999
    tmp_space_est = total_input_gb

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║            彩虹表索引构建器 - 按 prefix 排序             ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print(f"║  彩虹表目录: {str(rainbow_dir)[:43]}".ljust(59) + "║")
    print(f"║  输出文件:   {str(Path(output_path).name)[:43]}".ljust(59) + "║")
    print(f"║  临时目录:   {str(Path(tmpdir_base).name)[:43]}".ljust(59) + "║")
    print(f"║  并行进程:   {workers}".ljust(59) + "║")
    print(f"║  每进程内存: ~{peak_mem_est / workers:.1f} GB (chunk {chunk_gb:.2f} GB × 2.5)".ljust(59) + "║")
    print(f"║  总内存峰值: ~{peak_mem_est:.1f} GB".ljust(59) + "║")
    print(f"║  预估 chunk: ~{n_chunks_est:.0f} 个".ljust(59) + "║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print("║  📁 磁盘空间需求:                                        ║")
    print(f"║     输入数据:  {total_input_gb:.1f} GB".ljust(59) + "║")
    print(f"║     临时文件:  ~{tmp_space_est:.0f} GB ({tmpdir_base})".ljust(59) + "║")
    print(f"║     输出文件:  ~{total_input_gb:.0f} GB ({Path(output_path).name})".ljust(59) + "║")
    print(f"║     合计:      ~{tmp_space_est + total_input_gb:.0f} GB（临时文件完成后自动删除）".ljust(59) + "║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    if not args.force:
        resp = input("确认开始？(y/N): ").strip().lower()
        if resp != 'y':
            print("已取消")
            return
        print()

    if os.path.exists(output_path):
        if not args.force:
            print(f"⚠️ 输出文件已存在: {output_path}")
            resp = input("覆盖？(y/N): ").strip().lower()
            if resp != 'y':
                print("已取消")
                return
        os.remove(output_path)

    t_start = time.time()

    print(f"📦 第一阶段：分块排序（{workers} 进程并行）")
    print(f"   临时文件写入目录: {tmpdir_base}")
    with tempfile.TemporaryDirectory(prefix='rainbow_sort_', dir=tmpdir_base) as tmpdir:
        print(f"   临时目录: {tmpdir}\n")

        chunk_files = create_sorted_chunks(
            rainbow_dir, chunk_records, Path(tmpdir), args.read_buffer, workers
        )

        t_sort = time.time()
        print(f"  ⏱️ 排序耗时: {t_sort - t_start:.1f}s")

        print(f"\n🔀 第二阶段：归并")
        print(f"   归并后输出: {output_path}\n")
        total = merge_sorted_chunks(
            chunk_files, output_path,
            args.merge_block, Path(tmpdir)
        )

    t_end = time.time()
    print(f"\n{'='*60}")
    print(f"✅ 索引构建完成！")
    print(f"   总记录数: {total:,}")
    print(f"   输出文件: {output_path}")
    print(f"   文件大小: {total * RECORD_SIZE / 1024**3:.2f} GB")
    print(f"   总耗时:   {t_end - t_start:.1f}s ({(t_end-t_start)/60:.1f} 分钟)")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
