#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""冷藏车运营管理 - 共享服务器"""
import http.server
import json
import os
import socketserver
import urllib.parse
import urllib.request
from datetime import datetime, timezone

PORT = int(os.environ.get("PORT", "8080"))
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")
DATA_FILE = os.environ.get("DATA_FILE", os.path.join(os.path.dirname(__file__), "server_data.json"))
HTML_FILE = os.path.join(os.path.dirname(__file__), "index.html")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SUPABASE_TABLE = os.environ.get("SUPABASE_TABLE", "logistics_data")
DATA_ID = os.environ.get("DATA_ID", "main")

def use_supabase():
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)

def supabase_request(method, path, body=None):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if method == "POST":
        headers["Prefer"] = "resolution=merge-duplicates"
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else None

def load_data():
    if use_supabase():
        rows = supabase_request("GET", f"{SUPABASE_TABLE}?id=eq.{urllib.parse.quote(DATA_ID)}&select=data")
        if rows:
            return rows[0].get("data") or {"trucks": [], "expenses": []}
        return {"trucks": [], "expenses": []}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"trucks": [], "expenses": []}

def save_data(data):
    if use_supabase():
        supabase_request("POST", f"{SUPABASE_TABLE}?on_conflict=id", {
            "id": DATA_ID,
            "data": data,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        return
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_password_from_headers(handler):
    return handler.headers.get("X-App-Password", "")

def is_authorized(handler):
    return not APP_PASSWORD or get_password_from_headers(handler) == APP_PASSWORD

def send_unauthorized(handler):
    handler.send_response(401)
    handler.send_header("Content-Type", "application/json;charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(json.dumps({"error": "unauthorized"}).encode("utf-8"))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/data":
            if not is_authorized(self):
                send_unauthorized(self)
                return
            data = load_data()
            self.send_response(200)
            self.send_header("Content-Type", "application/json;charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        elif path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html;charset=utf-8")
            self.end_headers()
            if os.path.exists(HTML_FILE):
                with open(HTML_FILE, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            else:
                self.wfile.write(b"index.html not found")
        else:
            super().do_GET()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/data":
            if not is_authorized(self):
                send_unauthorized(self)
                return
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                new_data = json.loads(body)
                save_data(new_data)
                self.send_response(200)
                self.send_header("Content-Type", "application/json;charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json;charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-App-Password")
        self.end_headers()

if __name__ == "__main__":
    import socket
    host = socket.gethostbyname(socket.gethostname())
    print("=" * 50)
    print("  冷藏车运营管理系统 - 共享服务器")
    print("=" * 50)
    print(f"  本机访问: http://localhost:{PORT}")
    print(f"  局域网访问: http://{host}:{PORT}")
    print(f"  数据文件: {DATA_FILE}")
    print("=" * 50)
    print("  按 Ctrl+C 停止服务器")
    print("=" * 50)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
