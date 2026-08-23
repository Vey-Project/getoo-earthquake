![](https://images5.alphacoders.com/119/thumb-1920-1198137.jpg)
# 🤖 Bot Notifikasi Gempa Discord

Bot otomatis 24/7 yang memantau gempa dari **USGS** (global) & **BMKG** (Indonesia), lalu mengirim notifikasi real-time ke channel Discord.

## ✨ Fitur

| Fitur | Status |
|-------|--------|
| Notifikasi otomatis (scheduler) | ✅ |
| Sumber data: USGS (global) + BMKG (Indonesia), fetch paralel | ✅ |
| Filter magnitudo per server | ✅ |
| Filter wilayah (opsional) | ✅ |
| Anti-duplikat (SQLite, `UNIQUE(earthquake_id, source)`) | ✅ |
| Gambar peta lokasi (Mapbox Static) | ✅ |
| Slash commands lengkap | ✅ |
| Multi-server | ✅ |
| Auto-pruning log (>90 hari) | ✅ |
| Logging harian | ✅ |

> 🔒 Command `/setchannel`, `/setmagnitude`, `/setwilayah`, `/unsetchannel` hanya untuk user dengan izin **Manage Server**.

## 🚀 Cara Install & Jalankan

```bash
pip install -r requirements.txt
cp .env.example .env   # isi DISCORD_TOKEN
python main.py
```

## 🔑 Dapatkan Token

### Discord Bot Token
1. Buka [Discord Developer Portal](https://discord.com/developers/applications)
2. **New Application** → isi nama
3. **Bot** → **Reset Token** → copy token
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
| `/gempa` | Lihat gempa terbaru |
| `/peta <id>` | Peta lokasi gempa |
| `/detail <id>` | Detail gempa spesifik |
| `/setchannel <channel>` | Atur channel notifikasi *(admin)* |
| `/setmagnitude <nilai>` | Atur magnitudo minimal *(admin)* |
| `/setwilayah <wilayah>` | Filter wilayah, ketik `semua` untuk reset *(admin)* |
| `/unsetchannel` | Matikan notifikasi server ini *(admin)* |
| `/setwhere` | Lihat konfigurasi server saat ini |
| `/stats` | Statistik gempa minggu ini |
| `/help` | Panduan lengkap |

## 🏗️ Struktur Proyek

```
getoo-earthquake/
├── main.py                 # Entry point
├── config.py               # Konfigurasi (.env)
├── requirements.txt        # Dependencies (pinned)
├── test_bot.py             # Smoke test (python test_bot.py)
├── api/
│   ├── gempa.py            # Fetch USGS & BMKG (paralel)
│   └── peta.py             # Generate peta Mapbox
├── commands/
│   ├── gempa.py            # /gempa
│   ├── peta.py             # /peta
│   ├── detail.py           # /detail
│   ├── stats.py            # /stats
│   ├── help.py             # /help
│   ├── setwhere.py         # /setwhere
│   ├── setchannel.py       # /setchannel      (admin)
│   ├── setmagnitude.py     # /setmagnitude    (admin)
│   ├── setwilayah.py       # /setwilayah      (admin)
│   └── unsetchannel.py     # /unsetchannel    (admin)
├── scheduler/
│   └── notifikasi.py       # Notifikasi otomatis + pruning log
├── database/
│   ├── connection.py       # Koneksi & schema SQLite
│   └── queries.py          # Query CRUD
├── lib/
│   ├── embed.py            # Format embed Discord
│   └── logger.py           # Logging harian
└── data/
    └── bot.db              # SQLite (auto-generated)
```

## 🚂 Deploy ke Railway

```bash
npm i -g @railway/cli
railway login
railway init
railway variables --set "DISCORD_TOKEN=xxx MAPBOX_TOKEN=xxx"
railway up
```

### ⚠️ Wajib: pasang Volume

Filesystem container Railway **ephemeral** — tanpa volume, `data/bot.db` hilang tiap redeploy dan riwayat anti-duplikat ikut hilang (notifikasi bisa terkirim ulang).

1. Dashboard project → **Settings** → **Volumes** → **New Volume**
2. Mount point: `/app/data`
3. Redeploy

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

```bash
docker compose up -d --build
```

## 🧪 Test

```bash
python test_bot.py
```

## 📊 Logging

Log tersimpan di `logs/bot-YYYY-MM-DD.log` (rotasi harian).
