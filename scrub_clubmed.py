from playwright.sync_api import sync_playwright

URL = "https://www.clubmed.us/r/miches-playa-esmeralda/y?start_date=2027-01-16&end_date=2027-01-23&adults=2&children=0"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("Loading resort page…")
    page.goto(URL)
    page.wait_for_load_state("networkidle")

    # The price appears inside a span that contains a dollar sign
    price_locator = page.locator("span:has-text('$')").first
    price_text = price_locator.inner_text()

    print("\n=== Michès Price (HTML Extracted) ===")
    print(price_text)

    browser.close()
