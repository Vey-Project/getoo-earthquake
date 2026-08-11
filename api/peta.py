"""
api/peta.py - Generate peta lokasi gempa menggunakan Mapbox Static API
"""
import logging
from typing import Optional
import aiohttp

from config import MAPBOX_TOKEN

logger = logging.getLogger(__name__)

MAPBOX_STATIC_URL = "https://api.mapbox.com/styles/v1/mapbox/streets-v12/static"


async def generate_map(latitude: float, longitude: float, filename: str = "peta.png",
                       zoom: int = 6, width: int = 800, height: int = 500) -> Optional[str]:
    """
    Generate peta lokasi gempa menggunakan Mapbox Static Images API.
    Returns path file jika berhasil, None jika gagal.
    """
    if not MAPBOX_TOKEN:
        logger.warning("MAPBOX_TOKEN kosong, skip generate peta")
        return None

    # Marker pin merah di lokasi gempa
    marker = f"pin-l+%23e74c3c({longitude},{latitude})"
    url = f"{MAPBOX_STATIC_URL}/{marker}/{longitude},{latitude},{zoom}/{width}x{height}?access_token={MAPBOX_TOKEN}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    logger.warning("Mapbox return status %s", resp.status)
                    return None
                data = await resp.read()
                with open(filename, "wb") as f:
                    f.write(data)
                logger.info("Peta berhasil digenerate: %s", filename)
                return filename
    except Exception as e:
        logger.error("Error generating map: %s", e)
        return None