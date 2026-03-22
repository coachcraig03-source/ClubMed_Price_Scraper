import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

CSV_FILE = "miches_prices.csv"
IMAGE_FILE = "miches.jpg"   # Your JPEG here


def load_data():
    dates = []
    prices = []

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.append(datetime.fromisoformat(row["date"]))
            prices.append(float(row["price"]))

    return dates, prices


def show_dashboard():
    dates, prices = load_data()

    today_price = prices[-1]
    low_price = min(prices)
    high_price = max(prices)

    # --- Create a wide figure so we can place the image on the right ---
    fig = plt.figure(figsize=(14, 5))

    # --- Main plot on the left ---
    ax = fig.add_axes([0.05, 0.1, 0.60, 0.8])  # left, bottom, width, height

    ax.plot(dates, prices, marker="o", linewidth=2)
    ax.set_title("Club Med Michès – Best Price Trend", fontsize=16, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.grid(True)

    # --- Summary box inside the chart ---
    summary_text = (
        f"Today:  ${today_price:,.0f}\n"
        f"Lowest: ${low_price:,.0f}\n"
        f"Highest: ${high_price:,.0f}"
    )

    ax.text(
        0.02, 0.98,
        summary_text,
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8)
    )

    # --- JPEG image OUTSIDE the graph, 20% larger ---
    if os.path.exists(IMAGE_FILE):
        img = mpimg.imread(IMAGE_FILE)

        # Add a second axes on the right side
        img_ax = fig.add_axes([0.70, 0.15, 0.25, 0.70])  # x, y, width, height

        img_ax.imshow(img)
        img_ax.axis("off")

    plt.show()


if __name__ == "__main__":
    show_dashboard()
