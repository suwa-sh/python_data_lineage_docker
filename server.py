#!/usr/bin/env python3
import os
import sys
import http.server
import socketserver
import subprocess

def serve_http():
    """widget配下でHTTPサーバーを起動"""
    os.chdir("widget")
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://0.0.0.0:{PORT}/")
        httpd.serve_forever()

def run_dlineage(args):
    """dlineage.pyコマンドを実行"""
    cmd = ["python3", "dlineage.py"] + args
    result = subprocess.run(cmd, cwd="/app")
    sys.exit(result.returncode)

if __name__ == "__main__":
    # 引数がない場合、または最初の引数が"serve"の場合はHTTPサーバーを起動
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "serve"):
        serve_http()
    else:
        # それ以外の場合はdlineage.pyに引数を渡して実行
        run_dlineage(sys.argv[1:])