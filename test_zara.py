
import os
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone

URL = "https://www.zara.com/us/en/limited-edition-wool-blend-flower-hat-p02635204.html?v1=584098404"

API_URL = "https://api.brightdata.com/request"


def send_email(subject, body):
    sender = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = sender
    msg.set_content(body)

    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, timeout=30
    ) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

    print("Email sent successfully")


def check_zara():
    headers = {
        "Authorization": (
            "Bearer " + os.environ["BRIGHTDATA_API_KEY"]
        ),
        "Content-Type": "application/json"
    }

    payload = {
        "zone": os.environ["BRIGHTDATA_ZONE"],
        "url": URL,
        "format": "raw"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=120
    )

    print("Bright Data HTTP:", response.status_code)
    print("Response size:", len(response.content))

    response.raise_for_status()

    html = response.text
    lower = html.lower()

    print("Product name found:", "flower hat" in lower)
    print("Out of stock text:", "out of stock" in lower)
    print("Add to bag text:", "add to bag" in lower)

    blocked = any(x in lower for x in [
        "bm-verify",
        "/_sec/verify",
        "/interstitial/ic.html"
    ])

    print("Bot challenge detected:", blocked)

    if blocked:
        print("RESULT: UNKNOWN - Bot protection")
    elif "flower hat" not in lower:
        print("RESULT: UNKNOWN - Product not confirmed")
    else:
        print("RESULT: PRODUCT PAGE FOUND")
        print("Stock status: NOT YET VERIFIED")

    # Save response for later inventory parser development.
    with open("zara_response.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Response saved for inspection")


if __name__ == "__main__":
    print("Checked at:", datetime.now(timezone.utc))

    if os.getenv("TEST_EMAIL") == "true":
        send_email(
            "ZARA Monitor - Test Successful",
            "Gmail notification is working."
        )

    check_zara()
