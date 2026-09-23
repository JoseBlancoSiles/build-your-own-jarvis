"""The JARVIS brain: Claude decides what to say and which action to run.

A small manual agentic loop (no beta dependency) keeps latency low and gives us
the action log we surface in the HUD.
"""
from __future__ import annotations

import json

import anthropic

import config
from actions import mailer, spotify_control, system_control, weather, web_control

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY) if config.ANTHROPIC_API_KEY else None

SYSTEM_PROMPT = (
    "You are JARVIS, the AI assistant from Iron Man, running on the user's computer. "
    "You are calm, precise, quietly witty, and unfailingly loyal. Address the user as 'sir'. "
    "Your replies are SPOKEN ALOUD, so keep them to one or two short sentences of plain prose. "
    "Never use markdown, bullet points, emojis, code, or stage directions. "
    "When the user asks you to do something, use the appropriate tool, then confirm briefly "
    "in character (e.g. 'Right away, sir.'). If a tool reports it isn't configured or fails, "
    "relay that gracefully in one sentence. For casual chat, just answer — no tool needed. "
    "You can search the live web to answer questions about current events, news, prices, "
    "or anything you're unsure of. When you search, do NOT narrate that you're searching — "
    "just give the answer. Keep EVERY reply to at most two short sentences, even after a web "
    "search, and never speak URLs, source names, or citations aloud."
)

# ---- Tool schemas exposed to Claude ---------------------------------------
TOOLS = [
    {
        "name": "play_spotify",
        "description": "Search Spotify and start playing a song, artist, or playlist.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "What to play, e.g. 'Back in Black by AC/DC'"}},
            "required": ["query"],
        },
    },
    {
        "name": "control_spotify",
        "description": "Control current Spotify playback.",
        "input_schema": {
            "type": "object",
            "properties": {"action": {"type": "string", "enum": ["pause", "resume", "next", "previous"]}},
            "required": ["action"],
        },
    },
    {
        "name": "send_email",
        "description": "Send an email. If no recipient is given, sends to the user's own default inbox.",
        "input_schema": {
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "to": {"type": "string", "description": "Recipient email; omit to use the default."},
            },
            "required": ["subject", "body"],
        },
    },
    {
        "name": "set_volume",
        "description": "Set the system volume by absolute percent (level) OR relative direction.",
        "input_schema": {
            "type": "object",
            "properties": {
                "level": {"type": "integer", "description": "0-100 absolute volume"},
                "direction": {"type": "string", "enum": ["up", "down", "max", "mute", "unmute"]},
            },
        },
    },
    {
        "name": "set_brightness",
        "description": "Set the screen brightness by absolute percent (level) OR direction.",
        "input_schema": {
            "type": "object",
            "properties": {
                "level": {"type": "integer", "description": "0-100 absolute brightness"},
                "direction": {"type": "string", "enum": ["up", "down"]},
            },
        },
    },
    {
        "name": "open_website",
        "description": "Open a website in the browser (a known name, a domain, or a search).",
        "input_schema": {
            "type": "object",
            "properties": {"target": {"type": "string"}},
            "required": ["target"],
        },
    },
    {
        "name": "open_app",
        "description": "Open a desktop application (e.g. notepad, calculator, settings).",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "get_weather",
        "description": "Get the current weather. Location optional (defaults to the user's location).",
        "input_schema": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
        },
    },
    {
        "name": "get_time",
        "description": "Get the current local date and time.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "write_note",
        "description": (
            "Write text into Notepad for the user. YOU generate the full content "
            "(e.g. a note, poem, email draft, list, or letter) and pass it here."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short file title, e.g. 'shopping list'"},
                "content": {"type": "string", "description": "The full text to write."},
            },
            "required": ["title", "content"],
        },
    },
    # Server-side tool: Claude searches the live web itself (no client dispatch).
    {"type": "web_search_20250305", "name": "web_search", "max_uses": 3},
]


def _dispatch(name: str, args: dict) -> tuple[str, dict | None]:
    """Run one tool. Returns (spoken_result, ui_extra) where ui_extra is optional
    structured data for the front-end (e.g. the weather dashboard)."""
    if name == "play_spotify":
        return spotify_control.play_spotify(args.get("query", "")), None
    if name == "control_spotify":
        return spotify_control.control_spotify(args.get("action", "")), None
    if name == "send_email":
        return mailer.send_email(args.get("subject", ""), args.get("body", ""), args.get("to")), None
    if name == "set_volume":
        return system_control.set_volume(args.get("level"), args.get("direction")), None
    if name == "set_brightness":
        return system_control.set_brightness(args.get("level"), args.get("direction")), None
    if name == "open_website":
        return web_control.open_website(args.get("target", "")), None
    if name == "open_app":
        return web_control.open_app(args.get("name", "")), None
    if name == "get_weather":
        data = weather.fetch(args.get("location", ""))
        return weather.summary(data), {"weather": data}
    if name == "get_time":
        return web_control.get_time(), None
    if name == "write_note":
        return web_control.write_note(args.get("title", ""), args.get("content", "")), None
    return f"Unknown tool: {name}", None


def think(user_text: str, history: list | None = None) -> dict:
    """Run one turn. Returns {reply, actions, history}."""
    if _client is None:
        return {
            "reply": "My brain isn't connected, sir. Add your Anthropic API key to the .env file.",
            "actions": [],
            "history": history or [],
        }

    messages = list(history or [])
    messages.append({"role": "user", "content": user_text})
    actions: list[dict] = []

    # Manual agentic loop: keep executing tools until Claude is done.
    for _ in range(6):  # safety cap
        resp = _client.messages.create(
            model=config.JARVIS_MODEL,
            max_tokens=1024,         # headroom for web-search answers; replies stay short
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # A server tool (web_search) paused mid-work — resend to let it finish.
        if resp.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": resp.content})
            continue

        if resp.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                # Inputs may arrive with varied JSON escaping — always trust the parsed dict.
                args = block.input if isinstance(block.input, dict) else json.loads(block.input)
                result, extra = _dispatch(block.name, args)
                entry = {"tool": block.name, "result": result}
                if extra:
                    entry.update(extra)
                actions.append(entry)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "user", "content": tool_results})

    # Join all text blocks (web search returns the answer across several) and
    # collapse any stray whitespace so it reads cleanly when spoken.
    reply = " ".join(b.text for b in resp.content if b.type == "text" and b.text)
    reply = " ".join(reply.split())
    if not reply:
        reply = "Done, sir." if actions else "I'm not sure how to help with that, sir."

    # Persist a compact history (strip tool internals to keep future turns lean/fast).
    new_history = list(history or [])
    new_history.append({"role": "user", "content": user_text})
    new_history.append({"role": "assistant", "content": reply})
    new_history = new_history[-12:]  # keep the last few turns only

    return {"reply": reply, "actions": actions, "history": new_history}
