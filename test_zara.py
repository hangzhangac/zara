
import os
import json
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import requests
from bs4 import BeautifulSoup

PRODUCT_URL = (
    "https://www.zara.com/us/en/"
    "limited-edition-wool-blend-flower-hat-"
    "p02635204.html?v1=584098404"
)

API_URL = "https://api.brightdata.com/request"
STATE_FILE = Path("stock_state.json")
PRODUCT_NAME = "LIMITED EDITION WOOL BLEND FLOWER HAT"


def get_html():
    response = requests.post(
        API_URL,
        headers={
            "Authorization": (
                "Bearer " + os.environ["BRIGHTDATA_API_KEY"]
            ),
            "Content-Type": "application/json",
        },
        json={
            "zone": os.environ["BRIGHTDATA_ZONE"],
            "url": PRODUCT_URL,
            "format": "raw",
        },
        timeout=120,
    )

    print("Bright Data HTTP:", response.status_code)
    print("Response size:", len(response.content))

    response.raise_for_status()
    return response.text


def detect_stock(html):
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(" ", strip=True) if soup.title else ""

    if PRODUCT_NAME not in title.upper():
        return "UNKNOWN"

    # Confirmed purchase button.
    add_buttons = soup.select(
        'button[data-qa-action="add-to-cart"]'
    )

    for button in add_buttons:
        if (
            not button.has_attr("disabled")
            and button.get("aria-disabled", "").lower() != "true"
        ):
            return "IN_STOCK"

    # Explicit sold-out button.
    sold_out_buttons = soup.select(
        'button[data-qa-action="show-similar-products"]'
    )

    for button in sold_out_buttons:
        if "OUT OF STOCK" in button.get_text(
            " ", strip=True
        ).upper():
            return "OUT_OF_STOCK"

    return "UNKNOWN"


def load_state():
    if not STATE_FILE.exists():
        return {
            "last_status": "UNKNOWN",
            "alert_sent": False,
        }

    try:
        data = json.loads(STATE_FILE.read_text())
        return {
            "last_status": data.get("last_status", "UNKNOWN"),
            "alert_sent": bool(data.get("alert_sent", False)),
        }
    except (OSError, ValueError):
        return {
            "last_status": "UNKNOWN",
            "alert_sent": False,
        }


def save_state(state):
    STATE_FILE.write_text(
        json.dumps(state, indent=2) + "\n",
        encoding="utf-8",
    )


def send_email(subject, body):
    sender = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = sender
    message.set_content(body)

    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, timeout=30
    ) as smtp:
        smtp.login(sender, password)
        smtp.send_message(message)

    print("Email sent successfully")


def main():
    now = datetime.now(timezone.utc).isoformat()
    print("Checked at:", now)

    # Only send test email on explicit manual request.
    if os.getenv("TEST_EMAIL") == "true":
        send_email(
            "ZARA Monitor - Test Successful",
            "Gmail notification is working.",
        )

    try:
        html = get_html()
        status = detect_stock(html)
    except Exception as exc:
        print("Stock check failed:", exc)
        status = "UNKNOWN"

    print("CURRENT STATUS:", status)

    state = load_state()
    previous = state["last_status"]
    alert_sent = state["alert_sent"]

    print("PREVIOUS STATUS:", previous)
    print("ALERT ALREADY SENT:", alert_sent)

    if status == "IN_STOCK":
        if not alert_sent:
            send_email(
                "ZARA RESTOCK ALERT - FLOWER HAT",
                (
                    "The ZARA John Galliano flower hat "
                    "appears to be IN STOCK!\n\n"
                    f"Product: {PRODUCT_NAME}\n"
                    f"Link: {PRODUCT_URL}\n"
                    f"Checked: {now}\n\n"
                    "Availability may change quickly."
                ),
            )
            state["alert_sent"] = True
        else:
            print("Already alerted. Skipping email.")

        state["last_status"] = "IN_STOCK"

    elif status == "OUT_OF_STOCK":
        state["last_status"] = "OUT_OF_STOCK"
        state["alert_sent"] = False
        print("Out of stock. Alert reset.")

    else:
        # Preserve prior known state.
        print("Unknown status. State unchanged.")

    save_state(state)


if __name__ == "__main__":
    main()
