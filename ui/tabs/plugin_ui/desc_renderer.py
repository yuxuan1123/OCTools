"""
OCTools/ui/tabs/plugin_ui/desc_renderer.py
───────────────────────────────────────────────
控件树 JSON → PySide6 控件渲染器（desc 模式插件的主进程侧）。

协议（插件 describe_ui() 返回）：
  {
    "type": "VBox",                     # VBox/HBox/Grid/Form/Scroll
    "children": [
      {"type": "QLabel", "props": {"text": "..."}},
      {"type": "QPushButton",
       "props": {"text": "生成", "objectName": "btn_gen"},
       "actions": {"clicked": "generate"}},
      {"type": "QPlainTextEdit",
       "props": {"objectName": "out", "readOnly": true}}
    ]
  }

渲染规则：
  - 布局类型 VBox/HBox/Grid/Form/Scroll 作为容器递归渲染 children；
  - 控件类型查映射表动态创建，props 作为构造/属性设置；
  - actions 绑定信号 → 调 manager.invoke_action(plugin_id, action, params)，
    响应若含 "update" 则由宿主（HostTabWidget）重建界面。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QScrollArea,
    QLabel, QPushButton, QLineEdit, QTextEdit, QPlainTextEdit, QComboBox,
    QCheckBox, QRadioButton, QSpinBox, QDoubleSpinBox, QSlider, QProgressBar,
    QListWidget, QTableWidget, QFrame, QGroupBox, QTableWidgetItem,
)

# 布局类型 → 工厂
_LAYOUTS = {
    "VBox": QVBoxLayout,
    "HBox": QHBoxLayout,
    "Grid": QGridLayout,
    "Form": QFormLayout,
}

# 控件类型 → 工厂
_WIDGETS = {
    "QLabel": QLabel,
    "QPushButton": QPushButton,
    "QLineEdit": QLineEdit,
    "QTextEdit": QTextEdit,
    "QPlainTextEdit": QPlainTextEdit,
    "QComboBox": QComboBox,
    "QCheckBox": QCheckBox,
    "QRadioButton": QRadioButton,
    "QSpinBox": QSpinBox,
    "QDoubleSpinBox": QDoubleSpinBox,
    "QSlider": QSlider,
    "QProgressBar": QProgressBar,
    "QListWidget": QListWidget,
    "QTableWidget": QTableWidget,
    "QFrame": QFrame,
    "QGroupBox": QGroupBox,
}


def _apply_props(widget, props: dict):
    """把 props 应用到控件：objectName / text / 值 / 通用属性。"""
    if not isinstance(props, dict):
        return
    obj_name = props.get("objectName")
    if obj_name:
        widget.setObjectName(str(obj_name))
    for key, value in props.items():
        if key in ("objectName",):
            continue
        if key == "text" and hasattr(widget, "setText"):
            widget.setText(str(value))
        elif key == "placeholderText" and hasattr(widget, "setPlaceholderText"):
            widget.setPlaceholderText(str(value))
        elif key == "readOnly" and hasattr(widget, "setReadOnly"):
            widget.setReadOnly(bool(value))
        elif key == "checked" and hasattr(widget, "setChecked"):
            widget.setChecked(bool(value))
        elif key == "value" and hasattr(widget, "setValue"):
            try:
                widget.setValue(value)
            except (TypeError, ValueError):
                pass
        elif key == "range" and isinstance(value, (list, tuple)) and len(value) == 2:
            try:
                widget.setRange(int(value[0]), int(value[1]))
            except (TypeError, ValueError):
                pass
        elif key == "items" and isinstance(value, list):
            if isinstance(widget, QComboBox):
                widget.addItems([str(v) for v in value])
            elif isinstance(widget, QListWidget):
                widget.addItems([str(v) for v in value])
        elif key == "headers" and isinstance(value, list) and isinstance(widget, QTableWidget):
            widget.setColumnCount(len(value))
            widget.setHorizontalHeaderLabels([str(v) for v in value])
        else:
            try:
                widget.setProperty(key, value)
            except Exception:
                pass


def _widget_value(widget) -> object:
    """读取控件当前值，作为事件 params.value。"""
    if isinstance(widget, (QLineEdit, QTextEdit, QPlainTextEdit, QComboBox)):
        return widget.text() if hasattr(widget, "text") else None
    if isinstance(widget, (QCheckBox, QRadioButton)):
        return widget.isChecked()
    if isinstance(widget, (QSpinBox, QDoubleSpinBox, QSlider)):
        return widget.value()
    if isinstance(widget, QProgressBar):
        return widget.value()
    return None


class DescRenderer:
    """控件树 JSON 渲染器：render(desc) → QWidget。"""

    def __init__(self, plugin_id: str, invoke_cb):
        """
        Args:
            plugin_id: 插件 id（事件转发用）
            invoke_cb: callable(action_id, params) → 触发 invoke_action
        """
        self._plugin_id = plugin_id
        self._invoke_cb = invoke_cb
        self._object_map: dict[str, QWidget] = {}

    def render(self, desc: dict) -> QWidget:
        """渲染控件树，返回顶层 QWidget。"""
        self._object_map.clear()
        if not isinstance(desc, dict):
            desc = {"type": "VBox", "children": []}
        ctype = desc.get("type", "VBox")
        if ctype == "Scroll":
            host = QScrollArea()
            host.setWidgetResizable(True)
            host.setObjectName("bareScroll")
            inner = self._build_container(desc.get("children", []), "VBox")
            host.setWidget(inner)
            return host
        return self._build_container(desc.get("children", []), ctype)

    def _build_container(self, children: list, ctype: str) -> QWidget:
        host = QWidget()
        host.setObjectName("bareSurface")
        if ctype == "Grid":
            lay = QGridLayout(host)
        elif ctype == "Form":
            lay = QFormLayout(host)
        else:
            lay = QVBoxLayout(host) if ctype != "HBox" else QHBoxLayout(host)
        lay.setContentsMargins(0, 0, 0, 0)
        for node in children or []:
            if not isinstance(node, dict):
                continue
            item_type = node.get("type", "")
            if item_type in _LAYOUTS or item_type == "Scroll":
                sub = self._build_node(node)
                if sub is not None:
                    if isinstance(lay, QFormLayout):
                        lay.addRow(sub)
                    else:
                        lay.addWidget(sub)
            else:
                widget = self._build_widget(node)
                if widget is None:
                    continue
                if isinstance(lay, QGridLayout):
                    lay.addWidget(widget, lay.rowCount(), 0)
                elif isinstance(lay, QFormLayout):
                    label = node.get("label")
                    if label:
                        lay.addRow(str(label), widget)
                    else:
                        lay.addRow(widget)
                else:
                    lay.addWidget(widget)
        return host

    def _build_node(self, node: dict) -> QWidget | None:
        """递归构建子容器/控件。"""
        ntype = node.get("type", "")
        if ntype in _LAYOUTS:
            return self._build_container(node.get("children", []), ntype)
        if ntype == "Scroll":
            host = QScrollArea()
            host.setWidgetResizable(True)
            host.setObjectName("bareScroll")
            inner = self._build_container(node.get("children", []), "VBox")
            host.setWidget(inner)
            return host
        return self._build_widget(node)

    def _build_widget(self, node: dict) -> QWidget | None:
        ntype = node.get("type", "")
        factory = _WIDGETS.get(ntype)
        if factory is None:
            return None
        widget = factory()
        _apply_props(widget, node.get("props") or {})
        obj_name = (node.get("props") or {}).get("objectName")
        if obj_name:
            self._object_map[str(obj_name)] = widget
        for signal_name, action_id in (node.get("actions") or {}).items():
            self._bind_action(widget, signal_name, action_id, obj_name)
        return widget

    def _bind_action(self, widget, signal_name: str, action_id: str, obj_name):
        signal = getattr(widget, signal_name, None)
        if signal is None or not hasattr(signal, "connect"):
            return

        def _on_trigger(*_args):
            params = {"objectName": obj_name}
            value = _widget_value(widget)
            if value is not None:
                params["value"] = value
            if self._invoke_cb is not None:
                self._invoke_cb(action_id, params)

        try:
            signal.connect(_on_trigger)
        except TypeError:
            pass

    def apply_update(self, update: dict):
        """按增量更新已有控件（全量重建由宿主决定；此处仅重设 props）。"""
        if not isinstance(update, dict):
            return
        obj_name = update.get("objectName")
        props = update.get("props")
        if obj_name and props:
            widget = self._object_map.get(str(obj_name))
            if widget is not None:
                _apply_props(widget, props)
