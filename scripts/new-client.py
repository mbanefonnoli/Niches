#!/usr/bin/env python3
"""Create a client folder from templates/client.

Usage: python scripts/new-client.py <niche> "<Client Name>"
Example: python scripts/new-client.py horeca "Example Distributor SRL"
"""
import datetime
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "client"
NICHES = ROOT / "niches"
TEXT_SUFFIXES = {".md", ".csv", ".txt"}


def slugify(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")
    if not slug:
        raise SystemExit("Client name gives an empty folder name; use letters or digits.")
    return slug


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    niche, client_name = sys.argv[1], sys.argv[2].strip()

    niche_dir = NICHES / niche
    if not niche_dir.is_dir():
        available = ", ".join(sorted(p.name for p in NICHES.iterdir() if p.is_dir()))
        raise SystemExit(f"Unknown niche '{niche}'. Available: {available}")

    target = niche_dir / "clients" / slugify(client_name)
    if target.exists():
        raise SystemExit(f"Already exists: {target.relative_to(ROOT)}")

    shutil.copytree(TEMPLATE, target)
    for sub in ("assets", "brand", "outputs"):
        (target / sub).mkdir(exist_ok=True)
        keep = target / sub / ".gitkeep"
        if not any((target / sub).iterdir()):
            keep.touch()

    today = datetime.date.today().isoformat()
    for f in target.rglob("*"):
        if f.is_file() and f.suffix in TEXT_SUFFIXES:
            text = f.read_text(encoding="utf-8")
            text = (text.replace("{{CLIENT_NAME}}", client_name)
                        .replace("{{NICHE}}", niche)
                        .replace("{{DATE}}", today))
            f.write_text(text, encoding="utf-8")

    print(f"Created {target.relative_to(ROOT)}")
    print("Next: put the client's files in assets/, then run intake (studio-core, stage 2).")


if __name__ == "__main__":
    main()
