#!/usr/bin/env python3
"""Iron Man 2 IPA ZIP coverage ledger; metadata only, no asset extraction.

Usage:
    python3 ipa_coverage_audit.py original_1.0.0.ipa original_1.0.3.ipa --out report
This is an inventory accounting tool, NOT proof that all bytes are decoded.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from zipfile import ZipFile

PACKS = {
    "anims": ("animation_archive", "parsed archive + clip transform format"),
    "models": ("model_archive", "only supported meshes/rigs verified"),
    "textures": ("texture_archive", "selected textures/materials verified"),
    "clev": ("level_archive", "10 records indexed; instance graph unknown"),
}
MEDIA = ("audio", "sound", "sfx", "music", "voice", "speech", "dialog",
         "cinematic", "cutscene", "movie", "video", "subtitles")


def group(filename):
    basename = filename.rsplit("/", 1)[-1].lower()
    if basename in PACKS:
        return PACKS[basename]
    if any(h in filename.lower() for h in MEDIA):
        return ("media_candidate", "filename clue; no codec verified")
    if basename.endswith((".bdae", ".bclara", ".anim")):
        return ("possible_loose_asset", "extension only")
    return ("unknown", "unclassified; not necessarily encrypted")


def inspect_ipa(path):
    raw_total = path.stat().st_size
    records = []
    with ZipFile(path) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            family, status = group(info.filename)
            records.append(dict(
                path=info.filename,
                family=family,
                verification=status,
                compressed_bytes=info.compress_size,
                uncompressed_bytes=info.file_size,
                encrypted_flag=bool(info.flag_bits & 0x1),
            ))
    groups = {}
    for record in records:
        grp = groups.setdefault(record["family"], dict(files=0, compressed=0, uncompressed=0))
        grp["files"] += 1
        grp["compressed"] += record["compressed_bytes"]
        grp["uncompressed"] += record["uncompressed_bytes"]
    for grp in groups.values():
        grp["compressed_pct_of_ipa"] = round(100 * grp["compressed"] / raw_total, 4)
    summed_compressed = sum(row["compressed_bytes"] for row in records)
    return records, {
        "file_name": path.name,
        "ipa_zip_bytes": raw_total,
        "entries": len(records),
        "entries_compressed_bytes": summed_compressed,
        "entries_uncompressed_bytes": sum(row["uncompressed_bytes"] for row in records),
        "zip_headers_and_other_overhead_bytes": raw_total - summed_compressed,
        "zip_entries_with_encryption_bit": sum(row["encrypted_flag"] for row in records),
        "groups": groups,
        "warning": (
            "These are ZIP byte percentages, NOT the percentage of decoded game or "
            "implemented gameplay. Named pack archives can contain many inner files "
            "that require separate parsers; encryption flag applies only to ZIP layer."
        ),
    }


def run(paths, out):
    out.mkdir(parents=True, exist_ok=True)
    summary = {}
    for idx, path in enumerate(paths, 1):
        records, stats = inspect_ipa(path)
        summary["IPA_" + str(idx)] = stats
        with (out / ("IPA_" + str(idx) + "_ZIP_ENTRIES.csv")).open(
                "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "path", "family", "verification", "compressed_bytes",
                "uncompressed_bytes", "encrypted_flag"])
            writer.writeheader()
            writer.writerows(records)
    (out / "ZIP_BYTE_COVERAGE.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def selftest():
    import tempfile
    from zipfile import ZIP_DEFLATED
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        original = root / "synthetic.ipa"
        with ZipFile(original, "w", ZIP_DEFLATED) as z:
            z.writestr("Payload/IronMan2.app/anims", b"animation archive contents")
            z.writestr("Payload/IronMan2.app/clev", b"mission archive contents")
            z.writestr("Payload/IronMan2.app/voice_candidate.dat", b"unrecognized")
            z.writestr("Payload/IronMan2.app/app.bin", b"binary")
        report = run([original], root / "out")["IPA_1"]
        assert report["entries"] == 4
        assert report["zip_entries_with_encryption_bit"] == 0
        assert report["groups"]["animation_archive"]["files"] == 1
        assert report["groups"]["level_archive"]["files"] == 1
        assert report["groups"]["media_candidate"]["files"] == 1
        assert report["entries_compressed_bytes"] <= report["ipa_zip_bytes"]
        assert (root / "out" / "IPA_1_ZIP_ENTRIES.csv").exists()
    print("PASS: synthetic ZIP bytes, families, crypto flag and CSV/JSON accounting")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ipa", nargs="*", type=Path)
    parser.add_argument("--out", type=Path, default=Path("b19_coverage"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        selftest()
    else:
        if not args.ipa or len(args.ipa) > 2:
            parser.error("Supply one or two original IPA files, or --self-test")
        for item in args.ipa:
            if not item.is_file():
                parser.error("Missing original IPA: " + str(item))
        print(json.dumps(run(args.ipa, args.out), indent=2, ensure_ascii=False))
