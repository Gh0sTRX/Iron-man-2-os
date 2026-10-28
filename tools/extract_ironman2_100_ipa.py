#!/usr/bin/env python3
"""Extract user-provided Iron Man 2 iOS 1.0.0 IPA assets locally.
Usage: python tools/extract_ironman2_100_ipa.py /path/to/IronMan2_1.0.0_ios_2.2.1.ipa --out original_ipa_extracted
Does not download, redistribute, or commit proprietary game assets.
"""
import argparse
import hashlib
import json
import pathlib
import zipfile

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ipa", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("original_ipa_extracted"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    records = []
    with zipfile.ZipFile(args.ipa) as archive:
        for item in archive.infolist():
            if item.is_dir() or not item.filename.startswith("Payload/IronMan2.app/"):
                continue
            relative = pathlib.PurePosixPath(item.filename).relative_to("Payload/IronMan2.app")
            target = args.out.joinpath(*relative.parts)
            if not target.resolve().is_relative_to(args.out.resolve()):
                raise ValueError("Unsafe archive path")
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            with archive.open(item) as src, target.open("wb") as dst:
                while chunk := src.read(1024 * 1024):
                    dst.write(chunk)
                    digest.update(chunk)
            records.append({"path": str(relative), "size": item.file_size, "sha256": digest.hexdigest()})
    (args.out / "asset_manifest.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Extracted {len(records)} files to {args.out}")

if __name__ == "__main__":
    main()
