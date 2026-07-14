#!/usr/bin/env python3
"""Erzeugt die nicedroid-Android-Stub-Wheels (deterministisch, ohne Build-Backend).

Hintergrund (TOOLCHAIN.md, Schritt 1): NiceGUI bzw. `uvicorn[standard]` fordern
watchfiles/uvloop/httptools, für die es keine Android-Wheels gibt — zur Laufzeit
werden sie aber nachweislich nicht gebraucht (kein watchfiles-Import bei
reload=False; uvicorn fällt bei ImportError sauber auf asyncio/h11 zurück).
Diese Stubs stellen pip zufrieden und werfen beim Import ImportError — exakt das
Signal, das uvicorns Auto-Detection als „nicht installiert" behandelt.

Versionen tragen ein `+stub`-Local-Label: erfüllt alle Constraints
(watchfiles>=0.20, uvloop>=0.15.1, httptools>=0.8.0) und wird von künftigen
echten Android-Wheels mit höherer Version automatisch verdrängt.

Wird obsolet, sobald der NiceGUI-Upstream-PR (sys_platform-Marker) gemergt ist.
"""

import base64
import hashlib
import zipfile
from pathlib import Path

STUBS = {
    "watchfiles": "1.2.0+stub",
    "uvloop": "0.22.1+stub",
    "httptools": "0.8.0+stub",
}

DIST = Path(__file__).parent.parent / "wheels"
ZIP_DATE = (2026, 1, 1, 0, 0, 0)  # fixe Zeitstempel → reproduzierbare Wheels


def _record_entry(path: str, data: bytes) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
    return f"{path},sha256={digest},{len(data)}"


def build_stub(name: str, version: str) -> Path:
    init = (
        f'raise ImportError(\n'
        f'    "{name} is a nicedroid Android stub (no real Android wheel exists; "\n'
        f'    "not needed at runtime — uvicorn/nicegui fall back cleanly). "\n'
        f'    "See zauberzeug/nicedroid wheelindex/README.md."\n'
        f')\n'
    ).encode()
    metadata = (
        f"Metadata-Version: 2.1\n"
        f"Name: {name}\n"
        f"Version: {version}\n"
        f"Summary: nicedroid Android stub — raises ImportError on import\n"
        f"Home-page: https://github.com/zauberzeug/nicedroid\n"
    ).encode()
    wheel_meta = (
        "Wheel-Version: 1.0\n"
        "Generator: nicedroid-build-stubs\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n"
    ).encode()

    dist_info = f"{name}-{version}.dist-info"
    files = {
        f"{name}/__init__.py": init,
        f"{dist_info}/METADATA": metadata,
        f"{dist_info}/WHEEL": wheel_meta,
    }
    record = "\n".join(
        [_record_entry(p, d) for p, d in files.items()] + [f"{dist_info}/RECORD,,", ""]
    ).encode()

    DIST.mkdir(exist_ok=True)
    whl = DIST / f"{name}-{version}-py3-none-any.whl"
    with zipfile.ZipFile(whl, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, data in {**files, f"{dist_info}/RECORD": record}.items():
            info = zipfile.ZipInfo(path, date_time=ZIP_DATE)
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
    return whl


if __name__ == "__main__":
    for name, version in STUBS.items():
        print(f"built {build_stub(name, version).name}")
