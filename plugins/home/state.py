"""首页状态：home_state.json 的读写 + 打卡时段判定 + 任务集合。

只负责"数据"，不负责任何界面。
字段：am_date / am_time / pm_date / pm_time / tasks / next_id
"""

import json
from datetime import date, datetime

from home.constants import (
    AM_DEADLINE, AM_FIX_MIN, PM_START, DEFAULT_TASKS, STATE_FILE,
)


class HomeState:
    """打卡记录 + 任务清单的持久化容器。"""

    def __init__(self):
        self.tasks = []
        self.next_id = 1
        self.am_date = ""
        self.am_time = ""
        self.pm_date = ""
        self.pm_time = ""
        self.load()

    # ──────────────────────────────────────
    #  持久化
    # ──────────────────────────────────────
    def load(self):
        data = {}
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                data = {}
        self.tasks = data.get("tasks") or [dict(t) for t in DEFAULT_TASKS]
        max_id = max((t["id"] for t in self.tasks), default=0)
        self.next_id = data.get("next_id") or (max_id + 1)
        self.am_date = data.get("am_date", "")
        self.am_time = data.get("am_time", "")
        self.pm_date = data.get("pm_date", "")
        self.pm_time = data.get("pm_time", "")

    def save(self):
        data = {
            "tasks": self.tasks,
            "next_id": self.next_id,
            "am_date": self.am_date, "am_time": self.am_time,
            "pm_date": self.pm_date, "pm_time": self.pm_time,
        }
        try:
            STATE_FILE.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ──────────────────────────────────────
    #  打卡
    # ──────────────────────────────────────
    @property
    def today(self) -> str:
        return date.today().isoformat()

    @property
    def am_done(self) -> bool:
        return self.am_date == self.today

    @property
    def pm_done(self) -> bool:
        return self.pm_date == self.today

    @property
    def last_iso(self) -> str:
        """最近一次打卡的 ISO 串（优先下午）。"""
        return self.pm_time or self.am_time

    def punch(self, slot: str) -> str:
        """写入当前时段的打卡时间，返回 ISO 串。"""
        iso = datetime.now().isoformat(timespec="seconds")
        today = self.today
        if slot == "am":
            self.am_date, self.am_time = today, iso
        else:
            self.pm_date, self.pm_time = today, iso
        self.save()
        return iso

    def clockin_state(self) -> tuple:
        """返回 (slot, status, hint)。

        slot   : 'am' / 'pm' / 'none'
        status : 'pending' 可打卡 / 'done' 已完成 / 'off' 非打卡时段
        hint   : 展示用的一行说明
        """
        today = self.today
        now = datetime.now()
        m = now.hour * 60 + now.minute
        secs = now.hour * 3600 + now.minute * 60 + now.second

        # 09:05 前：上午时段（含补卡窗口）
        if m < AM_FIX_MIN:
            if self.am_date == today:
                return ("am", "done",
                        f"上午已打卡 · {self.am_time[11:19] if self.am_time else '—'}")
            rem = AM_DEADLINE * 3600 - secs
            if rem >= 0:
                return ("am", "pending",
                        f"上午待打卡 · 截止 09:00（剩 {rem // 3600:02d}:{rem % 3600 // 60:02d}）")
            over = int(-rem)
            return ("am", "pending",
                    f"请补卡 · 已超时 {over // 60:02d}分{over % 60:02d}秒")

        # 18:00 后：下午时段
        if m >= PM_START * 60:
            if self.pm_date == today:
                return ("pm", "done",
                        f"下午已打卡 · {self.pm_time[11:19] if self.pm_time else '—'}")
            return ("pm", "pending", "下午待打卡 · 下班时间")

        # 中间：非打卡时段
        if self.am_date == today:
            return ("none", "off", "上午已完成 · 等待 18:00 后打下午卡")
        return ("none", "off", "上午已过期 · 等待 18:00 后打下午卡")

    # ──────────────────────────────────────
    #  任务
    # ──────────────────────────────────────
    def add_task(self, text: str):
        text = (text or "").strip()
        if not text:
            return None
        task = {"id": self.next_id, "text": text, "done": False}
        self.tasks.append(task)
        self.next_id += 1
        self.save()
        return task

    def toggle_task(self, tid: int, done: bool):
        for t in self.tasks:
            if t["id"] == tid:
                t["done"] = done
                break
        self.save()

    def remove_task(self, tid: int):
        self.tasks = [t for t in self.tasks if t["id"] != tid]
        self.save()

    def done_count(self) -> int:
        return sum(1 for t in self.tasks if t.get("done"))
