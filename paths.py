from pathlib import Path
import socket
from datetime import datetime

# Local Synology Drive folder on Windows
BASE = Path(r"C:\Users\cbrow\SynologyDrive\clubmed")

# CSV paths
MICHES_CSV = BASE / "miches_prices.csv"
CANCUN_CSV = BASE / "cancun_prices.csv"
PUNTACANA_CSV = BASE / "puntacana_prices.csv"

# Unique temp file for safe multi-machine writes
def temp_file_for(resort_key: str) -> Path:
    hostname = socket.gethostname()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return BASE / f"{resort_key}_{hostname}_{timestamp}.tmp"

