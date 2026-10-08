
import requests

URL = "https://www.zara.com/us/en/limited-edition-wool-blend-flower-hat-p02635204.html?v1=584098404"

try:
    response = requests.get(
        URL,
        headers={
            "User-Agent": "PersonalStockMonitor/1.0",
            "Accept": "text/html"
        },
        timeout=20
    )

    print("===== HTTP RESPONSE =====")
    print("Status:", response.status_code)
    print("Response size:", len(response.content))
    print("Final URL:", response.url)
    print("Content-Type:", response.headers.get("Content-Type"))

    print("\n===== KEYWORD CHECK =====")
    html = response.text.lower()

    keywords = [
        "flower hat",
        "out of stock",
        "coming soon",
        "add to bag",
        "captcha",
        "access denied",
        "akamai",
        "cloudflare"
    ]

    for keyword in keywords:
        print(f"{keyword}: {keyword in html}")

    print("\n===== FULL HTML RESPONSE =====")
    print(response.text[:10000])
    print("===== END HTML =====")

except requests.RequestException as e:
    print("Request failed:", str(e))
