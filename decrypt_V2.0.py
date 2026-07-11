#!/usr/bin/env python3
"""
微信视频号批量解密工具 V2.0 - 桶化彩虹表版
=============================================
利用桶化彩虹表查找 decode_key，解密微信视频号加密视频。

V2.0 相比 V1.x 的改进：
  - 使用桶化彩虹表（65536 个桶文件），查找时只加载相关桶（~2.4MB）
  - box_size=28 优先检查（最常见的值）
  - 同一视频的 29 种 box_size 变体命中同一个桶（prefix[4:6] 恒定）
  - 所有路径支持命令行参数配置

原理：
  1. 读取加密视频前 8 字节
  2. 用 prefix[4:6] 计算桶编号，加载对应桶文件（~2.4MB）
  3. 在桶内遍历 box_size（28 优先），二分查找匹配的 decode_key
  4. 用 decode_key 生成完整 128KB 密钥流，反转后 XOR 解密
  5. 验证解密后 ftyp 签名 + box_size + major brand

彩虹表格式（桶文件）：
  每条记录 16 字节 = 8 字节 reversed keystream 前缀 + 8 字节 decode_key (uint64 BE)
  桶文件内部按完整 8 字节前缀字典序升序排列
  桶划分依据：prefix[4:6]（第5-6字节，对同一视频恒定）

用法：
  python decrypt_V2.0.py                            # 解密同目录下所有 .mp4 文件
  python decrypt_V2.0.py video1.mp4 video2.mp4      # 解密指定文件
  python decrypt_V2.0.py --bucket-dir D:/buckets     # 指定桶文件目录
  python decrypt_V2.0.py --scan-only video.mp4      # 仅查找 key，不解密
  python decrypt_V2.0.py --key 1234567890 video.mp4 # 直接用 key 解密

依赖：
  Python 3.8+
  可选: numpy (加速解密)
  Node.js (用于 Isaac64 密钥流生成)
  wasm_video_decode.wasm + wasm_video_decode.js (同目录)
"""

import os
import sys
import struct
import mmap
import subprocess
import time
import argparse
from pathlib import Path

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# ============================================================
#  配置项（默认值，可通过命令行参数覆盖）
# ============================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
KEYSTREAM_SIZE = 131072  # 128 KB
RECORD_SIZE = 16         # 每条彩虹表记录 16 字节
PREFIX_SIZE = 8          # reversed keystream 前缀 8 字节
NUM_BUCKETS = 65536      # 桶数量

# 默认路径
DEFAULT_BUCKET_DIR = SCRIPT_DIR / "buckets"   # 桶文件目录
DEFAULT_RAINBOW_DIR = SCRIPT_DIR              # 原始彩虹表目录（回退扫描用）

# MP4 ftyp 签名（字节 4-7）
FTYP_SIGNATURE = b'\x66\x74\x79\x70'  # 'ftyp'
# box_size 范围
BOX_SIZE_MIN, BOX_SIZE_MAX = 20, 48
# 优先检查的 box_size（最常见的值）
BOX_SIZE_PRIORITY = 28


# ============================================================
#  桶化索引查找
# ============================================================

def lookup_bucket(bucket_dir: str, enc_header_8: bytes) -> list:
    """
    在桶化彩虹表中查找匹配的 decode_key。

    桶划分依据：prefix[4:6]（对同一视频恒定 = enc[4:5] XOR "ft"）
    同一视频的所有 box_size 变体命中同一个桶。

    Args:
        bucket_dir: 桶文件目录路径
        enc_header_8: 加密视频的前 8 字节

    Returns:
        去重后的 decode_key 字符串列表，桶目录不存在时返回 None
    """
    # 计算桶编号（对同一视频恒定）
    bucket_id = (enc_header_8[4] << 8) | enc_header_8[5]

    # 加载桶文件
    bucket_path = os.path.join(bucket_dir, f"bucket_{bucket_id:04X}.bin")
    if not os.path.exists(bucket_path):
        # 桶目录存在但该桶文件不存在，说明视频不在这个彩虹表范围内
        return []

    bucket_size = os.path.getsize(bucket_path)
    if bucket_size == 0:
        return []

    n_records = bucket_size // RECORD_SIZE

    # ftyp 签名
    FTYP = b'\x66\x74\x79\x70'

    with open(bucket_path, 'rb') as f:
        def binary_search(target: bytes) -> int:
            """返回第一个 prefix >= target 的索引"""
            lo, hi = 0, n_records - 1
            while lo < hi:
                mid = (lo + hi) // 2
                f.seek(mid * RECORD_SIZE)
                mid_prefix = f.read(PREFIX_SIZE)
                if mid_prefix < target:
                    lo = mid + 1
                else:
                    hi = mid
            return lo

        def read_record(idx: int):
            f.seek(idx * RECORD_SIZE)
            data = f.read(RECORD_SIZE)
            return data[:PREFIX_SIZE], struct.unpack('>Q', data[PREFIX_SIZE:])[0]

        found_keys = []
        seen = set()

        # 构造 box_size 检查顺序：优先 28，然后 20-48（跳过 28）
        box_sizes = [BOX_SIZE_PRIORITY] + [
            bs for bs in range(BOX_SIZE_MIN, BOX_SIZE_MAX + 1)
            if bs != BOX_SIZE_PRIORITY
        ]

        for box_size in box_sizes:
            box_bytes = struct.pack('>I', box_size)

            # 构造目标 8 字节前缀
            target_prefix = bytes([
                enc_header_8[0] ^ box_bytes[0],
                enc_header_8[1] ^ box_bytes[1],
                enc_header_8[2] ^ box_bytes[2],
                enc_header_8[3] ^ box_bytes[3],
                enc_header_8[4] ^ FTYP[0],
                enc_header_8[5] ^ FTYP[1],
                enc_header_8[6] ^ FTYP[2],
                enc_header_8[7] ^ FTYP[3],
            ])

            # 二分查找
            idx = binary_search(target_prefix)

            # 检查命中
            prefix, key_int = read_record(idx)
            if prefix == target_prefix:
                key_str = str(key_int).zfill(10)
                if key_str not in seen:
                    seen.add(key_str)
                    found_keys.append(key_str)

    return found_keys


def find_bucket_dir(rainbow_dir: Path) -> str:
    """查找桶文件目录路径，不存在则返回 None"""
    candidates = [
        rainbow_dir / "buckets",
        rainbow_dir / "bucket",
    ]
    for c in candidates:
        if c.exists() and any(c.glob("bucket_*.bin")):
            return str(c)
    return None


# ============================================================
#  彩虹表扫描（回退方案）
# ============================================================

RAINBOW_FOLDERS = ["0-20亿", "20亿-40亿", "40亿-80亿", "80亿-100亿"]
PART_COUNT = 19


def scan_part_file_numpy(part_path: str, enc_header_8: bytes, ftyp_xor: bytes) -> list:
    """使用 numpy 向量化扫描单个 part 文件"""
    results = []
    try:
        fsize = os.path.getsize(part_path)
        if fsize == 0:
            return results

        n_records = fsize // RECORD_SIZE
        if n_records == 0:
            return results

        ftyp_target = np.frombuffer(ftyp_xor, dtype=np.uint8)
        CHUNK_RECORDS = 10_000_000
        CHUNK_BYTES = CHUNK_RECORDS * RECORD_SIZE

        with open(part_path, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            offset = 0
            while offset < fsize:
                chunk_end = min(offset + CHUNK_BYTES, fsize)
                chunk_size = chunk_end - offset
                mm.seek(offset)
                raw = mm.read(chunk_size)
                n_chunk = chunk_size // RECORD_SIZE
                data = np.frombuffer(raw, dtype=np.uint8)
                records = data[:n_chunk * RECORD_SIZE].reshape(n_chunk, RECORD_SIZE)
                ftyp_bytes = records[:, 4:8]
                match_mask = np.all(ftyp_bytes == ftyp_target, axis=1)
                match_indices = np.where(match_mask)[0]
                for idx in match_indices:
                    key_bytes = records[idx, PREFIX_SIZE:RECORD_SIZE].tobytes()
                    key_int = struct.unpack('>Q', key_bytes)[0]
                    key_str = str(key_int).zfill(10)
                    results.append((key_str,))
                offset = chunk_end
            mm.close()
    except Exception as e:
        print(f"  ⚠️ 扫描 {Path(part_path).name} 出错: {e}")
    return results


def scan_part_file_plain(part_path: str, enc_header_8: bytes, ftyp_xor: bytes) -> list:
    """纯 Python 扫描单个 part 文件"""
    results = []
    try:
        fsize = os.path.getsize(part_path)
        if fsize == 0:
            return results
        with open(part_path, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            offset = 0
            while offset + RECORD_SIZE <= fsize:
                prefix_ftyp = mm[offset + 4:offset + 8]
                if prefix_ftyp == ftyp_xor:
                    key_bytes = mm[offset + PREFIX_SIZE:offset + RECORD_SIZE]
                    key_int = struct.unpack('>Q', key_bytes)[0]
                    key_str = str(key_int).zfill(10)
                    results.append((key_str,))
                offset += RECORD_SIZE
            mm.close()
    except Exception as e:
        print(f"  ⚠️ 扫描 {Path(part_path).name} 出错: {e}")
    return results


def collect_part_files(rainbow_dir: Path) -> list:
    """收集所有彩虹表 part 文件路径"""
    part_files = []
    for folder_name in RAINBOW_FOLDERS:
        folder = rainbow_dir / folder_name
        if not folder.exists():
            continue
        for i in range(PART_COUNT):
            part_path = folder / f"part_{i:03d}.bin"
            if part_path.exists():
                part_files.append(str(part_path))
    return part_files


def scan_rainbow_table(rainbow_dir: Path, enc_header_8: bytes) -> list:
    """全量扫描彩虹表（回退方案）"""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    part_files = collect_part_files(rainbow_dir)
    if not part_files:
        print("  ❌ 未找到任何彩虹表文件！")
        return []

    scan_fn = scan_part_file_numpy if HAS_NUMPY else scan_part_file_plain
    mode_label = "numpy 向量化" if HAS_NUMPY else "纯 Python"
    print(f"  📂 找到 {len(part_files)} 个彩虹表文件 (扫描模式: {mode_label})")

    ftyp_xor = bytes(enc_header_8[4+i] ^ FTYP_SIGNATURE[i] for i in range(4))

    all_matches = []
    completed = 0
    total = len(part_files)
    workers = max((os.cpu_count() or 4) - 2, 1)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(scan_fn, pf, enc_header_8, ftyp_xor): pf
            for pf in part_files
        }
        for future in as_completed(futures):
            completed += 1
            pf = futures[future]
            try:
                matches = future.result()
                if matches:
                    all_matches.extend(matches)
                    print(f"  ✅ [{completed}/{total}] {Path(pf).name}: "
                          f"找到 {len(matches)} 个匹配")
                else:
                    if completed % 10 == 0 or completed == total:
                        print(f"  ⏳ [{completed}/{total}] 扫描中...")
            except Exception as e:
                print(f"  ❌ [{completed}/{total}] {Path(pf).name}: {e}")

    seen = set()
    unique = []
    for key_str, *_ in all_matches:
        if key_str not in seen:
            seen.add(key_str)
            unique.append(key_str)
    return unique


# ============================================================
#  密钥流生成与解密
# ============================================================

def generate_keystream(decode_key: str) -> bytes:
    """调用 Node.js helper 生成 131072 字节的 reversed keystream"""
    gen_script = SCRIPT_DIR / "keystream_gen.js"
    if not gen_script.exists():
        raise FileNotFoundError(f"找不到密钥流生成脚本: {gen_script}")

    result = subprocess.run(
        ["node", str(gen_script), decode_key],
        capture_output=True,
        timeout=30,
        cwd=str(SCRIPT_DIR)
    )

    if result.returncode != 0:
        stderr = result.stderr.decode('utf-8', errors='replace')
        raise RuntimeError(f"密钥流生成失败 (key={decode_key}): {stderr}")

    ks = result.stdout
    if len(ks) != KEYSTREAM_SIZE:
        raise RuntimeError(f"密钥流大小异常: 期望 {KEYSTREAM_SIZE}, 实际 {len(ks)}")
    return ks


def decrypt_video(enc_data: bytes, keystream: bytes) -> bytes:
    """用密钥流解密视频数据（前 128KB XOR，后续保留）"""
    decrypt_len = min(KEYSTREAM_SIZE, len(enc_data))
    if HAS_NUMPY:
        enc_arr = np.frombuffer(enc_data, dtype=np.uint8).copy()
        ks_arr = np.frombuffer(keystream[:decrypt_len], dtype=np.uint8)
        enc_arr[:decrypt_len] ^= ks_arr
        return enc_arr.tobytes()
    else:
        dec = bytearray(enc_data)
        for i in range(decrypt_len):
            dec[i] = enc_data[i] ^ keystream[i]
        return bytes(dec)


def verify_mp4_ftyp(data: bytes) -> bool:
    """验证解密后数据的 ftyp 签名（字节 4-7）"""
    if len(data) < 8:
        return False
    return data[4:8] == FTYP_SIGNATURE


def verify_mp4_header_full(data: bytes) -> bool:
    """验证解密后数据是否为有效的 MP4 ftyp box"""
    if len(data) < 12:
        return False
    if data[4:8] != FTYP_SIGNATURE:
        return False
    box_size = struct.unpack('>I', data[0:4])[0]
    if box_size < BOX_SIZE_MIN or box_size > BOX_SIZE_MAX:
        return False
    return True


# ============================================================
#  主流程
# ============================================================

def process_video(video_path: Path, bucket_dir: str, rainbow_dir: Path):
    """处理单个加密视频文件"""
    print(f"\n{'='*60}")
    print(f"📹 处理文件: {video_path.name}")
    print(f"{'='*60}")

    # 1. 读取加密视频前 8 字节
    with open(video_path, 'rb') as f:
        enc_header = f.read(8)
    if len(enc_header) < 8:
        print(f"  ❌ 文件太小，不足 8 字节")
        return

    print(f"  🔒 加密头前 8 字节: {enc_header.hex()}")
    print(f"  📋 ftyp 签名:       {FTYP_SIGNATURE.hex()} (字节 4-7 固定)")

    # 2. 查找 decode_key
    print(f"\n  🔍 查找 decode_key...")
    t0 = time.time()

    found_keys = None

    # 优先使用桶化索引
    if bucket_dir:
        bucket_id = (enc_header[4] << 8) | enc_header[5]
        print(f"  ⚡ 使用桶化索引 (桶 {bucket_id:04X}, "
              f"box_size={BOX_SIZE_PRIORITY} 优先)")
        found_keys = lookup_bucket(bucket_dir, enc_header)
        elapsed = time.time() - t0
        if found_keys is not None:
            print(f"  ⏱️ 查找耗时: {elapsed*1000:.1f}ms")

    # 回退：全量扫描
    if found_keys is None:
        print(f"  📂 未找到桶化索引，回退全量扫描")
        print(f"     (运行 build_buckets_V1.0.py 可大幅加速)")
        found_keys = scan_rainbow_table(rainbow_dir, enc_header)
        elapsed = time.time() - t0
        print(f"  ⏱️ 扫描耗时: {elapsed:.1f}s")

    if not found_keys:
        print(f"\n  ❌ 未找到匹配的 decode_key！")
        return

    print(f"\n  🎉 找到 {len(found_keys)} 个候选 decode_key:")
    for key_str in found_keys:
        print(f"     🔑 {key_str}")

    # 3. 读取完整加密视频
    file_size_mb = video_path.stat().st_size / 1024 / 1024
    print(f"\n  📖 读取加密视频 ({file_size_mb:.1f} MB)...")
    with open(video_path, 'rb') as f:
        enc_data = f.read()

    # 4. 逐个候选 key 验证并解密
    valid_keys = []
    for key_str in found_keys:
        print(f"\n  🔧 验证 key: {key_str}")
        try:
            print(f"     ⏳ 生成密钥流...")
            ks = generate_keystream(key_str)
            print(f"     ✅ 密钥流生成完成 ({len(ks)} bytes)")

            dec_header = bytearray(12)
            for i in range(12):
                dec_header[i] = enc_data[i] ^ ks[i]
            dec_header = bytes(dec_header)

            if verify_mp4_header_full(dec_header):
                box_size = struct.unpack('>I', dec_header[0:4])[0]
                brand = dec_header[8:12].decode('ascii', errors='replace')
                print(f"     ✅ MP4 验证通过！ "
                      f"(box_size={box_size}, brand={brand})")
                valid_keys.append((key_str, ks))
            else:
                if dec_header[4:8] == FTYP_SIGNATURE:
                    print(f"     ⚠️ ftyp 匹配但 box_size/brand 异常: "
                          f"{dec_header[:12].hex()}")
                else:
                    print(f"     ❌ ftyp 不匹配")
        except Exception as e:
            print(f"     ❌ 生成密钥流出错: {e}")

    if not valid_keys:
        print(f"\n  ❌ 所有候选 key 验证均失败！")
        return

    # 5. 解密并保存
    print(f"\n  💾 有效 decode_key: {len(valid_keys)} 个")
    for key_str, ks in valid_keys:
        print(f"     🔓 解密中...")
        dec_data = decrypt_video(enc_data, ks)

        if not verify_mp4_ftyp(dec_data):
            print(f"     ❌ key {key_str}: 最终验证失败，跳过")
            continue

        stem = video_path.stem
        suffix = video_path.suffix
        out_name = f"{stem}_key{key_str}{suffix}"
        out_path = video_path.parent / out_name

        with open(out_path, 'wb') as f:
            f.write(dec_data)

        print(f"     ✅ 已保存: {out_name} "
              f"({len(dec_data) / 1024 / 1024:.1f} MB)")


def decrypt_with_key(video_path: Path, decode_key: str):
    """用指定的 decode_key 直接解密视频"""
    print(f"\n{'='*60}")
    print(f"📹 解密: {video_path.name}")
    print(f"🔑 Key:  {decode_key}")
    print(f"{'='*60}")

    if not decode_key.isdigit() or len(decode_key) != 10:
        print(f"  ❌ decode_key 必须是10位纯数字，当前: {decode_key}")
        return False

    file_size_mb = video_path.stat().st_size / 1024 / 1024
    print(f"  📖 读取视频 ({file_size_mb:.1f} MB)...")
    with open(video_path, 'rb') as f:
        enc_data = f.read()

    print(f"  ⏳ 生成密钥流...")
    try:
        ks = generate_keystream(decode_key)
    except Exception as e:
        print(f"  ❌ {e}")
        return False
    print(f"  ✅ 密钥流生成完成 ({len(ks)} bytes)")

    dec_header = bytearray(12)
    for i in range(12):
        dec_header[i] = enc_data[i] ^ ks[i]
    dec_header = bytes(dec_header)

    if verify_mp4_header_full(dec_header):
        box_size = struct.unpack('>I', dec_header[0:4])[0]
        brand = dec_header[8:12].decode('ascii', errors='replace')
        print(f"  ✅ MP4 验证通过 (box_size={box_size}, brand={brand})")
    else:
        if dec_header[4:8] == FTYP_SIGNATURE:
            print(f"  ⚠️ ftyp 匹配但 box_size 异常，继续解密...")
        else:
            print(f"  ⚠️ ftyp 不匹配，key 可能错误，但仍尝试解密...")

    print(f"  🔓 解密中...")
    dec_data = decrypt_video(enc_data, ks)

    stem = video_path.stem
    suffix = video_path.suffix
    out_name = f"{stem}_key{decode_key}{suffix}"
    out_path = video_path.parent / out_name

    with open(out_path, 'wb') as f:
        f.write(dec_data)

    print(f"  ✅ 已保存: {out_name} ({len(dec_data) / 1024 / 1024:.1f} MB)")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="微信视频号批量解密工具 V2.0 - 桶化彩虹表版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python decrypt_V2.0.py                            # 解密同目录下所有 .mp4
  python decrypt_V2.0.py video1.mp4 video2.mp4      # 解密指定文件
  python decrypt_V2.0.py --bucket-dir D:/buckets     # 指定桶文件目录
  python decrypt_V2.0.py --scan-only video.mp4      # 仅查找 key，不解密
  python decrypt_V2.0.py --key 1234567890 video.mp4 # 直接用 key 解密

V2.0 改进:
  - 桶化彩虹表：查找时只加载相关桶（~2.4MB），而非整个索引
  - box_size=28 优先检查（最常见的值）
  - 同一视频所有 box_size 命中同一桶

依赖:
  Python 3.8+, 可选 numpy, Node.js, wasm_video_decode.wasm/.js
        """
    )
    parser.add_argument('videos', nargs='*',
                        help='要解密的 MP4 文件路径（默认：同目录下所有 .mp4）')
    parser.add_argument('--key', type=str, default=None,
                        help='直接指定 decode_key 解密（跳过彩虹表查找）')
    parser.add_argument('--bucket-dir', type=str, default=None,
                        help=f'桶文件目录（默认：自动查找或 {DEFAULT_BUCKET_DIR}）')
    parser.add_argument('--rainbow-dir', type=str, default=None,
                        help=f'原始彩虹表目录（回退扫描用，默认：{DEFAULT_RAINBOW_DIR}）')
    parser.add_argument('--scan-only', action='store_true',
                        help='仅查找 decode_key，不解密视频')

    args = parser.parse_args()

    # 解析视频文件列表
    if args.videos:
        video_files = [Path(v).resolve() for v in args.videos]
        for vf in video_files:
            if not vf.exists():
                print(f"❌ 文件不存在: {vf}")
                sys.exit(1)
    else:
        video_files = []

    # 直接 key 解密模式
    if args.key:
        if not video_files:
            print("❌ 使用 --key 时必须指定视频文件")
            sys.exit(1)
        for vf in video_files:
            decrypt_with_key(vf, args.key)
        return

    # 桶化索引 / 彩虹表路径
    if args.bucket_dir:
        bucket_dir = str(Path(args.bucket_dir).resolve())
    else:
        bucket_dir = find_bucket_dir(Path(SCRIPT_DIR))

    if args.rainbow_dir:
        rainbow_dir = Path(args.rainbow_dir).resolve()
    else:
        rainbow_dir = DEFAULT_RAINBOW_DIR

    # 检查依赖
    if not (SCRIPT_DIR / "keystream_gen.js").exists():
        print(f"❌ 找不到 keystream_gen.js，请确保它和本脚本在同一目录")
        sys.exit(1)
    if not (SCRIPT_DIR / "wasm_video_decode.wasm").exists():
        print(f"❌ 找不到 wasm_video_decode.wasm，请确保它和本脚本在同一目录")
        sys.exit(1)

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║        微信视频号批量解密工具 V2.0 - 桶化彩虹表版        ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    if bucket_dir:
        print(f"║  桶文件目录:  {str(bucket_dir)[:42]}".ljust(59) + "║")
    else:
        print(f"║  桶文件目录:  未找到（将回退全量扫描）".ljust(59) + "║")
    print(f"║  验证方式:    ftyp 签名 + box_size + brand".ljust(59) + "║")
    print(f"║  优先 box_size: {BOX_SIZE_PRIORITY}".ljust(59) + "║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    # 默认：脚本同目录下所有 .mp4 文件（排除已解密的 _key 文件）
    if not video_files:
        for f in sorted(SCRIPT_DIR.glob("*.mp4")):
            if "_key" in f.stem:
                continue
            video_files.append(f)

        if not video_files:
            print("❌ 当前目录下未找到 .mp4 文件")
            print("   请将加密视频放到此目录，或通过参数指定文件路径")
            sys.exit(1)

    print(f"📹 待处理视频: {len(video_files)} 个")
    for vf in video_files:
        size_mb = vf.stat().st_size / 1024 / 1024
        print(f"   • {vf.name} ({size_mb:.1f} MB)")

    # 处理每个视频
    t_start = time.time()
    for vf in video_files:
        if args.scan_only:
            with open(vf, 'rb') as f:
                enc_header = f.read(8)
            print(f"\n🔍 {vf.name}: enc={enc_header.hex()}")
            if bucket_dir:
                t0 = time.time()
                found_keys = lookup_bucket(bucket_dir, enc_header)
                elapsed = time.time() - t0
                if found_keys is not None:
                    print(f"   ⏱️ 查找: {elapsed*1000:.1f}ms "
                          f"(桶 {(enc_header[4]<<8)|enc_header[5]:04X})")
                else:
                    found_keys = scan_rainbow_table(rainbow_dir, enc_header)
            else:
                found_keys = scan_rainbow_table(rainbow_dir, enc_header)
            if found_keys:
                for key_str in found_keys:
                    print(f"   🔑 {key_str}")
            else:
                print(f"   ❌ 未找到")
        else:
            process_video(vf, bucket_dir, rainbow_dir)

    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"✅ 全部完成！总耗时: {elapsed:.1f}s")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
