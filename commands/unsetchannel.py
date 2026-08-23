"""
commands/unsetchannel.py - Handler untuk /unsetchannel — matikan notifikasi server
"""
import logging

import discord
from discord import app_commands

from database.queries import delete_server_config

logger = logging.getLogger(__name__)


async def setup_unsetchannel_command(tree: app_commands.CommandTree, guild=None):
    """Setup /unsetchannel slash command"""

    @tree.command(
        name="unsetchannel",
        description="🔇 Matikan notifikasi gempa untuk server ini",
        guild=guild
    )
    @app_commands.default_permissions(manage_guild=True)
    async def unsetchannel_slash(interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ Perintah ini hanya bisa di server.", ephemeral=True)
            return

        if not interaction.permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Perintah ini khusus admin (butuh izin **Manage Server**).",
                ephemeral=True
            )
            return

        delete_server_config(str(interaction.guild_id))

        embed = discord.Embed(
            title="🔇 Notifikasi Dimatikan",
            description=(
                "Notifikasi gempa tidak akan dikirim lagi ke server ini.\n"
                "Atur ulang kapan saja dengan `/setchannel`."
            ),
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
