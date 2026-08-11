"""
utils/embed.py - Format embed pesan untuk Discord
"""
import datetime
from typing import Optional

import discord

from config import COLOR_DANGER, COLOR_INFO, COLOR_WARNING


def magnitudo_color(mag: float) -> int:
    """Warna berdasarkan magnitudo"""
    if mag >= 6.0:
        return COLOR_DANGER
    elif mag >= 5.0:
        return COLOR_WARNING
    else:
        return COLOR_INFO


def format_magnitudo_badge(mag: float) -> str:
    """Badge emoji berdasarkan magnitudo"""
    if mag >= 7.0:
        return "🟥🔴"
    elif mag >= 6.0:
        return "🟧🟠"
    elif mag >= 5.0:
        return "🟨🟡"
    else:
        return "🟩🟢"


def humanize_time(ts: Optional[str]) -> str:
    """Format waktu ke WIB (UTC+7)"""
    try:
        if isinstance(ts, (int, float)):
            dt = datetime.datetime.utcfromtimestamp(ts / 1000)
        else:
            # BMKG format: "11-Aug-26 14:32:10 WIB" atau ISO
            if ts and "WIB" in ts:
                return ts.replace("WIB", "WIB")
            dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        dt = dt + datetime.timedelta(hours=7)  # UTC → WIB
        return dt.strftime("%d-%b-%Y %H:%M:%S WIB")
    except Exception:
        return ts or "Unknown"


def build_earthquake_embed(eq: dict) -> discord.Embed:
    """Buat embed notifikasi gempa"""
    mag = eq.get("magnitude", 0)
    source = eq.get("source", "usgs").upper()

    embed = discord.Embed(
        title=f"{format_magnitudo_badge(mag)} GEMPA BUMI MAGNITUDO {mag}",
        description=f"🔔 **Sumber: {source}**",
        color=magnitudo_color(mag),
        timestamp=datetime.datetime.utcnow()
    )

    embed.add_field(name="📍 Lokasi", value=eq.get("location", "Unknown"), inline=False)

    # Koordinat & kedalaman
    coord_text = f"{eq.get('latitude', 0):.4f}, {eq.get('longitude', 0):.4f}"
    embed.add_field(name="🗺️ Koordinat", value=coord_text, inline=True)

    depth = eq.get("depth", 0)
    if isinstance(depth, str):
        depth_clean = depth.replace("km", "").strip()
    else:
        depth_clean = depth
    embed.add_field(name="📏 Kedalaman", value=f"{depth_clean} km", inline=True)

    embed.add_field(name="🕐 Waktu", value=humanize_time(eq.get("time")), inline=False)

    # Info tsunami
    tsunami = eq.get("tsunami", 0)
    if tsunami and tsunami not in (0, "0", ""):
        embed.add_field(
            name="🌊 Peringatan Tsunami",
            value="⚠️ **BERPOTENSI TSUNAMI**" if tsunami not in (0, "0") else "Tidak ada",
            inline=False
        )

    if eq.get("url"):
        embed.add_field(name="🔗 Detail", value=eq["url"], inline=False)

    embed.set_footer(text="Bot Notifikasi Gempa • Data: USGS/BMKG")
    return embed


def build_help_embed() -> discord.Embed:
    """Embed untuk perintah /help"""
    embed = discord.Embed(
        title="📖 Panduan Bot Gempa",
        description="Bot notifikasi gempa otomatis 24/7. Berikut perintah yang tersedia:",
        color=COLOR_INFO
    )

    commands = [
        ("/gempa", "Lihat daftar gempa terbaru"),
        ("/setchannel <channel>", "Atur channel tujuan notifikasi"),
        ("/setmagnitude <nilai>", "Atur magnitudo minimal (default 4.5)"),
        ("/setwilayah <wilayah>", "Filter notifikasi per wilayah (opsional)"),
        ("/detail <id>", "Lihat detail gempa spesifik"),
        ("/peta <id>", "Lihat peta lokasi gempa"),
        ("/stats", "Statistik gempa minggu ini"),
        ("/help", "Tampilkan panduan ini"),
    ]

    for name, desc in commands:
        embed.add_field(name=f"`{name}`", value=desc, inline=False)

    embed.set_footer(text="Bot Notifikasi Gempa")
    return embed


def build_stats_embed(stats: dict) -> discord.Embed:
    """Embed statistik gempa"""
    embed = discord.Embed(
        title="📊 Statistik Gempa Minggu Ini",
        color=COLOR_INFO
    )
    embed.add_field(name="Total Gempa", value=stats.get("total", 0), inline=True)
    embed.add_field(name="Gempa ≥ 5.0", value=stats.get("significant", 0), inline=True)
    embed.add_field(name="Gempa ≥ 6.0", value=stats.get("major", 0), inline=True)
    embed.set_footer(text="Bot Notifikasi Gempa")
    return embed