/* ==========================================================================
   J.A.R.V.I.S  ·  front-end
   - mechanical gear/engine core that reacts to voice
   - auto-starts on load; wake with "Hey Jarvis" (hands-free) or hold Space
   - streams the Fish Audio voice for low latency
   ========================================================================== */

const $ = (id) => document.getElementById(id);
const body = document.body;

// ---- state: asleep | listening | thinking | speaking ----------------------
let state = "asleep";
const LABELS = {
  asleep:    ["DORMANT",    "say “Hey Jarvis” to wake me"],
  listening: ["LISTENING",  "go ahead, sir"],
  thinking:  ["PROCESSING", "one moment"],
  speaking:  ["SPEAKING",   ""],
};
function setState(s) {
  state = s;
  body.dataset.state = s;
  $("status").textContent = LABELS[s][0];
  $("statusSub").textContent = LABELS[s][1];
}
function setYou(t)    { $("you").textContent = t || ""; }
function setJarvis(t) { $("jarvis").textContent = t || ""; }
function setActions(list) {
  const el = $("actionlog");
  el.innerHTML = "";
  (list || []).forEach((a) => {
    const c = document.createElement("div");
    c.className = "chip";
    c.textContent = a.tool.replace(/_/g, " ");
    el.appendChild(c);
  });
}

// ---- weather dashboard ----
let wxTimer = null;
function wxIcon(c, day) {
  if (c === 0) return day ? "☀️" : "🌙";
  if (c <= 2) return day ? "🌤️" : "☁️";
  if (c === 3) return "☁️";
  if (c === 45 || c === 48) return "🌫️";
  if (c >= 51 && c <= 57) return "🌦️";
  if (c >= 61 && c <= 67) return "🌧️";
  if (c >= 71 && c <= 77) return "❄️";
  if (c >= 80 && c <= 82) return "🌦️";
  if (c >= 85 && c <= 86) return "🌨️";
  if (c >= 95) return "⛈️";
  return "🌡️";
}
function showWeather(d) {
  if (!d) return;
  const wx = $("wx");
  const days = d.days.map((day) => {
    const dow = new Date(day.date).toLocaleDateString(undefined, { weekday: "short" });
    return `<div class="wx-day"><span class="wx-dow">${dow}</span>` +
           `<span class="wx-ic">${wxIcon(day.code, 1)}</span>` +
           `<span class="wx-hl"><b>${day.hi}°</b> ${day.lo}°</span></div>`;
  }).join("");
  wx.innerHTML =
    `<div class="wx-top">
       <div><div class="wx-loc">${d.location}</div><div class="wx-desc">${d.desc}</div></div>
       <div class="wx-now"><span class="wx-bigic">${wxIcon(d.code, d.is_day)}</span>` +
       `<span class="wx-temp">${d.temp}<sup>${d.units.temp}</sup></span></div>
     </div>
     <div class="wx-stats">
       <div><span>Feels like</span><b>${d.feels}${d.units.temp}</b></div>
       <div><span>Humidity</span><b>${d.humidity}%</b></div>
       <div><span>Wind</span><b>${d.wind} ${d.units.wind}</b></div>
     </div>
     <div class="wx-forecast">${days}</div>`;
  wx.hidden = false;
  clearTimeout(wxTimer);
  wxTimer = setTimeout(hideWeather, 30000);
}
function hideWeather() { $("wx").hidden = true; }

// ==========================================================================
//  Canvas engine (gears)
// ==========================================================================
const canvas = $("reactor");
const ctx = canvas.getContext("2d");
let W, H, CX, CY, DPR;
function resize() {
  DPR = Math.min(window.devicePixelRatio || 1, 2);
  W = canvas.width = innerWidth * DPR;
  H = canvas.height = innerHeight * DPR;
  canvas.style.width = innerWidth + "px";
  canvas.style.height = innerHeight + "px";
  CX = W / 2;
  CY = H / 2 - 40 * DPR;
}
addEventListener("resize", resize);
resize();

const COLORS = {
  asleep:    "#1b9fc4",
  listening: "#37f0a0",
  thinking:  "#ffcf6b",
  speaking:  "#8fe9ff",
};

let energy = 0.08;   // smoothed audio energy 0..1
let t = 0;

function draw() {
  t += 0.016;
  ctx.clearRect(0, 0, W, H);
  const col = COLORS[state] || "#38e1ff";
  const dim = state === "asleep" ? 0.6 : 1;
  const base = Math.min(1, energy) * dim;
  const R = Math.min(W, H) * 0.19;

  // ---- outer bloom ----
  const glow = ctx.createRadialGradient(CX, CY, R * 0.2, CX, CY, R * (2.2 + base));
  glow.addColorStop(0, hex(col, (0.28 + base * 0.35) * dim));
  glow.addColorStop(0.5, hex(col, 0.06 * dim));
  glow.addColorStop(1, "transparent");
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, W, H);

  // ---- rotating tick rings + dashed arcs ----
  ring(R * 1.9, 90, t * 0.25, col, 0.5 * dim, base);
  arcs(R * 1.55, -t * 0.5, col, base, dim);
  ring(R * 1.28, 160, t * 0.4, col, 0.35 * dim, base);

  // ---- audio-reactive frequency ring ----
  freqRing(R * 1.05, col, base);

  // ---- glowing core ----
  const coreR = R * (0.62 + base * 0.16 + Math.sin(t * 2) * 0.02);
  const core = ctx.createRadialGradient(CX, CY, 0, CX, CY, coreR);
  core.addColorStop(0, "#ffffff");
  core.addColorStop(0.25, hex(col, 0.95 * dim));
  core.addColorStop(0.7, hex(col, 0.35 * dim));
  core.addColorStop(1, "transparent");
  ctx.fillStyle = core;
  ctx.beginPath();
  ctx.arc(CX, CY, coreR, 0, Math.PI * 2);
  ctx.fill();

  requestAnimationFrame(draw);
}

function freqRing(radius, col, base) {
  ctx.save();
  ctx.translate(CX, CY);
  ctx.strokeStyle = hex(col, 0.9);
  ctx.lineWidth = 2 * DPR;
  const bars = 72;
  for (let i = 0; i < bars; i++) {
    const a = (i / bars) * Math.PI * 2;
    const n = (Math.sin(i * 1.7 + t * 6) * 0.5 + 0.5) * base;
    const r2 = radius + (4 + n * 46) * DPR;
    ctx.globalAlpha = 0.3 + n * 0.7;
    ctx.beginPath();
    ctx.moveTo(Math.cos(a) * radius, Math.sin(a) * radius);
    ctx.lineTo(Math.cos(a) * r2, Math.sin(a) * r2);
    ctx.stroke();
  }
  ctx.restore();
}

function ring(radius, ticks, rot, col, alpha, base) {
  ctx.save();
  ctx.translate(CX, CY);
  ctx.rotate(rot);
  ctx.strokeStyle = hex(col, alpha);
  ctx.lineWidth = 1 * DPR;
  for (let i = 0; i < ticks; i++) {
    const a = (i / ticks) * Math.PI * 2;
    const long = i % 6 === 0;
    const r2 = radius + (long ? 12 : 5) * DPR + base * 8 * DPR;
    ctx.globalAlpha = long ? alpha + 0.3 : alpha;
    ctx.beginPath();
    ctx.moveTo(Math.cos(a) * radius, Math.sin(a) * radius);
    ctx.lineTo(Math.cos(a) * r2, Math.sin(a) * r2);
    ctx.stroke();
  }
  ctx.restore();
}

function arcs(radius, rot, col, base, dim) {
  ctx.save();
  ctx.translate(CX, CY);
  ctx.rotate(rot);
  ctx.strokeStyle = hex(col, 0.75 * dim);
  ctx.lineWidth = 2.5 * DPR;
  ctx.shadowColor = col;
  ctx.shadowBlur = (8 + base * 18) * DPR;
  for (const [start, len] of [[0, 1.1], [Math.PI * 0.75, 0.6], [Math.PI * 1.25, 0.9]]) {
    ctx.beginPath();
    ctx.arc(0, 0, radius, start, start + len);
    ctx.stroke();
  }
  ctx.restore();
}

function hex(c, a) {
  const n = parseInt(c.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}
draw();

// ==========================================================================
//  Audio energy (mic in + TTS out)
// ==========================================================================
let actx, micAnalyser, ttsAnalyser, audioEl, audioUnlocked = false;
const tbuf = new Uint8Array(1024);

function readEnergy(an) {
  if (!an || !actx || actx.state !== "running") return 0;
  an.getByteTimeDomainData(tbuf);
  let s = 0;
  for (let i = 0; i < tbuf.length; i++) { const x = (tbuf[i] - 128) / 128; s += x * x; }
  return Math.sqrt(s / tbuf.length);
}

setInterval(() => {
  let target = 0.07 + Math.sin(t * 1.5) * 0.02;
  if (state === "speaking") target = Math.min(1, readEnergy(ttsAnalyser) * 3.2 + 0.15);
  else if (state === "listening") target = Math.min(1, readEnergy(micAnalyser) * 4 + 0.12);
  else if (state === "thinking") target = 0.4 + Math.sin(t * 8) * 0.18;
  energy += (target - energy) * 0.18;
}, 33);

async function initAudio() {
  try {
    actx = new (window.AudioContext || window.webkitAudioContext)();
    audioEl = new Audio();
    audioEl.crossOrigin = "anonymous";
    const srcNode = actx.createMediaElementSource(audioEl);
    ttsAnalyser = actx.createAnalyser();
    ttsAnalyser.fftSize = 2048;
    srcNode.connect(ttsAnalyser);
    ttsAnalyser.connect(actx.destination);
    audioEl.onended = onSpeakEnd;

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const micNode = actx.createMediaStreamSource(stream);
    micAnalyser = actx.createAnalyser();
    micAnalyser.fftSize = 2048;
    micNode.connect(micAnalyser);
  } catch (e) {
    console.warn("Audio/mic init:", e);
  }
}

// One user gesture unlocks audio output (a hard browser rule we can't skip).
function unlockAudio() {
  if (audioUnlocked) return;
  audioUnlocked = true;
  if (actx && actx.state !== "running") actx.resume().catch(() => {});
  $("enable").classList.add("hidden");
}
["pointerdown", "keydown", "touchstart"].forEach((ev) =>
  addEventListener(ev, unlockAudio, { passive: true }));

// ==========================================================================
//  Speech recognition — wake word + push-to-talk
// ==========================================================================
let recog = null, recogRunning = false;
let awake = false, awakeUntil = 0, ignoreUntil = 0;
let ptt = false;

const WAKE = /\b(hey jarvis|jarvis wake up|wake up jarvis|okay jarvis|ok jarvis)\b/;

function initSpeech() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { setJarvis("Speech recognition needs Chrome or Edge, sir."); return; }
  recog = new SR();
  recog.continuous = true;
  recog.interimResults = true;
  recog.lang = "en-US";

  recog.onresult = (e) => {
    let interim = "", final = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const txt = e.results[i][0].transcript;
      if (e.results[i].isFinal) final += txt; else interim += txt;
    }

    if (ptt) {
      setYou((final || interim).trim());
      return;
    }
    if (state === "speaking" || state === "thinking") return;
    if (Date.now() < ignoreUntil) return;   // brief echo guard after speaking

    const shown = final || interim;
    if (awake) { awakeUntil = Date.now() + 60000; setYou(shown); }  // stay awake while talking

    if (!final) return;
    const lower = final.toLowerCase();

    if (!awake || Date.now() >= awakeUntil) {
      // dormant: only a wake phrase activates
      const m = lower.match(WAKE);
      if (!m) return;
      wake();
      const cmd = final.slice(lower.indexOf(m[0]) + m[0].length).replace(/^[\s,.:!?]+/, "").trim();
      if (cmd) send(cmd); else { setState("listening"); greet(); }
    } else {
      // awake session: treat speech as a command (strip a leading "jarvis")
      const cmd = final.replace(/^\s*(hey\s+)?jarvis[\s,.:!?]*/i, "").trim();
      if (cmd) send(cmd);
    }
  };
  recog.onend = () => { if (recogRunning) { try { recog.start(); } catch (_) {} } };
  recog.onerror = () => {};

  recogRunning = true;
  try { recog.start(); } catch (_) {}
}

function wake() { awake = true; awakeUntil = Date.now() + 60000; setState("listening"); }
function greet() {
  const g = "Yes, sir?";
  setJarvis(g);
  speak(g);
}

// hold Space to talk (bypasses wake word)
addEventListener("keydown", (e) => {
  if (e.code === "Space" && !e.repeat) {
    e.preventDefault();
    ptt = true; awake = true; awakeUntil = Date.now() + 60000;
    setState("listening"); setYou(""); setJarvis("");
  }
});
addEventListener("keyup", (e) => {
  if (e.code === "Space" && ptt) {
    e.preventDefault();
    ptt = false;
    const cmd = ($("you").textContent || "").trim();
    if (cmd) send(cmd); else setState("listening");
  }
});

function onSpeakEnd() {
  ignoreUntil = Date.now() + 700;  // don't hear our own tail
  if (awake && Date.now() < awakeUntil) setState("listening");
  else { awake = false; setState("asleep"); setYou(""); }
}

// ==========================================================================
//  Round trip: transcript -> Claude -> Fish Audio voice
// ==========================================================================
async function send(text) {
  if (!text) return;
  awakeUntil = Date.now() + 60000;   // keep the session alive
  setState("thinking");
  setYou(text);
  setJarvis("");
  setActions([]);
  hideWeather();
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await r.json();
    setJarvis(data.reply || "");
    setActions(data.actions);
    const wx = (data.actions || []).find((a) => a.weather);
    if (wx && wx.weather) showWeather(wx.weather);
    if (data.reply) await speak(data.reply);
    else onSpeakEnd();
  } catch (e) {
    console.error(e);
    setJarvis("I lost the connection, sir.");
    onSpeakEnd();
  }
}

async function speak(text) {
  try {
    const res = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) { onSpeakEnd(); return; }
    setState("speaking");

    // Stream via MediaSource for low latency; fall back to a full blob.
    if (window.MediaSource && MediaSource.isTypeSupported("audio/mpeg")) {
      await playStream(res);
    } else {
      const buf = await res.arrayBuffer();
      audioEl.src = URL.createObjectURL(new Blob([buf], { type: "audio/mpeg" }));
      await safePlay();
    }
  } catch (e) {
    console.error(e);
    onSpeakEnd();
  }
}

function playStream(res) {
  return new Promise((resolve) => {
    const ms = new MediaSource();
    audioEl.src = URL.createObjectURL(ms);
    ms.addEventListener("sourceopen", async () => {
      let sb;
      try { sb = ms.addSourceBuffer("audio/mpeg"); }
      catch (_) { resolve(); return; }
      const queue = [];
      let done = false;
      const pump = () => {
        if (sb.updating) return;
        if (queue.length) sb.appendBuffer(queue.shift());
        else if (done) { try { ms.endOfStream(); } catch (_) {} }
      };
      sb.addEventListener("updateend", pump);
      safePlay();
      const reader = res.body.getReader();
      while (true) {
        const { value, done: d } = await reader.read();
        if (d) { done = true; pump(); break; }
        queue.push(value); pump();
      }
      resolve();
    });
  });
}

async function safePlay() {
  try {
    await audioEl.play();
    audioUnlocked = true;
    $("enable").classList.add("hidden");
  } catch (_) {
    // autoplay blocked -> ask for the one-time gesture
    $("enable").classList.remove("hidden");
  }
}

// ==========================================================================
//  Status pills + collab link + boot
// ==========================================================================
async function loadStatus() {
  try {
    const s = await fetch("/api/status").then((r) => r.json());
    const pills = [["brain", s.claude], ["voice", s.fish], ["spotify", s.spotify], ["email", s.email]];
    $("pills").innerHTML = pills
      .map(([n, on]) => `<span class="pill ${on ? "on" : "off"}"><span class="dot"></span>${n}</span>`)
      .join("");
    if (s.utm) $("collab").href = s.utm;
  } catch (_) {}
}

// Auto-start everything on load (no button).
(async function boot() {
  loadStatus();
  await initAudio();
  initSpeech();
  setState("asleep");
})();
