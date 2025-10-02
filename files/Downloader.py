# downloader.py
import os
import sys
import time
import subprocess
from pathlib import Path
import glob
import psutil

# === CONFIG ===
show_console = "min"       # "hidden", "min", "max", "shown"
open_folder = True
docs = Path.home() / "Documents"
flask_formatter_exe = "ytlinkserver.exe"  # EXE name of Flask+Formatter

# === YT-DLP CONFIG ===
# Option 1: use bundled Python module (recommended for EXE)
def get_yt_dlp_cmd():
    return [sys.executable, "-m", "yt_dlp"]

# Option 2: use standalone yt-dlp.exe (uncomment and set path if needed)
# yt_dlp_path = Path(r"C:\path\to\yt-dlp.exe")
# def get_yt_dlp_cmd():
#     return [str(yt_dlp_path)]

# ---- Auto-start Flask+Formatter if not running ----
def ensure_other_running(other_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == other_name:
            return
    other_path = Path(sys.argv[0]).parent / other_name
    if other_path.exists():
        try:
            subprocess.Popen([str(other_path)], cwd=other_path.parent)
            print(f"Started {other_name}")
        except Exception as e:
            print(f"Failed to start {other_name}: {e}")

ensure_other_running(flask_formatter_exe)

# ---- Parsing formatted .txt files ----
def parse_link_file(file_path):
    link = type_ = save_path = None
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("Link:"):
                link = line[5:].strip()
            elif line.startswith("Type:"):
                type_ = line[5:].strip()
            elif line.startswith("SavePath:"):
                save_path = line[9:].strip()
    return link, type_, save_path

# ---- Run yt-dlp ----
def run_yt_dlp(link, type_, save_path):
    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)

    cmd = get_yt_dlp_cmd()
    if type_ == "Audio":
        cmd += ["-x", "--audio-format", "mp3"]
    cmd.append(link)

    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        if show_console == "hidden":
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0  # SW_HIDE
        elif show_console == "min":
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 2  # SW_MINIMIZE
        elif show_console == "max":
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 3  # SW_MAXIMIZE

        subprocess.run(cmd, cwd=save_path, startupinfo=si)
    else:
        # Non-Windows fallback
        subprocess.run(cmd, cwd=save_path)

    if open_folder:
        subprocess.run(["explorer", str(save_path)])

# ---- Check queue and ytlink.txt ----
def check_queue():
    ytlink = docs / "ytlink.txt"
    if ytlink.exists():
        link, type_, save_path = parse_link_file(ytlink)
        if link and type_ and save_path:
            print(f"Downloading: {link} -> {save_path} ({type_})")
            run_yt_dlp(link, type_, save_path)
        ytlink.unlink()
    else:
        queue_files = sorted(glob.glob(str(docs / "Queue*.txt")))
        if queue_files:
            first_queue = Path(queue_files[0])
            first_queue.rename(docs / "ytlink.txt")
            print(f"Moved {first_queue.name} to ytlink.txt for processing")

# ---- Main loop ----
if __name__ == "__main__":
    print("Watching for formatted .txt files to download...")
    while True:
        try:
            check_queue()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)
