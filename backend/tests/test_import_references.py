def test_reference_importer_exists():
    from app.tools import import_references  # noqa: F401
    cls = getattr(import_references, 'ReferenceImporter', None)
    assert cls is not None
