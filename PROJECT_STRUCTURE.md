# Synthos 目录结构

> 基于当前仓库实际结构整理，已省略 `.git/`、`.idea/`、`__pycache__/` 等非核心目录。

```text
Synthos/
├─ main.py                      # 客户端主入口（启动 UI）
├─ settings.py                  # 全局配置（数据库、API 地址、路径等）
├─ requirements.txt             # 项目统一依赖清单
├─ README.md                    # 使用与部署说明
├─ PROJECT_STRUCTURE.md         # 当前目录结构说明文档
├─ LICENSE                      # 开源许可证
├─ __init__.py                  # 包标识文件
├─ api/                         # FastAPI 服务端
│  ├─ app/
│  ├─ resource/                 # API 侧资源打包/资源索引逻辑
│  ├─ src/
│  ├─ static/
│  ├─ templates/
│  ├─ .env.example              # API 环境变量模板
│  ├─ app_api.py                # 应用相关接口
│  ├─ common.py                 # API 公共函数
│  ├─ config.py                 # API 配置读取
│  ├─ docker-compose.yml        # API 容器编排
│  ├─ Dockerfile                # API 镜像构建
│  ├─ docker_run                # 运行辅助脚本
│  ├─ index_api.py              # 首页/索引类接口
│  ├─ main.py                   # API 启动入口
│  ├─ plugin_api.py             # 插件上传下载接口
│  ├─ security.py               # 鉴权/安全处理
│  ├─ user_api.py               # 用户相关接口
│  └─ __init__.py
├─ core/                        # 核心公共模块
│  ├─ bootstrap.py              # 兼容导出 bootstrap 能力
│  ├─ constants.py              # 常量定义
│  ├─ paths.py                  # 路径与文件落地逻辑
│  └─ __init__.py
├─ example/                     # 示例插件与模板
│  ├─ plugins/                  # 示例插件二进制产物
│  │  ├─ icon.png
│  │  ├─ main.pyd
│  │  ├─ plugin.json
│  │  ├─ step.pyd
│  │  └─ step_ui.pyd
│  ├─ plugins_template/         # 示例插件源码模板
│  │  ├─ get_widget.py
│  │  ├─ main.py
│  │  ├─ step.py
│  │  └─ step_ui.py
│  └─ update_launcher.exe       # 客户端更新辅助程序
├─ models/                      # SQLAlchemy 数据模型
│  ├─ apps.py                   # 应用表模型
│  ├─ base.py                   # 模型基类与会话基础
│  ├─ directories.py            # 目录表模型
│  ├─ favourite.py              # 收藏表模型
│  ├─ logger.py                 # 日志表模型
│  ├─ roles.py                  # 角色表模型
│  ├─ users.py                  # 用户表模型
│  ├─ version.py                # 版本表模型
│  └─ __init__.py
├─ scripts/                     # 命令行脚本与打包脚本
│  ├─ initialize_project.py     # 初始化脚本入口（命令行）
│  ├─ nuitka_to_exe.py          # 主程序打包脚本
│  └─ nuitka_to_exe_updater.py  # 更新器打包脚本
├─ services/                    # 业务与数据库访问层
│  ├─ appQuery.py               # 应用查询/写入
│  ├─ base.py                   # DB 会话封装
│  ├─ bootstrap_runtime.py      # 初始化主流程（建表/种子数据）
│  ├─ common.py                 # 服务层公共函数
│  ├─ createTable.py            # 建表辅助
│  ├─ directoryQuery.py         # 目录查询/写入
│  ├─ favouriteQuery.py         # 收藏查询/写入
│  ├─ loggerQuery.py            # 日志查询/写入
│  ├─ roleQuery.py              # 角色查询/写入
│  ├─ userQuery.py              # 用户查询/写入
│  ├─ versionQuery.py           # 版本查询/写入
│  └─ __init__.py
├─ static/                      # 静态资源
│  ├─ images/                   # 图片资源
│  ├─ resource.py               # Qt 资源映射代码
│  └─ resource.qrc              # Qt 资源清单
├─ ui/                          # 客户端 UI 模块
│  ├─ AppManage/                # 应用管理模块
│  ├─ Directory/                # 应用目录模块
│  ├─ GeneralWidgets/           # 常用QT组件
│  ├─ HomePage/                 # 主页模块
│  ├─ Information/              # 消息模块
│  ├─ LoginView/                # 登录窗口模块
│  ├─ MySettings/               # 个人设置模块
│  ├─ UserManage/               # 用户管理摸块
│  ├─ Dashboard.py              # 仪表盘页面
│  ├─ LoginUi.py                # 登录窗口
│  └─ __init__.py
└─ utils/                       # 工具函数与客户端能力模块
   ├─ app_download.py           # 应用包下载
   ├─ creds.py                  # 本地凭据存储/读取
   ├─ driver_download.py        # 驱动下载与解压
   ├─ plugin_interface.py       # 插件协议定义
   ├─ plugin_manager.py         # 插件加载与生命周期管理
   ├─ resource_download.py      # 资源包下载与解压
   ├─ style_sheet.py            # 样式加载
   ├─ traverse_nested_files.py  # 递归遍历工具
   ├─ updater.py                # 更新检查与更新流程
   ├─ update_launcher.py        # 更新启动器逻辑
   └─ __init__.py
```

## 模块职责速览

- `api/`：对外提供插件、资源、用户等 HTTP 接口，支持 Docker 部署。
- `core/`：放全局常量和路径/文件初始化逻辑，避免散落在各处。
- `services/`：承载数据库业务逻辑（查询、写入、初始化种子）。
- `models/`：定义数据库表结构（ORM）。
- `ui/`：客户端页面和组件实现。
- `utils/`：下载、更新、插件管理等独立工具能力。
- `scripts/`：命令行初始化与打包入口。
- `example/`：示例插件与模板，供初始化和联调用。
