# flask_formatter.py
import os
import time
import threading
import tkinter as tk
from tkinter import filedialog
from flask import Flask, request
from flask_cors import CORS
from pathlib import Path
import glob
import subprocess
import sys
import psutil

# === CONFIG ===
docs = Path.home() / "Documents"
queue_limit = 50
downloader_exe = "downloader.exe"  # name of downloader exe in the same folder

# ---- Auto-start downloader if not running ----
def ensure_other_running(other_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == other_name:
            return  # already running
    other_path = Path(sys.argv[0]).parent / other_name
    if other_path.exists():
        try:
            subprocess.Popen([str(other_path)], cwd=other_path.parent)
            print(f"Started {other_name}")
        except Exception as e:
            print(f"Failed to start {other_name}: {e}")

ensure_other_running(downloader_exe)

# ---- Flask app ----
app = Flask(__name__)
CORS(app)

@app.route('/save', methods=['POST'])
def save_url():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return "Missing URL", 400

    for i in range(queue_limit + 1):
        base = "ytlink" if i == 0 else f"Queue{i}"
        for suffix in ["", "_temp"]:
            path = docs / f"{base}{suffix}.txt"
            if path.exists():
                if path.read_text(encoding="utf-8").strip() == url:
                    return f"Duplicate: already in {base}{suffix}.txt", 200

    for i in range(queue_limit + 1):
        base = "ytlink" if i == 0 else f"Queue{i}"
        final_path = docs / f"{base}.txt"
        temp_path = docs / f"{base}_temp.txt"

        if not final_path.exists() and not temp_path.exists():
            temp_path.write_text(url, encoding="utf-8")
            return f"Written to {base}_temp.txt", 200

    return "Queue full", 429

# ---- GUI for type/folder selection ----
def ask_user_settings():
    result = {"type": None, "path": None}

    def set_choice(choice):
        result["type"] = choice
        win.after(100, choose_folder)

    def choose_folder():
        folder = filedialog.askdirectory(title="Choose save folder")
        if folder:
            result["path"] = folder
        win.destroy()

    win = tk.Tk()
    win.title("Choose Format")
    win.geometry("300x100")
    win.eval('tk::PlaceWindow . center')
    win.resizable(False, False)

    tk.Label(win, text="Choose download type:").pack(pady=10)

    button_frame = tk.Frame(win)
    button_frame.pack()

    tk.Button(button_frame, text="Audio", width=12, command=lambda: set_choice("Audio")).pack(side="left", padx=10)
    tk.Button(button_frame, text="Normal", width=12, command=lambda: set_choice("Normal")).pack(side="right", padx=10)

    win.mainloop()
    return result["type"], result["path"]

# ---- Watcher thread ----
def watch_temp_files():
    print("Watching for _temp.txt files in Documents...")
    while True:
        temp_files = [f for f in os.listdir(docs) if f.endswith("_temp.txt")]
        for temp_file in temp_files:
            temp_path = docs / temp_file
            final_path = docs / temp_file.replace("_temp.txt", ".txt")

            url = temp_path.read_text(encoding="utf-8").strip()
            if not url:
                temp_path.unlink()
                continue

            format_type, folder = ask_user_settings()
            if not format_type or not folder:
                print("Cancelled by user.")
                temp_path.unlink()
                continue

            formatted = f"Link:{url}\nType:{format_type}\nSavePath:{folder}"
            final_path.write_text(formatted, encoding="utf-8")
            print(f"Formatted and saved to {final_path}")
            temp_path.unlink()
            print(f"Deleted temp file: {temp_path}")

        time.sleep(1)

if __name__ == "__main__":
    watcher_thread = threading.Thread(target=watch_temp_files, daemon=True)
    watcher_thread.start()
    app.run()
