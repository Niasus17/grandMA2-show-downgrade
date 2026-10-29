"""Перевод шоу grandMA2 (.show.gz) под более старую версию 3.9.x.

Формат (проверено 2026-10-30 на 3.9.60.45 / 3.9.61.5 / 3.9.63.11): .show.gz — gzip с заголовком ровно 10 байт
(без имени и времени, OS=0x0b), внутри поток «MA DATA\\0». Байты 8–11 потока — версия MA младшим байтом вперёд:
build, release, minor, major (3.9.60.45 = 2d 3c 09 03). Байты 16–19 — указатель на последнюю запись истории, его не трогать.
Устройство объектов между 3.9.60, 3.9.61 и 3.9.63 одинаковое: перевод = записать версию цели в байты 8–11 и упаковать как MA.
Шоу, где используются функции только новой версии, не проверены.

Один модуль — и для вкладки «Обмен» Extended Remote, и для отдельной программы «grandMA2 Show Downgrade».
"""
from __future__ import annotations

import gzip
import struct
import zlib
from pathlib import Path

MAGIC = b"MA DATA\x00"
# известные сборки grandMA2 3.9 (сайт MA и сторонние источники); проверены вживую — VERIFIED
KNOWN = ["3.9.60.45", "3.9.60.65", "3.9.60.91",
         "3.9.61.1", "3.9.61.3", "3.9.61.5",
         "3.9.63.6", "3.9.63.10", "3.9.63.11"]
VERIFIED = {"3.9.60.45", "3.9.61.5", "3.9.63.11"}


def parse_ver(s: str) -> tuple[int, int, int, int]:
    p = [int(x) for x in str(s).strip().split(".")]
    if len(p) != 4 or p[0] != 3 or p[1] != 9 or not all(0 <= x <= 255 for x in p):
        raise ValueError("версия — 3.9.<выпуск>.<сборка>, например 3.9.60.45")
    return p[0], p[1], p[2], p[3]


def ver_str(v: tuple[int, int, int, int]) -> str:
    return ".".join(map(str, v))


def read_version(path: Path | str) -> tuple[int, int, int, int]:
    """Версия шоу — без распаковки целиком (первые 12 байт потока)."""
    with gzip.open(path, "rb") as f:
        head = f.read(12)
    if head[:8] != MAGIC:
        raise ValueError("это не шоу grandMA2 (нет «MA DATA»)")
    b, r, mi, ma = head[8], head[9], head[10], head[11]
    return ma, mi, r, b


def targets(src: tuple[int, int, int, int]) -> list[str]:
    """Куда имеет смысл переводить: известные 3.9-версии ниже версии шоу (более новая MA откроет его и так)."""
    return [v for v in KNOWN if parse_ver(v) < src]


def ma_gzip(data: bytes) -> bytes:
    """gzip как у MA: заголовок 10 байт без имени и времени, raw deflate, crc32 и длина."""
    c = zlib.compressobj(6, zlib.DEFLATED, -15)
    body = c.compress(data) + c.flush()
    return b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x0b" + body + struct.pack("<II", zlib.crc32(data) & 0xFFFFFFFF, len(data) & 0xFFFFFFFF)


def convert(src: Path | str, target: str, dst: Path | str | None = None) -> Path:
    """Шоу src → под версию target. dst не задан — рядом: «имя (3.9.60.45).show.gz»; существующий файл не затирается."""
    src = Path(src)
    t = parse_ver(target)
    data = bytearray(gzip.decompress(src.read_bytes()))
    if bytes(data[:8]) != MAGIC:
        raise ValueError("это не шоу grandMA2 (нет «MA DATA»)")
    cur = (data[11], data[10], data[9], data[8])
    if t >= cur:
        raise ValueError(f"шоу и так версии {ver_str(cur)} — переводить можно только в более старую")
    data[8:12] = bytes([t[3], t[2], t[1], t[0]])
    if dst is None:
        stem = src.name[:-8] if src.name.lower().endswith(".show.gz") else src.stem
        dst = src.with_name(f"{stem} ({target}).show.gz")
    dst = Path(dst)
    if dst.exists():
        base = dst.name[:-8]
        for i in range(2, 100):
            dst = dst.with_name(f"{base} {i}.show.gz")
            if not dst.exists():
                break
    tmp = dst.with_name(dst.name + ".part")
    tmp.write_bytes(ma_gzip(bytes(data)))
    tmp.replace(dst)
    return dst
