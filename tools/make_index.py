#!/usr/bin/env python3
"""Erzeugt aus wheels/*.whl einen statischen PEP-503-Index unter simple/.

Wird von GitHub Pages ausgeliefert; pip nutzt ihn via
  --extra-index-url https://zauberzeug.github.io/nicedroid-wheels/simple/
"""

import hashlib
import re
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
WHEELS = ROOT / "wheels"
SIMPLE = ROOT / "simple"


def normalize(name: str) -> str:
    """PEP-503-Projektname: lowercase, Läufe von -_. zu einem '-'."""
    return re.sub(r"[-_.]+", "-", name).lower()


def main() -> None:
    projects: dict[str, list[Path]] = defaultdict(list)
    for whl in sorted(WHEELS.glob("*.whl")):
        projects[normalize(whl.name.split("-")[0])].append(whl)

    if SIMPLE.exists():
        shutil.rmtree(SIMPLE)
    SIMPLE.mkdir()

    for project, files in sorted(projects.items()):
        links = []
        for whl in files:
            digest = hashlib.sha256(whl.read_bytes()).hexdigest()
            links.append(
                f'    <a href="../../wheels/{whl.name}#sha256={digest}">{whl.name}</a><br>'
            )
        (SIMPLE / project).mkdir()
        (SIMPLE / project / "index.html").write_text(
            "<!DOCTYPE html><html><head><title>{p}</title></head><body>\n"
            "{links}\n</body></html>\n".format(p=project, links="\n".join(links))
        )

    (SIMPLE / "index.html").write_text(
        "<!DOCTYPE html><html><head><title>nicedroid-wheels</title></head><body>\n"
        + "\n".join(f'    <a href="{p}/">{p}</a><br>' for p in sorted(projects))
        + "\n</body></html>\n"
    )
    # Pages/Jekyll würde Pfade mit Unterstrichen ignorieren → abschalten
    (ROOT / ".nojekyll").touch()
    print(f"Index: {len(projects)} Projekte, {sum(len(f) for f in projects.values())} Wheels")


if __name__ == "__main__":
    main()
