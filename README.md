# nicedroid-wheels

Static [PEP 503](https://peps.python.org/pep-0503/) wheel index with
[PEP 738](https://peps.python.org/pep-0738/) **Android wheels** for the
nicedroid toolchain (packaging [NiceGUI](https://nicegui.io) apps as Android
APKs via Briefcase/Chaquopy).

**Index URL:** `https://zauberzeug.github.io/nicedroid-wheels/simple/`

```
pip install nicegui --extra-index-url https://zauberzeug.github.io/nicedroid-wheels/simple/
```

## Contents

Two kinds of wheels, fully transparent:

1. **Mirrored wheels** — Android (`android_24_arm64_v8a`, cp313) builds of
   native packages that do not (yet) publish official Android wheels on PyPI:
   pydantic-core, orjson, lxml (+ libxml2/libxslt/libyaml helper wheels),
   pyyaml, markupsafe, yarl, rpds-py. Mirrored unmodified from
   [pypi.flet.dev](https://pypi.flet.dev) (built by the
   [Flet](https://flet.dev) project with
   [Mobile Forge](https://github.com/beeware/mobile-forge)); each file's
   sha256 is pinned in the index. Mirroring makes our builds reproducible and
   independent of a third-party service.
2. **Stub wheels** (`*+stub` versions) — `watchfiles`, `uvloop`, `httptools`:
   tiny pure-Python wheels that **raise `ImportError` on import**. These
   packages are required by NiceGUI / `uvicorn[standard]` metadata but are
   provably unused at runtime on Android (no auto-reload; uvicorn's
   auto-detection treats `ImportError` as "not installed" and falls back to
   asyncio/h11). They exist only so that standard pip resolution works with
   unmodified NiceGUI, and will be removed once NiceGUI's metadata gains
   `sys_platform == "android"` markers. A future real Android wheel with a
   higher version automatically supersedes its stub.

As the ecosystem catches up (e.g. **aiohttp ships official Android wheels on
PyPI since 3.14.1**), entries are removed from this index.

## Regenerating

```bash
python3 tools/build_stubs.py   # stub wheels  -> wheels/
python3 tools/mirror.py        # mirror wheels -> wheels/
python3 tools/make_index.py    # PEP 503 tree  -> simple/
```

All mirrored packages keep their original licenses; see each project.
Maintained by [Zauberzeug](https://zauberzeug.com) — part of the nicedroid
project (NiceGUI on Android).
