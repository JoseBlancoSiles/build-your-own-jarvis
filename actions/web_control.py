"""Zero-credential actions: open websites/apps, weather, and time."""
from __future__ import annotations

import os
import subprocess
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime

# Friendly name -> URL for quick "open X" commands.
SITES = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "spotify": "https://open.spotify.com",
    "maps": "https://maps.google.com",
    "calendar": "https://calendar.google.com",
    "fish audio": "https://fish.audio",
}

# Friendly name -> Windows launch target for "open app X".
APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "files": "explorer.exe",
    "camera": "microsoft.windows.camera:",
    "settings": "ms-settings:",
    "terminal": "wt.exe",
    "cmd": "cmd.exe",
}


def open_website(target: str) -> str:
    key = target.lower().strip()
    url = SITES.get(key)
    if not url:
        if "." in key and " " not in key:
            url = key if key.startswith("http") else f"https://{key}"
        else:
            url = f"https://www.google.com/search?q={target.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Opening {target}."


def open_app(name: str) -> str:
    key = name.lower().strip()
    target = APPS.get(key)
    if not target:
        return f"I don't know the app '{name}'. Try notepad, calculator, or settings."
    try:
        if target.endswith(":"):  # URI-style launch (camera, settings)
            os.startfile(target)  # noqa: S606  (Windows-only, trusted map)
        else:
            os.startfile(target)  # noqa: S606
        return f"Opening {name}."
    except Exception as e:  # noqa: BLE001
        return f"Couldn't open {name} ({e.__class__.__name__})."


def get_weather(location: str = "") -> str:
    """Quick weather via wttr.in (no API key needed)."""
    try:
        loc = urllib.parse.quote(location.strip())
        fmt = urllib.parse.quote("%l: %C, %t (feels %f), wind %w")
        url = f"https://wttr.in/{loc}?format={fmt}"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=8) as r:  # noqa: S310
            text = r.read().decode("utf-8", "replace").strip()
        return text or "Weather service is unavailable right now."
    except Exception:  # noqa: BLE001
        return "Weather service is unavailable right now."


def get_time() -> str:
    now = datetime.now()
    return now.strftime("It's %I:%M %p on %A, %B %d.")


def write_note(title: str, content: str) -> str:
    """Save text to a .txt file and open it in Notepad (JARVIS 'writes' for you)."""
    try:
        notes = os.path.join(os.path.dirname(__file__), "..", "notes")
        os.makedirs(notes, exist_ok=True)
        safe = "".join(c for c in (title or "note") if c.isalnum() or c in " -_").strip()
        safe = safe or "note"
        path = os.path.abspath(os.path.join(notes, safe + ".txt"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(content or "")
        try:
            subprocess.Popen(["notepad.exe", path])  # noqa: S603,S607
        except Exception:  # noqa: BLE001
            os.startfile(path)  # noqa: S606  (fallback: default .txt handler)
        return f"Written and opened '{safe}.txt' in Notepad."
    except Exception as e:  # noqa: BLE001
        return f"Couldn't write the note ({e.__class__.__name__})."
