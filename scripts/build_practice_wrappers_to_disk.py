"""One-time generator: write Markdown wrappers to disk for practice .py files.

This is a fallback to ensure the site works immediately if mkdocs-gen-files
virtual generation is not taking effect in your environment. It creates
`docs/OpAgentsOlympus/practice/<name>.md` for each `.py` file in the same folder when a
wrapper does not already exist. Safe to run multiple times.

Usage:
    python scripts/build_practice_wrappers_to_disk.py
"""
from __future__ import annotations

from pathlib import Path

DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"
PRACTICE = DOCS_ROOT / "OpAgentsOlympus" / "practice"

SKIP = {
    "tempCodeRunnerFile.py",
}

WRAPPER = """# {title}

???+ note "Source code in OpAgentsOlympus/practice/{filename}"
    ```python title="OpAgentsOlympus/practice/{filename}"
    --8<-- "{filename}"
    ```
"""

def titleize(stem: str) -> str:
    return " ".join(p.capitalize() for p in stem.replace("_", " ").split())


def main() -> None:
    if not PRACTICE.exists():
        raise SystemExit(f"Practice folder not found: {PRACTICE}")

    created = 0
    for py in sorted(PRACTICE.glob("*.py")):
        if py.name in SKIP:
            continue
        md = py.with_suffix(".md")
        if md.exists():
            continue
        md.write_text(WRAPPER.format(title=titleize(py.stem), filename=py.name), encoding="utf-8")
        print(f"Wrote {md.relative_to(DOCS_ROOT)}")
        created += 1

    print(f"Done. {created} wrapper(s) created.")


if __name__ == "__main__":
    main()
