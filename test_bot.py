"""
test_bot.py - Smoke test fungsi murni (tanpa framework, tanpa network).
Jalan: python test_bot.py
"""
import datetime
import sys

sys.path.insert(0, ".")

from config import COLOR_DANGER, COLOR_INFO, COLOR_WARNING
from lib.embed import (
    build_earthquake_embed,
    format_magnitudo_badge,
    humanize_time,
    magnitudo_color,
)


def test_humanize_time_epoch_ke_wib():
    # 2025-08-24 01:46:40 UTC (+7h) = 08:46:40 WIB
    dt = datetime.datetime(2025, 8, 24, 1, 46, 40, tzinfo=datetime.timezone.utc)
    ts_ms = int(dt.timestamp() * 1000)
    assert humanize_time(ts_ms) == "24-Aug-2025 08:46:40 WIB", humanize_time(ts_ms)


def test_humanize_time_bmkg_passthrough():
    # Format WIB BMKG ditampilkan apa adanya
    assert humanize_time("11-Aug-26 14:32:10 WIB") == "11-Aug-26 14:32:10 WIB"


def test_humanize_time_iso():
    assert humanize_time("2025-08-24T08:46:40Z") == "24-Aug-2025 15:46:40 WIB"


def test_humanize_time_garbage():
    assert humanize_time(None) == "Unknown"
    assert humanize_time("bukan-waktu") == "bukan-waktu"


def test_badges():
    assert format_magnitudo_badge(7.2) == "🟥🔴"
    assert format_magnitudo_badge(6.1) == "🟧🟠"
    assert format_magnitudo_badge(5.0) == "🟨🟡"
    assert format_magnitudo_badge(4.0) == "🟩🟢"


def test_colors():
    assert magnitudo_color(6.5) == COLOR_DANGER
    assert magnitudo_color(5.5) == COLOR_WARNING
    assert magnitudo_color(4.0) == COLOR_INFO


def test_embed_fields():
    eq = {
        "id": "us7000abc", "source": "usgs", "magnitude": 5.4,
        "location": "Test Loc", "latitude": -6.5, "longitude": 107.1,
        "depth": 10, "time": None, "tsunami": 0, "url": "https://example.com",
    }
    e = build_earthquake_embed(eq)
    names = [f.name for f in e.fields]
    assert any("Lokasi" in n for n in names), names
    assert any("Koordinat" in n for n in names), names
    assert any("Kedalaman" in n for n in names), names
    assert any("Waktu" in n for n in names), names


def test_embed_depth_string_bmkg():
    # BMKG kirim kedalaman sebagai "10 km" — harus tetap tampil "10 km"
    eq = {"id": "bmkg-x", "source": "bmkg", "magnitude": 4.2, "location": "L",
          "latitude": -6.5, "longitude": 107.1, "depth": "10 km",
          "time": None, "tsunami": 0}
    e = build_earthquake_embed(eq)
    depth_field = next(f for f in e.fields if f.name.startswith("📏"))
    assert depth_field.value == "10 km", depth_field.value


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as err:
            failed += 1
            print(f"FAIL {fn.__name__}: {err}")
    print(f"{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
