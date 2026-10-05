"""Cut a stored bottom-origin bbox out of a caller RGB raster."""

from __future__ import annotations

import math
import struct
import zlib

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def crop_bbox(
    pixels: bytes,
    width: int,
    height: int,
    bbox: tuple[float, float, float, float] | None,
) -> bytes | None:
    if bbox is None:
        return None
    x0, y0, x1, y1 = bbox
    row0 = _clamp(math.floor((1.0 - y1) * height), height)
    row1 = _clamp(math.ceil((1.0 - y0) * height), height)
    col0 = _clamp(math.floor(x0 * width), width)
    col1 = _clamp(math.ceil(x1 * width), width)
    if row1 <= row0 or col1 <= col0:
        return None
    out_w = col1 - col0
    span = out_w * 3
    cropped = bytearray((row1 - row0) * span)
    dst = 0
    for row in range(row0, row1):
        start = (row * width + col0) * 3
        cropped[dst : dst + span] = pixels[start : start + span]
        dst += span
    return _encode_png_rgb(bytes(cropped), out_w, row1 - row0)


def _clamp(value: int, limit: int) -> int:
    if value < 0:
        return 0
    if value > limit:
        return limit
    return value


def _encode_png_rgb(pixels: bytes, width: int, height: int) -> bytes:
    stride = width * 3
    raw = bytearray()
    for row in range(height):
        raw.append(0)
        raw.extend(pixels[row * stride : (row + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        _PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw)))
        + _chunk(b"IEND", b"")
    )


def _chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)
