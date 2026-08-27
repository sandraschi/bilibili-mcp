"""Generate placeholder PNG assets (icon + dashboard screenshot) without PIL.

Produces a valid 256x256 dark icon and a 1200x600 dark dashboard placeholder
so the repo has real PNGs before a live screenshot is captured. Pure stdlib.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _chunk(tag: bytes, data: bytes) -> bytes:
    c = tag + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)


def make_png(path: Path, width: int, height: int, rgb: tuple[int, int, int]) -> None:
    raw = b""
    row = b"\x00" + bytes(rgb) * width
    for _ in range(height):
        raw += row
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(raw))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def main() -> None:
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    shots = ROOT / "docs" / "screenshots"
    shots.mkdir(parents=True, exist_ok=True)
    make_png(assets / "icon.png", 256, 256, (24, 24, 32))  # zinc-950
    make_png(shots / "dashboard.png", 1200, 600, (24, 24, 32))
    print("wrote assets/icon.png and docs/screenshots/dashboard.png")


if __name__ == "__main__":
    main()
