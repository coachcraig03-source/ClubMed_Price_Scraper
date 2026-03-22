import csv
import os
import re
from datetime import date
from playwright.sync_api import sync_playwright

RESORT_URL = "https://www.clubmed.us/r/miches-playa-esmeralda/y?start_date=2027-01-16&end_date=2027-01-23&adults=2&children=0"
CSV_FILE = "miches_prices.csv"


def extract_price():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(RESORT_URL)
        page.wait_for_load_state("networkidle")

        # Extract ALL text from the booking page
        full_text = page.inner_text("body")
        print("DEBUG FULL PAGE TEXT EXTRACTED")

        browser.close()

    # Extract ALL dollar amounts from the page
    matches = re.findall(r"\$[\d,]+", full_text)

    if len(matches) < 2:
        raise Exception("ERROR: Could not find enough price values on the page.")

    # Best price is ALWAYS the second dollar amount
    best_price = matches[1]
    print("DEBUG BEST PRICE FOUND:", best_price)

    # Convert to float
    price = float(best_price.replace("$", "").replace(",", ""))
    return price


def append_to_csv(price):
    today = date.today().isoformat()

    # Create file if missing
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "price"])

    # Avoid duplicate entries for same day
    with open(CSV_FILE, "r") as f:
        lines = f.readlines()
        if any(today in line for line in lines):
            return

    # Append new row
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([today, price])


def run_tracker():
    price = extract_price()
    append_to_csv(price)
    print(f"Logged {price} for {date.today()}")


if __name__ == "__main__":
    run_tracker()
