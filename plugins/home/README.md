# tab_home.py 拆分说明

原来的 `tab_home.py`（约 900 行，UI + 逻辑 + 样式 + 外部脚本全塞一起）
按"一个文件只干一件事"拆成下面的结构，界面与行为保持 100% 一致。

## 顶层包名：`home`

**所有导入一律以 `home.` 开头**，不再经过 `mvp.`。
磁盘上仍是 `OCTools/mvp/home/`，`mvp` 只是文件夹、不是包（已无 `__init__.py`）。

因此主程序需要把 **home 的父目录**（`OCTools/mvp`）放进 `sys.path`：

```python
# 主程序里加一次（或把 OCTools/mvp 设为 IDE 的 Sources Root）
sys.path.insert(0, r"<你的路径>/OCTools/mvp")

from home import TabHome              # 推荐
# 或 from home.tab_home import TabHome
```

`home/__init__.py` 与 `tab_home.py` 内部都自带路径引导，会自动补上：

| 路径 | 用途 |
|---|---|
| `OCTools/mvp` | 让 `from home.xxx import` 生效 |
| `OCTools` | 让 `from config.ui_config import` / `from ui.toast import` 生效 |

所以即便外部忘了配置，`import home` 也能自愈。

## 目录

```
OCTools/mvp/                 ← 需加入 sys.path（home 的父目录）
└── home/
    ├── __init__.py          包入口：路径引导 + 导出 TabHome
    ├── __main__.py          独立预览入口（python -m home）
    ├── constants.py         路径 / 时间窗口 / 设计令牌 / 默认任务
    ├── format_utils.py      纯函数：秒→xx小时xx分、秒→xx分xx秒、颜色插值
    ├── greeting.py          时段化问候逻辑（纯逻辑，可单测，不碰 Qt）
    ├── state.py             HomeState：home_state.json 读写 + 打卡时段判定 + 任务集合
    ├── styles.py            全部 QSS 字符串（卡片/按钮/输入框/阴影…）
    ├── tab_home.py          组装层：布局 + 每秒 tick + 信号接线（仅此一个"胶水"文件）
    ├── services/
    │   ├── net_service.py   网络加速：状态探测（线程安全回调）+ net.ps1 静默开关
    │   └── workmode_service.py  一键工作模式：home.bat 静默启动
    ├── widgets/
    │   ├── slide_switch.py  SlideSwitch：整行长滑块（拖拽/流光/呼吸/回弹）
    │   └── task_row.py      TaskRow：单条任务行（勾选 + 删除线 + 删除）
    └── sections/
        ├── hero.py          HeroSection + HeroModel（超大时钟 / 问候 / 徽章）
        ├── clockin_card.py  ClockInCard：智能打卡卡
        ├── workmode_card.py WorkModeCard：一键工作模式卡
        ├── net_card.py      NetCard：网络加速卡（内含 8s 轮询）
        └── task_card.py     TaskCard：今日任务卡
```

## 导入约定

- **跨子包**用绝对导入：`from home.styles import card_qss`
- **同一子包内**用相对导入：`services/__init__.py` 里 `from . import net_service`

## 依赖方向（单向，无环）

```
constants ──► format_utils ──► greeting
    │
    ├──► state（数据层）
    ├──► styles ──► sections / widgets
    ├──► services ──► sections
    └──► tab_home（组装，依赖以上全部）
```

`sections` 与 `widgets` 之间不互相引用：区块只发信号，TabHome 负责接线。

## 运行

```bash
# 主程序挂载
sys.path.insert(0, ".../OCTools/mvp")
from home import TabHome

# 独立预览（在 OCTools/mvp 目录下）
python -m home
```

## 回归测试（可选）

包内 `tests/` 为拆分时用的冒烟测试，跑法：

```bash
cd OCTools
python tests/test_home.py     # 七时段问候 / 状态读写 / 打卡 / 任务增删勾选 / 网络卡信号
python tests/test_switch.py   # 滑块真实拖拽 + 整窗绘制
```

`tests/_stub/` 是 `config.ui_config` 与 `ui.toast` 的最小桩实现，
仅用于脱离主程序跑测试；确认无误后可整目录删除。

## 迁移注意

1. 导入前缀 `mvp.home.` → `home.`，主程序记得把 `OCTools/mvp` 加入 `sys.path`。
2. 仍依赖 `config.ui_config.CONFIG` 与 `ui.toast.show_toast`，与原文件一致。
3. 状态文件、bat / ps1 路径全部按 `constants.py` 里的 `__file__` 推算，位置不变。
4. `home_state.json` 字段完全未改，老数据可直接沿用。
