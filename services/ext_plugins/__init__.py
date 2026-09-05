"""
OCTools/services/ext_plugins  ─  外部插件系统（子进程隔离）。

- paths.py         路径解析（源码/打包兼容）
- detection.py     解释器/uv 定位、插件扫描
- config_store.py  config.json 读写
- log_store.py     统一日志
- ipc.py           JSON Lines IPC 协议
- process.py       子进程 + 心跳 + 读线程
- installer.py     依赖安装（uv / pip 回退）
- manager.py       状态机 + 生命周期 + 定时器
"""

from services.ext_plugins import paths  # noqa: F401
