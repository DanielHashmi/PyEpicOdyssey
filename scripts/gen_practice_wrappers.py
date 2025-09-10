"""Generate Markdown wrappers for Python example files at build time.

This script is executed by the mkdocs-gen-files plugin during `mkdocs build` or
`mkdocs serve`. It scans `docs/OpAgentsOlympus/practice/` for `.py` files and creates
virtual `.md` wrapper pages (if a corresponding `.md` file does not already
exist on disk) so that Python files render inline with collapsible, highlighted
source using pymdownx.snippets.

Rules:
- If an explicit `.md` wrapper file already exists beside the `.py`, we do not
  overwrite it (your hand-authored content wins).
- Only `.py` files are wrapped. You can extend the script if you want more types.
- Skips clearly transient or undesirable files by name.
"""
from __future__ import annotations

import traceback
from pathlib import Path

import mkdocs_gen_files
from mkdocs_gen_files import config as gen_config

PRACTICE_DIR = Path(gen_config.docs_dir).resolve() / "OpAgentsOlympus" / "practice"

# Names to skip (case-sensitive)
SKIP_FILES = {
    "tempCodeRunnerFile.py",
}

# Directories to skip
SKIP_DIRS = {
    "openai-agents-python",
}

WRAPPER_TEMPLATE = """# {title}\n\n???+ note \"Source code in OpAgentsOlympus/practice/{filename}\"\n    ```python title=\"OpAgentsOlympus/practice/{filename}\"\n    --8<-- \"{filename}\"\n    ```\n"""

WRAPPER_TEMPLATE_ABS = """# {title}\n\n???+ note \"Source code in {abs_path}\"\n    ```python title=\"{abs_path}\"\n    --8<-- \"{abs_path}\"\n    ```\n"""

WRAPPER_TEMPLATE_INCLUDE_RAW = """# {title}\n\n--8<-- \"{abs_path}\"\n"""

INDEX_HEADER = """# 100 MCQs Answer\n\nBelow are all MCQ example scripts, rendered with collapsible source.\n"""
PRACTICE_INDEX_HEADER = """# All Practice Examples\n\nQuick index of all practice scripts.\n"""

def title_from_stem(stem: str) -> str:
    # Simple titleizer: replace underscores with spaces and capitalize words
    return " ".join(part.capitalize() for part in stem.replace("_", " ").split())


def main() -> None:
    try:
        docs_root = Path(gen_config.docs_dir).resolve()
        practice_dir = docs_root / "OpAgentsOlympus" / "practice"
        agents_dir = docs_root / "OpAgentsOlympus"
        # Preferred MCQ source location (kept inside docs tree, near practice examples)
        mcq_src_dir = docs_root / "OpAgentsOlympus" / "practice" / "mcqs-src"
        mcq_default_dir = docs_root / "OpAgentsOlympus" / "practice" / "100 MCQs Answer"
        print(f"[gen-files] Practice wrapper generator starting… docs_dir={docs_root}")

        if not agents_dir.exists():
            print(f"[gen-files] OpAgentsOlympus dir not found: {agents_dir}")
            return

        py_files = sorted(practice_dir.rglob("*.py")) + sorted(agents_dir.glob("*.py"))
        print(f"[gen-files] Scanning {practice_dir} (recursive) -> {len(py_files)} .py files")

        # MCQ sources (kept inside docs under a safe folder name)
        mcq_py_files = []
        mcq_md_like_files = []  # markdown-like content files to include raw
        # Prefer mcqs-src, otherwise fall back to original folder with spaces (legacy)
        if mcq_src_dir.exists():
            mcq_py_files = sorted(mcq_src_dir.glob("*.py"))
            # Also accept plain .md so README.md works out-of-the-box
            mcq_md_like_files = sorted(
                list(mcq_src_dir.glob("*.md")) +
                list(mcq_src_dir.glob("*.mdsrc")) +
                list(mcq_src_dir.glob("*.md.txt"))
            )
            print(f"[gen-files] MCQ src: {mcq_src_dir} -> {len(mcq_py_files)} .py, {len(mcq_md_like_files)} md-like files")
        elif mcq_default_dir.exists():
            mcq_py_files = sorted(mcq_default_dir.glob("*.py"))
            mcq_md_like_files = sorted(list(mcq_default_dir.glob("*.md")))
            print(f"[gen-files] MCQ src (fallback): {mcq_default_dir} -> {len(mcq_py_files)} .py, {len(mcq_md_like_files)} .md")

        # Probing disabled now that generation is verified

        # Collect lists to build indices
        mcq_entries = []  # list[tuple[str, str]] -> (title, target_rel_md)

        def slugify(name: str) -> str:
            import re
            s = name.lower()
            s = re.sub(r"[^a-z0-9]+", "-", s)
            s = re.sub(r"^-+|-+$", "", s)
            return s or "item"

        def is_excluded_path(path: Path) -> bool:
            # Check if the path contains openai-agents-python folder
            parts = path.parts
            if "openai-agents-python" in parts:
                return True
            return False

        for py_path in py_files:
            if py_path.name in SKIP_FILES or is_excluded_path(py_path):
                print(f"[gen-files] Skipping excluded file: {py_path}")
                continue

            rel_to_docs = py_path.resolve().relative_to(docs_root)
            parts = rel_to_docs.parts
            title = title_from_stem(py_path.stem)

            # Default target path: mirror alongside source (same folder), .md extension
            target_rel_md = rel_to_docs.with_suffix(".md").as_posix()

            # Regular practice files only (MCQs handled from mcq_src_dir or fallback below)
            if "100 MCQs Answer" in parts or "mcqs-src" in parts:
                # Skip generating in-place wrappers for problematic MCQ filenames
                continue
            # Skip if a real .md exists next to the .py (author-provided content wins)
            if py_path.with_suffix('.md').exists():
                print(f"[gen-files] Skipping existing wrapper on disk: {py_path.with_suffix('.md')}")
                continue
            content = WRAPPER_TEMPLATE.format(title=title, filename=py_path.name)

            with mkdocs_gen_files.open(target_rel_md, "w") as f:  # type: ignore[call-arg]
                f.write(content)
            print(f"[gen-files] Generated wrapper: {target_rel_md}")
            # No overall practice index generation (kept nav curated)

        # MCQ wrappers (from moved source dir)
        safe_dir = "OpAgentsOlympus/practice/100-mcqs-answer"
        for py in mcq_py_files:
            if is_excluded_path(py):
                print(f"[gen-files] Skipping excluded MCQ file: {py}")
                continue
            title = title_from_stem(py.stem)
            safe_name = slugify(py.stem) + ".md"
            target_rel_md = f"{safe_dir}/{safe_name}"
            abs_src_path = py.resolve().relative_to(docs_root).as_posix()  # e.g. assets/mcqs-src/1-...py
            content = WRAPPER_TEMPLATE_ABS.format(title=title, abs_path=abs_src_path)
            with mkdocs_gen_files.open(target_rel_md, "w") as f:  # type: ignore[call-arg]
                f.write(content)
            print(f"[gen-files] Generated wrapper: {target_rel_md}")
            mcq_entries.append((title, target_rel_md))

        for md_like in mcq_md_like_files:
            if is_excluded_path(md_like):
                print(f"[gen-files] Skipping excluded MCQ markdown file: {md_like}")
                continue
            raw_stem = md_like.stem.replace('.md', '')  # handle .mdsrc or .md.txt, or plain .md
            title = title_from_stem(raw_stem.lstrip('#').strip())
            # Preserve README filename so a nav link to README.md works out-of-the-box
            if raw_stem.lower() == 'readme':
                safe_name = 'README.md'
            else:
                safe_name = slugify(raw_stem) + ".md"
            target_rel_md = f"{safe_dir}/{safe_name}"
            abs_src_path = md_like.resolve().relative_to(docs_root).as_posix()
            content = WRAPPER_TEMPLATE_INCLUDE_RAW.format(title=title, abs_path=abs_src_path)
            with mkdocs_gen_files.open(target_rel_md, "w") as f:  # type: ignore[call-arg]
                f.write(content)
            print(f"[gen-files] Generated wrapper: {target_rel_md}")
            mcq_entries.append((title, target_rel_md))

        # Write an index page for the MCQs folder for easy navigation
        if mcq_entries:
            from pathlib import Path as _P
            mcq_entries.sort(key=lambda x: x[0].lower())
            lines = [INDEX_HEADER, "\n"]
            for title, rel_md in mcq_entries:
                # Use a relative link from within the index folder, include .md to satisfy MkDocs validation
                href = _P(rel_md).name
                lines.append(f"- [{title}]({href})")
            index_content = "\n".join(lines) + "\n"
            with mkdocs_gen_files.open("OpAgentsOlympus/practice/100-mcqs-answer/index.md", "w") as f:  # type: ignore[call-arg]
                f.write(index_content)
            print("[gen-files] Generated wrapper: OpAgentsOlympus/practice/100-mcqs-answer/index.md")

        # No overall practice index (user prefers curated nav only)
    except Exception:
        print("[gen-files] ERROR in gen_practice_wrappers.py:\n" + traceback.format_exc())


if __name__ == "__main__":
    main()

# Ensure generation runs when the script is imported by mkdocs-gen-files
main()
