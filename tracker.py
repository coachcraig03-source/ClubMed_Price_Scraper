import csv
import os
import re
from datetime import date
from playwright.sync_api import sync_playwright

from paths import (
    MICHES_CSV,
    CANCUN_CSV,
    PUNTACANA_CSV,
    temp_file_for
)

# --- Resort definitions ---
RESORTS = {
    "miches": {
        "name": "Miches Playa Esmeralda",
        "url": "https://www.clubmed.us/r/miches-playa-esmeralda/y",
        "csv": MICHES_CSV
    },
    "cancun": {
        "name": "Cancun",
        "url": "https://www.clubmed.us/r/cancun-yucatan/y",
        "csv": CANCUN_CSV
    },
    "puntacana": {
        "name": "Punta Cana",
        "url": "https://www.clubmed.us/r/punta-cana/y",
        "csv": PUNTACANA_CSV
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

    # --- DEBUG: Extract and print the price block around "Initial price" ---
    price_block = re.search(
        r"(Initial price[\s\S]{0,200}Best price[\s\S]{0,200}Total price)",
        full_text,
        re.IGNORECASE
    )

    if price_block:
        print("\n================ PRICE BLOCK ================")
        print(price_block.group(1))
        print("=============================================\n")
    else:
        print("\n[DEBUG] Could not locate price block.\n")

    # --- Primary extraction: literal "Best price $X,XXX" ---
    best_price_match = re.search(
        r"Best price\s*\$([\d,]+)",
        full_text,
        re.IGNORECASE
    )

    if best_price_match:
        price_str = best_price_match.group(1)
        price = float(price_str.replace(",", ""))
        print(f"FOUND BEST PRICE: ${price_str}")
        return price

    # --- Fallback: print price candidates with context ---
    matches = re.findall(r"\$[\d,]+", full_text)

    print("\n--- PRICE CANDIDATES FOUND (fallback) ---")
    for m in matches[:10]:
        idx = full_text.find(m)
        start = max(0, idx - 80)
        end = idx + len(m) + 80
        context = full_text[start:end].replace("\n", " ")
        print(f"\nPRICE: {m}")
        print(f"CONTEXT: ...{context}...")
    print("------------------------------------------\n")

    raise Exception("Could not find 'Best price' on page.")





def safe_append(csv_path, price):
    today = date.today().isoformat()

    # Ensure CSV exists
    if not csv_path.exists():
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "price"])

    # Avoid duplicate entries for the same day
    with csv_path.open("r") as f:
        if any(today in line for line in f.readlines()):
            return

    # Write to a temp file first (safe for multi-machine)
    tmp = temp_file_for(csv_path.stem)
    with tmp.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([today, price])

    # Merge temp file into main CSV
    with csv_path.open("a", newline="") as main, tmp.open("r") as t:
        for line in t:
            main.write(line)

    # Remove temp file
    tmp.unlink()


def run_all_resorts():
    for key, info in RESORTS.items():
        url = build_url(info["url"])
        price = extract_price(url)
        safe_append(info["csv"], price)
        print(f"Logged {price} for {info['name']}")


if __name__ == "__main__":
    run_all_resorts()
