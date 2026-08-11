"""
commands/gempa.py - Handler untuk /gempa — versi stabil tanpa dropdown
"""
import logging

import discord
from discord import app_commands

import api.gempa as gempa_api
from lib.embed import build_earthquake_embed, humanize_time

logger = logging.getLogger(__name__)


async def setup_gempa_command(tree: app_commands.CommandTree, guild=None):
    """Setup /gempa slash command"""

    @tree.command(
        name="gempa",
        description="🌍 Lihat daftar gempa terbaru",
        guild=guild
    )
    async def gempa_slash(interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                earthquakes = await gempa_api.fetch_usgs(session)

            if not earthquakes:
                await interaction.followup.send("❌ Tidak ada data gempa saat ini.")
                return

            # Urutkan dari terbaru
            earthquakes.sort(key=lambda x: x.get("time", 0) if isinstance(x.get("time"), (int, float)) else 0, reverse=True)
            top = earthquakes[:5]

            if len(top) == 1:
                embed = build_earthquake_embed(top[0])
                await interaction.followup.send(embed=embed)
                return

            # Tampilkan sebagai list embed biasa (tanpa dropdown)
            embed = discord.Embed(
                title="🌍 5 Gempa Terbaru",
                description="Gunakan `/detail <id>` untuk info lengkap",
                color=0x3498db
            )

            for i, eq in enumerate(top, 1):
                mag = eq.get("magnitude", 0)
                loc = (eq.get("location", "Unknown") or "Unknown")[:60]
                waktu = humanize_time(eq.get("time"))
                eq_id = eq.get("id", "-")[:20]
                embed.add_field(
                    name=f"{'🟥' if mag >= 6 else '🟧' if mag >= 5 else '🟩'} M{mag} — {loc}",
                    value=f"🕐 {waktu}\n`ID: {eq_id}`",
                    inline=False
                )

            embed.set_footer(text="Bot Notifikasi Gempa • Data: USGS/BMKG")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error("Error /gempa: %s", e)
            await interaction.followup.send(f"❌ Gagal mengambil data: {str(e)[:100]}")