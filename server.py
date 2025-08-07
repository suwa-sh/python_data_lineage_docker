#!/usr/bin/env python3
import os
import sys
import http.server
import socketserver
import subprocess
import json
import glob

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """カスタムHTTPリクエストハンドラー"""
    
    def do_GET(self):
        if self.path == "/api/json-files":
            # JSONファイルのリストを返す
            self.send_json_file_list()
        elif self.path == "/api/er-json-files":
            # ER図のJSONファイルのリストを返す
            self.send_er_json_file_list()
        else:
            # 通常のファイルサービング
            super().do_GET()
    
    def send_json_file_list(self):
        """json/ディレクトリ内のJSONファイルリストを返す"""
        try:
            # json/ディレクトリ内のJSONファイルを検索
            json_files = glob.glob("data/output/dlineage/lineageGraph_*.json")
            # ファイル名のみを取得
            file_names = [os.path.basename(f) for f in json_files]
            # 更新時刻でソート（新しい順）
            file_names.sort(key=lambda f: os.path.getmtime(f"data/output/dlineage/{f}"), reverse=True)
            
            # レスポンスを送信
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(file_names).encode())
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def send_er_json_file_list(self):
        """ER図のJSONファイルリストを返す"""
        try:
            # data/output/dlineage/ディレクトリ内のER図JSONファイルを検索
            json_files = glob.glob("data/output/dlineage/erGraph_*.json")
            # ファイル名のみを取得
            file_names = [os.path.basename(f) for f in json_files]
            # 更新時刻でソート（新しい順）
            if file_names:
                file_names.sort(key=lambda f: os.path.getmtime(f"data/output/dlineage/{f}"), reverse=True)
            
            # レスポンスを送信
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(file_names).encode())
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

def serve_http():
    """widget配下でHTTPサーバーを起動"""
    os.chdir("widget")
    PORT = 8000
    Handler = CustomHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://0.0.0.0:{PORT}/")
        httpd.serve_forever()

def run_dlineage(args):
    """dlineage.pyコマンドを実行"""
    cmd = ["python3", "dlineage.py"] + args
    result = subprocess.run(cmd, cwd="/app")
    sys.exit(result.returncode)

def run_analyze_delete(args):
    """analyze_delete.pyコマンドを実行"""
    cmd = ["python3", "analyze_delete.py"] + args
    result = subprocess.run(cmd, cwd="/app")
    sys.exit(result.returncode)

def run_bulk_dlineage(args):
    """bulk_dlineage.pyコマンドを実行"""
    cmd = ["python3", "bulk_dlineage.py"] + args
    result = subprocess.run(cmd, cwd="/app")
    sys.exit(result.returncode)

def run_split(args):
    """split.pyコマンドを実行"""
    cmd = ["python3", "split.py"] + args
    result = subprocess.run(cmd, cwd="/app")
    sys.exit(result.returncode)

if __name__ == "__main__":
    # 引数がない場合、または最初の引数が"serve"の場合はHTTPサーバーを起動
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "serve"):
        serve_http()
    elif len(sys.argv) > 1:
        # 第1引数によってコマンドをルーティング
        command = sys.argv[1]
        args = sys.argv[2:]  # 残りの引数
        
        if command == "analyze_delete":
            run_analyze_delete(args)
        elif command == "bulk_dlineage":
            run_bulk_dlineage(args)
        elif command == "split":  
            run_split(args)
        else:
            # 既存の動作: dlineage.pyに全引数を渡す（後方互換性）
            run_dlineage(sys.argv[1:])