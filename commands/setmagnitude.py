"""
commands/setmagnitude.py - Handler untuk /setmagnitude
"""
import logging

import discord
from typing import Optional
from discord import app_commands

from database.queries import set_server_magnitude, get_server_config

logger = logging.getLogger(__name__)


async def setup_setmagnitude_command(tree: app_commands.CommandTree, guild=None):
    """Setup /setmagnitude slash command"""

    @tree.command(
        name="setmagnitude",
        description="📏 Atur magnitudo minimal untuk notifikasi (default 4.5)",
        guild=guild
    )
    @app_commands.describe(magnitude="Nilai magnitudo minimal (contoh: 5.0)")
    async def setmagnitude_slash(interaction: discord.Interaction, magnitude: app_commands.Range[float, 0.0, 10.0]):
        if not interaction.guild:
            await interaction.response.send_message("❌ Perintah ini hanya bisa di server.", ephemeral=True)
            return

        set_server_magnitude(str(interaction.guild_id), magnitude)

        config = get_server_config(str(interaction.guild_id))
        channel_mention = f"<#{config['channel_id']}>" if config and config.get('channel_id') else "Belum diatur"

        embed = discord.Embed(
            title="📏 Magnitudo Minimal Diperbarui",
            description=f"Notifikasi hanya akan dikirim untuk gempa **≥ M{magnitude}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Nilai Baru", value=f"M {magnitude}")
        embed.add_field(name="Channel Notifikasi", value=channel_mention)
        embed.set_footer(text="Gunakan /setchannel untuk atur channel")

        await interaction.response.send_message(embed=embed, ephemeral=True)