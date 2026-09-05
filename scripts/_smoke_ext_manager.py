# -*- coding: utf-8 -*-
"""插件管理器级测试：direct 直载守卫 + lazy 按需启动 + 模式切换 + 崩溃自动重启 + 退出清理。

测试对象：
  - demo_hello（direct）：不启动子进程，call 被守卫拦截；
  - demo_tk（window）：依赖仅标准库（tkinter），无需 pip 安装即可跑完整生命周期。
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer

from services.ext_plugins import config_store, detection, paths
from services.ext_plugins.manager import PluginManager

app = QCoreApplication(sys.argv)

PASS = []


def check(name, cond, detail=""):
    PASS.append(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def wait_until(cond, timeout=10.0, interval=0.05):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if cond():
            return True
        QEventLoop().processEvents()
        time.sleep(interval)
    return False


def main():
    # 隔离测试配置：demo_tk 默认 lazy 并启用；demo_hello 启用（验证 direct 守卫）；
    # demo_numpy_a/b 禁用，避免触发 pip 安装
    cfg = config_store.load_config()
    cfg.setdefault("plugins", {})
    for pid in ("demo_hello", "demo_tk", "demo_numpy_a", "demo_numpy_b"):
        cfg["plugins"][pid] = {
            "enabled": pid in ("demo_hello", "demo_tk"),
            "load_mode": "lazy",
        }
    config_store.save_config(cfg)

    mgr = PluginManager()
    results = []
    responses = []
    states = []
    mgr.call_result.connect(lambda pid, ok, msg: results.append((pid, ok, msg)))
    mgr.call_response.connect(lambda pid, ok, result: responses.append((pid, ok, result)))
    mgr.plugin_state_changed.connect(lambda pid, st: states.append((pid, st)))

    mgr.start()
    srcs = mgr.scan()
    check("扫描到 demo_hello / demo_tk",
          "demo_hello" in srcs and "demo_tk" in srcs)

    # ── 1. direct 插件：无子进程，call 被守卫拦截 ──────────
    info = mgr.info("demo_hello")
    check("direct 模式判定", info.ui_mode == detection.UI_DIRECT
          and info.state == "READY", f"mode={info.ui_mode} state={info.state}")
    mgr.call("demo_hello", "echo", {"text": "hi"})
    ok = wait_until(lambda: any(r[0] == "demo_hello" and not r[1]
                                for r in responses), 5.0)
    check("direct 调用被守卫拦截", ok, f"responses={responses[-2:]}")
    check("direct 无子进程", "demo_hello" not in mgr._processes)

    # ── 2. lazy 模式：start 后不应自动启动 ─────────────────
    time.sleep(0.5)
    QEventLoop().processEvents()
    info = mgr.info("demo_tk")
    check("lazy 启动后无进程", info.load_mode == "lazy"
          and "demo_tk" not in mgr._processes, f"state={info.state}")

    # ── 3. 按需调用 → 进程启动并响应（sysinfo 无需额外依赖）─
    mgr.call("demo_tk", "sysinfo")
    ok = wait_until(lambda: any(r[0] == "demo_tk" and r[1] and "plugin_id" in str(r[2])
                                for r in responses), 8.0)
    check("lazy 按需启动并响应", ok, f"responses={responses[-3:]}")

    # ── 4. 切换 always → 进程保持常驻 ──────────────────────
    mgr.set_load_mode("demo_tk", "always")
    time.sleep(0.5)
    QEventLoop().processEvents()
    info = mgr.info("demo_tk")
    check("切换 always 后 RUNNING", info.state == "RUNNING"
          and mgr._processes.get("demo_tk") is not None, f"state={info.state}")

    # ── 5. 崩溃 → 自动重启 ────────────────────────────────
    proc_before = mgr._processes.get("demo_tk")
    results.clear()
    responses.clear()
    mgr.call("demo_tk", "crash")
    restarted = wait_until(
        lambda: (mgr._processes.get("demo_tk") is not None
                 and mgr._processes["demo_tk"] is not proc_before
                 and mgr._processes["demo_tk"].alive()
                 and mgr.info("demo_tk").state == "RUNNING"), 15.0)
    check("崩溃后自动重启", restarted,
          f"state={(mgr.info('demo_tk') or None) and mgr.info('demo_tk').state}")

    # ── 6. 心跳 tick ×3 后进程仍存活（无虚假强杀）────────
    proc_after = mgr._processes.get("demo_tk")
    alive_after_ticks = True
    for _ in range(3):
        mgr._heartbeat_tick()
        time.sleep(0.4)
        QEventLoop().processEvents()
        if (mgr._processes.get("demo_tk") is not proc_after
                or not mgr._processes["demo_tk"].alive()):
            alive_after_ticks = False
            break
    check("心跳后进程存活", alive_after_ticks)

    # ── 7. 退出清理 ───────────────────────────────────────
    mgr.shutdown()
    remaining = [p for p in mgr._processes.values() if p.alive()]
    check("退出后无残留进程", not remaining, f"alive={len(remaining)}")

    # 还原配置：恢复默认（避免污染 dev config）
    cfg = config_store.load_config()
    for pid in ("demo_hello", "demo_tk", "demo_numpy_a", "demo_numpy_b"):
        cfg["plugins"].pop(pid, None)
    config_store.save_config(cfg)

    ok_all = all(PASS)
    print("\n" + ("ALL PASS" if ok_all else "SOME FAILED"))
    app.exit(0 if ok_all else 1)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
