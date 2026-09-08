#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TabMd 本地服务 —— 零依赖（只用标准库）

作用：
  1. 自动扫描同级 md/ 目录下的所有 .md 文件，提供列表接口
  2. 提供读取 / 保存 / 删除 / 新建接口，让页面能真正把改动写回磁盘
  3. 静态托管本目录（直接双击 html 也能用，但只有启了服务才能保存）

用法：
  python3 server.py            # 默认 http://localhost:8848
  python3 server.py 9000       # 指定端口
  python3 server.py 8848 --no-open   # 不自动打开浏览器
"""
import json
import os
import sys
import webbrowser
import threading
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

ROOT = os.path.dirname(os.path.abspath(__file__))
MD_DIR = os.path.join(ROOT, "md")
os.makedirs(MD_DIR, exist_ok=True)


def safe_name(name):
    """只允许 md 目录下的 .md 文件，禁止 ../ 等穿越。"""
    name = unquote(name or "").strip()
    name = os.path.basename(name)
    if not name:
        raise ValueError("文件名不能为空")
    if not name.lower().endswith(".md"):
        name += ".md"
    return name


def first_heading(text):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()[:80]
    return ""


def scan():
    files = []
    for fn in os.listdir(MD_DIR):
        p = os.path.join(MD_DIR, fn)
        if not fn.lower().endswith(".md") or not os.path.isfile(p):
            continue
        st = os.stat(p)
        title = ""
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                title = first_heading(f.read(4096))
        except Exception:
            pass
        files.append({"name": fn, "size": st.st_size, "mtime": st.st_mtime, "title": title})
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return files


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    # ---------- 工具 ----------
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _text(self, s, code=200, ct="text/plain; charset=utf-8"):
        body = s.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n).decode("utf-8", errors="replace") if n else ""

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s - %s\n" % (self.address_string(), fmt % args))

    # ---------- 路由 ----------
    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)

        if u.path == "/api/files":
            return self._json(scan())

        if u.path == "/api/file":
            try:
                name = safe_name(q.get("name", [""])[0])
            except ValueError as e:
                return self._json({"error": str(e)}, 400)
            p = os.path.join(MD_DIR, name)
            if not os.path.exists(p):
                return self._json({"error": "文件不存在: " + name}, 404)
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                return self._text(f.read())

        if u.path == "/api/manifest":
            data = {"updated": datetime.now().isoformat(timespec="seconds"), "files": scan()}
            if q.get("write", [""])[0] == "1":      # 落盘，供纯静态部署使用
                with open(os.path.join(MD_DIR, "manifest.json"), "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            return self._json(data)

        return super().do_GET()

    def do_PUT(self):
        self._write_file()

    def do_POST(self):
        self._write_file()

    def _write_file(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path != "/api/file":
            return self._json({"error": "not found"}, 404)
        try:
            name = safe_name(q.get("name", [""])[0])
        except ValueError as e:
            return self._json({"error": str(e)}, 400)
        with open(os.path.join(MD_DIR, name), "w", encoding="utf-8") as f:
            f.write(self._body())
        return self._json({"ok": True, "name": name, "files": len(scan())})

    def do_DELETE(self):
        q = parse_qs(urlparse(self.path).query)
        if urlparse(self.path).path != "/api/file":
            return self._json({"error": "not found"}, 404)
        try:
            name = safe_name(q.get("name", [""])[0])
        except ValueError as e:
            return self._json({"error": str(e)}, 400)
        p = os.path.join(MD_DIR, name)
        if os.path.exists(p):
            os.remove(p)
            return self._json({"ok": True, "name": name})
        return self._json({"error": "文件不存在"}, 404)


def main():
    port = 8848
    auto_open = True
    for a in sys.argv[1:]:
        if a == "--no-open":
            auto_open = False
        elif a.isdigit():
            port = int(a)

    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    url = "http://localhost:%d" % port
    print("=" * 52)
    print("  TabMd 已启动")
    print("  目录     : %s" % MD_DIR)
    print("  文件数   : %d" % len(scan()))
    print("  访问     : %s" % url)
    print("  静默启动 : python3 server.py %d --no-open" % port)
    print("  停止     : Ctrl+C")
    print("=" * 52)
    if auto_open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        srv.shutdown()


if __name__ == "__main__":
    main()
