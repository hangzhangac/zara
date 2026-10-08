
import requests

URL = "https://www.zara.com/us/en/limited-edition-wool-blend-flower-hat-p02635204.html?v1=584098404"

try:
    response = requests.get(
        URL,
        headers={"User-Agent": "PersonalStockMonitor/1.0"},
        timeout=20
    )

    print("Status:", response.status_code)
    print("Response size:", len(response.content))
    print("Final URL:", response.url)

    html = response.text.lower()

    for keyword in [
        "flower hat",
        "out of stock",
        "coming soon",
        "add to bag",
        "captcha"
    ]:
        print(f"{keyword}: {keyword in html}")

except requests.RequestException as e:
    print("Request failed:", str(e))
