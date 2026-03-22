import csv
import os
import re
from datetime import date
from playwright.sync_api import sync_playwright

# --- Resort definitions ---
RESORTS = {
    "miches": {
        "name": "Miches Playa Esmeralda",
        "url": "https://www.clubmed.us/r/miches-playa-esmeralda/y"
    },
    "cancun": {
        "name": "Cancun",
        "url": "https://www.clubmed.us/r/cancun-yucatan/y"
    },
    "puntacana": {
        "name": "Punta Cana",
        "url": "https://www.clubmed.us/r/punta-cana/y"
    }
}

START_DATE = "2027-01-16"
END_DATE = "2027-01-23"
ADULTS = 2
CHILDREN = 0


def build_url(base_url):
    return (
        f"{base_url}"
        f"?start_date={START_DATE}"
        f"&end_date={END_DATE}"
        f"&adults={ADULTS}"
        f"&children={CHILDREN}"
    )


def extract_price(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")

        full_text = page.inner_text("body")
        browser.close()

    matches = re.findall(r"\$[\d,]+", full_text)

    if len(matches) < 2:
        raise Exception("Could not find Best price on page.")

    best_price = matches[1]
    price = float(best_price.replace("$", "").replace(",", ""))
    return price


def append_to_csv(csv_file, price):
    today = date.today().isoformat()

    if not os.path.exists(csv_file):
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "price"])

    with open(csv_file, "r") as f:
        if any(today in line for line in f.readlines()):
            return

    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([today, price])


def run_all_resorts():
    for key, info in RESORTS.items():
        url = build_url(info["url"])
        price = extract_price(url)
        csv_file = f"{key}_prices.csv"
        append_to_csv(csv_file, price)
        print(f"Logged {price} for {info['name']}")


if __name__ == "__main__":
    run_all_resorts()
