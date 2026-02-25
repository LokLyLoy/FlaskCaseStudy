from datetime import datetime
import json
import os
from html import escape

import requests
from flask import render_template, request, jsonify

from app import app

@app.route('/checkout')
def checkout():
    return render_template('page/checkout.html')

def _send_telegram_order_alert(order_details: str) -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN and/or TELEGRAM_CHAT_ID in environment (.env)")

    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    resp = requests.post(
        telegram_url,
        data={"chat_id": chat_id, "text": order_details},
        timeout=10,
    )
    resp.raise_for_status()


@app.post('/api/checkout')
def checkout_alert():
    # Accept JSON from the frontend (recommended) and fall back to form data.
    payload = request.get_json(silent=True)
    if isinstance(payload, dict):
        data = payload
    else:
        data = request.form.to_dict(flat=True)

    cart = data.get("cart", [])
    if isinstance(cart, str):
        try:
            cart = json.loads(cart) if cart else []
        except json.JSONDecodeError:
            cart = []

    if not isinstance(cart, list) or not cart:
        return jsonify({"success": False, "error": "Cart is empty or invalid."}), 400

    total = sum(float(item.get("price", 0)) * int(item.get("quantity", 0)) for item in cart)
    order_id = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    customer_name = escape(str(data.get("name", "-")))
    customer_phone = escape(str(data.get("phone", "-")))
    customer_email = escape(str(data.get("email", "-")))
    customer_address = escape(str(data.get("address", "-")))

    lines = []
    lines.append("<b>🛒 NEW ORDER</b>")
    lines.append(f"<b>📋 Order ID:</b> <code>{escape(order_id)}</code>")
    lines.append("")

    lines.append("<b>👤 CUSTOMER DETAILS</b>")
    lines.append(f"├ <b>Name:</b> {customer_name}")
    lines.append(f"├ <b>Phone:</b> {customer_phone}")
    lines.append(f"├ <b>Email:</b> {customer_email}")
    lines.append(f"└ <b>Address:</b> {customer_address}")
    lines.append("")

    lines.append("<b>📦 ORDER ITEMS</b>")

    for item in cart:
        name = escape(str(item.get("name", "Item")))
        qty = int(item.get("quantity", 0))
        price = float(item.get("price", 0))
        line_total = price * qty
        lines.append(f"│ • {name}")
        lines.append(f"│   <code>{qty} × ${price:.2f} = ${line_total:.2f}</code>")

    lines.append("")
    lines.append("<b>💰 ORDER SUMMARY</b>")
    lines.append(f"<b>└ Total Amount:</b> <code>${total:.2f}</code>")

    order_details = "\n".join(lines)

    try:
        # Use Telegram HTML parse mode for clean formatting.
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not bot_token or not chat_id:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN and/or TELEGRAM_CHAT_ID in environment (.env)")
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(
            telegram_url,
            data={
                "chat_id": chat_id,
                "text": order_details,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as e:
        app.logger.exception("Failed to send Telegram order alert: %s", e)
        return jsonify({"success": False, "error": "Failed to notify store owner. Please try again."}), 500

    return jsonify({"success": True, "order_id": order_id})