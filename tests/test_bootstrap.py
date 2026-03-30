import pytest


def test_bootstrap_module_importable():
    pytest.importorskip("sqlalchemy")
    from services.bootstrap_runtime import BootstrapResult

    result = BootstrapResult()
    assert result.created_tables is False
