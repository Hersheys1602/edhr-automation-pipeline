from pathlib import Path

base = Path(__file__).resolve().parent

paths = [
    base / "state" / "metadata.json",
    base / "data" / "output" / "02S032600010_edhr.json",
    base / "data" / "output" / "02S032600010_edhr.docx",
]

for p in paths:
    if p.exists():
        p.unlink()
        print("Deleted:", p)
    else:
        print("Not found:", p)