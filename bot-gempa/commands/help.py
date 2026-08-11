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
        embed = build_help_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)