"""Real weather data via Open-Meteo (free, no API key) for the on-screen dashboard.

Returns a structured dict the front-end renders, plus a short spoken summary.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

# WMO weather codes -> human descriptions
WMO = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    56: "Freezing drizzle", 57: "Freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Freezing rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Light showers", 81: "Showers", 82: "Violent showers",
    85: "Snow showers", 86: "Snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with hail",
}


def _get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "jarvis"})
    with urllib.request.urlopen(req, timeout=8) as r:  # noqa: S310
        return json.load(r)


def _resolve(location: str):
    """Return (lat, lon, name, country_code) for a place name, or by IP if blank."""
    if location and location.strip():
        q = urllib.parse.quote(location.strip())
        d = _get_json(
            f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=en&format=json"
        )
        res = d.get("results") or []
        if res:
            r = res[0]
            return r["latitude"], r["longitude"], r.get("name", location), r.get("country_code", "")
        return None
    # No location -> geolocate by IP.
    try:
        d = _get_json("http://ip-api.com/json/?fields=status,city,countryCode,lat,lon")
        if d.get("status") == "success":
            return d["lat"], d["lon"], d.get("city", "Here"), d.get("countryCode", "")
    except Exception:  # noqa: BLE001
        pass
    return None


def fetch(location: str = "") -> dict | None:
    """Fetch current conditions + a 5-day forecast as a structured dict."""
    try:
        loc = _resolve(location)
        if not loc:
            return None
        lat, lon, name, cc = loc
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            "weather_code,wind_speed_10m,is_day"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min"
            "&timezone=auto&forecast_days=5"
        )
        d = _get_json(url)
        cur = d.get("current", {})
        daily = d.get("daily", {})
        codes = daily.get("weather_code", [])
        hi = daily.get("temperature_2m_max", [])
        lo = daily.get("temperature_2m_min", [])
        dates = daily.get("time", [])
        days = [
            {
                "date": dates[i],
                "code": codes[i],
                "desc": WMO.get(codes[i], "—"),
                "hi": round(hi[i]),
                "lo": round(lo[i]),
            }
            for i in range(min(5, len(dates)))
        ]
        code = cur.get("weather_code")
        return {
            "location": f"{name}{', ' + cc if cc else ''}",
            "temp": round(cur.get("temperature_2m", 0)),
            "feels": round(cur.get("apparent_temperature", 0)),
            "humidity": cur.get("relative_humidity_2m"),
            "wind": round(cur.get("wind_speed_10m", 0)),
            "code": code,
            "desc": WMO.get(code, "—"),
            "is_day": cur.get("is_day", 1),
            "units": {"temp": "°C", "wind": "km/h"},
            "days": days,
        }
    except Exception:  # noqa: BLE001
        return None


def summary(data: dict | None) -> str:
    if not data:
        return "I couldn't reach the weather service, sir."
    return (
        f"It's {data['temp']} degrees and {data['desc'].lower()} in {data['location']}, "
        f"sir, feeling like {data['feels']}."
    )
