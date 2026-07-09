#!/usr/bin/env python3
"""
微信视频号批量解密工具 - 彩虹表版
====================================
利用彩虹表查找 decode_key，解密微信视频号加密视频。

原理：
  1. 读取加密视频前 8 字节
  2. 遍历所有可能的 box_size（20~48），结合 ftyp 签名构造完整 8 字节前缀
  3. 在排序索引上二分查找匹配的 decode_key（或全量扫描）
  4. 用 decode_key 生成完整 128KB 密钥流，反转后 XOR 解密
  5. 验证解密后 ftyp 签名 + box_size + major brand

彩虹表格式：
  每条记录 16 字节 = 8 字节 reversed keystream 前缀 + 8 字节 decode_key (uint64 大端序)
  每个 part 文件约 2GB，包含约 1.31 亿条记录

用法：
  python decrypt.py                          # 解密同目录下所有 .mp4 文件
  python decrypt.py video1.mp4 video2.mp4    # 解密指定文件
  python decrypt.py --rainbow-dir D:/table   # 指定彩虹表父目录
  python decrypt.py --scan-only video.mp4    # 仅查找 key，不解密
"""

import os
import sys
import struct
import mmap
import subprocess
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# ============================================================
#  配置
# ============================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
KEYSTREAM_SIZE = 131072  # 128 KB
RECORD_SIZE = 16         # 每条彩虹表记录 16 字节
PREFIX_SIZE = 8          # reversed keystream 前缀 8 字节

# 4 个彩虹表文件夹名
RAINBOW_FOLDERS = ["0-20亿", "20亿-40亿", "40亿-80亿", "80亿-100亿"]
PART_COUNT = 19  # 每个文件夹 19 个 part 文件 (part_000.bin ~ part_018.bin)

# MP4 ftyp 签名（字节 4-7，唯一固定部分）
FTYP_SIGNATURE = b'\x66\x74\x79\x70'  # 'ftyp'
# 常见 major brand（用于验证，非严格过滤）
COMMON_BRANDS = [
    b'isom', b'iso2', b'iso3', b'iso4', b'iso5', b'iso6',
    b'mp41', b'mp42', b'mp71',
    b'avc1', b'avci', b'avcl',
    b'M4A ', b'M4V ', b'M4VP', b'M4A ',
    b'MSNV', b'MSDA', b'MSDB',
    b'NDAS', b'NDSC', b'NDSH', b'NDSM', b'NDSP', b'NDSS', b'NDXC', b'NDXH', b'NDXM', b'NDXP', b'NDXS',
    b'f4v ', b'kddi', b'LGMM', b'MMP4', b'MTK ', b'Nokia', b'SAMS', b'SGH1',
]
# box_size 常见范围
BOX_SIZE_MIN, BOX_SIZE_MAX = 20, 48

# ============================================================
#  排序索引二分查找
# =============================================================

def lookup_sorted_index(sorted_path: str, enc_header_8: bytes) -> list:
    """
    在已排序的索引文件中查找匹配的 decode_key。

    由于 MP4 只有 ftyp 签名（字节 4-7）是固定的，box_size（字节 0-3）可变，
    我们遍历所有可能的 box_size（20~48），对每个构造完整的 8 字节前缀，
    在排序索引上做二分查找。

    Args:
        sorted_path: 排序索引文件路径
        enc_header_8: 加密视频的前 8 字节

    Returns:
        去重后的 decode_key 字符串列表
    """
    fsize = os.path.getsize(sorted_path)
    n_records = fsize // RECORD_SIZE
    if n_records == 0:
        return []

    # ftyp 签名（固定）
    FTYP = b'\x66\x74\x79\x70'  # 'ftyp'

    def read_record(idx: int):
        f.seek(idx * RECORD_SIZE)
        data = f.read(RECORD_SIZE)
        return data[:PREFIX_SIZE], struct.unpack('>Q', data[PREFIX_SIZE:])[0]

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

    found_keys = []
    seen = set()

    with open(sorted_path, 'rb') as f:
        # 遍历所有可能的 box_size (20~48)
        for box_size in range(20, 49):
            box_bytes = struct.pack('>I', box_size)

            # 构造目标 8 字节前缀:
            # prefix[i] = enc[i] XOR plain[i]
            # plain[0:4] = box_bytes (大端序，不反转)
            # plain[4:8] = ftyp
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


def find_sorted_index(rainbow_dir: Path) -> str:
    """查找排序索引文件路径，不存在则返回 None"""
    candidates = [
        rainbow_dir / "rainbow_sorted.bin",
        rainbow_dir / "sorted.bin",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


# ============================================================
#  彩虹表扫描（回退方案）
# ============================================================

def scan_part_file_numpy(part_path: str, enc_header_8: bytes, ftyp_xor: bytes) -> list:
    """
    使用 numpy 向量化扫描单个 part 文件。
    检查每条记录的 prefix[4:8] 是否匹配 ftyp XOR 结果。
    返回 [(decode_key_str,), ...]
    """
    results = []
    try:
        fsize = os.path.getsize(part_path)
        if fsize == 0:
            return results

        n_records = fsize // RECORD_SIZE
        if n_records == 0:
            return results

        ftyp_target = np.frombuffer(ftyp_xor, dtype=np.uint8)

        # 分块处理，每块 1000 万条记录（约 160MB）
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

                # 只比较 prefix 的后4字节（bytes 4-7，对应 ftyp 签名）
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
    """
    纯 Python 扫描单个 part 文件（无 numpy 依赖时使用）。
    检查每条记录的 prefix[4:8] 是否匹配 ftyp XOR 结果。
    """
    results = []
    try:
        fsize = os.path.getsize(part_path)
        if fsize == 0:
            return results

        with open(part_path, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            offset = 0
            while offset + RECORD_SIZE <= fsize:
                # 只比较 prefix 的后4字节（bytes 4-7，对应 ftyp 签名）
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
            print(f"  ⚠️ 彩虹表文件夹不存在: {folder}")
            continue
        for i in range(PART_COUNT):
            part_path = folder / f"part_{i:03d}.bin"
            if part_path.exists():
                part_files.append(str(part_path))
    return part_files


def scan_rainbow_table(rainbow_dir: Path, enc_header_8: bytes) -> list:
    """
    全量扫描彩虹表，查找匹配的 decode_key。
    对每条记录，用 ftyp 签名计算前缀，检查前 4 字节是否匹配。
    返回去重后的 decode_key 字符串列表。
    """
    part_files = collect_part_files(rainbow_dir)
    if not part_files:
        print("  ❌ 未找到任何彩虹表文件！")
        return []

    scan_fn = scan_part_file_numpy if HAS_NUMPY else scan_part_file_plain
    mode_label = "numpy 向量化" if HAS_NUMPY else "纯 Python"
    print(f"  📂 找到 {len(part_files)} 个彩虹表文件 (扫描模式: {mode_label})")

    # 预计算所有可能的前缀（基于不同 box_size）
    ftyp_xor = bytes(enc_header_8[4+i] ^ FTYP_SIGNATURE[i] for i in range(4))
    # ftyp_xor 是 reversed keystream 的 bytes[4:8]

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
                    print(f"  ✅ [{completed}/{total}] {Path(pf).name}: 找到 {len(matches)} 个匹配")
                else:
                    if completed % 10 == 0 or completed == total:
                        print(f"  ⏳ [{completed}/{total}] 扫描中...")
            except Exception as e:
                print(f"  ❌ [{completed}/{total}] {Path(pf).name}: {e}")

    # 去重
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
    """
    调用 Node.js helper 生成 131072 字节的 reversed keystream。
    """
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
    """
    用密钥流解密视频数据。
    前 128KB 逐字节 XOR，后续部分原样保留。
    """
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
    """
    验证解密后数据的 ftyp 签名（字节 4-7）。
    只检查这4字节是否为 'ftyp'，因为其他字节可变。
    """
    if len(data) < 8:
        return False
    return data[4:8] == FTYP_SIGNATURE


def verify_mp4_header_full(data: bytes) -> bool:
    """
    验证解密后数据是否为有效的 MP4 ftyp box。
    检查: ftyp 签名 + box_size 合理性。
    major brand 仅用于日志，不作为硬性过滤条件。
    """
    if len(data) < 12:
        return False
    # 检查 ftyp 签名
    if data[4:8] != FTYP_SIGNATURE:
        return False
    # 检查 box_size 是否在合理范围
    box_size = struct.unpack('>I', data[0:4])[0]
    if box_size < BOX_SIZE_MIN or box_size > BOX_SIZE_MAX:
        return False
    return True


# ============================================================
#  主流程
# ============================================================

def process_video(video_path: Path, rainbow_dir: Path):
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

    # 2. 查找 decode_key（优先排序索引，回退全量扫描）
    print(f"\n  🔍 查找 decode_key...")
    t0 = time.time()

    sorted_index = find_sorted_index(rainbow_dir)
    if sorted_index:
        print(f"  ⚡ 使用排序索引: {Path(sorted_index).name}")
        print(f"     遍历 box_size {BOX_SIZE_MIN}~{BOX_SIZE_MAX}，逐个二分查找...")
        found_keys = lookup_sorted_index(sorted_index, enc_header)
        elapsed = time.time() - t0
        print(f"  ⏱️ 查找耗时: {elapsed*1000:.1f}ms")
    else:
        print(f"  📂 未找到排序索引，回退全量扫描（运行 build_index.py 可大幅加速）")
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
            # 生成完整密钥流
            print(f"     ⏳ 生成密钥流...")
            ks = generate_keystream(key_str)
            print(f"     ✅ 密钥流生成完成 ({len(ks)} bytes)")

            # 解密前 12 字节验证 ftyp 签名 + box_size + major brand
            dec_header = bytearray(12)
            for i in range(12):
                dec_header[i] = enc_data[i] ^ ks[i]
            dec_header = bytes(dec_header)

            if verify_mp4_header_full(dec_header):
                box_size = struct.unpack('>I', dec_header[0:4])[0]
                brand = dec_header[8:12].decode('ascii', errors='replace')
                print(f"     ✅ MP4 验证通过！ (box_size={box_size}, brand={brand})")
                valid_keys.append((key_str, ks))
            else:
                if dec_header[4:8] == FTYP_SIGNATURE:
                    print(f"     ⚠️ ftyp 匹配但 box_size/brand 异常: {dec_header[:12].hex()}")
                else:
                    print(f"     ❌ ftyp 不匹配 (got {dec_header[4:8].hex()}, expected {FTYP_SIGNATURE.hex()})")
        except Exception as e:
            print(f"     ❌ 生成密钥流出错: {e}")

    if not valid_keys:
        print(f"\n  ❌ 所有候选 key 验证均失败！")
        return

    # 5. 解密并保存
    print(f"\n  💾 有效 decode_key: {len(valid_keys)} 个")
    for key_str, ks in valid_keys:
        # 解密完整视频
        print(f"     🔓 解密中...")
        dec_data = decrypt_video(enc_data, ks)

        # 最终验证
        if not verify_mp4_ftyp(dec_data):
            print(f"     ❌ key {key_str}: 最终验证失败，跳过")
            continue

        # 生成输出文件名
        stem = video_path.stem
        suffix = video_path.suffix
        out_name = f"{stem}_key{key_str}{suffix}"
        out_path = video_path.parent / out_name

        with open(out_path, 'wb') as f:
            f.write(dec_data)

        print(f"     ✅ 已保存: {out_name} ({len(dec_data) / 1024 / 1024:.1f} MB)")


def decrypt_with_key(video_path: Path, decode_key: str):
    """用指定的 decode_key 直接解密视频"""
    print(f"\n{'='*60}")
    print(f"📹 解密: {video_path.name}")
    print(f"🔑 Key:  {decode_key}")
    print(f"{'='*60}")

    # 验证 key 格式
    if not decode_key.isdigit() or len(decode_key) != 10:
        print(f"  ❌ decode_key 必须是10位纯数字，当前: {decode_key}")
        return False

    # 读取视频
    file_size_mb = video_path.stat().st_size / 1024 / 1024
    print(f"  📖 读取视频 ({file_size_mb:.1f} MB)...")
    with open(video_path, 'rb') as f:
        enc_data = f.read()

    # 生成密钥流
    print(f"  ⏳ 生成密钥流...")
    try:
        ks = generate_keystream(decode_key)
    except Exception as e:
        print(f"  ❌ {e}")
        return False
    print(f"  ✅ 密钥流生成完成 ({len(ks)} bytes)")

    # 解密前12字节验证
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

    # 解密
    print(f"  🔓 解密中...")
    dec_data = decrypt_video(enc_data, ks)

    # 保存
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
        description="微信视频号批量解密工具 - 彩虹表版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python build_index.py                        # 先构建排序索引（一次性）
  python decrypt.py                            # 解密同目录下所有 .mp4 文件
  python decrypt.py video1.mp4 video2.mp4      # 解密指定文件
  python decrypt.py --rainbow-dir D:/table     # 指定彩虹表父目录
  python decrypt.py --scan-only video.mp4      # 仅查找 key，不解密
  python decrypt.py --key 1234567890 video.mp4 # 直接用 key 解密（跳过彩虹表）

有排序索引时自动使用二分查找（<1ms），无索引时回退全量扫描（~36s）。
运行 build_index.py 可构建排序索引。

依赖:
  Python 3.8+
  可选: numpy (加速全量扫描)
  Node.js (用于 Isaac64 密钥流生成)
  wasm_video_decode.wasm + wasm_video_decode.js (同目录)
        """
    )
    parser.add_argument('videos', nargs='*', help='要解密的 MP4 文件路径（默认：同目录下所有 .mp4）')
    parser.add_argument('--key', type=str, default=None,
                        help='直接指定 decode_key 解密（跳过彩虹表查找）')
    parser.add_argument('--rainbow-dir', type=str, default=None,
                        help='彩虹表父目录（默认：脚本同目录）')
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

    # 彩虹表查找模式
    if args.rainbow_dir:
        rainbow_dir = Path(args.rainbow_dir).resolve()
    else:
        rainbow_dir = SCRIPT_DIR

    if not rainbow_dir.exists():
        print(f"❌ 彩虹表目录不存在: {rainbow_dir}")
        sys.exit(1)

    # 检查依赖
    if not (SCRIPT_DIR / "keystream_gen.js").exists():
        print(f"❌ 找不到 keystream_gen.js，请确保它和本脚本在同一目录")
        sys.exit(1)
    if not (SCRIPT_DIR / "wasm_video_decode.wasm").exists():
        print(f"❌ 找不到 wasm_video_decode.wasm，请确保它和本脚本在同一目录")
        sys.exit(1)
    if not (SCRIPT_DIR / "wasm_video_decode.js").exists():
        print(f"❌ 找不到 wasm_video_decode.js，请确保它和本脚本在同一目录")
        sys.exit(1)

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║          微信视频号批量解密工具 - 彩虹表版               ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print(f"║  彩虹表目录: {str(rainbow_dir)[:43]}".ljust(59) + "║")
    print(f"║  验证方式:   ftyp 签名 (字节 4-7) + box_size + brand".ljust(59) + "║")
    sorted_idx = find_sorted_index(rainbow_dir)
    if sorted_idx:
        print(f"║  排序索引:   {Path(sorted_idx).name}".ljust(59) + "║")
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
    sorted_index = find_sorted_index(rainbow_dir)
    if sorted_index:
        print(f"⚡ 排序索引: {sorted_index}")

    t_start = time.time()
    for vf in video_files:
        if args.scan_only:
            with open(vf, 'rb') as f:
                enc_header = f.read(8)
            print(f"\n🔍 {vf.name}: enc={enc_header.hex()}")
            if sorted_index:
                t0 = time.time()
                found_keys = lookup_sorted_index(sorted_index, enc_header)
                elapsed = time.time() - t0
                print(f"   ⏱️ 查找: {elapsed*1000:.1f}ms")
            else:
                found_keys = scan_rainbow_table(rainbow_dir, enc_header)
            if found_keys:
                for key_str in found_keys:
                    print(f"   🔑 {key_str}")
            else:
                print(f"   ❌ 未找到")
        else:
            process_video(vf, rainbow_dir)

    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"✅ 全部完成！总耗时: {elapsed:.1f}s")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
