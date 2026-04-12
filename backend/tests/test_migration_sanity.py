import ast
import pytest


def test_initial_migration_has_upgrade_and_downgrade():
    path = "backend/alembic/versions/001_create_initial.py"
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    tree = ast.parse(src)
    names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert 'upgrade' in names, "Migration must define an upgrade() function"
    assert 'downgrade' in names, "Migration must define a downgrade() function"
