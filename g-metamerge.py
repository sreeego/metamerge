import json
import os
import sys
import subprocess
import shutil
import argparse
import tempfile
import re
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(
    encoding='utf-8',
    line_buffering=True
)

FFMPEG_BIN = os.environ.get("FFMPEG_PATH", "ffmpeg")
FFPROBE_BIN = os.environ.get("FFPROBE_PATH", "ffprobe")

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    print("⚠️ pillow-heif not installed, HEIC/HEIF files will be skipped", flush=True)

import piexif
from PIL import Image

SUPPORTED_EXIF  = {".jpg", ".jpeg", ".heic", ".heif", ".tiff", ".png", ".webp", ".bmp", ".gif"}
SUPPORTED_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".3gp", ".wmv"}
SUPPORTED       = SUPPORTED_EXIF | SUPPORTED_VIDEO


def find_sidecar(media_path: Path) -> Path | None:
    name = media_path.name
    original_name = name.replace("-edited", "") if "-edited" in name else name
    for f in media_path.parent.iterdir():
        if f.name.startswith(original_name) and f.suffix.lower() == ".json":
            return f
    return None


def parse_sidecar(json_path: Path) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    meta = {}
    ts = data.get("photoTakenTime", {}).get("timestamp")
    if ts:
        meta["datetime"] = datetime.fromtimestamp(int(ts), tz=timezone.utc)
    geo = data.get("geoDataExif") or data.get("geoData")
    if geo:
        lat = geo.get("latitude", 0.0)
        lon = geo.get("longitude", 0.0)
        if lat != 0.0 or lon != 0.0:
            meta["gps"] = {
                "lat": lat,
                "lon": lon,
                "alt": geo.get("altitude", 0.0)
            }
    return meta


def to_rational_tuple(value):
    value = abs(value)
    degrees = int(value)
    minutes = int((value - degrees) * 60)
    seconds = round((value - degrees - minutes / 60) * 3600 * 10000)
    return ((degrees, 1), (minutes, 1), (seconds, 10000))


def inspect_image(image_path: Path) -> dict:
    existing = {"datetime": False, "gps": False}
    try:
        img = Image.open(image_path)
        raw_exif = img.info.get("exif", b"")
        if not raw_exif:
            return existing

        exif_dict = piexif.load(raw_exif)

        if (exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal) or
                exif_dict["0th"].get(piexif.ImageIFD.DateTime)):
            existing["datetime"] = True

        gps = exif_dict.get("GPS", {})
        lat = gps.get(piexif.GPSIFD.GPSLatitude)
        lon = gps.get(piexif.GPSIFD.GPSLongitude)
        if lat and lon:
            def to_decimal(rational):
                d, m, s = rational
                return d[0]/d[1] + m[0]/m[1]/60 + s[0]/s[1]/3600
            if to_decimal(lat) != 0.0 or to_decimal(lon) != 0.0:
                existing["gps"] = True
    except Exception:
        pass
    return existing


def inspect_video(video_path: Path) -> dict:
    existing = {"datetime": False, "gps": False}
    try:
        result = subprocess.run(
            [FFPROBE_BIN, "-v", "quiet", "-print_format", "json", "-show_format", str(video_path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return existing
        data = json.loads(result.stdout)
        tags = data.get("format", {}).get("tags", {})

        if tags.get("creation_time"):
            existing["datetime"] = True

        loc = tags.get("location") or tags.get("location-eng")
        if loc:
            parts = re.findall(r"[+-]\d+\.\d+", loc.strip("/"))
            if len(parts) >= 2:
                if float(parts[0]) != 0.0 or float(parts[1]) != 0.0:
                    existing["gps"] = True
    except Exception:
        pass
    return existing


def format_log(wrote: list, skipped: list, no_data: list) -> str:
    parts = []
    if wrote:
        parts.append(f"wrote: {', '.join(wrote)}")
    if skipped:
        parts.append(f"skipped: {', '.join(skipped)}")
    if no_data:
        parts.append(f"no data: {', '.join(no_data)}")
    return ' | '.join(parts) if parts else 'nothing to do'


def embed_exif(image_path: Path, meta: dict, output_path: Path):
    img = Image.open(image_path)
    raw_exif = img.info.get("exif", b"")

    try:
        exif_dict = piexif.load(raw_exif)
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "Interop": {}}

    existing = inspect_image(image_path)
    wrote = []
    skipped = []
    no_data = []

    write_date = False
    write_gps = False

    if "datetime" in meta:
        if not existing["datetime"]:
            write_date = True
        else:
            skipped.append("date")
    else:
        no_data.append("date")

    if "gps" in meta:
        if not existing["gps"]:
            write_gps = True
        else:
            skipped.append("gps")
    else:
        no_data.append("gps")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not write_date and not write_gps:
        # Nothing to write — copy as-is, only fix filesystem date
        shutil.copy2(image_path, output_path)
        if "datetime" in meta:
            ts = meta["datetime"].timestamp()
            os.utime(output_path, (ts, ts))
        return wrote, skipped, no_data

    if write_date:
        dt_str = meta["datetime"].strftime("%Y:%m:%d %H:%M:%S").encode()
        exif_dict["0th"][piexif.ImageIFD.DateTime] = dt_str
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = dt_str
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = dt_str
        wrote.append("date")

    if write_gps:
        g = meta["gps"]
        exif_dict["GPS"] = {
            piexif.GPSIFD.GPSLatitudeRef: ("N" if g["lat"] >= 0 else "S").encode(),
            piexif.GPSIFD.GPSLatitude: to_rational_tuple(g["lat"]),
            piexif.GPSIFD.GPSLongitudeRef: ("E" if g["lon"] >= 0 else "W").encode(),
            piexif.GPSIFD.GPSLongitude: to_rational_tuple(g["lon"]),
            piexif.GPSIFD.GPSAltitudeRef: 0,
            piexif.GPSIFD.GPSAltitude: (int(abs(g["alt"]) * 100), 100),
        }
        wrote.append("gps")

    try:
        exif_bytes = piexif.dump(exif_dict)
    except Exception:
        exif_bytes = raw_exif

    img.save(output_path, exif=exif_bytes, quality=95)

    if "datetime" in meta:
        ts = meta["datetime"].timestamp()
        os.utime(output_path, (ts, ts))

    return wrote, skipped, no_data


def embed_video(video_path: Path, meta: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    existing = inspect_video(video_path)
    wrote = []
    skipped = []
    no_data = []

    write_date = False
    write_gps = False

    if "datetime" in meta:
        if not existing["datetime"]:
            write_date = True
        else:
            skipped.append("date")
    else:
        no_data.append("date")

    if "gps" in meta:
        if not existing["gps"]:
            write_gps = True
        else:
            skipped.append("gps")
    else:
        no_data.append("gps")

    if not write_date and not write_gps:
        shutil.copy2(video_path, output_path)
        if "datetime" in meta:
            ts = meta["datetime"].timestamp()
            os.utime(output_path, (ts, ts))
        return wrote, skipped, no_data

    temp_output = Path(tempfile.mktemp(suffix=video_path.suffix))

    cmd = [
        FFMPEG_BIN, "-nostdin", "-hide_banner", "-loglevel", "error",
        "-i", str(video_path),
        "-map_metadata", "0",
    ]

    if write_date:
        dt_str = meta["datetime"].strftime("%Y-%m-%dT%H:%M:%SZ")
        cmd += ["-metadata", f"creation_time={dt_str}"]
        wrote.append("date")

    if write_gps:
        g = meta["gps"]
        location = f"{g['lat']:+.4f}{g['lon']:+.4f}/"
        cmd += ["-metadata", f"location={location}"]
        cmd += ["-metadata", f"location-eng={location}"]
        cmd += ["-movflags", "use_metadata_tags"]
        wrote.append("gps")

    cmd += ["-c", "copy", "-y", str(temp_output)]

    result = subprocess.run(
        cmd, capture_output=True, text=True,
        stdin=subprocess.DEVNULL, timeout=120
    )

    if result.returncode != 0:
        raise Exception(result.stderr.strip() or "Unknown ffmpeg error")

    shutil.move(str(temp_output), str(output_path))

    if "datetime" in meta:
        ts = meta["datetime"].timestamp()
        os.utime(output_path, (ts, ts))

    return wrote, skipped, no_data


def delete_sidecar(sidecar: Path):
    try:
        if sidecar.exists():
            sidecar.unlink()
            print(f"🗑️ Deleted sidecar: {sidecar.name}", flush=True)
    except Exception as e:
        print(f"⚠️ Failed to delete sidecar {sidecar.name}: {str(e)}", flush=True)


def run(input_dir: str, output_dir: str, inplace=False):
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"❌ Input folder not found: {input_dir}", flush=True)
        return

    if not inplace:
        output_path = Path(output_dir) / (input_path.name + ".g-metamerge")

    ffmpeg_available = shutil.which(FFMPEG_BIN) is not None or Path(FFMPEG_BIN).exists()
    if not ffmpeg_available:
        print("⚠️ ffmpeg not found - video files will be skipped", flush=True)

    ffprobe_available = shutil.which(FFPROBE_BIN) is not None or Path(FFPROBE_BIN).exists()
    if not ffprobe_available:
        print("⚠️ ffprobe not found - video inspection disabled", flush=True)

    files = [p for p in input_path.rglob("*") if p.suffix.lower() in SUPPORTED]

    if not files:
        print("❌ No supported media files found", flush=True)
        return

    print(f"📂 Found {len(files)} supported files\n", flush=True)
    print(f"⚙️ Mode: {'In-place' if inplace else 'Standard'}\n", flush=True)

    merged = 0
    no_sidecar = 0
    errors = 0

    for index, media_file in enumerate(files, start=1):
        suffix = media_file.suffix.lower()

        print(f"[{index}/{len(files)}] {media_file.name}", flush=True)

        try:
            if suffix in SUPPORTED_VIDEO and not ffmpeg_available:
                print(f"⏭️ Skipped — ffmpeg not found", flush=True)
                continue

            sidecar = find_sidecar(media_file)

            if inplace:
                destination = media_file
            else:
                destination = output_path / media_file.relative_to(input_path)

            if not sidecar:
                if not inplace:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(media_file, destination)
                print(f"⚠️ No sidecar — copied as-is", flush=True)
                no_sidecar += 1
                continue

            meta = parse_sidecar(sidecar)

            if suffix in SUPPORTED_EXIF:
                wrote, skipped, no_data = embed_exif(media_file, meta, destination)
            elif suffix in SUPPORTED_VIDEO:
                wrote, skipped, no_data = embed_video(media_file, meta, destination)

            print(f"✅ {media_file.name} — {format_log(wrote, skipped, no_data)}", flush=True)
            merged += 1

            if inplace and sidecar:
                delete_sidecar(sidecar)

        except subprocess.TimeoutExpired:
            print(f"❌ {media_file.name} — ffmpeg timeout", flush=True)
            errors += 1

        except Exception as e:
            print(f"❌ {media_file.name} — {str(e)}", flush=True)
            errors += 1

    print(f"\n🏁 Done!\n", flush=True)
    print(f"✅ Merged:      {merged}", flush=True)
    print(f"⚠️ No sidecar:  {no_sidecar}", flush=True)
    print(f"❌ Errors:      {errors}", flush=True)

    if not inplace:
        print(f"\n📁 Output: {str(output_path)}", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="G-MetaMerge - restore metadata from Google Photos Takeout"
    )
    parser.add_argument("--input",   "-i", required=True, help="Google Takeout folder")
    parser.add_argument("--output",  "-o", default="",    help="Output folder")
    parser.add_argument("--inplace", action="store_true", help="Modify files directly and delete sidecars")

    args = parser.parse_args()
    run(args.input, args.output, args.inplace)


if __name__ == "__main__":
    main()