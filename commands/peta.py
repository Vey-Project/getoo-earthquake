"""
commands/peta.py - Handler untuk /peta — generate & kirim peta lokasi gempa
"""
import logging
import os

import discord
from discord import app_commands

import api.gempa as gempa_api
from api.peta import generate_map

logger = logging.getLogger(__name__)


async def setup_peta_command(tree: app_commands.CommandTree, guild=None):
    """Setup /peta slash command"""

    @tree.command(
        name="peta",
        description="🗺️ Lihat peta lokasi gempa berdasarkan ID",
        guild=guild
    )
    @app_commands.describe(earthquake_id="ID gempa (contoh: us7000abc)")
    async def peta_slash(interaction: discord.Interaction, earthquake_id: str):
        if not earthquake_id:
            await interaction.response.send_message("❌ Masukkan ID gempa. Contoh: `/peta us7000abc`", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                earthquakes = await gempa_api.fetch_usgs(session)
                bmkg = await gempa_api.fetch_bmkg(session)
                earthquakes.extend(bmkg)

            eq = None
            for e in earthquakes:
                if e.get("id") and earthquake_id.lower() in e["id"].lower():
                    eq = e
                    break

            if not eq:
                await interaction.followup.send(
                    f"❌ Gempa dengan ID '{earthquake_id}' tidak ditemukan.\n"
                    f"Gunakan `/gempa` untuk melihat daftar ID gempa terbaru."
                )
                return

            lat = eq.get("latitude", 0)
            lon = eq.get("longitude", 0)
            loc = eq.get("location", "Unknown")
            mag = eq.get("magnitude", 0)

            if not lat or not lon:
                await interaction.followup.send("❌ Gempa ini tidak memiliki data koordinat.")
                return

            # Generate peta
            map_file = await generate_map(lat, lon)

            embed = discord.Embed(
                title=f"🗺️ Peta Lokasi Gempa M{mag}",
                description=f"📍 {loc}\n🌐 {lat:.4f}, {lon:.4f}",
                color=0x3498db
            )

            if map_file and os.path.exists(map_file):
                file = discord.File(map_file, filename="peta_gempa.png")
                embed.set_image(url="attachment://peta_gempa.png")
                embed.set_footer(text="Mapbox • Sumber: USGS/BMKG")
                await interaction.followup.send(embed=embed, file=file)
                try:
                    os.remove(map_file)
                except Exception:
                    pass
            else:
                embed.add_field(name="ℹ️", value="Peta tidak tersedia (MAPBOX_TOKEN belum diisi)", inline=False)
                embed.set_footer(text="Daftar gratis di mapbox.com untuk mengaktifkan peta")
                await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error("Error /peta: %s", e)
            await interaction.followup.send(f"❌ Gagal generate peta: {str(e)[:100]}")