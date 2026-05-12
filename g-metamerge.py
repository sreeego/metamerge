# metamerge.py

import json
import os
import sys
import subprocess
import shutil
import argparse
import tempfile
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(
    encoding='utf-8',
    line_buffering=True
)

FFMPEG_BIN = os.environ.get(
    "FFMPEG_PATH",
    "ffmpeg"
)

try:
    import pillow_heif
    pillow_heif.register_heif_opener()

except ImportError:
    print(
        "⚠️ pillow-heif not installed, HEIC/HEIF files will be skipped",
        flush=True
    )

import piexif
from PIL import Image

SUPPORTED_EXIF = {
    ".jpg",
    ".jpeg",
    ".heic",
    ".heif",
    ".tiff",
    ".png",
    ".webp",
    ".bmp",
    ".gif",
}

SUPPORTED_VIDEO = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".3gp",
    ".wmv",
}

SUPPORTED = SUPPORTED_EXIF | SUPPORTED_VIDEO


def find_sidecar(media_path: Path) -> Path | None:
    name = media_path.name

    original_name = (
        name.replace("-edited", "")
        if "-edited" in name
        else name
    )

    for f in media_path.parent.iterdir():
        if (
            f.name.startswith(original_name)
            and f.suffix.lower() == ".json"
        ):
            return f

    return None


def parse_sidecar(json_path: Path) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = {}

    ts = data.get("photoTakenTime", {}).get("timestamp")

    if ts:
        meta["datetime"] = datetime.fromtimestamp(
            int(ts),
            tz=timezone.utc
        )

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

    seconds = round(
        (value - degrees - minutes / 60) * 3600 * 10000
    )

    return (
        (degrees, 1),
        (minutes, 1),
        (seconds, 10000)
    )


def embed_exif(image_path: Path, meta: dict, output_path: Path):
    img = Image.open(image_path)

    exif = img.getexif()

    if "datetime" in meta:
        dt_str = meta["datetime"].strftime(
            "%Y:%m:%d %H:%M:%S"
        )

        exif[0x0132] = dt_str
        exif[0x9003] = dt_str
        exif[0x9004] = dt_str

    if "gps" in meta:
        gps = meta["gps"]

        gps_ifd = {
            1: "N" if gps["lat"] >= 0 else "S",
            2: to_rational_tuple(gps["lat"]),
            3: "E" if gps["lon"] >= 0 else "W",
            4: to_rational_tuple(gps["lon"]),
            5: 0,
            6: (
                int(abs(gps["alt"]) * 100),
                100
            ),
        }

        exif[0x8825] = piexif.dump({
            "GPS": gps_ifd
        })

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    img.save(
        output_path,
        exif=exif.tobytes(),
        quality=95
    )

    if "datetime" in meta:
        ts = meta["datetime"].timestamp()

        os.utime(output_path, (ts, ts))


def embed_video(video_path: Path, meta: dict, output_path: Path):
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dt_str = meta["datetime"].strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    temp_output = Path(
        tempfile.mktemp(
            suffix=video_path.suffix
        )
    )

    cmd = [
        FFMPEG_BIN,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video_path),
    ]

    cmd += [
        "-metadata",
        f"creation_time={dt_str}"
    ]

    if "gps" in meta:
        gps = meta["gps"]

        lat = gps["lat"]
        lon = gps["lon"]

        location = f"{lat:+.4f}{lon:+.4f}/"

        cmd += [
            "-metadata",
            f"location={location}"
        ]

        cmd += [
            "-metadata",
            f"location-eng={location}"
        ]

        cmd += [
            "-movflags",
            "use_metadata_tags"
        ]

    cmd += [
        "-c",
        "copy",
        "-y",
        str(temp_output)
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=120
    )

    if result.returncode != 0:
        error_message = result.stderr.strip()

        if not error_message:
            error_message = "Unknown ffmpeg error"

        raise Exception(error_message)

    shutil.move(
        str(temp_output),
        str(output_path)
    )

    if "datetime" in meta:
        ts = meta["datetime"].timestamp()

        os.utime(output_path, (ts, ts))


def delete_sidecar(sidecar: Path):
    try:
        if sidecar.exists():
            sidecar.unlink()

            print(
                f"🗑️ Deleted sidecar: {sidecar.name}",
                flush=True
            )

    except Exception as e:
        print(
            f"⚠️ Failed to delete sidecar "
            f"{sidecar.name}: {str(e)}",
            flush=True
        )


def run(input_dir: str, output_dir: str, inplace=False):
    input_path = Path(input_dir)

    if not input_path.exists():
        print(
            f"❌ Input folder not found: {input_dir}",
            flush=True
        )
        return

    if not inplace:
        input_root_name = input_path.name + ".g-metamerge"

        output_path = (
            Path(output_dir) /
            input_root_name
        )

    ffmpeg_available = (
        shutil.which(FFMPEG_BIN) is not None
        or Path(FFMPEG_BIN).exists()
    )

    if not ffmpeg_available:
        print(
            "⚠️ ffmpeg not found - video files will be skipped",
            flush=True
        )

    files = [
        p for p in input_path.rglob("*")
        if p.suffix.lower() in SUPPORTED
    ]

    if not files:
        print(
            "❌ No supported media files found",
            flush=True
        )
        return

    print(
        f"📂 Found {len(files)} supported files\n",
        flush=True
    )

    if inplace:
        print(
            "⚠️ Running in IN-PLACE mode",
            flush=True
        )

    merged = 0
    no_sidecar = 0
    errors = 0

    for index, media_file in enumerate(files, start=1):
        suffix = media_file.suffix.lower()

        print(
            f"[{index}/{len(files)}] Processing: "
            f"{media_file.name}",
            flush=True
        )

        try:
            if (
                suffix in SUPPORTED_VIDEO
                and not ffmpeg_available
            ):
                print(
                    f"⏭️ {media_file.name} "
                    f"-> ffmpeg not found",
                    flush=True
                )

                continue

            sidecar = find_sidecar(media_file)

            if inplace:
                destination = media_file

            else:
                destination = (
                    output_path /
                    media_file.relative_to(input_path)
                )

            if not sidecar:
                if not inplace:
                    destination.parent.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    shutil.copy2(
                        media_file,
                        destination
                    )

                print(
                    f"⚠️ {media_file.name} "
                    f"-> copied/no sidecar",
                    flush=True
                )

                no_sidecar += 1
                continue

            meta = parse_sidecar(sidecar)

            if suffix in SUPPORTED_EXIF:
                embed_exif(
                    media_file,
                    meta,
                    destination
                )

                print(
                    f"✅ {media_file.name}",
                    flush=True
                )

            elif suffix in SUPPORTED_VIDEO:
                embed_video(
                    media_file,
                    meta,
                    destination
                )

                print(
                    f"✅ {media_file.name}",
                    flush=True
                )

            merged += 1

            if inplace:
                delete_sidecar(sidecar)

        except subprocess.TimeoutExpired:
            print(
                f"❌ {media_file.name} "
                f"-> ffmpeg timeout",
                flush=True
            )

            errors += 1

        except Exception as e:
            print(
                f"❌ {media_file.name} "
                f"-> {str(e)}",
                flush=True
            )

            errors += 1

    print("\n🏁 Done!\n", flush=True)

    print(
        f"✅ Merged:      {merged}",
        flush=True
    )

    print(
        f"⚠️ No sidecar:  {no_sidecar}",
        flush=True
    )

    print(
        f"❌ Errors:      {errors}",
        flush=True
    )

    if not inplace:
        print("\n📁 Output:", flush=True)

        print(
            str(output_path),
            flush=True
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "G-MetaMerge - restore metadata from "
            "Google Photos Takeout"
        )
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Google Takeout folder"
    )

    parser.add_argument(
        "--output",
        "-o",
        default="",
        help="Output folder"
    )

    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Modify files directly"
    )

    args = parser.parse_args()

    run(
        args.input,
        args.output,
        args.inplace
    )


if __name__ == "__main__":
    main()