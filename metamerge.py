import shutil
import argparse


def run(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        print(f"❌ Input folder not found: {input_dir}")
        return

    images = [p for p in input_path.rglob("*") if p.suffix.lower() in SUPPORTED]

    if not images:
        print("No supported images found.")
        return

    ok, no_sidecar, errors = 0, 0, 0

    for img_path in images:
        sidecar = find_sidecar(img_path)
        dest = output_path / img_path.relative_to(input_path)

        if not sidecar:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(img_path, dest)
            print(f"⚠️  {img_path.name}  →  copied, no sidecar")
            no_sidecar += 1
            continue

        try:
            meta = parse_sidecar(sidecar)
            embed(img_path, meta, dest)
            print(f"✅ {img_path.name}")
            ok += 1
        except Exception as e:
            print(f"❌ {img_path.name}  →  {e}")
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
        description="metamerge — embed Google Takeout metadata back into your photos"
    )
    parser.add_argument("--input",  "-i", required=True, help="Google Takeout Google Photos folder")
    parser.add_argument("--output", "-o", required=True, help="Output folder")
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == "__main__":
    main()