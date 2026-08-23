"""
scheduler/notifikasi.py - Scheduler notifikasi gempa otomatis
"""
import logging
import os
import tempfile

import aiohttp
import discord

from api.gempa import fetch_all
from api.peta import generate_map
from database.queries import (
    get_all_active_servers, is_earthquake_sent, log_earthquake, prune_old_logs
)
from lib.embed import build_earthquake_embed, humanize_time

logger = logging.getLogger(__name__)


async def check_and_notify(bot: discord.Client):
    """Cek gempa baru dan kirim notifikasi ke semua server"""
    logger.info("Memeriksa gempa baru...")

    # Pruning log anti-duplikat (>90 hari) — murah, sekali per tick
    try:
        pruned = prune_old_logs(90)
        if pruned:
            logger.info("Pruned %s log gempa >90 hari", pruned)
    except Exception as e:
        logger.warning("Gagal pruning log: %s", e)

    async with aiohttp.ClientSession() as session:
        earthquakes = await fetch_all(session)

    if not earthquakes:
        logger.debug("Tidak ada data gempa")
        return

    # Urutkan dari yang terbaru
    earthquakes.sort(key=lambda x: x.get("time", 0) if isinstance(x.get("time"), (int, float)) else 0, reverse=True)

    # Ambil server aktif
    servers = get_all_active_servers()
    if not servers:
        logger.debug("Belum ada server yang mengatur channel")
        return

    for eq in earthquakes:
        eq_id = eq.get("id", "")
        source = eq.get("source", "usgs")
        mag = eq.get("magnitude", 0)

        if not eq_id:
            continue

        # Cek duplikat
        if is_earthquake_sent(eq_id, source):
            continue

        for server in servers:
            server_id = server.get("server_id")
            channel_id = server.get("channel_id")
            min_mag = server.get("min_magnitude", 4.5)
            region = server.get("region", "")

            if not channel_id:
                continue

            # Filter magnitudo
            if mag < min_mag:
                continue

            # Filter wilayah (parsial, case-insensitive)
            if region:
                loc = (eq.get("location", "") or "").lower()
                if region.lower() not in loc:
                    continue

            # Kirim notifikasi
            await send_notification(bot, server_id, channel_id, eq)

        # Tandai sudah dikirim
        log_earthquake(
            eq_id, source, mag,
            eq.get("location", ""),
            eq.get("latitude", 0),
            eq.get("longitude", 0),
            eq.get("depth", 0),
            str(eq.get("time", ""))
        )


async def send_notification(bot: discord.Client, server_id: str, channel_id: str, eq: dict):
    """Kirim notifikasi gempa ke channel"""
    try:
        channel = bot.get_channel(int(channel_id))
        if not channel:
            try:
                channel = await bot.fetch_channel(int(channel_id))
            except Exception:
                logger.warning("Channel %s tidak ditemukan untuk server %s", channel_id, server_id)
                return

        embed = build_earthquake_embed(eq)
        mag = eq.get("magnitude", 0)

        # Notifikasi text
        if mag >= 6.0:
            text = f"🔴 **GEMPA BESAR!** Magnitudo {mag} — {eq.get('location', 'Unknown')}"
        elif mag >= 5.0:
            text = f"🟠 **GEMPA** Magnitudo {mag} — {eq.get('location', 'Unknown')}"
        else:
            text = f"🟢 **Gempa** M{mag} — {eq.get('location', 'Unknown')}"

        # Generate peta (coba)
        map_file = None
        try:
            lat = eq.get("latitude", 0)
            lon = eq.get("longitude", 0)
            if lat and lon:
                map_file = await generate_map(lat, lon)
        except Exception as e:
            logger.warning("Gagal generate peta: %s", e)

        if map_file and os.path.exists(map_file):
            file = discord.File(map_file, filename="peta_gempa.png")
            embed.set_image(url="attachment://peta_gempa.png")
            await channel.send(content=text, embed=embed, file=file)
            # Cleanup
            try:
                os.remove(map_file)
            except Exception:
                pass
        else:
            await channel.send(content=text, embed=embed)

        logger.info("Notifikasi gempa %s M%s terkirim ke server %s", eq.get("id"), mag, server_id)

    except discord.Forbidden:
        logger.warning("Tidak punya izin kirim ke channel %s (server %s)", channel_id, server_id)
    except Exception as e:
        logger.error("Gagal kirim notifikasi ke %s: %s", channel_id, e)