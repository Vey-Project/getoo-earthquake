"""
commands/stats.py - Handler untuk /stats — statistik gempa minggu ini (dari USGS)
"""
import logging

import discord
from discord import app_commands

import api.gempa as gempa_api
from lib.embed import build_stats_embed

logger = logging.getLogger(__name__)

USGS_WEEK_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson"


async def setup_stats_command(tree: app_commands.CommandTree, guild=None):
    """Setup /stats slash command"""

    @tree.command(
        name="stats",
        description="📊 Statistik gempa minggu ini",
        guild=guild
    )
    async def stats_slash(interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(USGS_WEEK_URL, timeout=15) as resp:
                    if resp.status != 200:
                        await interaction.followup.send("❌ Gagal mengambil data statistik.")
                        return
                    data = await resp.json()

            features = data.get("features", [])
            total = len(features)
            significant = 0
            major = 0

            for feat in features:
                mag = feat.get("properties", {}).get("mag", 0) or 0
                if mag >= 5.0:
                    significant += 1
                if mag >= 6.0:
                    major += 1

            stats = {
                "total": total,
                "significant": significant,
                "major": major,
            }

            embed = discord.Embed(
                title="📊 Statistik Gempa 7 Hari Terakhir",
                description="Data global (USGS)",
                color=0x3498db
            )
            embed.add_field(name="Total Gempa", value=total, inline=True)
            embed.add_field(name="Gempa ≥ M5.0", value=significant, inline=True)
            embed.add_field(name="Gempa ≥ M6.0", value=major, inline=True)
            embed.set_footer(text="Bot Notifikasi Gempa • USGS")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error("Error /stats: %s", e)
            await interaction.followup.send(f"❌ Gagal mengambil statistik: {str(e)[:100]}")