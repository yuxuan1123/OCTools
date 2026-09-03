"""
OCTools/core/__init__.py
───────────────────────────────────────────────
核心引擎层：只封装第三方库，不写业务逻辑。

分层：
  - formats.py    格式域数据（单一真相源）
  - engines/      各类格式与算法的底层能力封装
  - utils/        通用工具（无业务、无 UI）

配置数据模型与预设管理统一收口于 config/ 包。
"""

from core import formats  # noqa: F401

__all__ = ["formats"]
