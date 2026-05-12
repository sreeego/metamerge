import json
import os
import subprocess
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timezone

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    print("⚠️  pillow-heif not installed, HEIC/HEIF files will be skipped")

import piexif
from PIL import Image

SUPPORTED_EXIF  = {".jpg", ".jpeg", ".heic", ".heif", ".tiff", ".png", ".webp", ".bmp", ".gif"}
SUPPORTED_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".3gp", ".wmv"}
SUPPORTED       = SUPPORTED_EXIF | SUPPORTED_VIDEO


def find_sidecar(image_path: Path) -> Path | None:
    name = image_path.name
    original_name = name.replace("-edited", "") if "-edited" in name else name
    for f in image_path.parent.iterdir():
        if f.name.startswith(original_name) and f.suffix == ".json":
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
    if geo and (geo.get("latitude") != 0.0 or geo.get("longitude") != 0.0):
        meta["gps"] = {
            "lat": geo["latitude"],
            "lon": geo["longitude"],
            "alt": geo.get("altitude", 0.0)
        }
    return meta


def to_rational_tuple(val):
    val = abs(val)
    d = int(val)
    m = int((val - d) * 60)
    s = round((val - d - m / 60) * 3600 * 10000)
    return ((d, 1), (m, 1), (s, 10000))


def embed_exif(image_path: Path, meta: dict, output_path: Path):
    img = Image.open(image_path)
    exif = img.getexif()

    if "datetime" in meta:
        dt_str = meta["datetime"].strftime("%Y:%m:%d %H:%M:%S")
        exif[0x0132] = dt_str
        exif[0x9003] = dt_str
        exif[0x9004] = dt_str

    if "gps" in meta:
        g = meta["gps"]
        gps_ifd = {
            1: "N" if g["lat"] >= 0 else "S",
            2: to_rational_tuple(g["lat"]),
            3: "E" if g["lon"] >= 0 else "W",
            4: to_rational_tuple(g["lon"]),
            5: 0,
            6: (int(abs(g["alt"]) * 100), 100),
        }
        exif[0x8825] = piexif.dump({"GPS": gps_ifd})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, exif=exif.tobytes(), quality=95)

    if "datetime" in meta:
        ts = meta["datetime"].timestamp()
        os.utime(output_path, (ts, ts))


def embed_video(video_path: Path, meta: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dt_str = meta["datetime"].strftime("%Y-%m-%dT%H:%M:%SZ")
    
    cmd = ["ffmpeg", "-i", str(video_path)]
    
    cmd += ["-metadata", f"creation_time={dt_str}"]
    
    if "gps" in meta:
        g = meta["gps"]
        lat = g["lat"]
        lon = g["lon"]
        # ISO 6709 format: +DD.DDDD+DDD.DDDD/
        location = f"{lat:+.4f}{lon:+.4f}/"
        cmd += ["-metadata", f"location={location}"]
        cmd += ["-metadata", f"location-eng={location}"]
        cmd += ["-movflags", "use_metadata_tags"]

    cmd += ["-c", "copy", "-y", str(output_path)]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(result.stderr.splitlines()[-1])
    if "datetime" in meta:
        ts = meta["datetime"].timestamp()
        os.utime(output_path, (ts, ts))


def run(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        print(f"❌ Input folder not found: {input_dir}")
        return

    # Check ffmpeg availability
    ffmpeg_available = shutil.which("ffmpeg") is not None
    if not ffmpeg_available:
        print("⚠️  ffmpeg not found — video files will be skipped")
        print("   Download: https://ffmpeg.org/download.html\n")

    files = [p for p in input_path.rglob("*") if p.suffix.lower() in SUPPORTED]

    if not files:
        print("No supported files found.")
        return

    ok, no_sidecar, errors = 0, 0, 0

    for f in files:
        suffix = f.suffix.lower()

        if suffix in SUPPORTED_VIDEO and not ffmpeg_available:
            print(f"⏭️  {f.name}  →  skipped, ffmpeg not found")
            continue

        sidecar = find_sidecar(f)
        dest = output_path / f.relative_to(input_path)

        if not sidecar:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            print(f"⚠️  {f.name}  →  copied, no sidecar")
            no_sidecar += 1
            continue

        try:
            meta = parse_sidecar(sidecar)

            if suffix in SUPPORTED_EXIF:
                embed_exif(f, meta, dest)
                print(f"✅ {f.name}")
            elif suffix in SUPPORTED_VIDEO:
                embed_video(f, meta, dest)
                print(f"✅ {f.name}")

            ok += 1
        except Exception as e:
            print(f"❌ {f.name}  →  {e}")
            errors += 1

    print(f"""
Done!
  Merged:     {ok}
  No sidecar: {no_sidecar} (copied as-is)
  Errors:     {errors}
  Output:     {output_dir}
""")


def main():
    parser = argparse.ArgumentParser(
        description="metamerge — embed Google Takeout metadata back into your photos and videos"
    )
    parser.add_argument("--input",  "-i", required=True, help="Google Takeout Google Photos folder")
    parser.add_argument("--output", "-o", required=True, help="Output folder")
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == "__main__":
    main()