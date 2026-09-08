"""时段化问候：根据时间 + 打卡状态，算出 Hero 的四要素。

纯逻辑模块（不碰 Qt、不碰 UI），输入 datetime，输出文案与配色。

时段划分：
  ~09:00        请打卡（黄，倒计时距 09:00）
  09:00–09:05   请补卡（红，超时计时）
  09:05–12:00   距离吃饭还剩（黑，倒计时距 12:00）
  12:00–13:00   午休时间（黑，当前时间）
  13:00–17:30   距离下班还剩（黑，倒计时距 18:00）
  17:30–18:00   记得打卡，开启倒计时（黄，倒计时距 18:00）
  18:00~        快打卡（红）/ 已打卡则"下班！"（黑），均为当前时间
"""

from datetime import datetime

from home.constants import (
    AM_MIN, AM_FIX_MIN, NOON_MIN, NAP_END_MIN, PM_TIP_MIN, PM_MIN,
    INK, WARN, DANGER,
)
from home.format_utils import hm, ms, clock_hms


def greeting(now: datetime, am_done: bool = False, pm_done: bool = False):
    """返回 (提示, 时钟, 颜色, 徽章)。

      提示 —— Hero 大字文案
      时钟 —— 倒计时 'xx小时xx分'，或当前时间 'HH:MM:SS'
      颜色 —— INK 墨黑 / WARN 琥珀黄 / DANGER 危险红
      徽章 —— 右上角短标签
    """
    m = now.hour * 60 + now.minute                  # 当前时刻（分钟）
    s = now.hour * 3600 + now.minute * 60 + now.second
    cur = clock_hms(now)                            # 当前时间 HH:MM:SS

    def left(target: int) -> int:                   # 距目标时刻剩余秒
        return target * 60 - s

    if m < AM_MIN:                                  # ① 09:00 前
        if am_done:
            return "距离吃饭还剩", hm(left(NOON_MIN)), INK, "已打卡"
        return "请打卡", hm(left(AM_MIN)), WARN, "请打卡"

    if m < AM_FIX_MIN:                              # ② 09:00–09:05 补卡窗口
        if am_done:
            return "距离吃饭还剩", hm(left(NOON_MIN)), INK, "已打卡"
        return "请补卡", "超时 " + ms(-left(AM_MIN)), DANGER, "请补卡"

    if m < NOON_MIN:                                # ③ 09:05–12:00
        return "距离吃饭还剩", hm(left(NOON_MIN)), INK, "工作中"

    if m < NAP_END_MIN:                             # ④ 12:00–13:00
        return "午休时间", cur, INK, "午休"

    if m < PM_TIP_MIN:                              # ⑤ 13:00–17:30
        return "距离下班还剩", hm(left(PM_MIN)), INK, "工作中"

    if m < PM_MIN:                                  # ⑥ 17:30–18:00
        return "记得打卡，开启倒计时", hm(left(PM_MIN)), WARN, "待打卡"

    if pm_done:                                     # ⑦ 18:00 后 · 已打卡
        return "下班！", cur, INK, "已打卡"
    return "快打卡", cur, DANGER, "待打卡"          # ⑦ 18:00 后 · 未打卡
