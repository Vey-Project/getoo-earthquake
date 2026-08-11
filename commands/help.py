"""
commands/help.py - Handler untuk /help
"""
import logging

import discord
from typing import Optional
from discord import app_commands

from lib.embed import build_help_embed

logger = logging.getLogger(__name__)


async def setup_help_command(tree: app_commands.CommandTree, guild=None):
    """Setup /help slash command"""

    @tree.command(
        name="help",
        description="📖 Tampilkan panduan lengkap bot gempa",
        guild=guild
    )
    async def help_slash(interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 Panduan Bot Gempa",
            description="Bot notifikasi gempa otomatis 24/7. Berikut perintah yang tersedia:",
            color=0x3498db
        )

        commands = [
            ("🌍 /gempa", "Lihat daftar 5 gempa terbaru"),
            ("🗺️ /peta <id>", "Lihat peta lokasi gempa"),
            ("🔍 /detail <id>", "Lihat detail lengkap gempa"),
            ("📊 /stats", "Statistik gempa 7 hari terakhir"),
            ("📢 /setchannel <#channel>", "Atur channel tujuan notifikasi"),
            ("📏 /setmagnitude <nilai>", "Atur magnitudo minimal (default 4.5)"),
            ("📍 /setwilayah <wilayah>", "Filter notifikasi per wilayah"),
            ("📋 /setwhere", "Lihat konfigurasi server saat ini"),
            ("📖 /help", "Tampilkan panduan ini"),
        ]

        for name, desc in commands:
            embed.add_field(name=f"`{name}`", value=desc, inline=False)

        embed.add_field(
            name="🤖 Notifikasi Otomatis",
            value="Bot akan mengirim notifikasi tanpa diminta ke channel yang sudah diatur.\n"
                  "Cek otomatis setiap **2 menit**.\n"
                  "Sumber: **USGS** (global) + **BMKG** (Indonesia)",
            inline=False
        )
        embed.set_footer(text="Bot Notifikasi Gempa • by @vey-6")
        await interaction.response.send_message(embed=embed, ephemeral=True)