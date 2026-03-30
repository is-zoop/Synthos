from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure repo root is importable when running:
#   python scripts/initialize_project.py
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.constants import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME
from services.bootstrap_runtime import bootstrap_project


def main() -> int:
    result = bootstrap_project()
    print("Synthos initialization complete.")
    print(f"Default admin username: {DEFAULT_ADMIN_USERNAME}")
    print(f"Default admin password: {DEFAULT_ADMIN_PASSWORD}")

    avatar_targets = [
        item.split("default_avatar:", 1)[1]
        for item in result.plugin_targets
        if item.startswith("default_avatar:")
    ]
    resource_targets = [
        item.split("resource_json:", 1)[1]
        for item in result.plugin_targets
        if item.startswith("resource_json:")
    ]
    launcher_targets = [
        item.split("update_launcher:", 1)[1]
        for item in result.plugin_targets
        if item.startswith("update_launcher:")
    ]

    if avatar_targets:
        print("已生成默认头像：")
        for path in avatar_targets:
            print(f"  - {path}")
    if resource_targets:
        print("已生成资源索引(resource.json)：")
        for path in resource_targets:
            print(f"  - {path}")
    if launcher_targets:
        print("已复制 update_launcher.exe：")
        for path in launcher_targets:
            print(f"  - {path}")

    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
