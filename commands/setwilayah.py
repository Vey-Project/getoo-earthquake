"""
commands/setwilayah.py - Handler untuk /setwilayah (opsional)
"""
import logging

import discord
from typing import Optional
from discord import app_commands

from database.queries import set_server_region, get_server_config

logger = logging.getLogger(__name__)


async def setup_setwilayah_command(tree: app_commands.CommandTree, guild=None):
    """Setup /setwilayah slash command"""

    @tree.command(
        name="setwilayah",
        description="📍 Filter notifikasi hanya untuk wilayah tertentu (ketik 'semua' untuk reset)",
        guild=guild
    )
    @app_commands.describe(wilayah="Nama wilayah/kota (contoh: Sukabumi, atau 'semua' untuk reset)")
    async def setwilayah_slash(interaction: discord.Interaction, wilayah: str):
        if not interaction.guild:
            await interaction.response.send_message("❌ Perintah ini hanya bisa di server.", ephemeral=True)
            return

        if wilayah.lower() in ("semua", "all", "reset", "-"):
            set_server_region(str(interaction.guild_id), "")
            embed = discord.Embed(
                title="🌍 Filter Wilayah Dihapus",
                description="Notifikasi akan dikirim untuk **semua wilayah**",
                color=discord.Color.green()
            )
        else:
            set_server_region(str(interaction.guild_id), wilayah.strip())
            embed = discord.Embed(
                title="📍 Filter Wilayah Diatur",
                description=f"Notifikasi hanya untuk gempa yang mengandung kata **{wilayah.strip()}**",
                color=discord.Color.green()
            )
            embed.set_footer(text="Filter bersifat parsial (case-insensitive)")

        await interaction.response.send_message(embed=embed, ephemeral=True)