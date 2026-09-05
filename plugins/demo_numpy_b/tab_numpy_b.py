# -*- coding: utf-8 -*-
"""
OCTools 插件 demo_numpy_b：desc 模式示例。
───────────────────────────────────────────────
desc：插件也用 PySide6，但带主进程没有/版本不同的库（numpy==1.26.4）。
依赖安装到 deps/demo_numpy_b/ 实现隔离；插件返回控件树 JSON，主进程渲染。

与 demo_numpy_a（numpy==2.0.2）同时运行互不冲突。
"""


class TabNumpyB:
    """desc 模式：子进程隔离 numpy==1.26.4，控件树 JSON 由主进程渲染。"""

    def describe_ui(self) -> dict:
        import numpy
        return {
            "type": "VBox",
            "children": [
                {"type": "QLabel",
                 "props": {"text": f"numpy {numpy.__version__}（demo_numpy_b 隔离环境）"}},
                {"type": "QPushButton",
                 "props": {"text": "刷新", "objectName": "btn_refresh"},
                 "actions": {"clicked": "refresh"}},
            ],
        }

    def invoke_action(self, action: str, params: dict) -> dict:
        # 演示局部刷新：返回全量控件树，主进程重建界面
        return {"ui": self.describe_ui()}
