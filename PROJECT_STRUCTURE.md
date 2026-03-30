# Synthos 2.0 目录结构

> 说明：以下目录树基于当前项目实际代码整理，已省略 `__pycache__`、`.idea/` 等非核心内容。

```text
Synthos 2.0/
├─ main.py
├─ settings.py
├─ resource.py
├─ resource.json
├─ README.md
├─ PROJECT_STRUCTURE.md
├─ nuitka_to_exe.py
├─ nuitka_to_exe_for_dev.py
├─ nuitka_to_exe_updater.py
├─ core/
│  ├─ __init__.py
│  ├─ bootstrap.py
│  ├─ constants.py
│  └─ paths.py
├─ models/
│  ├─ __init__.py
│  ├─ base.py
│  ├─ apps.py
│  ├─ directories.py
│  ├─ favourite.py
│  ├─ logger.py
│  ├─ roles.py
│  ├─ users.py
│  └─ version.py
├─ services/
│  ├─ __init__.py
│  ├─ appQuery.py
│  ├─ base.py
│  ├─ common.py
│  ├─ createTable.py
│  ├─ directoryQuery.py
│  ├─ favouriteQuery.py
│  ├─ loggerQuery.py
│  ├─ roleQuery.py
│  ├─ userQuery.py
│  └─ versionQuery.py
├─ ui/
│  ├─ Dashboard.py
│  ├─ LoginUi.py
│  ├─ AppManage/
│  ├─ Directory/
│  ├─ GeneralWidgets/
│  ├─ HomePage/
│  ├─ Infomation/        # 旧路径，保留兼容
│  ├─ information/       # 新规范入口
│  ├─ LoginView/
│  ├─ MySettings/
│  └─ UserManage/
├─ utils/
│  ├─ app_download.py
│  ├─ creds.py
│  ├─ driver_download.py
│  ├─ plugin_interface.py
│  ├─ plugin_manager.py
│  ├─ resource_download.py
│  ├─ style_sheet.py
│  ├─ traverse_nested_files.py
│  ├─ update_launcher.py
│  └─ updater.py
├─ initialize_project.py
├─ init_project.bat
├─ smoke_check.py
├─ scripts/               # 早期脚本目录，保留兼容
├─ tests/
│  ├─ test_bootstrap.py
│  ├─ test_paths.py
│  └─ test_smoke_imports.py
├─ example/
│  ├─ icon.png
│  ├─ main.pyd
│  ├─ plugin.json
│  ├─ step.pyd
│  └─ step_ui.pyd
├─ api/
│  ├─ __init__.py
│  ├─ app_api.py
│  ├─ common.py
│  ├─ config.py
│  ├─ Dockerfile
│  ├─ docker-compose.yml
│  ├─ docker_run
│  ├─ index_api.py
│  ├─ main.py
│  ├─ plugin_api.py
│  ├─ requirements.txt
│  ├─ security.py
│  ├─ user_api.py
│  ├─ resource/
│  └─ templates/
└─ static/
   ├─ images/
   ├─ qss/
   └─ resource.qrc
```

## 分层说明

- `core/`: 放置常量、路径规则、example 插件自检和项目初始化逻辑。
- `models/`: 定义数据库实体。
- `services/`: 负责数据库查询和业务更新。
- `ui/`: 桌面端界面实现；新旧命名入口同时保留，保证兼容。
- `utils/`: 负责插件加载、资源下载、更新器、凭据存储等工具能力。
- `scripts/`: 放置一键初始化脚本和系统包装脚本。
- `tests/`: 最小化测试与 smoke check。
- `api/`: FastAPI 服务端及模板、Docker 配置。
- `example/`: 仓库内置示例插件，用于初始化和联调。

## 关键流程

1. `main.py` 启动客户端并在启动前补齐 example 插件。
2. `initialize_project.py` 可幂等创建表、管理员、基础角色、示例应用与插件落地。
3. `ui/Directory/` 与 `utils/plugin_manager.py` 一起完成插件下载、加载、展示与卸载。
4. `api/` 提供插件文件、资源包、头像和更新文件的上传下载接口。
