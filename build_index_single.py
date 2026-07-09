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

# numpy 结构化 dtype：8字节prefix + 8字节key
# 用两个 uint64 比直接用 bytes 排序更快、内存更紧凑
DTYPE = np.dtype([('prefix', 'u8'), ('key', 'u8')])


def swap_u64_bytes(arr: np.ndarray) -> np.ndarray:
    """将 uint64 数组的字节序反转（大端 ↔ 小端），in-place。"""
    arr.view(np.uint8).reshape(-1, 8)[:, ::-1] = \
        arr.view(np.uint8).reshape(-1, 8)[:, ::-1].copy()


# ============================================================
#  第一阶段：分块排序（numpy in-place）
# ============================================================

def sort_chunk_numpy(raw: bytes) -> bytes:
    """
    用 numpy 对一块二进制记录按 prefix 排序。
    数据是大端序，排序时需要转为本机字节序比较，但不修改原数据。
    """
    n = len(raw) // RECORD_SIZE
    arr = np.frombuffer(raw, dtype=DTYPE, count=n).copy()

    # 用 argsort 对 byteswap 后的 prefix 排序（不修改原数据）
    order = arr['prefix'].byteswap().argsort()
    arr = arr[order]

    return arr.tobytes()


def create_sorted_chunks(rainbow_dir: Path, chunk_records: int,
                          tmpdir: Path, read_buffer_mb: int) -> list:
    """
    读取彩虹表，按 chunk 排序后写入临时文件。
    返回临时文件路径列表。
    """
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
    chunk_files = []
    buffer = bytearray()
    total_records = 0
    chunk_id = 0
    total_tmp_bytes = 0

    def flush_buffer():
        nonlocal buffer, chunk_id, total_tmp_bytes
        if not buffer:
            return
        n_rec = len(buffer) // RECORD_SIZE
        print(f"  🔧 排序 chunk {chunk_id}: {n_rec:,} 条记录 ({len(buffer)/1024**3:.2f} GB)...")
        sorted_data = sort_chunk_numpy(bytes(buffer))
        chunk_path = tmpdir / f"chunk_{chunk_id:04d}.bin"
        with open(chunk_path, 'wb') as f:
            f.write(sorted_data)
        chunk_files.append(str(chunk_path))
        total_tmp_bytes += len(sorted_data)
        chunk_id += 1
        # 释放内存
        buffer = bytearray()
        del sorted_data

    for pf_idx, pf in enumerate(part_files):
        fsize = os.path.getsize(pf)
        if fsize == 0:
            continue

        print(f"  📖 [{pf_idx+1}/{len(part_files)}] {Path(pf).name} ({fsize/1024**3:.2f} GB)")

        with open(pf, 'rb') as f:
            import mmap
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

    print(f"  ✅ 共 {total_records:,} 条记录，分为 {len(chunk_files)} 个 chunk")
    print(f"  📁 临时文件总量: {total_tmp_bytes/1024**3:.2f} GB")
    return chunk_files


# ============================================================
#  第二阶段：两轮归并（控制内存）
# ============================================================

class ChunkReader:
    """从排序后的 chunk 文件中逐条读取记录，使用 numpy 减少内存拷贝"""

    def __init__(self, filepath: str, block_records: int):
        self.filepath = filepath
        self.block_bytes = block_records * RECORD_SIZE
        self.f = open(filepath, 'rb')
        self.fsize = os.path.getsize(filepath)
        self.arr = None   # numpy 结构化数组视图
        self.idx = 0      # 当前消费位置
        self.total = 0    # 总记录数
        self._load_block()

    def _load_block(self):
        remaining = self.fsize - self.f.tell()
        if remaining <= 0:
            self.arr = None
            return
        read_size = min(self.block_bytes, remaining)
        raw = self.f.read(read_size)
        n = len(raw) // RECORD_SIZE
        self.arr = np.frombuffer(raw, dtype=DTYPE, count=n)
        self.idx = 0
        self.total = n

    def peek_prefix(self):
        """返回当前记录的 prefix（大端序 uint64），已到末尾返回 None"""
        if self.arr is None or self.idx >= self.total:
            self._load_block()
            if self.arr is None or self.idx >= self.total:
                return None
        # numpy 读出来是本机字节序，需要 byteswap 回大端
        return int(self.arr[self.idx]['prefix'].byteswap())

    def pop_record(self) -> bytes:
        """取出当前记录（16字节，大端序），并推进位置"""
        if self.arr is None or self.idx >= self.total:
            self._load_block()
            if self.arr is None or self.idx >= self.total:
                return None
        # 文件本身就是大端序，直接取原始字节
        rec = bytes(self.arr[self.idx])
        self.idx += 1
        return rec

    def close(self):
        self.f.close()

    def __lt__(self, other):
        a = self.peek_prefix()
        b = other.peek_prefix()
        if a is None: return False
        if b is None: return True
        return a < b


def merge_pass(chunk_files: list, output_path: str,
               block_records: int, label: str) -> int:
    """一轮归并：将多个 chunk 文件归并为一个输出文件"""
    readers = []
    for cf in chunk_files:
        r = ChunkReader(cf, block_records)
        if r.peek_prefix() is not None:
            readers.append(r)

    if not readers:
        return 0

    # 初始化堆：(prefix_uint64, reader_index)
    heap = []
    for idx, reader in enumerate(readers):
        pfx = reader.peek_prefix()
        if pfx is not None:
            heap.append((pfx, idx))
    heapq.heapify(heap)

    out = open(output_path, 'wb')
    written = 0
    last_progress = time.time()

    while heap:
        pfx, idx = heapq.heappop(heap)
        reader = readers[idx]
        record = reader.pop_record()
        if record is None:
            reader.close()
            continue

        out.write(record)
        written += 1

        next_pfx = reader.peek_prefix()
        if next_pfx is not None:
            heapq.heappush(heap, (next_pfx, idx))
        else:
            reader.close()

        now = time.time()
        if now - last_progress >= 5:
            gb = written * RECORD_SIZE / 1024**3
            print(f"     {label}: 已写入 {written:,} 条 ({gb:.2f} GB)")
            last_progress = now

    out.close()
    # 清理已读完的 reader
    for r in readers:
        try: r.close()
        except: pass

    return written


def merge_sorted_chunks(chunk_files: list, output_path: str,
                         merge_block_records: int, tmpdir: Path,
                         max_open_files: int = 50):
    """
    两轮归并，控制同时打开的文件数。
    第一轮：每 max_open_files 个 chunk 合并为一个中间文件
    第二轮：将所有中间文件合并为最终输出
    """
    total_intermediates = []

    if len(chunk_files) <= max_open_files:
        # chunk 数量不多，一轮搞定
        print(f"\n  🔀 一轮归并 {len(chunk_files)} 个 chunk...")
        total = merge_pass(chunk_files, output_path, merge_block_records, "归并")
    else:
        # 第一轮：分组归并
        groups = [chunk_files[i:i+max_open_files]
                  for i in range(0, len(chunk_files), max_open_files)]
        print(f"\n  🔀 第一轮归并: {len(chunk_files)} 个 chunk → {len(groups)} 个中间文件")

        intermediates = []
        for gi, group in enumerate(groups):
            mid_path = str(tmpdir / f"merge_pass1_{gi:04d}.bin")
            print(f"  📦 归并组 {gi+1}/{len(groups)} ({len(group)} 个 chunk)...")
            merge_pass(group, mid_path, merge_block_records, f"组{gi+1}")
            intermediates.append(mid_path)

        total_intermediates = intermediates

        # 第二轮：归并中间文件
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

    # 临时目录
    if args.tmpdir:
        tmpdir_base = args.tmpdir
    else:
        tmpdir_base = str(rainbow_dir)

    # 确保临时目录存在
    os.makedirs(tmpdir_base, exist_ok=True)

    # 计算 chunk 大小
    # numpy argsort 需要额外 8字节/条的索引数组，加上原始数据和视图，
    # 实际需要约 2.5x chunk 数据量的内存
    if args.chunk_records:
        chunk_records = args.chunk_records
    else:
        # 系统保留 2GB，剩余的 40% 用于 chunk 数据（留 60% 给 numpy 排序）
        available_bytes = int((args.memory - 2) * 0.4 * 1024**3)
        chunk_records = max(available_bytes // RECORD_SIZE, 1_000_000)

    chunk_gb = chunk_records * RECORD_SIZE / 1024**3

    # 扫描实际数据量
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
    tmp_space_est = total_input_gb  # 临时文件约等于输入大小

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║            彩虹表索引构建器 - 按 prefix 排序             ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print(f"║  彩虹表目录: {str(rainbow_dir)[:43]}".ljust(59) + "║")
    print(f"║  输出文件:   {str(Path(output_path).name)[:43]}".ljust(59) + "║")
    print(f"║  临时目录:   {str(Path(tmpdir_base).name)[:43]}".ljust(59) + "║")
    print(f"║  排序内存:   {args.memory:.1f} GB".ljust(59) + "║")
    print(f"║  Chunk 大小: {chunk_records:,} 条 ({chunk_gb:.2f} GB)".ljust(59) + "║")
    print(f"║  预估 chunk: ~{n_chunks_est:.0f} 个".ljust(59) + "║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print("║  📁 磁盘空间需求:                                        ║")
    print(f"║     输入数据:  {total_input_gb:.1f} GB".ljust(59) + "║")
    print(f"║     临时文件:  ~{tmp_space_est:.0f} GB ({tmpdir_base})".ljust(59) + "║")
    print(f"║     输出文件:  ~{total_input_gb:.0f} GB ({Path(output_path).name})".ljust(59) + "║")
    print(f"║     合计:      ~{tmp_space_est + total_input_gb:.0f} GB（临时文件完成后自动删除）".ljust(59) + "║")
    print("╚═══════════════════════════════════════════════════════════╝")
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

    # 第一阶段：分块排序
    print("📦 第一阶段：分块排序（numpy in-place）")
    print(f"   临时文件写入目录: {tmpdir_base}")
    with tempfile.TemporaryDirectory(prefix='rainbow_sort_', dir=tmpdir_base) as tmpdir:
        print(f"   临时目录: {tmpdir}\n")

        chunk_files = create_sorted_chunks(
            rainbow_dir, chunk_records, Path(tmpdir), args.read_buffer
        )

        t_sort = time.time()
        print(f"  ⏱️ 排序耗时: {t_sort - t_start:.1f}s")

        # 第二阶段：归并
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
