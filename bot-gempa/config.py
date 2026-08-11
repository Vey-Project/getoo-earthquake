"""
config.py - Konfigurasi global bot gempa
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# Gempa API
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "2"))
DEFAULT_MIN_MAGNITUDE = float(os.getenv("DEFAULT_MIN_MAGNITUDE", "4.5"))

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/bot.db")

# Mapbox
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# URL API
USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
BMKG_URL = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"

# Embed colors
COLOR_INFO = 0x3498db
COLOR_WARNING = 0xf39c12
COLOR_DANGER = 0xe74c3c
COLOR_SUCCESS = 0x2ecc71