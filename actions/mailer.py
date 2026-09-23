"""Send email via Gmail SMTP. Falls back to saving a .eml draft locally if no
SMTP credentials are configured, so the demo never breaks."""
from __future__ import annotations

import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

import config


def send_email(subject: str, body: str, to: str | None = None) -> str:
    recipient = (to or config.EMAIL_DEFAULT_TO or "").strip()
    if not recipient:
        return "No recipient set. Add EMAIL_DEFAULT_TO in .env or name someone."

    msg = EmailMessage()
    msg["Subject"] = subject or "(no subject)"
    msg["From"] = config.EMAIL_ADDRESS or "jarvis@localhost"
    msg["To"] = recipient
    msg.set_content(body or "")

    # No creds -> write a draft file instead of failing.
    if not (config.EMAIL_ADDRESS and config.EMAIL_APP_PASSWORD):
        outbox = os.path.join(os.path.dirname(__file__), "..", "outbox")
        os.makedirs(outbox, exist_ok=True)
        fname = datetime.now().strftime("%Y%m%d-%H%M%S") + ".eml"
        with open(os.path.join(outbox, fname), "wb") as f:
            f.write(bytes(msg))
        return f"Email saved as a draft ({fname}) — SMTP isn't configured yet."

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
            smtp.login(config.EMAIL_ADDRESS, config.EMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        return f"Email sent to {recipient}."
    except Exception as e:  # noqa: BLE001
        return f"Couldn't send the email ({e.__class__.__name__})."
