"""
api/gempa.py - Fetch data gempa dari USGS dan BMKG
"""
import logging
import aiohttp

from config import USGS_URL, BMKG_URL

logger = logging.getLogger(__name__)


async def fetch_usgs(session: aiohttp.ClientSession) -> list:
    """Fetch gempa global dari USGS (1 jam terakhir)"""
    try:
        async with session.get(USGS_URL, timeout=15) as resp:
            if resp.status != 200:
                logger.warning("USGS return status %s", resp.status)
                return []
            data = await resp.json()

        earthquakes = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [0, 0, 0])
            earthquakes.append({
                "id": feature.get("id") or props.get("code"),
                "source": "usgs",
                "magnitude": props.get("mag", 0),
                "location": props.get("place", "Unknown"),
                "latitude": coords[1],
                "longitude": coords[0],
                "depth": coords[2] if len(coords) > 2 else 0,
                "time": props.get("time"),
                "tsunami": props.get("tsunami", 0),
                "url": props.get("url"),
            })
        return earthquakes
    except Exception as e:
        logger.error("Error fetching USGS: %s", e)
        return []


async def fetch_bmkg(session: aiohttp.ClientSession) -> list:
    """Fetch gempa terbaru dari BMKG (Indonesia)"""
    try:
        async with session.get(BMKG_URL, timeout=15) as resp:
            if resp.status != 200:
                logger.warning("BMKG return status %s", resp.status)
                return []
            data = await resp.json()

        gempa = data.get("Infogempa", {}).get("gempa", {})
        if not gempa:
            return []

        # Koordinat BMKG format "3.42,97.17"
        coords = gempa.get("Coordinates", "0,0").split(",")
        lat = float(coords[0].strip())
        lon = float(coords[1].strip())

        # Generate ID dari DateTime (tidak ada EventID di API)
        eq_id = f"bmkg-{gempa.get('DateTime', '').replace(':', '').replace('-', '').replace('T', '')}"

        # Parse potensi tsunami
        tsunami = gempa.get("Potensi", "")
        tsunami_flag = 1 if tsunami and "tsunami" in tsunami.lower() else 0

        # Normalize depth to float km
        depth_raw = gempa.get("Kedalaman", "0 km")
        if isinstance(depth_raw, str):
            depth_val = float(depth_raw.replace("km", "").strip())
        else:
            depth_val = float(depth_raw)

        return [{
            "id": eq_id,
            "source": "bmkg",
            "magnitude": float(gempa.get("Magnitude", "0")),
            "location": gempa.get("Wilayah", "Unknown"),
            "latitude": lat,
            "longitude": lon,
            "depth": depth_val,
            "time": gempa.get("DateTime", ""),
            "tsunami": tsunami_flag,
            "url": "https://bmkg.go.id/gempabumi/",
        }]
    except Exception as e:
        logger.error("Error fetching BMKG: %s", e)
        return []


async def fetch_all(session: aiohttp.ClientSession) -> list:
    """Fetch dari semua sumber"""
    usgs = await fetch_usgs(session)
    bmkg = await fetch_bmkg(session)
    return usgs + bmkg