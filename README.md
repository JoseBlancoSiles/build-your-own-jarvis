<div align="center">

# 🤖 J.A.R.V.I.S
### Build your own Iron-Man-style AI assistant — with a real voice from [**Fish Audio**](https://fish.audio/?fpr=rcic6s)

Say **“Hey Jarvis”**, ask it anything, and watch the arc-reactor HUD light up as it answers
in the iconic JARVIS voice — then checks the weather, writes you a note, searches the web, or sends an email.

**⏱ ~15 minutes · 💸 free to start · 🪟 Windows · ⚡ Powered by [Fish Audio](https://fish.audio/?fpr=rcic6s) (voice) + Claude (brain)**

</div>

---

## 📋 What you'll need before you start

1. A **Windows PC**
2. **Python** — free, installed in Step 1 below
3. A **Fish Audio API key** — free → **[get one here](https://fish.audio/?fpr=rcic6s)** *(this powers the voice)*
4. A **Claude (Anthropic) API key** → **[console.anthropic.com](https://console.anthropic.com)** *(this powers the brain)*

Grab both keys (Steps 3 & 4 walk you through it) — you'll paste them in once and you're done.

---

## ✨ What it can do
🌤️ Live weather dashboard · 📝 Writes notes in Notepad · 📧 Sends email · 🌐 Searches the live web · 🔊 Controls volume & brightness · 🚀 Opens apps & websites · 🎙️ Hands-free “Hey Jarvis”

> 🧩 **And you can teach it almost anything.** JARVIS is built to be extended — smart-home lights, timers & reminders, your calendar, a morning news briefing, stock/crypto prices, launching any program, telling jokes… Adding a new skill takes ~3 lines. See **[Make it your own](#-make-it-your-own)** below.

---

## 🚀 Get it running

### 1. Install Python (the engine)
Download and install it once → **[python.org/downloads](https://www.python.org/downloads/)**

> ⚠️ **On the first installer screen, tick “Add python.exe to PATH”** before clicking Install. Nothing works without it.

### 2. Get the code
Open a terminal (PowerShell) wherever you want JARVIS to live, and run:
```bash
git clone https://github.com/JoseBlancoSiles/build-your-own-jarvis.git
cd build-your-own-jarvis
```
> 🤷 **Don't have git?** No problem — click the green **`Code ▾`** button at the top of this page → **Download ZIP** → unzip it wherever you like.

### 3. Get your Fish Audio key (the voice) 🐟
👉 **[Create your free Fish Audio account](https://fish.audio/?fpr=rcic6s)** → click your **profile → API Keys → Create** → copy the key (starts with `sk-…`).

### 4. Get your Claude key (the brain) 🧠
Go to **[console.anthropic.com](https://console.anthropic.com)** → **API Keys → Create Key** → copy it (starts with `sk-ant-…`).

### 5. Add your keys
In the project folder, make a copy of **`.env.example`** and rename the copy to **`.env`**.
*(Or just run `run.bat` once — it creates the `.env` for you automatically, then tells you to add your keys.)*

Open **`.env`** with Notepad and paste your two keys:
```env
FISH_API_KEY=paste-your-fish-key-here
ANTHROPIC_API_KEY=paste-your-claude-key-here
```
Save and close.

> 🎙️ **You don't need to choose a voice** — the classic JARVIS voice is already set for you. The moment your Fish key is in, JARVIS speaks as JARVIS. *(Want a different voice? See [Change the voice](#-change-the-voice).)*

### 6. Run it — step by step
1. Open the **`build-your-own-jarvis`** folder.
2. **Double-click `run.bat`.**
3. **First run only:** a black window opens and installs everything — this takes **2–3 minutes**. Leave it open and wait.
4. When the window shows **`JARVIS online -> http://localhost:8000`**, it's ready.
5. Open **Chrome or Edge** and go to **http://localhost:8000**
6. **Click once** anywhere on the page (this lets it play sound), and click **Allow** when it asks for your microphone.
7. Say:

> ### 🎙️ “Hey Jarvis, what’s the weather?”

**That’s it — JARVIS is alive.** 🎉

> ⏹️ **To stop JARVIS:** close the black window. **To start again:** double-click `run.bat` (it's instant after the first time).
>
> 🛡️ If Windows shows **“Windows protected your PC,”** click **More info → Run anyway** (it's just your own file).

---

## 🗣️ Try saying
- *“Hey Jarvis, what’s the weather in Tokyo?”* → live dashboard
- *“Hey Jarvis, write me a caption for my reel in notepad”*
- *“Hey Jarvis, what’s the latest AI news?”* → live web search
- *“Hey Jarvis, turn the volume down”* · *“Hey Jarvis, open YouTube”*

💡 Tip: you can also **hold the Space bar** and talk (great for a clean recording).

---

## 🎙️ Change the voice
The JARVIS voice is a Fish Audio **`reference_id`**, already set in your `.env`:
```env
FISH_VOICE_ID=612b878b113047d9a770c069c8b4fdfe   # "Jarvis (MCU)"
```
Want a different one? Browse the **[Fish Audio Voice Library](https://fish.audio/?fpr=rcic6s)**, open any voice, copy its model ID, paste it as `FISH_VOICE_ID`, and re-run. You can also tweak `FISH_LATENCY` (`low` = snappiest) and `FISH_MODEL`.

---

## 🧩 Make it your own
Adding a new skill is genuinely 3 small steps:

1. **Write a function** in `actions/` that does the thing and returns a short sentence.
2. **Describe it** as a tool (name + inputs) in `brain.py`, and add one line to `_dispatch()`.
3. Done — Claude will start using it automatically when you ask.

**Ideas to add:** 💡 smart-home lights (Philips Hue / smart plugs) · ⏰ timers & reminders · 📅 read/create calendar events · 📰 a spoken morning briefing · 💹 stock & crypto prices · 🎬 launch any program by name · 🗺️ directions · 😄 jokes · 🌡️ read your PC's stats.

---

## 📧 Optional: let JARVIS send email
Gmail needs a special **App Password** (your normal one won’t work):
1. Turn on **[2-Step Verification](https://myaccount.google.com/security)**
2. Create an **[App Password](https://myaccount.google.com/apppasswords)** named `JARVIS`, copy the 16-char code
3. Add these to `.env`, then re-run `run.bat`:
```env
EMAIL_ADDRESS=youremail@gmail.com
EMAIL_APP_PASSWORD=your16charcode
EMAIL_DEFAULT_TO=youremail@gmail.com
```

## 🎵 Optional: Spotify (needs Premium)
Create a free app at **[developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)** (redirect URI `http://127.0.0.1:8888/callback`), then fill `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` in `.env`.

---

## 🔧 Troubleshooting
<details><summary><b>“python is not recognized…”</b></summary>
You missed the tick box in Step 1. Reinstall Python and tick <b>“Add python.exe to PATH.”</b>
</details>
<details><summary><b>I can’t hear JARVIS</b></summary>
Browsers block sound until you interact — <b>click once anywhere on the page</b>, then it talks. Check your volume too.
</details>
<details><summary><b>JARVIS can’t hear me</b></summary>
Use <b>Chrome or Edge</b>, click <b>Allow</b> for the mic, and speak clearly: “Hey Jarvis…”. Or hold <b>Space</b> to talk.
</details>
<details><summary><b>The black window closed / errors</b></summary>
Finish Step 1 (with the PATH tick) and make sure both keys are pasted in <code>.env</code> (Step 5), then double-click <b>run.bat</b> again.
</details>

---

## 🛠️ How it works
```
🎤 Browser (Web Speech)  ──►  Claude (brain + tools)  ──►  runs actions
      ▲                                                          │
🔊 reactor + voice  ◄──────────────  Fish Audio (the voice)  ◄──┘
```
- `server.py` — serves the HUD, bridges to Claude & Fish Audio
- `brain.py` — Claude tool-calling loop + the JARVIS persona
- `actions/` — weather, notes, email, system control, web
- `web/` — the cinematic front-end (HTML/CSS/JS)

---

<div align="center">

Built as a collaboration with **[Fish Audio](https://fish.audio/?fpr=rcic6s)** — give your projects the best voice on the planet. 🐟🔊

⭐ **Star this repo if JARVIS made your day.**

</div>
