# -*- coding: utf-8 -*-
"""
OCTools/services/ext_plugins/host.py
───────────────────────────────────────────────
统一插件子进程运行时（替代各插件自带的 main.py）。

由主进程以 `python host.py <plugin_id>` 启动（plugin_id 亦可经 PLUGIN_ID 环境变量传入）。

职责：
  - 读取 plugins/manifests/<plugin_id>.json，按 ui_mode 分发：
      desc   : import 插件模块 → 实例化 → 处理 describe_ui / invoke_action 请求，
               插件返回控件树 JSON，由主进程渲染；
      window : 实例化 → 调用 show() 创建独立窗口，窗口完全由子进程绘制，
               主进程仅通过 IPC 管理生命周期。
  - 兼容旧 main.py 格式：将未识别的 method 直接转发给插件实例同名方法。

JSON Lines 协议（与主进程 ipc.py 一致）：
  - 请求   {"id": N, "method": "...", "params": {...}}
  - 响应   {"id": N, "result": {...}} | {"id": N, "error": {...}}
  - 心跳   {"ping": true} → {"pong": true}；关闭 {"shutdown": true}
"""

import importlib
import json
import os
import sys
import threading


def _project_root() -> str:
    """services/ext_plugins/host.py → 项目根目录。"""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


def load_manifest(plugin_id: str, root: str) -> dict:
    mf = os.path.join(root, "plugins", "manifests", f"{plugin_id}.json")
    with open(mf, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"manifest 格式错误：{mf}")
    return data


def build_instance(manifest: dict):
    """按 manifest 导入模块并实例化插件类。"""
    module_path = manifest.get("module_path", "")
    class_name = manifest.get("class_name", "")
    if not module_path or not class_name:
        raise ValueError(f"manifest 缺少 module_path/class_name：{manifest.get('name', '')}")
    module = importlib.import_module(module_path)
    return getattr(module, class_name)()


def handle(instance, method: str, params: dict):
    """方法分发：返回结果；异常交由主循环转为 error 响应。"""
    params = params or {}
    if method == "sysinfo":
        # 诊断：验证依赖隔离 / 环境注入
        return {
            "python": sys.version.split()[0],
            "plugin_id": os.environ.get("PLUGIN_ID", ""),
            "pythonpath": os.environ.get("PYTHONPATH", ""),
            "cwd": os.getcwd(),
        }
    if method == "describe_ui":
        ui = instance.describe_ui()
        return ui if isinstance(ui, dict) else {"type": "VBox", "children": []}
    if method == "invoke_action":
        action = params.get("action", "")
        action_params = params.get("params") or {}
        result = instance.invoke_action(action, action_params)
        return result if isinstance(result, dict) else {"result": result}
    if method == "crash":
        # 崩溃重启测试
        os._exit(3)
    if method == "sleep":
        # 心跳超时测试
        secs = min(float(params.get("seconds", 15)), 60)
        threading.Event().wait(secs)
        return {"slept": secs}
    # 兼容旧 main.py 格式：转发到实例同名方法
    handler = getattr(instance, method, None)
    if callable(handler):
        result = handler(params)
        return result if isinstance(result, dict) else {"result": result}
    raise ValueError(f"unknown method: {method}")


def main():
    plugin_id = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PLUGIN_ID", "")
    if not plugin_id:
        print(json.dumps({"error": {"code": -1, "message": "缺少 plugin_id"}}), flush=True)
        return
    root = _project_root()
    if root not in sys.path:
        sys.path.insert(0, root)

    instance = None
    try:
        manifest = load_manifest(plugin_id, root)
        instance = build_instance(manifest)
    except Exception as e:  # noqa: BLE001 - 启动阶段需向主进程报告
        print(json.dumps({"error": {"code": -1,
                                    "message": f"init: {type(e).__name__}: {e}"}}),
              flush=True)
        return

    ui_mode = manifest.get("ui_mode", "desc")
    if ui_mode == "window":
        show = getattr(instance, "show", None)
        if callable(show):
            # 独立窗口在守护线程中创建：mainloop 阻塞不占用主线程，
            # 主线程继续处理 stdin（心跳 ping / shutdown 才能及时响应）。
            def _run_window():
                try:
                    show()
                except Exception as e:  # noqa: BLE001 - 窗口创建失败需上报
                    print(json.dumps({"error": {"code": -1,
                                                "message": f"show: {type(e).__name__}: {e}"}}),
                          flush=True)

            threading.Thread(target=_run_window, daemon=True).start()

    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if not isinstance(msg, dict):
            continue
        if msg.get("ping") is True:
            print(json.dumps({"pong": True}), flush=True)
            continue
        if msg.get("shutdown"):
            print(json.dumps({"event": "bye"}), flush=True)
            sys.exit(0)
        req_id = msg.get("id")
        if req_id is None:
            continue
        try:
            result = handle(instance, msg.get("method"), msg.get("params"))
            print(json.dumps({"id": req_id, "result": result}), flush=True)
        except Exception as e:  # noqa: BLE001 - 协议边界需捕获一切异常
            print(json.dumps({
                "id": req_id,
                "error": {"code": -1, "message": f"{type(e).__name__}: {e}"},
            }), flush=True)


if __name__ == "__main__":
    main()
