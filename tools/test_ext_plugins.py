# -*- coding: utf-8 -*-
"""
OCTools/tools/test_ext_plugins.py
───────────────────────────────────────────────
外部插件系统冒烟测试（无头运行，无需管理员权限）。

验证检查点：
  1. 扫描 / 状态机：demo_hello（无依赖）直接就绪；demo_numpy_*（有依赖）进入待安装。
  2. 模式切换：lazy → always 立即启动子进程。
  3. IPC 调用：env / echo 返回正确结果（含 PYTHONPATH 隔离环境）。
  4. 崩溃重启：调用 crash → 进程退出 → always 模式自动重启（≤3 次）。
  5. 心跳超时：调用 sleep(15) 阻塞 → 12s 无心跳 → 强制终止并重启。
  6. 依赖安装 + 隔离：pip（无 uv 时回退）安装 numpy 到各自 deps/，
     两个插件分别返回 numpy 2.0.x 与 1.26.x，互不污染。
  7. 退出清理：shutdown 后无存活子进程。

用法：.venv\\Scripts\\python.exe tools/test_ext_plugins.py
"""

import os
import sys
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

app = QApplication([])

from services.ext_plugins.manager import PluginManager  # noqa: E402

T0 = time.monotonic()


def now() -> float:
    return time.monotonic() - T0


mgr = PluginManager.instance()
RESULTS: dict[str, list] = {}
STATES: dict[str, list] = {}
mgr.call_result.connect(
    lambda pid, ok, msg: RESULTS.setdefault(pid, []).append((ok, msg)))
mgr.plugin_state_changed.connect(
    lambda pid, st: STATES.setdefault(pid, []).append(st))


def snapshot(tag: str):
    print(f"\n=== {tag}  t={now():.1f}s ===", flush=True)
    for pid, info in sorted(mgr.scan().items()):
        print(f"  {pid}: state={info.state} enabled={info.enabled} "
              f"mode={info.load_mode} has_deps={info.has_deps}", flush=True)
    for pid, rs in sorted(RESULTS.items()):
        print(f"  results[{pid}][-2:] = {rs[-2:]}", flush=True)
    for pid, ss in sorted(STATES.items()):
        print(f"  states[{pid}] = {ss}", flush=True)


def fail(msg: str):
    print(f"  ❌ {msg}", flush=True)


def ok(msg: str):
    print(f"  ✔ {msg}", flush=True)


def schedule(delay: float, fn):
    QTimer.singleShot(int(delay * 1000), fn)


def final_verify():
    print("\n=== 验证汇总 ===", flush=True)
    fails = []

    # 1. demo_hello 调用结果
    rs = RESULTS.get("demo_hello", [])
    if not any(okk and "echo" in m for okk, m in rs):
        fails.append("demo_hello echo 无成功结果")
    env_rs = [m for okk, m in rs if okk and m.startswith("[env]")]
    if not env_rs or "deps" not in env_rs[-1] and "demo_hello" not in env_rs[-1]:
        fails.append("demo_hello env 未返回隔离环境")
    else:
        ok(f"env → {env_rs[-1]}")
    # 2. 崩溃重启：崩溃后状态应回到 RUNNING
    st = STATES.get("demo_hello", [])
    if st.count("CRASHED") >= 2:
        fails.append("demo_hello 崩溃超过一次（重启失败）")
    if st[-1] not in ("RUNNING", "STOPPING"):
        fails.append(f"demo_hello 最终状态异常: {st[-1]}")
    # 3. numpy 隔离
    ra = RESULTS.get("demo_numpy_a", [])
    rb = RESULTS.get("demo_numpy_b", [])
    va = [m for okk, m in ra if okk and "numpy_version" in m]
    vb = [m for okk, m in rb if okk and "numpy_version" in m]
    if not va or not vb:
        fails.append("numpy 版本调用未成功")
    else:
        if "2.0" in va[-1] and "1.26" in vb[-1]:
            ok(f"隔离验证：A={va[-1]}  B={vb[-1]}")
        else:
            fails.append(f"版本异常：A={va[-1] if va else '?'} B={vb[-1] if vb else '?'}")
    # 4. 退出清理
    alive = [pid for pid, p in mgr._processes.items() if p.alive()]
    if alive:
        fails.append(f"退出后仍有存活进程: {alive}")

    if fails:
        print("\n❌ 测试失败：")
        for f in fails:
            print(f"  - {f}", flush=True)
    else:
        print("\n✅ 全部检查点通过", flush=True)
    app.quit()


# ── 步骤调度 ─────────────────────────────
def step1():
    print("=== 启动管理器（demo_numpy_* 依赖安装已在后台开始） ===", flush=True)
    mgr.start()
    snapshot("启动后")
    schedule(3.0, step2)


def step2():
    snapshot("3s")
    mgr.set_load_mode("demo_hello", "always")   # lazy → always，立即启动
    ok("demo_hello 模式切换为 always")
    schedule(3.0, step3)


def step3():
    snapshot("6s")
    mgr.call("demo_hello", "env", {})
    mgr.call("demo_hello", "echo", {"text": "你好"})
    ok("已调用 env + echo")
    schedule(3.0, step4)


def step4():
    snapshot("9s")
    mgr.call("demo_hello", "crash")
    ok("已调用 crash（应自动重启）")
    schedule(5.0, step5)


def step5():
    snapshot("14s")
    if STATES.get("demo_hello", []) and STATES["demo_hello"][-1] == "RUNNING":
        ok("崩溃后已自动重启为 RUNNING")
    else:
        fail("崩溃后未自动重启")
    schedule(3.0, step6)


def step6():
    snapshot("17s")
    mgr.call("demo_hello", "sleep", {"seconds": 15})
    ok("已调用 sleep(15)（应触发心跳超时）")
    schedule(16.0, step7)


def step7():
    snapshot("33s")
    if STATES.get("demo_hello", []) and STATES["demo_hello"][-1] == "RUNNING":
        ok("心跳超时后已自动重启为 RUNNING")
    else:
        fail("心跳超时未恢复 RUNNING")
    schedule(2.0, step8)


def step8():
    # 等待 numpy 依赖安装完成（后台队列串行执行）
    print("\n=== 等待 demo_numpy_* 依赖安装 ===", flush=True)
    wait_install()


def wait_install():
    infos = mgr.scan()
    a = infos.get("demo_numpy_a")
    b = infos.get("demo_numpy_b")
    done = (a and a.state in ("READY", "INSTALL_FAILED", "RUNNING")
            and b and b.state in ("READY", "INSTALL_FAILED", "RUNNING"))
    if not done:
        if now() > 240:
            fail("依赖安装超时")
            schedule(0.5, final_verify)
            return
        if a and a.state == "INSTALLING":
            pass
        QTimer.singleShot(5000, wait_install)
        return
    snapshot("安装完成")
    if a.state == "INSTALL_FAILED" or b.state == "INSTALL_FAILED":
        fail("依赖安装失败")
        schedule(0.5, final_verify)
        return
    mgr.set_load_mode("demo_numpy_a", "always")
    mgr.set_load_mode("demo_numpy_b", "always")
    ok("numpy 插件切换为 always 并启动")
    schedule(3.0, step9)


def step9():
    snapshot("numpy 启动后")
    mgr.call("demo_numpy_a", "numpy_version", {})
    mgr.call("demo_numpy_b", "numpy_version", {})
    ok("已调用 numpy_version")
    schedule(3.0, step10)


def step10():
    snapshot("numpy 结果")
    schedule(1.0, final_verify)


schedule(0.5, step1)
print("运行中，预计 1-4 分钟（含 numpy 下载安装）…", flush=True)
sys.exit(app.exec())
