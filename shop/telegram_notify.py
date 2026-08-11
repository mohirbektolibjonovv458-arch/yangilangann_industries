import html
import logging
import os

import requests
from django.utils import timezone


logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


def send_telegram_message(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error(
            "Telegram sozlamalari topilmadi. "
            "TELEGRAM_BOT_TOKEN=%s, TELEGRAM_CHAT_ID=%s",
            bool(TELEGRAM_BOT_TOKEN),
            bool(TELEGRAM_CHAT_ID),
        )
        return False

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    try:
        response = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
            },
            timeout=10,
        )

        if response.ok:
            logger.info(
                "Telegram xabari muvaffaqiyatli yuborildi."
            )
            return True

        logger.error(
            "Telegram xabar yuborilmadi. HTTP %s. Javob: %s",
            response.status_code,
            response.text,
        )
        return False

    except requests.Timeout:
        logger.error(
            "Telegram API javob bermadi (timeout, 10s)."
        )
        return False

    except requests.RequestException as exc:
        logger.error(
            "Telegram xabar yuborishda xatolik: %s",
            exc,
        )
        return False


def notify_wholesale_order(order) -> bool:
    local_time = (
        timezone.localtime(order.created_at)
        if order.created_at
        else timezone.localtime()
    )

    text = (
        f"🛒 <b>YANGI BUYURTMA</b>\n\n"
        f"👤 Ism: {html.escape(str(order.name))}\n"
        f"📞 Telefon: {html.escape(str(order.phone))}\n"
        + (
            f"🏢 Korxona: "
            f"{html.escape(str(order.company_name))}\n"
            if order.company_name
            else ""
        )
        + (
            f"📦 Mahsulot: "
            f"{html.escape(str(order.product))}\n"
            if order.product
            else "📦 Mahsulot: —\n"
        )
        + f"🔢 Miqdor: {order.quantity} dona\n"
        f"📝 Izoh: "
        f"{html.escape(str(order.comment)) if order.comment else '—'}\n"
        f"🆔 Buyurtma ID: #{order.pk}\n"
        f"🕐 Vaqt: {local_time.strftime('%Y-%m-%d %H:%M')}"
    )

    return send_telegram_message(text)


def notify_contact_message(msg) -> bool:
    text = (
        "✉️ <b>Yangi xabar (Bog'lanish formasi)</b>\n\n"
        f"👤 Ism: {html.escape(str(msg.name))}\n"
        f"📞 Telefon: "
        f"{html.escape(str(msg.phone)) if msg.phone else '—'}\n"
        f"📧 Email: "
        f"{html.escape(str(msg.email)) if msg.email else '—'}\n"
        f"💬 Xabar: {html.escape(str(msg.message))}"
    )

    return send_telegram_message(text)