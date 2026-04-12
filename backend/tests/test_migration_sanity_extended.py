import importlib.util
from pathlib import Path


def test_migration_file_has_upgrade_and_downgrade():
    path = Path("backend/alembic/versions/001_create_initial.py")
    spec = importlib.util.spec_from_file_location("mig_001", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    assert hasattr(mod, "upgrade"), "Migration should define upgrade()"
    assert hasattr(mod, "downgrade"), "Migration should define downgrade()"
