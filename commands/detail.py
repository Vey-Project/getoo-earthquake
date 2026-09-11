"""
commands/detail.py - Handler untuk /detail (opsional)
"""
import logging

import discord
from typing import Optional
from discord import app_commands

import api.gempa as gempa_api
from lib.embed import build_earthquake_embed

logger = logging.getLogger(__name__)


async def setup_detail_command(tree: app_commands.CommandTree, guild=None):
    """Setup /detail slash command"""

    @tree.command(
        name="detail",
        description="🔍 Lihat detail gempa berdasarkan ID",
        guild=guild
    )
    @app_commands.describe(earthquake_id="ID gempa dari daftar /gempa")
    async def detail_slash(interaction: discord.Interaction, earthquake_id: str):
        await interaction.response.defer(ephemeral=True)

        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                earthquakes = await gempa_api.fetch_usgs(session)
                earthquakes.extend(await gempa_api.fetch_bmkg(session))

            eq = None
            for e in earthquakes:
                if e.get("id") and earthquake_id.lower() in e["id"].lower():
                    eq = e
                    break

            if not eq:
                await interaction.followup.send(
                    f"❌ Gempa dengan ID '{earthquake_id}' tidak ditemukan.",
                    ephemeral=True
                )
                return

            embed = build_earthquake_embed(eq)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error("Error /detail: %s", e)
            await interaction.followup.send(f"❌ Error: {str(e)[:100]}", ephemeral=True)
