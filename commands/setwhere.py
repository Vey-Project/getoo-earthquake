"""
commands/setwhere.py - Handler untuk /setwhere — cek konfigurasi server saat ini
"""
import logging

import discord
from discord import app_commands

from database.queries import get_server_config

logger = logging.getLogger(__name__)


async def setup_setwhere_command(tree: app_commands.CommandTree, guild=None):
    """Setup /setwhere slash command"""

    @tree.command(
        name="setwhere",
        description="📋 Lihat konfigurasi notifikasi server saat ini",
        guild=guild
    )
    async def setwhere_slash(interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ Perintah ini hanya bisa di server.", ephemeral=True)
            return

        config = get_server_config(str(interaction.guild_id))

        if not config:
            embed = discord.Embed(
                title="📋 Konfigurasi Server",
                description="Server ini **belum dikonfigurasi**.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Langkah", value="1. `/setchannel #channel` — atur channel notifikasi\n2. `/setmagnitude 5.0` — atur threshold (opsional)\n3. `/setwilayah sukabumi` — filter wilayah (opsional)")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        channel_id = config.get("channel_id")
        channel_mention = f"<#{channel_id}>" if channel_id else "❌ Belum diatur"

        embed = discord.Embed(
            title="📋 Konfigurasi Server",
            description=f"**{interaction.guild.name}**",
            color=discord.Color.green()
        )
        embed.add_field(name="📢 Channel Notifikasi", value=channel_mention, inline=False)
        embed.add_field(name="📏 Magnitudo Minimal", value=f"M {config.get('min_magnitude', 4.5)}", inline=True)
        embed.add_field(name="📍 Filter Wilayah", value=config.get("region") or "Semua wilayah", inline=True)
        embed.add_field(name="🌐 Bahasa", value=config.get("language", "id"), inline=True)
        embed.set_footer(text="Gunakan /setchannel, /setmagnitude, /setwilayah untuk mengubah")

        await interaction.response.send_message(embed=embed, ephemeral=True)