"""首页全局常量：路径 · 时间窗口 · 设计令牌 · 默认任务。

职责单一：只放"不会变的值"，不依赖 Qt、不依赖业务逻辑。
"""

from pathlib import Path

# ── 路径 ─────────────────────────────────
_HOME_DIR = Path(__file__).resolve().parent
STATE_FILE = _HOME_DIR / "home_state.json"     # 打卡 + 任务持久化
BAT_FILE = _HOME_DIR / "home.bat"              # 一键工作模式脚本
NET_PS1 = _HOME_DIR / "net.ps1"                # 网络加速脚本

# ── 打卡时间窗口（分钟级判定）──────────────
AM_DEADLINE = 9                                # 09:00 上午打卡截止
AM_FIX_MIN = 9 * 60 + 5                        # 09:05 补卡窗口关闭
PM_START = 18                                  # 18:00 下午打卡开放

# ── 时段边界（当日 0 点起的分钟数）─────────
AM_MIN = 9 * 60                                # 09:00
NOON_MIN = 12 * 60                             # 12:00 吃饭
NAP_END_MIN = 13 * 60                          # 13:00 午休结束
PM_TIP_MIN = 17 * 60 + 30                      # 17:30 提醒打卡
PM_MIN = 18 * 60                               # 18:00 下班

# ── 网络加速静态 IP（用于状态探测）────────
NET_STATIC_IP = "172.17.174.5"

# ══════════════════════════════════════════
#  设计令牌（白灰高级 · 墨黑强调 · 零蓝色）
# ══════════════════════════════════════════
INK = "#18181B"        # 墨黑：主文字 / 主按钮 / 开启态
GRAPHITE = "#27272A"   # 石墨：hover 加深
MUTED = "#71717A"      # 次要文字
FAINT = "#A1A1AA"      # 弱化文字
WARN = "#D97706"       # 琥珀黄：请打卡 / 下班倒计时
DANGER = "#DC2626"     # 危险红：请补卡 / 下班未打卡
BORDER = "#E8E8EB"     # 卡片描边
BORDER_HV = "#D4D4D8"  # hover 描边
SOFT_BG = "#F4F4F5"    # 浅底
CARD_BG = "#FFFFFF"
PAGE_A = "#FCFCFD"     # 页面渐变起
PAGE_B = "#EFEFF2"     # 页面渐变止
SUCCESS = "#059669"    # 完成态点缀
SUCCESS_BG = "#ECFDF5"
TRACK_OFF = "#E4E4E7"  # 滑块关闭轨道
TRACK_ON = "#18181B"   # 滑块开启轨道（墨黑）
THUMB_C = "#FFFFFF"    # 滑块圆钮

# ── 默认任务 ───────────────────────────────
DEFAULT_TASKS = [
    {"id": 1, "text": "每日站会", "done": False},
    {"id": 2, "text": "代码 Review", "done": False},
    {"id": 3, "text": "提交工时", "done": False},
]
