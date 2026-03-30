from __future__ import annotations

import importlib


MODULES = [
    "core.paths",
    "services.bootstrap_runtime",
    "ui.information.information_page",
    "ui.UserManage.user_funcs",
]


def main() -> int:
    for module_name in MODULES:
        importlib.import_module(module_name)
        print(f"[OK] {module_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
