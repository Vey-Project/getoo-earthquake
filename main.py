"""
main.py - Entry point Bot Notifikasi Gempa

Cara jalanin:
  1. Copy .env.example → .env, isi token
  2. pip install -r requirements.txt
  3. python main.py
"""
import asyncio
import logging
import os
import signal
import sys
import platform

import discord
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import DISCORD_TOKEN, CHECK_INTERVAL_MINUTES, DATABASE_PATH, MAPBOX_TOKEN
from database.connection import init_database
from lib.logger import setup_logger

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)


class EarthquakeBot(discord.Client):
    """Bot Discord untuk notifikasi gempa"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.scheduler = AsyncIOScheduler()
        self.guild = None

    async def setup_hook(self):
        """Setup saat bot siap"""
        # Inisialisasi database
        init_database()
        logger.info("Database initialized")

        # Register commands
        from commands.help import setup_help_command
        from commands.gempa import setup_gempa_command
        from commands.setchannel import setup_setchannel_command
        from commands.setmagnitude import setup_setmagnitude_command
        from commands.setwilayah import setup_setwilayah_command
        from commands.detail import setup_detail_command
        from commands.peta import setup_peta_command
        from commands.stats import setup_stats_command
        from commands.unsetchannel import setup_unsetchannel_command
        from commands.setwhere import setup_setwhere_command

        # Coba daftar global dulu, fallback ke guild
        try:
            await setup_help_command(self.tree)
            await setup_gempa_command(self.tree)
            await setup_setchannel_command(self.tree)
            await setup_setmagnitude_command(self.tree)
            await setup_setwilayah_command(self.tree)
            await setup_detail_command(self.tree)
            await setup_peta_command(self.tree)
            await setup_stats_command(self.tree)
            await setup_unsetchannel_command(self.tree)
            await setup_setwhere_command(self.tree)
            await self.tree.sync()
            logger.info("Global commands registered")
        except Exception as e:
            logger.warning("Gagal sync global commands: %s, coba per-guild...", e)
            # Fallback: sync per guild yang sudah ada
            for guild in self.guilds:
                try:
                    g = discord.Object(id=guild.id)
                    await setup_help_command(self.tree, g)
                    await setup_gempa_command(self.tree, g)
                    await setup_setchannel_command(self.tree, g)
                    await setup_setmagnitude_command(self.tree, g)
                    await setup_setwilayah_command(self.tree, g)
                    await setup_detail_command(self.tree, g)
                    await setup_peta_command(self.tree, g)
                    await setup_stats_command(self.tree, g)
                    await setup_unsetchannel_command(self.tree, g)
                    await setup_setwhere_command(self.tree, g)
                    await self.tree.sync(guild=g)
                    logger.info("Commands synced for guild %s", guild.id)
                except Exception as guild_err:
                    logger.error("Gagal sync guild %s: %s", guild.id, guild_err)

        # Setup scheduler untuk notifikasi otomatis
        self.setup_scheduler()

        logger.info("Bot setup complete")

    def setup_scheduler(self):
        """Setup APScheduler untuk cek gempa berkala"""
        from scheduler.notifikasi import check_and_notify

        self.scheduler.add_job(
            check_and_notify,
            trigger='interval',
            minutes=CHECK_INTERVAL_MINUTES,
            args=[self],
            id='check_earthquake',
            name='Cek gempa baru',
            replace_existing=True,
            misfire_grace_time=60
        )
        self.scheduler.start()
        logger.info("Scheduler started: cek setiap %s menit", CHECK_INTERVAL_MINUTES)

    async def on_ready(self):
        logger.info("=" * 50)
        logger.info("Bot Gempa Aktif!")
        logger.info("User: %s", self.user)
        logger.info("ID: %s", self.user.id)
        logger.info("Server: %s", [g.name for g in self.guilds])
        logger.info("Interval: %s menit", CHECK_INTERVAL_MINUTES)
        logger.info("=" * 50)

        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"🌍 gempa | /help"
            )
        )

    async def on_guild_join(self, guild):
        """Bot masuk server baru - coba sync commands"""
        logger.info("Masuk server baru: %s (%s)", guild.name, guild.id)
        try:
            g = discord.Object(id=guild.id)
            from commands.help import setup_help_command
            from commands.gempa import setup_gempa_command
            from commands.setchannel import setup_setchannel_command
            from commands.setmagnitude import setup_setmagnitude_command
            from commands.setwilayah import setup_setwilayah_command
            from commands.detail import setup_detail_command
            from commands.peta import setup_peta_command
            from commands.stats import setup_stats_command
            from commands.unsetchannel import setup_unsetchannel_command
            from commands.setwhere import setup_setwhere_command
            await setup_help_command(self.tree, g)
            await setup_gempa_command(self.tree, g)
            await setup_setchannel_command(self.tree, g)
            await setup_setmagnitude_command(self.tree, g)
            await setup_setwilayah_command(self.tree, g)
            await setup_detail_command(self.tree, g)
            await setup_peta_command(self.tree, g)
            await setup_stats_command(self.tree, g)
            await setup_unsetchannel_command(self.tree, g)
            await setup_setwhere_command(self.tree, g)
            await self.tree.sync(guild=g)
            logger.info("Commands synced for new guild %s", guild.id)
        except Exception as e:
            logger.error("Gagal sync guild baru %s: %s", guild.id, e)

    async def on_error(self, event_method, *args, **kwargs):
        logger.error("Error in %s: %s", event_method, sys.exc_info())


async def main():
    """Main entry point"""
    missing = []
    if not DISCORD_TOKEN:
        missing.append("DISCORD_TOKEN")
    if not DATABASE_PATH:
        missing.append("DATABASE_PATH")
    if missing:
        logger.error("❌ Env var required but missing: %s", ", ".join(missing))
        logger.error("   Copy .env.example → .env, lalu isi kredensial yang dibutuhkan.")
        return

    if not MAPBOX_TOKEN:
        logger.warning("⚠️ MAPBOX_TOKEN kosong, fitur peta tidak akan aktif.")

    bot = EarthquakeBot()

    # Handle shutdown
    async def shutdown():
        logger.info("Shutting down bot...")
        bot.scheduler.shutdown(wait=False)
        await bot.close()

    # Signal handlers
    def signal_handler():
        asyncio.create_task(shutdown())

    try:
        if platform.system() != "Windows":
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                try:
                    loop.add_signal_handler(sig, signal_handler)
                except NotImplementedError:
                    pass

        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        await shutdown()
    except Exception as e:
        logger.error("Fatal error: %s", e)
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main())