"""Scripts to import reference course structures into the database (skeleton).

This is a lightweight skeleton intended to outline how the import would work.
It does not modify any database in this staging patch.
"""
from pathlib import Path


def scan_fastbook(root: Path) -> list[dict]:
    chapters = []
    book_root = root / "01_intro.ipynb"
    if not book_root.exists():
        return chapters
    # Minimal placeholder: collect notebook paths under fastbook
    for path in root.rglob("*.ipynb"):
        chapters.append({"path": str(path), "title": path.stem})
    return chapters


def scan_llm_from_scratch(root: Path) -> list[dict]:
    docs = []
    docs_dir = root / "docs"
    if not docs_dir.exists():
        return docs
    for p in docs_dir.glob("**/*.md"):
        docs.append({"path": str(p), "title": p.stem})
    return docs


def main():
    base = Path(__file__).resolve().parents[1]  # backend/.. project root
    fastbook_root = Path(base / "references/fastbook")
    llm_root = Path(base / "references/llm-from-scratch")
    print("Fastbook chapters:", scan_fastbook(fastbook_root))
    print("LLM-from-scratch docs:", scan_llm_from_scratch(llm_root))


if __name__ == "__main__":
    main()
