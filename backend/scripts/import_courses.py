"""Import reference course structures into the database (production-ready skeleton)."""
import asyncio
from pathlib import Path

from app.tools.import_references import ReferenceImporter
from app.core.database import AsyncSessionLocal


async def _run_import():
    async with AsyncSessionLocal() as db:
        importer = ReferenceImporter(db)
        results = await importer.import_all_references()
        print("Import results:", results)


def main():
    asyncio.run(_run_import())


if __name__ == "__main__":  # pragma: no cover
    main()
