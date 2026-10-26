from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

WEB_DIR = Path(__file__).resolve().parent / 'web'
MIME = {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript'}


def gcc_version():
    gcc = shutil.which('gcc')
    if not gcc:
        return 'No disponible'
    try:
        return subprocess.run([gcc, '--version'], capture_output=True,
                              text=True, timeout=3).stdout.splitlines()[0]
    except (OSError, subprocess.TimeoutExpired, IndexError):
        return 'No disponible'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def respond(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/ping':
            return self.respond(200, {'ok': True, 'gcc': gcc_version()})
        if path == '/':
            path = '/index.html'
        if path not in ('/index.html', '/styles.css', '/arena.js', '/api.js'):
            return self.respond(404, {'error': 'No encontrado'})
        file = WEB_DIR / path.lstrip('/')
        try:
            body = file.read_bytes()
        except OSError:
            return self.respond(404, {'error': 'Archivo no encontrado'})
        self.send_response(200)
        self.send_header('Content-Type', MIME[file.suffix] + '; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlsplit(self.path).path != '/api/battle':
            return self.respond(404, {'error': 'No encontrado'})
        try:
            length = int(self.headers.get('Content-Length', '-1'))
            if not 0 < length <= 1024:
                return self.respond(400, {'error': 'Solicitud demasiado grande'})
            payload = json.loads(self.rfile.read(length))
            n = payload.get('n')
            if type(n) is not int or not 2 <= n <= 20:
                return self.respond(400, {'error': 'Elige un entero entre 2 y 20'})
            if not shutil.which('gcc'):
                return self.respond(503, {'error': 'Instala GCC para la carrera nativa'})
            proc = subprocess.run([sys.executable, '-m', 'fiblang.battle_worker', str(n)],
                                  cwd=str(WEB_DIR.parent.parent), capture_output=True,
                                  text=True, timeout=12)
            if proc.returncode != 0:
                return self.respond(500, {'error': 'Error al ejecutar el experimento: ' + proc.stderr[-400:]})
            return self.respond(200, json.loads(proc.stdout))
        except subprocess.TimeoutExpired:
            return self.respond(504, {'error': 'La carrera excedió 12 segundos. Prueba con un número menor.'})
        except (ValueError, json.JSONDecodeError, UnicodeError) as exc:
            return self.respond(400, {'error': str(exc)})
        except Exception as exc:
            return self.respond(500, {'error': type(exc).__name__ + ': ' + str(exc)})


def serve(port=8765, open_browser=True):
    try:
        httpd = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    except OSError:
        httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    url = f'http://127.0.0.1:{httpd.server_address[1]}/'
    print('FibLang Battle Arena:', url)
    print('GCC:', gcc_version())
    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nArena cerrada.')
    finally:
        httpd.server_close()
