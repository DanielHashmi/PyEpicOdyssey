#!/usr/bin/env python
"""
generate_ref_files.py

Create missing Markdown reference stubs for mkdocstrings.

Usage:
    python scripts/generate_ref_files.py

This scans your `src/` tree for Python modules and creates
`docs/ref/.../*.md` stubs that use mkdocstrings directives (:::).
Existing .md files are preserved.
"""
from __future__ import annotations

from pathlib import Path
from string import capwords

# ---- Paths -----------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent  # repo root
SRC_ROOT = REPO_ROOT / "src"  # scan entire src tree
DOCS_ROOT = REPO_ROOT / "docs" / "PyDeepOlympus"  # where stubs go

# ---- Helpers ---------------------------------------------------------

def discover_top_packages(src_root: Path) -> set[str]:
    """Return names of top-level packages under src/ (dirs with __init__.py)."""
    pkgs: set[str] = set()
    if not src_root.exists():
        return pkgs
    for p in src_root.iterdir():
        if p.is_dir() and (p / "__init__.py").exists():
            pkgs.add(p.name)
    return pkgs


def to_identifier(py_path: Path, top_packages: set[str]) -> str | None:
    """Convert src/<pkg>/foo/bar.py -> '<pkg>.foo.bar'.

    Returns None for files not under a recognized top-level package.
    Handles __init__.py by returning the package path without the final segment.
    """
    try:
        rel = py_path.relative_to(SRC_ROOT)
    except ValueError:
        return None

    parts = list(rel.parts)
    if not parts:
        return None

    top = parts[0]
    if top not in top_packages:
        return None

    # Drop suffix and handle __init__.py specially
    if parts[-1] == "__init__.py":
        # Remove the file and keep the package path
        parts = parts[:-1]
    else:
        parts[-1] = Path(parts[-1]).stem

    return ".".join(parts)


def md_target(py_path: Path) -> Path:
    """Return docs/ref/.../*.md path corresponding to py_path under src/."""
    rel = py_path.relative_to(SRC_ROOT)
    if rel.name == "__init__.py":
        rel = rel.with_name("index.py")  # map package __init__ to index.md
    return (DOCS_ROOT / rel).with_suffix(".md")


def pretty_title(last_segment: str) -> str:
    """Convert 'tool_context' -> 'Tool Context'."""
    cleaned = last_segment.replace("_", " ").replace("-", " ")
    return capwords(cleaned)


# ---- Main ------------------------------------------------------------

def main() -> None:
    if not SRC_ROOT.exists():
        raise SystemExit(f"Source path not found: {SRC_ROOT}")

    top_packages = discover_top_packages(SRC_ROOT)
    if not top_packages:
        print("No top-level packages discovered under src/. Nothing to do.")
        return

    created = 0
    for py_file in SRC_ROOT.rglob("*.py"):
        # Skip dunder/private modules
        if py_file.name.startswith("_"):
            continue

        identifier = to_identifier(py_file, top_packages)
        if not identifier:
            continue

        md_path = md_target(py_file)
        if md_path.exists():
            continue  # keep existing

        md_path.parent.mkdir(parents=True, exist_ok=True)

        title_seg = identifier.split(".")[-1]
        title = pretty_title(title_seg)

        md_content = f"""# `{title}`

::: {identifier}
    handler: python
    options:
      show_source: true
"""
        md_path.write_text(md_content, encoding="utf-8")
        created += 1
        try:
            rel_print = md_path.relative_to(REPO_ROOT)
        except ValueError:
            rel_print = md_path
        print(f"Created {rel_print}")

    if created == 0:
        print("All reference files were already present.")
    else:
        print(f"Done. {created} new file(s) created.")


if __name__ == "__main__":
    main()
