from __future__ import annotations

import json

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
    if avatar_targets:
        print("已生成默认头像：")
        for path in avatar_targets:
            print(f"  - {path}")
    if resource_targets:
        print("已生成资源索引(resource.json)：")
        for path in resource_targets:
            print(f"  - {path}")

    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
