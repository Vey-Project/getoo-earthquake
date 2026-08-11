![](https://images5.alphacoders.com/119/thumb-1920-1198137.jpg)
# 🤖 Bot Notifikasi Gempa Discord

Bot otomatis 24/7 yang memantau gempa dari **USGS** (global) & **BMKG** (Indonesia), lalu mengirim notifikasi real-time ke channel Discord.

## ✨ Fitur

| Fitur | Status |
|-------|--------|
| ✅ Notifikasi otomatis tanpa diminta | ✅ |
| ✅ Sumber data: USGS (global) + BMKG (Indonesia) | ✅ |
| ✅ Filter magnitudo (bisa diatur per server) | ✅ |
| ✅ Filter wilayah (opsional) | ✅ |
| ✅ Anti-duplikat | ✅ |
| ✅ Gambar peta lokasi (Mapbox) | ✅ |
| ✅ Slash commands lengkap | ✅ |
| ✅ Multi-server | ✅ |
| ✅ Logging harian | ✅ |
| ✅ Siap deploy ke Railway/Fly.io | ✅ |

## 🚀 Cara Install & Jalankan

### 1. Clone / Download
```bash
cd getoo-earthquake
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment
```bash
cp .env.example .env
```
Edit `.env`:
```
DISCORD_TOKEN=token_bot_kamu_disini
MAPBOX_TOKEN=token_mapbox_kamu_disini
```

### 4. Jalankan
```bash
python main.py
```

## 🆕 Dapatkan Token

### Discord Bot Token
1. Buka [Discord Developer Portal](https://discord.com/developers/applications)
2. **New Application** → isi nama
3. **Bot** → **Add Bot** → **Reset Token** → copy token
4. **OAuth2 > URL Generator**:
   - Scopes: `bot` `applications.commands`
   - Permissions: `Send Messages` `Embed Links` `Attach Files` `Read Message History`
   - Buka URL, invite bot ke server

### Mapbox Token (untuk generate peta)
1. Daftar gratis di [mapbox.com](https://account.mapbox.com/)
2. Buat token di **Access tokens**
3. Opsional — bot tetap jalan tanpa peta

## 📋 Slash Commands

| Perintah | Fungsi |
|----------|--------|
| `/gempa` | Lihat 5 gempa terbaru (pilih untuk detail) |
| `/setchannel #channel` | Atur channel notifikasi |
| `/setmagnitude 5.0` | Atur magnitudo minimal |
| `/setwilayah Sukabumi` | Filter wilayah (ketik 'semua' untuk reset) |
| `/detail <id>` | Detail gempa spesifik |
| `/help` | Panduan lengkap |

## 🏗️ Struktur Proyek

```
bot-gempa/
├── main.py                 # Entry point
├── config.py               # Konfigurasi
├── .env                    # Token & secrets
├── requirements.txt        # Python dependencies
├── api/
│   ├── gempa.py            # Fetch USGS & BMKG
│   └── peta.py             # Generate peta Mapbox
├── commands/
│   ├── gempa.py            # /gempa
│   ├── setchannel.py       # /setchannel
│   ├── setmagnitude.py     # /setmagnitude
│   ├── setwilayah.py       # /setwilayah
│   ├── detail.py           # /detail
│   └── help.py             # /help
├── scheduler/
│   └── notifikasi.py       # Notifikasi otomatis
├── database/
│   ├── connection.py       # Koneksi SQLite
│   └── queries.py          # Query CRUD
├── utils/
│   ├── embed.py            # Format embed Discord
│   └── logger.py           # Logging
└── data/
    └── bot.db              # SQLite database (auto-generated)
```

## 🚀 Deploy ke Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template?template=https://github.com/yourusername/bot-gempa)

Atau manual:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Init project
railway init

# Set environment variables
railway env set DISCORD_TOKEN=your_token
railway env set MAPBOX_TOKEN=your_token

# Deploy
railway up
```

## ⚙️ Konfigurasi `.env`

| Variable | Default | Keterangan |
|----------|---------|------------|
| `DISCORD_TOKEN` | — | **Wajib.** Token bot Discord |
| `MAPBOX_TOKEN` | — | Opsional. Untuk generate peta |
| `CHECK_INTERVAL_MINUTES` | 2 | Interval cek gempa (menit) |
| `DEFAULT_MIN_MAGNITUDE` | 4.5 | Threshold magnitudo default |
| `DATABASE_PATH` | data/bot.db | Lokasi file database |
| `LOG_LEVEL` | INFO | Level logging |

## 🐳 Docker (Alternatif)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

## 📊 Logging

Log tersimpan di `logs/bot-YYYY-MM-DD.log` (rotasi harian).
