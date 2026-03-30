import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "services.bootstrap_runtime",
        "core.paths",
        "ui.information.information_page",
        "ui.UserManage.user_funcs",
    ],
)
def test_module_import_smoke(module_name):
    if module_name.startswith("ui."):
        pytest.importorskip("PyQt5")
        pytest.importorskip("qfluentwidgets")
    importlib.import_module(module_name)
