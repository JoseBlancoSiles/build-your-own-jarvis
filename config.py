"""Central config — loads .env and exposes typed settings the app uses."""
import os
from dotenv import load_dotenv

load_dotenv()


def _get(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


# --- Fish Audio ---
FISH_API_KEY = _get("FISH_API_KEY")
FISH_VOICE_ID = _get("FISH_VOICE_ID", "612b878b113047d9a770c069c8b4fdfe")
FISH_MODEL = _get("FISH_MODEL", "s2.1-pro")
FISH_LATENCY = _get("FISH_LATENCY", "balanced")

# --- Claude (the brain) ---
ANTHROPIC_API_KEY = _get("ANTHROPIC_API_KEY")
JARVIS_MODEL = _get("JARVIS_MODEL", "claude-haiku-4-5")

# --- Email ---
EMAIL_ADDRESS = _get("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = _get("EMAIL_APP_PASSWORD")
EMAIL_DEFAULT_TO = _get("EMAIL_DEFAULT_TO") or EMAIL_ADDRESS

# --- Spotify ---
SPOTIPY_CLIENT_ID = _get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = _get("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = _get("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")

# --- Collab link ---
FISH_AUDIO_UTM = _get("FISH_AUDIO_UTM", "https://fish.audio/?utm_source=YOUR_UTM_HERE")


def status() -> dict:
    """A quick readout of which integrations are configured (shown in the UI)."""
    return {
        "fish": bool(FISH_API_KEY),
        "claude": bool(ANTHROPIC_API_KEY),
        "email": bool(EMAIL_ADDRESS and EMAIL_APP_PASSWORD),
        "spotify": bool(SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET),
        "model": JARVIS_MODEL,
        "voice": FISH_VOICE_ID,
    }
