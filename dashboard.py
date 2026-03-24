import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
from pathlib import Path

BASE = Path(r"C:\Users\cbrow\SynologyDrive\clubmed")


# --- Resort definitions ---
RESORTS = {
    "miches": {
        "name": "Miches Playa Esmeralda",
        "csv": BASE / "miches_prices.csv",
        "color": "#1f77b4"
    },
    "cancun": {
        "name": "Cancun",
        "csv": BASE / "cancun_prices.csv",
        "color": "#ff7f0e"
    },
    "puntacana": {
        "name": "Punta Cana",
        "csv": BASE / "puntacana_prices.csv",
        "color": "#2ca02c"
    }
}


IMAGE_FILE = "dashboard.jpg"   # Your single photo

def load_csv(csv_file):
    dates = []
    prices = []

    if not os.path.exists(csv_file):
        return dates, prices

    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_date = row["date"].strip()

            # Try ISO first (fast path)
            try:
                dt = datetime.fromisoformat(raw_date)
            except ValueError:
                # Try multiple common formats Excel might produce
                parsed = None
                for fmt in [
                    "%m/%d/%Y",
                    "%m/%d/%y",
                    "%Y/%m/%d",
                    "%Y-%m-%d",
                    "%Y-%m-%d",
                    "%m-%d-%Y",
                    "%m-%d-%y",
                    "%d-%b-%Y",
                    "%d-%b-%y",
                    "%b %d %Y",
                    "%b %d, %Y",
                    "%d %b %Y",
                ]:
                    try:
                        parsed = datetime.strptime(raw_date, fmt)
                        break
                    except ValueError:
                        continue

                if parsed is None:
                    print(f"[WARNING] Could not parse date: {raw_date}")
                    continue

                dt = parsed

            # Parse price normally
            try:
                price = float(row["price"])
            except:
                print(f"[WARNING] Bad price value: {row['price']}")
                continue

            dates.append(dt)
            prices.append(price)

    return dates, prices


def show_dashboard():
    # Wider figure to fit chart + image + summary lines
    fig = plt.figure(figsize=(16, 8))

    # --- Main plot on the left ---
    ax = fig.add_axes([0.05, 0.30, 0.60, 0.60])  # left, bottom, width, height

    summary_data = []  # Collect summary info for all resorts

    # --- Plot each resort ---
    for key, info in RESORTS.items():
        dates, prices = load_csv(info["csv"])

        if len(dates) == 0:
            continue

        ax.plot(
            dates,
            prices,
            marker="o",
            linewidth=2,
            color=info["color"],
            label=info["name"]
        )

        today_price = prices[-1]
        low_price = min(prices)
        high_price = max(prices)

        summary_data.append({
            "name": info["name"],
            "today": today_price,
            "low": low_price,
            "high": high_price,
            "color": info["color"]
        })

    # --- Chart formatting ---
    ax.set_title("Club Med – Best Price Trends", fontsize=22, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.grid(True)
    ax.legend()

    # --- Add single photo outside the graph ---
    if os.path.exists(IMAGE_FILE):
        img = mpimg.imread(IMAGE_FILE)
        img_ax = fig.add_axes([0.70, 0.25, 0.28, 0.70])  # larger image
        img_ax.imshow(img)
        img_ax.axis("off")

    # --- Summary lines UNDER the chart ---
    y_start = 0.06        # baseline
    y_step = 0.075        # tighter spacing

    for i, s in enumerate(summary_data):
        # Lower Punta Cana slightly (your request)
        y_offset = 0.015 if "Punta Cana" in s["name"] else 0

        fig.text(
            0.05,
            y_start + i * y_step - y_offset,
            f"{s['name']}   Today: ${s['today']:,.0f}   "
            f"Low: ${s['low']:,.0f}   High: ${s['high']:,.0f}",
            fontsize=12,
            color=s["color"],
            fontweight="bold"
        )

    plt.show()


if __name__ == "__main__":
    show_dashboard()
