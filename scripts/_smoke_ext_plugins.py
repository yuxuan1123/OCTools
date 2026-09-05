# -*- coding: utf-8 -*-
"""插件统一架构冒烟测试：
ui_mode 自动检测 + host.py 统一运行时 + IPC/心跳/崩溃 + desc 控件树 + window 独立窗口。
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.ext_plugins import detection
from services.ext_plugins.process import PluginProcess
from services.ext_plugins.paths import plugins_dir, deps_dir, app_root

HOST_PY = os.path.join(ROOT, "services", "ext_plugins", "host.py")


def make_proc(plugin_id):
    p = PluginProcess(plugin_id)
    ok = p.start(
        python_exe=sys.executable,
        main_py=HOST_PY,
        deps_dir=os.path.join(deps_dir(), plugin_id),
        cwd=os.path.join(plugins_dir(), plugin_id),
        home=app_root(),
    )
    return p, ok


def req(proc, method, params=None, timeout=8.0):
    """发送请求并等待响应。"""
    box = {}

    def cb(resp):
        box["resp"] = resp

    req_id = proc.send_request(method, params, cb)
    t0 = time.time()
    while time.time() - t0 < timeout:
        if "resp" in box:
            return box["resp"]
        time.sleep(0.05)
    return {"_timeout": True, "id": req_id}


PASS = []


def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    PASS.append(cond)
    print(f"[{tag}] {name} {detail}")
    return cond


def main():
    # ── 0. ui_mode 自动检测（detect_ui_mode）───────────────
    check("无依赖 → direct", detection.detect_ui_mode("") == detection.UI_DIRECT)
    check("仅 PySide6 → direct",
          detection.detect_ui_mode("pyside6\npyside6-essentials") == detection.UI_DIRECT)
    check("PySide6 + numpy → desc",
          detection.detect_ui_mode("pyside6\nnumpy==2.0.2") == detection.UI_DESC)
    check("仅 numpy → desc",
          detection.detect_ui_mode("numpy==2.0.2") == detection.UI_DESC)
    check("tkinter → window",
          detection.detect_ui_mode("tkinter") == detection.UI_WINDOW)
    srcs = detection.scan_plugins()
    check("扫描 demo_hello direct",
          srcs.get("demo_hello") and srcs["demo_hello"].ui_mode == detection.UI_DIRECT,
          f"got={srcs.get('demo_hello') and srcs['demo_hello'].ui_mode}")
    check("扫描 demo_numpy_a desc",
          srcs.get("demo_numpy_a") and srcs["demo_numpy_a"].ui_mode == detection.UI_DESC,
          f"got={srcs.get('demo_numpy_a') and srcs['demo_numpy_a'].ui_mode}")
    check("扫描 demo_tk window",
          srcs.get("demo_tk") and srcs["demo_tk"].ui_mode == detection.UI_WINDOW,
          f"got={srcs.get('demo_tk') and srcs['demo_tk'].ui_mode}")

    # ── 1. host.py 运行时：desc 插件 IPC ────────────────────
    p, ok = make_proc("demo_numpy_a")
    check("desc 进程启动", ok and p.alive())
    time.sleep(0.8)

    r = req(p, "sysinfo")
    si = r.get("result", {}) or {}
    check("sysinfo 响应", bool(si), f"got={r}")
    check("PLUGIN_ID 注入", si.get("plugin_id") == "demo_numpy_a", f"got={si.get('plugin_id')}")
    check("PYTHONPATH 隔离", deps_dir() in si.get("pythonpath", ""),
          f"got={si.get('pythonpath')}")
    check("cwd 指向插件目录", si.get("cwd", "").endswith("demo_numpy_a"),
          f"got={si.get('cwd')}")

    r = req(p, "bogus_method")
    check("未知方法返回 error", "error" in r, f"got={r}")

    # ── 2. 心跳 pong ───────────────────────────────────────
    t_before = p.last_pong
    p.ping()
    time.sleep(0.5)
    check("心跳 pong", p.last_pong > t_before, f"before={t_before} after={p.last_pong}")

    # ── 3. shutdown 正常退出 ───────────────────────────────
    exit_box = {}
    p.exited.connect(lambda pid, code: exit_box.setdefault("code", code))
    p.shutdown()
    t0 = time.time()
    while time.time() - t0 < 5 and p.alive():
        time.sleep(0.1)
    check("shutdown 后退出", not p.alive(), f"exit_code={exit_box.get('code')}")

    # ── 4. crash 后 exited 信号带非零码 ────────────────────
    p2, ok = make_proc("demo_numpy_a")
    time.sleep(0.8)
    r_crash = req(p2, "crash")
    print("  [diag] crash req ->", r_crash)
    t0 = time.time()
    while time.time() - t0 < 5 and p2.alive():
        time.sleep(0.05)
    code = p2.proc.returncode if p2.proc else None
    check("crash 退出码非零", code not in (None, 0), f"code={code}")

    # ── 5. desc 控件树（依赖已安装时）──────────────────────
    if os.path.isdir(os.path.join(deps_dir(), "demo_numpy_a")):
        p3, _ = make_proc("demo_numpy_a")
        time.sleep(0.8)
        r = req(p3, "describe_ui")
        ui = r.get("result") or {}
        check("describe_ui 返回控件树", ui.get("type") == "VBox"
              and isinstance(ui.get("children"), list), f"got={str(ui)[:120]}")
        r = req(p3, "invoke_action", {"action": "refresh", "params": {}})
        inv = r.get("result") or {}
        check("invoke_action 返回 UI", inv.get("ui", {}).get("type") == "VBox",
              f"got={str(inv)[:120]}")
        check("invoke_action 携带 toast 协议",
              isinstance(inv.get("toast"), dict) and inv["toast"].get("message"),
              f"got={inv.get('toast')}")
        p3.shutdown()
        time.sleep(0.5)
    else:
        print("[SKIP] deps 未安装，跳过控件树验证（可先运行主程序自动安装）")

    # ── 6. window 模式（demo_tk：独立 tkinter 窗口）────────
    pw, ok = make_proc("demo_tk")
    check("window 进程启动", ok and pw.alive())
    time.sleep(1.2)   # 等待窗口线程创建
    check("window 进程存活（窗口线程未阻塞主循环）", pw.alive())
    t_before = pw.last_pong
    pw.ping()
    time.sleep(0.5)
    check("window 心跳 pong", pw.last_pong > t_before,
          f"before={t_before} after={pw.last_pong}")
    exit_box.clear()
    pw.exited.connect(lambda pid, code: exit_box.setdefault("code", code))
    pw.shutdown()
    t0 = time.time()
    while time.time() - t0 < 5 and pw.alive():
        time.sleep(0.1)
    check("window shutdown 退出", not pw.alive(), f"exit_code={exit_box.get('code')}")

    # ── 清理残留 ──────────────────────────────────────────
    for proc in (p, p2):
        if proc.alive():
            proc.send_shutdown()
    time.sleep(0.8)
    for proc in (p, p2, pw):
        if proc.alive():
            proc.kill_tree(grace_s=1)

    ok_all = all(PASS)
    print("\n" + ("ALL PASS" if ok_all else "SOME FAILED"))
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
