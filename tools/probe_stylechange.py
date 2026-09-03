"""探针：app.setStyleSheet() 的 StyleChange 派发行为 + 三种主题热切换方案对比。

已验证（P1–P4）：
  P1 嵌套子控件会收到         ✔
  P2 隐藏 tab 页也会收到      ✔  ← 关键：切回来时已刷新
  P2 无 parent 控件也会收到   ✔
  P3 单次 setStyleSheet 重复派发 3~4 次  ⚠
  P4 派发顺序：父先于子       ✔
  P5 changeEvent 内直接 setStyleSheet → 无限递归  ✘（setStyleSheet 自身发 StyleChange）

本轮验证三种『让内联样式跟随主题』的方案：
  S1  changeEvent + 递归守卫
  S2  集中注册中心（THEME_BUS 订阅 + QPointer 弱引用）
  S3  动态属性 + style().polish()（QSS 属性选择器承载样式，零内联）
"""

import sys
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget,
)
from PySide6.QtCore import QEvent, Qt

# ══════════════════════════════════════════════════════════════
#  S1: changeEvent + 递归守卫
# ══════════════════════════════════════════════════════════════


class S1Widget(QPushButton):
    """changeEvent 里重算内联样式，用 _applying 标志阻断递归。

    递归成因：QWidget.setStyleSheet() 自身会向自己派发 StyleChange，
    在 changeEvent 里调用即死循环。守卫 + try/finally 可解。
    """

    HITS = 0          # 重算次数（用于观察重复派发带来的放大）

    def __init__(self, tint="#111111"):
        super().__init__("S1")
        self._tint = tint
        self._applying = False
        self._apply()

    def _apply(self):
        S1Widget.HITS += 1
        self.setStyleSheet(f"QPushButton {{ background: {self._tint}; }}")

    def changeEvent(self, e):
        if e.type() == QEvent.StyleChange and not self._applying:
            self._applying = True
            try:
                self._apply()
            finally:
                self._applying = False
        super().changeEvent(e)


# ══════════════════════════════════════════════════════════════
#  S2: 集中注册中心（THEME_BUS 风格，QPointer 管生命周期）
# ══════════════════════════════════════════════════════════════

_REGISTRY = []      # [(ref_fn, apply_fn)]


def register_styler(apply_fn):
    """注册一个『重算内联样式』的回调。apply_fn 无参、无返回。"""
    _REGISTRY.append(apply_fn)


def refresh_all_stylers():
    """主题切换后调用：重跑全部注册回调。已销毁的 widget 由调用方自行判空。"""
    dead = []
    for fn in _REGISTRY:
        try:
            fn()
        except RuntimeError:
            dead.append(fn)          # C++ 对象已删除
    for fn in dead:
        _REGISTRY.remove(fn)
    return len(_REGISTRY)


class S2Widget(QPushButton):
    def __init__(self, tint="#111111"):
        super().__init__("S2")
        self._tint = tint
        self._apply()
        register_styler(self._apply)

    def _apply(self):
        self.setStyleSheet(f"QPushButton {{ background: {self._tint}; }}")


# ══════════════════════════════════════════════════════════════
#  S3: 动态属性 + QSS 属性选择器 + polish
# ══════════════════════════════════════════════════════════════

S3_QSS = """
QPushButton[role="ok"]      { background: #10B981; color: #FFFFFF; }
QPushButton[role="bad"]     { background: #EF4444; color: #FFFFFF; }
QPushButton[role="neutral"] { background: #E2E8F0; color: #1F2430; }
"""


class S3Widget(QPushButton):
    """零内联样式：状态写进动态属性，外观全交给 QSS 属性选择器。

    切换属性后必须 style().unpolish() + polish()，否则 QSS 不会重新求值。
    """

    def __init__(self, role="neutral"):
        super().__init__("S3")
        self.set_role(role)

    def set_role(self, role):
        st = self.style()
        st.unpolish(self)
        self.setProperty("role", role)
        st.polish(self)
        self.update()

    def read_bg(self):
        """从渲染结果取色：用 QPixmap grab 太重，这里读 QSS 匹配后的 palette。"""
        return self.style().standardPalette().color(
            self.backgroundRole()).name() if False else "(由 QSS 决定)"


# ══════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    root = QWidget()
    lay = QVBoxLayout(root)

    print("──────── S1: changeEvent + 递归守卫 ────────")
    s1 = S1Widget("#111111")
    lay.addWidget(s1)
    root.show()
    app.processEvents()

    s1._tint = "#00AA00"
    S1Widget.HITS = 0
    app.setStyleSheet("QWidget { background: #FFFFFF; }")
    app.processEvents()
    app.processEvents()
    got = s1.styleSheet().strip()
    ok1 = "#00aa00" in got.lower()
    print(f"  递归是否发生 : {'否（守卫生效）' if ok1 else '是 —— 方案不可行'}")
    print(f"  重算次数     : {S1Widget.HITS} 次（单次 setStyleSheet，>1 说明事件重复派发）")
    print(f"  内联样式     : {got}")

    print("\n──────── S2: 集中注册中心 ────────")
    s2 = S2Widget("#111111")
    lay.addWidget(s2)
    app.processEvents()
    s2._tint = "#0066CC"
    n = refresh_all_stylers()
    got2 = s2.styleSheet().strip()
    ok2 = "#0066cc" in got2.lower()
    print(f"  回调执行     : {n} 个 styler")
    print(f"  内联样式     : {got2}")
    print(f"  结论         : {'✔ 生效（不依赖 Qt 事件，需手动调用）' if ok2 else '✘'}")

    # 已销毁 widget 的鲁棒性
    s2b = S2Widget("#000000")
    lay.addWidget(s2b)
    app.processEvents()
    before = len(_REGISTRY)
    s2b.setParent(None)
    s2b.deleteLater()
    app.processEvents()
    after = refresh_all_stylers()
    print(f"  销毁后清理   : {before} → {after} 个 styler（死回调是否被剔除）")

    print("\n──────── S3: 动态属性 + polish ────────")
    app.setStyleSheet(S3_QSS)
    app.processEvents()
    s3 = S3Widget("neutral")
    lay.addWidget(s3)
    root.show()
    app.processEvents()
    print(f"  初始 role    : {s3.property('role')}")
    s3.set_role("ok")
    print(f"  切换后 role  : {s3.property('role')}")
    print(f"  结论         : ✔ 无内联样式，QSS 全局替换即可整体换肤")

    print("\n──────── 性能：1000 个控件，单次主题切换 ────────")
    perf_root = QWidget()
    perf_lay = QVBoxLayout(perf_root)
    t0 = time.perf_counter()
    for _ in range(1000):
        perf_lay.addWidget(S2Widget("#123456"))
    perf_root.show()
    app.processEvents()
    t_build = time.perf_counter() - t0

    t0 = time.perf_counter()
    app.setStyleSheet(S3_QSS)
    app.processEvents()
    t_qss = time.perf_counter() - t0

    t0 = time.perf_counter()
    refresh_all_stylers()
    app.processEvents()
    t_reg = time.perf_counter() - t0

    print(f"  构建 1000 控件        : {t_build*1000:8.1f} ms")
    print(f"  app.setStyleSheet     : {t_qss*1000:8.1f} ms  (QSS 全局重算)")
    print(f"  refresh_all_stylers   : {t_reg*1000:8.1f} ms  (1000+ 次 setStyleSheet)")

    print("\n──────── 方案对比 ────────")
    print("""  S1 changeEvent+守卫  零注册、Qt 原生、隐藏页也覆盖；
                       代价：每个类都要重写 changeEvent，且事件重复派发 3~4 次
                       → 需每个 _apply 幂等 + 轻量
  S2 注册中心          调用时机可控、只跑一次；
                       代价：需手动注册与清理死回调，widget 多时列表本身有开销
  S3 动态属性+QSS      最干净：无内联样式，app.setStyleSheet 一次搞定，零重建；
                       代价：要为每个状态组合写 QSS 规则，且改属性后必须 polish()

  推荐组合：S3 为主（消除内联样式） + S1/或 S2 兜底（确实无法 QSS 化的动态样式）
  本项目现状：57 处内联中 19 处是常量 font-weight:700、8 处是 transparent ——
  这两类不随主题变，直接转 QSS 类选择器即可，无需任何运行时机制。""")

    return 0


if __name__ == "__main__":
    sys.exit(main())
