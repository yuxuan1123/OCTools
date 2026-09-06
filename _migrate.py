# -*- coding: utf-8 -*-
"""临时：QComboBox → Combo 批量迁移（dry-run 输出改动点）"""
import re
import os

ROOT = r"d:\Project\PythonProject\OCTools"
FILES = [
    "ui/tabs/tab_plugin.py",
    "ui/tabs/tab_component/set_format.py",
    "ui/tabs/tab_component/docx_format_card.py",
    "ui/options/set_ui.py",
    "plugins/_shared/set_tts.py",
    "plugins/_shared/set_stt.py",
    "plugins/_shared/set_pdf_docx.py",
    "plugins/_shared/set_image_docx.py",
    "plugins/tree/set_tts.py",
    "plugins/tree/card_options.py",
    "plugins/translation/set_translator.py",
    "plugins/translation/set_screen_region.py",
    "plugins/translation/card_direction.py",
    "plugins/terminal/visual_dialog.py",
    "plugins/terminal/tab_terminal.py",
    "plugins/merge/card_target.py",
    "plugins/conversion/card_target.py",
    "mvp/tree/set_tts.py",
    "mvp/tree/card_options.py",
    "mvp/terminal/tab_terminal.py",
]

# 这些文件用裸 QComboBox 做 isinstance / 类映射比较，必须保留原生引用，不迁移
SKIP = {
    "ui/tabs/plugin_ui/desc_renderer.py",
    "plugins/style_lab/tab_style_lab.py",
}

ADD_LINE = "from ui.ui_component.combo_component import Combo\n"
MULTI_IMPORT = re.compile(r"from PySide6\.QtWidgets import \([^)]*\)", re.S)
SINGLE_IMPORT = re.compile(r"from PySide6\.QtWidgets import [^\n]*")


def strip_qcombobox_tokens(text: str) -> str:
    """从 import 块文本中删除 QComboBox token（保留逗号结构）"""
    return re.sub(r"QComboBox\s*,\s*", "", text).replace("QComboBox", "")


def migrate(path: str, apply: bool) -> list:
    fp = os.path.join(ROOT, path)
    with open(fp, encoding="utf-8") as f:
        src = f.read()
    diffs = []
    new = src

    # 1) 类属性常量
    if "QComboBox.NoInsert" in new:
        new = new.replace("QComboBox.NoInsert", "Combo.NoInsert")
        diffs.append(("常量", "QComboBox.NoInsert", "Combo.NoInsert"))

    # 2) 多行 import 块
    m = MULTI_IMPORT.search(new)
    if m and "QComboBox" in m.group(0):
        block = m.group(0)
        stripped = strip_qcombobox_tokens(block)
        diffs.append(("import多行", "QComboBox 在块内删除", path))
        new = new.replace(block, stripped)

    # 3) 单行 import
    for m in SINGLE_IMPORT.finditer(new):
        line = m.group(0)
        if "QComboBox" in line and "(" not in line:
            stripped = strip_qcombobox_tokens(line).strip()
            if stripped.startswith("from PySide6.QtWidgets import") and not stripped.endswith(",") and len(stripped) > 34:
                diffs.append(("import单行", line.strip(), stripped))
                new = new.replace(line, stripped)
            elif "QComboBox" in line:
                diffs.append(("import单行删", line.strip(), "<删除>"))
                new = new.replace(line, "")

    # 4) 实例化
    for m in re.finditer(r"QComboBox\(", new):
        ctx = new[max(0, m.start() - 60):m.start() + 20].splitlines()[-1]
        diffs.append(("实例化", ctx.strip(), ctx.strip().replace("QComboBox(", "Combo(")))
    new = new.replace("QComboBox(", "Combo(")

    # 5) 残留检查（非 import/注释行）
    residual = [l for l in new.splitlines()
                if "QComboBox" in l and not l.strip().startswith("#")]

    # 6) Combo import：已存在 ui_component 导入时合并，否则新增一行
    if "from ui.ui_component.combo_component import" in new:
        if "import Combo" not in new:
            new = new.replace(
                "from ui.ui_component.combo_component import DescComboBox",
                "from ui.ui_component.combo_component import Combo, DescComboBox")
            diffs.append(("import合并", "DescComboBox", "Combo, DescComboBox"))
    else:
        lines = new.splitlines(keepends=True)
        for i, l in enumerate(lines):
            if l.startswith("import ") or l.startswith("from "):
                lines.insert(i, ADD_LINE)
                break
        new = "".join(lines)
        diffs.append(("import添加", ADD_LINE.strip(), ""))

    if apply:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(new)
    return diffs, residual


if __name__ == "__main__":
    apply = os.environ.get("APPLY") == "1"
    total = 0
    for path in FILES:
        if path in SKIP:
            print(f"### {path}  [跳过：保留原生 QComboBox 引用]")
            continue
        diffs, residual = migrate(path, apply)
        if not diffs and not residual:
            continue
        print(f"### {path}")
        for kind, old, new in diffs:
            total += 1
            print(f"  [{kind}] {old} -> {new}")
        for r in residual:
            print(f"  [残留!] {r.strip()}")
    print(f"\n共 {total} 处改动（{'已写入' if apply else 'dry-run'}）")
