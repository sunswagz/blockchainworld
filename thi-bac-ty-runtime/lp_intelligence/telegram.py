"""Minimal Telegram Bot API sender; token/chat ID are environment-only secrets."""
from __future__ import annotations

import html
import os
import httpx


class TelegramDeliveryError(RuntimeError):
    pass


def send_message(text: str, *, token: str | None = None, chat_id: str | None = None,
                 client: httpx.Client | None = None) -> dict:
    token = token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise TelegramDeliveryError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    own_client = client is None
    session = client or httpx.Client(timeout=15.0)
    try:
        response = session.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        })
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            raise TelegramDeliveryError(str(payload.get("description", "Telegram API rejected message")))
        return payload.get("result", {})
    except (httpx.HTTPError, ValueError) as exc:
        raise TelegramDeliveryError(str(exc)) from exc
    finally:
        if own_client:
            session.close()


def format_alert(alert: dict) -> str:
    severity = str(alert.get("severity", "warning")).upper()
    lines = [
        f"[LP INTELLIGENCE] {severity}",
        str(alert.get("title", "LP alert")),
        str(alert.get("message", "")),
    ]
    for evidence in alert.get("evidence", []):
        position = evidence.get("position_id") or evidence.get("token_id")
        chain = evidence.get("chain_id", "")
        if position:
            lines.append(f"Position: {position} | Chain: {chain}")
        current = evidence.get("current_tick")
        lower, upper = evidence.get("tick_lower"), evidence.get("tick_upper")
        if current is not None and lower is not None and upper is not None:
            lines.append(f"Tick: {current} | Range: {lower} – {upper}")
    checks = alert.get("recommended_checks") or []
    if checks:
        lines.append("Kiểm tra:")
        lines.extend(f"• {item}" for item in checks[:3])
    return "\n".join(html.escape(line) for line in lines)
