<div align="center">

# 🤖 J.A.R.V.I.S
### Build your own Iron-Man-style AI assistant — with a real voice from [**Fish Audio**](https://fish.audio/?utm_source=YOUR_UTM_HERE)

Say **“Hey Jarvis”**, ask it anything, and watch the arc-reactor HUD light up as it answers
in the iconic JARVIS voice — then checks the weather, writes you a note, searches the web, or sends an email.

**⏱ ~15 minutes · 💸 free to start · 🪟 Windows · 🧠 no coding required**

**⚡ Powered by [Fish Audio](https://fish.audio/?utm_source=YOUR_UTM_HERE) (the voice) + Claude (the brain)**

</div>

> 📌 **Repo owner:** replace every `https://fish.audio/?utm_source=YOUR_UTM_HERE` in this file with your real Fish Audio link before sharing.

---

## ✨ What it can do
🌤️ Live weather dashboard · 📝 Writes notes in Notepad · 📧 Sends email · 🌐 Searches the live web · 🔊 Controls volume & brightness · 🎙️ Hands-free “Hey Jarvis”

---

## 🚀 Get it running (6 steps)

### 1. Install Python (the engine)
Download it once → **[python.org/downloads](https://www.python.org/downloads/)**

> ⚠️ **On the first installer screen, tick “Add python.exe to PATH”** before clicking Install. This is the #1 thing people forget — nothing works without it.

### 2. Download JARVIS
Click the green **`Code ▾`** button at the top of this page → **Download ZIP** → unzip it to your **Desktop**.

<details><summary>💻 Prefer the command line? (optional)</summary>

```bash
git clone https://github.com/JoseBlancoSiles/build-your-own-jarvis.git
```
</details>

### 3. Give JARVIS its voice — Fish Audio 🐟
👉 **[Create your free Fish Audio account](https://fish.audio/?utm_source=YOUR_UTM_HERE)**

Then: click your **profile → API Keys → Create**, and copy the key (starts with `sk-…`).

### 4. Give JARVIS a brain — Claude 🧠
Get a key at **[console.anthropic.com](https://console.anthropic.com)** → **API Keys → Create Key** → copy it (starts with `sk-ant-…`).

### 5. Paste in your 2 keys
Open the `jarvis` folder, find the file named **`.env`** (see note below if you don’t), open it with **Notepad**, and paste your keys:

```env
FISH_API_KEY=paste-your-fish-key-here
ANTHROPIC_API_KEY=paste-your-claude-key-here
```
Save and close.

> 👀 **No `.env` file?** First run **`run.bat`** once (Step 6) — it creates the `.env` for you automatically. Then open it, paste the keys, and run again.

### 6. Launch it
Double-click **`run.bat`**. The first time, a black window installs everything (2–3 min) — leave it open.

> 🛡️ If Windows shows **“Windows protected your PC,”** click **More info → Run anyway** (it’s just your own file).

When it says **“JARVIS online,”** open **Chrome or Edge** at **http://localhost:8000**, click once on the page, allow the mic, and say:

> ### 🎙️ “Hey Jarvis, what’s the weather?”

**That’s it — JARVIS is alive.** 🎉

---

## 🗣️ Try saying
- *“Hey Jarvis, what’s the weather in Tokyo?”* → live dashboard
- *“Hey Jarvis, write me a caption for my reel in notepad”*
- *“Hey Jarvis, what’s the latest AI news?”* → live web search
- *“Hey Jarvis, turn the volume down”*

💡 Tip: you can also **hold the Space bar** and talk (great for a clean take).

---

## 📧 Optional: let JARVIS send email
Gmail needs a special **App Password** (your normal one won’t work):

1. Turn on **[2-Step Verification](https://myaccount.google.com/security)**
2. Create an **[App Password](https://myaccount.google.com/apppasswords)** named `JARVIS`, copy the 16-char code
3. Add these to your `.env`, then re-run `run.bat`:
```env
EMAIL_ADDRESS=youremail@gmail.com
EMAIL_APP_PASSWORD=your16charcode
EMAIL_DEFAULT_TO=youremail@gmail.com
```

## 🎵 Optional: Spotify (needs Premium)
Create a free app at **[developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)** (add redirect URI `http://127.0.0.1:8888/callback`), then fill `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` in `.env`.

---

## 🎛️ Change the voice
The JARVIS voice is a Fish Audio **`reference_id`** in `.env`:
```env
FISH_VOICE_ID=612b878b113047d9a770c069c8b4fdfe   # "Jarvis (MCU)"
```
Browse the [Fish Audio Voice Library](https://fish.audio/?utm_source=YOUR_UTM_HERE), open any voice, and paste its ID here.

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
Finish Step 1 (with the PATH tick) and paste both keys in Step 5, then double-click <b>run.bat</b> again.
</details>

---

## 🧩 How it works (for the curious)
```
🎤 Browser (Web Speech)  ──►  Claude (brain + tools)  ──►  runs actions
      ▲                                                          │
🔊 reactor + voice  ◄──────────────  Fish Audio (the voice)  ◄──┘
```
- `server.py` — serves the HUD, bridges to Claude & Fish Audio
- `brain.py` — Claude tool-calling loop + the JARVIS persona
- `actions/` — weather, notes, email, system control, web
- `web/` — the cinematic front-end

---

<div align="center">

Built as a collaboration with **[Fish Audio](https://fish.audio/?utm_source=YOUR_UTM_HERE)** — give your projects the best voice on the planet. 🐟🔊

⭐ **Star this repo if JARVIS made your day.**

</div>
