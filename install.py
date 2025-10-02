# installer.py
import os
import sys
import subprocess
from pathlib import Path
import urllib.request

APP_NAME = "YTDownloader"
INSTALL_DIR = Path(r"C:\ProgramData") / APP_NAME
STARTUP_DIR = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

# ---------------- FILE LINKS ----------------
# Keys include relative subfolder paths
files_to_download = {
    "ytlinkserver.py": "https://raw.githubusercontent.com/FootGod-bot/YTDownloader/refs/heads/main/files/ytlinkserver.py",
    "Downloader.py": "https://raw.githubusercontent.com/FootGod-bot/YTDownloader/refs/heads/main/files/Downloader.py",
    "ext/content.js": "https://raw.githubusercontent.com/FootGod-bot/YTDownloader/refs/heads/main/files/ext/content.js",
    "ext/icon48.png": "https://raw.githubusercontent.com/FootGod-bot/YTDownloader/refs/heads/main/files/ext/icon48.png",
    "ext/icon128.png": "https://raw.githubusercontent.com/FootGod-bot/YTDownloader/refs/heads/main/files/ext/icon128.png",
    "ext/manifest.json": "https://raw.githubusercontent.com/FootGod-bot/YTDownloader/refs/heads/main/files/ext/manifest.json",
    "requirements.txt": "https://raw.githubusercontent.com/FootGod-bot/YTDownloader/refs/heads/main/requirements.txt"
}

# ---------------- CREATE INSTALL DIRECTORY ----------------
INSTALL_DIR.mkdir(parents=True, exist_ok=True)
print(f"Installing to {INSTALL_DIR}")

# ---------------- DOWNLOAD FILES ----------------
for relative_path, url in files_to_download.items():
    file_path = INSTALL_DIR / relative_path
    # Ensure subfolders exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {relative_path}...")
    try:
        urllib.request.urlretrieve(url, file_path)
    except Exception as e:
        print(f"Failed to download {relative_path}: {e}")
        sys.exit(1)

# ---------------- INSTALL PIP REQUIREMENTS ----------------
req_file = INSTALL_DIR / "requirements.txt"
if req_file.exists():
    print("Installing pip packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(req_file)], check=True)
    req_file.unlink()
    print("requirements.txt removed after installation.")

# ---------------- CREATE STARTUP SHORTCUTS ----------------
for script_name in ["flask_formatter.py", "downloader.py"]:
    target_path = INSTALL_DIR / script_name
    shortcut_path = STARTUP_DIR / f"{Path(script_name).stem}.lnk"
    ps_cmd = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{sys.executable}'
$Shortcut.Arguments = '{target_path}'
$Shortcut.WorkingDirectory = '{INSTALL_DIR}'
$Shortcut.Save()
"""
    subprocess.run(["powershell", "-Command", ps_cmd], check=True)
    print(f"Created startup shortcut for {script_name}")

# ---------------- RUN APPS IMMEDIATELY ----------------
for script_name in ["flask_formatter.py", "downloader.py"]:
    script_path = INSTALL_DIR / script_name
    print(f"Launching {script_name}...")
    subprocess.Popen([sys.executable, str(script_path)], cwd=str(INSTALL_DIR))

print("Installation complete! Apps will also run on Windows startup.")
