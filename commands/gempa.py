"""
commands/gempa.py - Handler untuk /gempa
"""
import logging

import discord
from typing import Optional
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
            earthquakes.sort(key=lambda x: x.get("time", 0), reverse=True)
            top = earthquakes[:5]

            if len(top) == 1:
                eq = top[0]
                embed = build_earthquake_embed(eq)
                await interaction.followup.send(embed=embed)
                return

            # Multiple → pilih
            options = []
            for i, eq in enumerate(top[:5], 1):
                mag = eq.get("magnitude", 0)
                loc = eq.get("location", "Unknown")[:50]
                waktu = humanize_time(eq.get("time"))
                options.append(
                    discord.SelectOption(
                        label=f"M{mag} - {loc}",
                        description=waktu,
                        value=str(i)
                    )
                )

            view = EarthquakeSelectView(top, interaction.user.id)
            view.select_placeholder = "Pilih gempa untuk lihat detail..."
            view.select_options = options

            embed = discord.Embed(
                title="🌍 5 Gempa Terbaru",
                description="Silakan pilih gempa untuk melihat detail lengkap:",
                color=0x3498db
            )
            for i, eq in enumerate(top, 1):
                mag = eq.get("magnitude", 0)
                loc = eq.get("location", "Unknown")[:60]
                waktu = humanize_time(eq.get("time"))
                embed.add_field(
                    name=f"{i}. M{mag} - {loc}",
                    value=f"🕐 {waktu}",
                    inline=False
                )

            msg = await interaction.followup.send(embed=embed, view=view)
            view.message = msg

        except Exception as e:
            logger.error("Error /gempa: %s", e)
            await interaction.followup.send(f"❌ Gagal mengambil data: {str(e)[:100]}")


class EarthquakeSelectView(discord.ui.View):
    """Dropdown untuk memilih gempa dari daftar"""

    def __init__(self, earthquakes: list, user_id: int):
        super().__init__(timeout=120)
        self.earthquakes = earthquakes
        self.user_id = user_id
        self.select_placeholder = "Pilih gempa..."
        self.select_options = []
        self.message = None

    @discord.ui.select(placeholder="Pilih gempa...")
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Bukan perintah kamu!", ephemeral=True)
            return

        idx = int(select.values[0]) - 1
        if idx < 0 or idx >= len(self.earthquakes):
            await interaction.response.send_message("❌ Data tidak valid.", ephemeral=True)
            return

        eq = self.earthquakes[idx]
        embed = build_earthquake_embed(eq)
        await interaction.response.edit_message(embed=embed, view=None)

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(view=None)
            except Exception:
                pass