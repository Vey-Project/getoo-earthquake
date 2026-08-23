"""
commands/setchannel.py - Handler untuk /setchannel
"""
import logging

import discord
from typing import Optional
from discord import app_commands

from database.queries import set_server_channel

logger = logging.getLogger(__name__)


async def setup_setchannel_command(tree: app_commands.CommandTree, guild=None):
    """Setup /setchannel slash command"""

    @tree.command(
        name="setchannel",
        description="📢 Atur channel tujuan notifikasi gempa",
        guild=guild
    )
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(channel="Channel untuk notifikasi (contoh: #gempa-alert)")
    async def setchannel_slash(interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.guild:
            await interaction.response.send_message("❌ Perintah ini hanya bisa di server.", ephemeral=True)
            return

        if not interaction.permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Perintah ini khusus admin (butuh izin **Manage Server**).",
                ephemeral=True
            )
            return

        # Cek permission
        me = interaction.guild.me
        channel_perms = channel.permissions_for(me)
        if not channel_perms.send_messages:
            await interaction.response.send_message(
                f"❌ Saya tidak punya izin **Send Messages** di {channel.mention}.",
                ephemeral=True
            )
            return
        if not channel_perms.embed_links:
            await interaction.response.send_message(
                f"⚠️ Saya tidak punya izin **Embed Links** di {channel.mention}. Notifikasi akan tanpa embed.",
                ephemeral=True
            )

        set_server_channel(str(interaction.guild_id), str(channel.id))

        embed = discord.Embed(
            title="✅ Channel Notifikasi Diatur",
            description=f"Notifikasi gempa akan dikirim ke {channel.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="Server", value=interaction.guild.name)
        embed.add_field(name="Channel", value=channel.mention)
        embed.set_footer(text="Gunakan /setmagnitude untuk atur threshold")

        await interaction.response.send_message(embed=embed, ephemeral=True)