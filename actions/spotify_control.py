"""Spotify playback control via spotipy (requires Spotify Premium).

On first use a browser window opens once for OAuth; the token is cached to
.spotify_cache so it won't ask again.
"""
from __future__ import annotations

import config

_client = None


def _sp():
    """Lazily build an authenticated Spotify client."""
    global _client
    if _client is not None:
        return _client
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth

    auth = SpotifyOAuth(
        client_id=config.SPOTIPY_CLIENT_ID,
        client_secret=config.SPOTIPY_CLIENT_SECRET,
        redirect_uri=config.SPOTIPY_REDIRECT_URI,
        scope="user-modify-playback-state user-read-playback-state",
        cache_path=".spotify_cache",
        open_browser=True,
    )
    _client = spotipy.Spotify(auth_manager=auth)
    return _client


def _active_device(sp):
    """Return an active device id, preferring one that's already active."""
    devices = sp.devices().get("devices", [])
    if not devices:
        return None
    for d in devices:
        if d.get("is_active"):
            return d["id"]
    return devices[0]["id"]  # fall back to the first available device


def play_spotify(query: str) -> str:
    """Search for a track/artist/playlist and start playback."""
    if not (config.SPOTIPY_CLIENT_ID and config.SPOTIPY_CLIENT_SECRET):
        return "Spotify isn't configured yet (add your client ID/secret in .env)."
    try:
        sp = _sp()
        device = _active_device(sp)
        if not device:
            return "No Spotify device is open. Start Spotify on any device first."

        results = sp.search(q=query, type="track", limit=1)
        items = results.get("tracks", {}).get("items", [])
        if not items:
            return f"Couldn't find anything for '{query}' on Spotify."

        track = items[0]
        sp.start_playback(device_id=device, uris=[track["uri"]])
        artist = track["artists"][0]["name"] if track["artists"] else ""
        return f"Now playing {track['name']} by {artist}."
    except Exception as e:  # noqa: BLE001
        return f"Spotify error ({e.__class__.__name__}). Is Premium active and a device open?"


def control_spotify(action: str) -> str:
    """pause / resume / next / previous the current playback."""
    if not (config.SPOTIPY_CLIENT_ID and config.SPOTIPY_CLIENT_SECRET):
        return "Spotify isn't configured yet."
    try:
        sp = _sp()
        device = _active_device(sp)
        if action == "pause":
            sp.pause_playback(device_id=device)
            return "Paused."
        if action in ("resume", "play"):
            sp.start_playback(device_id=device)
            return "Resumed."
        if action in ("next", "skip"):
            sp.next_track(device_id=device)
            return "Skipped to the next track."
        if action in ("previous", "back"):
            sp.previous_track(device_id=device)
            return "Went back a track."
        return f"Unknown Spotify action: {action}."
    except Exception as e:  # noqa: BLE001
        return f"Spotify error ({e.__class__.__name__})."
