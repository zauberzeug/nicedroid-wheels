#!/usr/bin/env python3
"""Spiegelt die benötigten Android-Wheels von pypi.flet.dev nach wheels/.

Supply-Chain-Versicherung für die nicedroid-Toolchain: Builds sollen nicht live
von einem fremden Index abhängen. Gespiegelt wird je Projekt nur die neueste
Version der cp313/arm64-Wheels (bzw. py3-none für die reinen C-Lib-Pakete).

Nutzung:  python3 tools/mirror.py            # lädt nach wheels/
Danach:   python3 tools/make_index.py        # PEP-503-Index neu erzeugen
"""

import re
import urllib.request
from pathlib import Path

SOURCE = "https://pypi.flet.dev"
WHEELS = Path(__file__).parent.parent / "wheels"

# Projekte, deren native Android-Wheels wir (noch) nicht von PyPI bekommen.
# Rausnehmen, sobald ein Projekt offizielle Android-Wheels publiziert
# (wie aiohttp seit 3.14.1).
PROJECTS = [
    "pydantic-core",
    "orjson",
    "lxml",
    "flet-libxml2",   # C-Libs für lxml
    "flet-libxslt",
    "flet-libyaml",   # C-Lib für pyyaml
    "pyyaml",
    "markupsafe",
    "yarl",
    "rpds-py",        # für jsonschema/mcp
    # NICHT gespiegelt: multidict/frozenlist/propcache — liefern auf PyPI
    # pure-Python-Fallback-Wheels (py3-none-any); aiohttp publiziert seit
    # 3.14.1 selbst offizielle Android-Wheels auf PyPI.
]

MATCH = re.compile(r"-(?:cp313-cp313|py3-none)-android_24_arm64_v8a\.whl$")


def _version_key(filename: str):
    # Wheel-Name: {name}-{version}[-{build}]-{python}-{abi}-{platform}.whl
    parts = filename[:-4].split("-")
    version, build = parts[1], parts[2] if len(parts) == 6 else "0"
    key = [int(x) if x.isdigit() else 0 for x in re.split(r"[.+]", version)]
    return (key, int(build) if build.isdigit() else 0)


def mirror(project: str) -> None:
    try:
        with urllib.request.urlopen(f"{SOURCE}/{project}/") as r:
            html = r.read().decode()
    except urllib.error.HTTPError as e:
        print(f"!! {project}: {SOURCE} antwortet {e.code}")
        return
    candidates = {}
    for href, name in re.findall(r'href="([^"]+)"[^>]*>([^<]+\.whl)', html):
        if MATCH.search(name):
            candidates[name] = href
    if not candidates:
        print(f"!! {project}: keine passenden Wheels auf {SOURCE}")
        return
    newest = max(candidates, key=_version_key)
    dest = WHEELS / newest
    if dest.exists():
        print(f"   {newest} (schon da)")
        return
    url = candidates[newest]
    if url.startswith("/"):
        url = SOURCE + url
    urllib.request.urlretrieve(url, dest)
    print(f"++ {newest} ({dest.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    WHEELS.mkdir(exist_ok=True)
    for project in PROJECTS:
        mirror(project)
