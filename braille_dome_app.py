"""braille_dome_app.py v3 — usa waitress + handler global de erros"""

from __future__ import annotations

import os
import sys
import socket
import threading
import time
import traceback
import webbrowser
from pathlib import Path

if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
    sys.path.insert(0, str(base_path))
else:
    base_path = Path(__file__).parent
    sys.path.insert(0, str(base_path))

from app import app

DEBUG = os.environ.get('BRAILLE_DEBUG') == '1'


@app.errorhandler(Exception)
def handle_any_error(err):
    tb = traceback.format_exc()
    if DEBUG:
        print('\n=== ERRO ===\n' + tb + '============\n', flush=True)
    html = f"""
    <!doctype html><meta charset="utf-8">
    <style>body{{font-family:sans-serif;max-width:760px;margin:2rem auto;padding:1rem}}
    pre{{background:#fff3f3;border-left:4px solid #ff5050;padding:1rem;overflow:auto;font-size:.85rem;white-space:pre-wrap}}
    a{{color:#2364ff}}</style>
    <h1 style="color:#ff5050">Erro ao gerar STL</h1>
    <p><strong>{type(err).__name__}:</strong> {err}</p>
    <pre>{tb}</pre>
    <p><a href="/">&larr; Voltar ao formulário</a></p>
    """
    return html, 500


def find_free_port(preferred: int = 5000) -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', preferred))
        s.close()
        return preferred
    except OSError:
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        return port


def run_server(port: int):
    try:
        from waitress import serve
        if DEBUG:
            print(f'[waitress] http://127.0.0.1:{port}', flush=True)
        serve(app, host='127.0.0.1', port=port, threads=4, _quiet=not DEBUG)
    except ImportError:
        import logging
        logging.getLogger('werkzeug').setLevel(
            logging.DEBUG if DEBUG else logging.ERROR)
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)


def main():
    port = find_free_port(5000)
    url = f'http://127.0.0.1:{port}'

    t = threading.Thread(target=run_server, args=(port,), daemon=True)
    t.start()
    time.sleep(1.5)

    webbrowser.open(url)

    try:
        import tkinter as tk
        from tkinter import ttk

        root = tk.Tk()
        root.title('Braille Dome' + (' (DEBUG)' if DEBUG else ''))
        root.geometry('420x240')
        root.resizable(False, False)
        BG = '#fafafa'; AZUL = '#2364ff'
        root.configure(bg=BG)

        ttk.Label(root, text='Braille Dome',
                  font=('Segoe UI', 18, 'bold'),
                  foreground=AZUL, background=BG).pack(pady=(20, 5))
        ttk.Label(root, text='A app está a correr no teu navegador.',
                  font=('Segoe UI', 10), background=BG).pack()
        ttk.Label(root, text=url,
                  font=('Consolas', 10), foreground=AZUL,
                  background=BG).pack(pady=(5, 5))

        if DEBUG:
            ttk.Label(root, text='[ MODO DEBUG — vê a janela preta para logs ]',
                      font=('Consolas', 8), foreground='#aa6600',
                      background=BG).pack(pady=(0, 8))

        def reabrir(): webbrowser.open(url)
        def sair(): root.destroy(); os._exit(0)

        btn_frame = tk.Frame(root, bg=BG)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text='Reabrir no navegador', command=reabrir,
                  bg=AZUL, fg='white', font=('Segoe UI', 10, 'bold'),
                  padx=15, pady=6, bd=0, cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text='Fechar', command=sair,
                  bg='#ddd', fg='black', font=('Segoe UI', 10),
                  padx=15, pady=6, bd=0, cursor='hand2').pack(side='left', padx=5)

        ttk.Label(root, text='Buinho FabLab · Messejana',
                  font=('Segoe UI', 8), foreground='#888',
                  background=BG).pack(side='bottom', pady=8)
        root.protocol('WM_DELETE_WINDOW', sair)
        root.mainloop()

    except ImportError:
        print(f'\n  Braille Dome a correr em {url}')
        print('  Carrega Ctrl+C para fechar.\n')
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt: pass


if __name__ == '__main__':
    main()
