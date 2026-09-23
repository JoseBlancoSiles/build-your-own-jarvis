"""JARVIS server — serves the HUD and bridges the browser to Claude + Fish Audio.

Run:  python server.py   (or)   uvicorn server:app --port 8000
Then open http://localhost:8000 in Chrome or Edge.
"""
from __future__ import annotations

import json
import os
import urllib.request

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import config
import brain

app = FastAPI(title="JARVIS")

WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

# Single-user local app: keep conversation history in memory.
_history: list = []

FISH_TTS_URL = "https://api.fish.audio/v1/tts"


@app.get("/")
def index():
    return FileResponse(os.path.join(WEB_DIR, "index.html"))


@app.get("/api/status")
def status():
    """Which integrations are wired up (drives the HUD status pills + collab link)."""
    s = config.status()
    s["utm"] = config.FISH_AUDIO_UTM
    return s


@app.post("/api/chat")
async def chat(request: Request):
    """Take the user's transcript, run the brain, return spoken reply + actions."""
    global _history
    data = await request.json()
    user_text = (data.get("text") or "").strip()
    if not user_text:
        return JSONResponse({"reply": "", "actions": []})

    result = brain.think(user_text, _history)
    _history = result["history"]
    return JSONResponse({"reply": result["reply"], "actions": result["actions"]})


@app.post("/api/reset")
async def reset():
    global _history
    _history = []
    return {"ok": True}


def _fish_audio_stream(text: str):
    """Stream MP3 audio from Fish Audio, chunk by chunk, for low latency."""
    body = json.dumps({
        "text": text,
        "reference_id": config.FISH_VOICE_ID,
        "format": "mp3",
        "mp3_bitrate": 128,
        "latency": config.FISH_LATENCY,   # low | normal | balanced
        "normalize": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        FISH_TTS_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {config.FISH_API_KEY}",
            "Content-Type": "application/json",
            "model": config.FISH_MODEL,   # e.g. s2.1-pro
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
        while True:
            chunk = resp.read(4096)
            if not chunk:
                break
            yield chunk


@app.post("/api/tts")
async def tts(request: Request):
    """Turn text into JARVIS's voice via Fish Audio and stream it back as MP3."""
    data = await request.json()
    text = (data.get("text") or "").strip()
    if not text:
        return JSONResponse({"error": "no text"}, status_code=400)
    if not config.FISH_API_KEY:
        return JSONResponse({"error": "FISH_API_KEY not set"}, status_code=503)

    return StreamingResponse(_fish_audio_stream(text), media_type="audio/mpeg")


# Static assets (styles.css, app.js) served from /web
app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")


if __name__ == "__main__":
    import uvicorn

    print("\n  J.A.R.V.I.S online  ->  http://localhost:8000  (open in Chrome/Edge)\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
