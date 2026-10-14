#!/usr/bin/env python3
"""Source-only inspection of original 2010 Underwater Object01 (29v) attachment.

Read user-owned IPA locally in an ephemeral CI runner. Never infer Object01
parent from proximity, mesh name, or shared text; emit evidence, not a rig.
No modifications to released G8 assets or Vita executable.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np

from b24_original_underwater_armor import decode_bres
from b24_owner_pack_extract import decode, get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13

ROOT = Path(__file__).resolve().parents[2]
NEEDLES = (
    b"Object01\0", b"Object01-node\0", b"Object01-mesh\0",
    b"underwater01-node\0", b"underwater01-mesh\0",
    b"Bip01-node\0",
)


def string_pointer_evidence(raw: bytes, needle: bytes) -> list[dict]:
    """Count exact, 4-byte aligned BRES offset references; never assign meaning."""
    out = []
    start = 0
    while True:
        offset = raw.find(needle, start)
        if offset < 0:
            break
        start = offset + 1
        key = struct.pack("<I", offset)
        refs = [i for i in range(0, len(raw) - 3, 4) if raw[i:i + 4] == key]
        out.append({"string_offset": offset, "aligned_ref_count": len(refs),
                    "aligned_ref_offsets": refs[:32],
                    "refs_truncated": len(refs) > 32})
    return out


def bbox(points: np.ndarray) -> dict:
    p = np.asarray(points, dtype=np.float64)
    if p.ndim != 2 or p.shape[1] != 3 or not np.isfinite(p).all():
        raise ValueError("original mesh has invalid 3D coordinates")
    return {"minimum": p.min(axis=0).tolist(), "maximum": p.max(axis=0).tolist(),
            "centroid": p.mean(axis=0).tolist()}


def inspect(ipa: Path) -> dict:
    with zipfile.ZipFile(ipa) as package:
        packed = package.read("Payload/IronMan2.app/models")
    raw = get_exact(packed, decode(packed, ".bdae"), "LC_MC_UnderWater.bdae")
    _, _, meshes = decode_bres(raw, ROOT / "research/B11_C1L1_Source_Parser.zip")
    if [len(m["positions"]) for m in meshes] != [811, 29]:
        raise ValueError("2010 underwater source geometry changed")
    with tempfile.TemporaryDirectory(prefix="underwater_aux_original_b13_") as tmp:
        b13 = load_original_b13(Path(tmp))
        nodes = b13.parse_rig(raw)
    if len(nodes) != 97:
        raise ValueError("2010 source skeleton changed")
    relevant = [
        {"name": str(n["name"]), "parent": str(n["parent"]),
         "node_offset": int(n["offset"])}
        for n in nodes
        if any(t in str(n["name"]).casefold() for t in ("object", "underwater"))
    ]
    evidence = {needle.decode("ascii").rstrip("\0"): string_pointer_evidence(raw, needle)
                for needle in NEEDLES}
    result = {
        "source_model": "LC_MC_UnderWater.bdae",
        "source_bres_bytes": len(raw),
        "verified_original_main_skinned_vertices": 811,
        "verified_original_auxiliary_vertices": 29,
        "verified_original_rig_nodes": len(nodes),
        "source_mesh_names": [str(m.get("name", "<unnamed>")) for m in meshes],
        "mesh_bbox": [bbox(np.asarray(m["positions"])) for m in meshes],
        "relevant_rig_nodes": relevant,
        "exact_string_pointer_evidence": evidence,
        "auxiliary_source_parent_proven": False,
        "auxiliary_source_transform_proven": False,
        "auxiliary_skin_weights_proven": False,
        "original_skinning_change_made": False,
        "g8_vita_runtime_modified": False,
        "interpretation": (
            "Offset references are forensic candidates, NOT verified mesh-to-node "
            "edges. Do not bind Object01 to a bone unless original BRES relation "
            "and transform are independently decoded and checked at rest."
        ),
    }
    return result


def self_test() -> None:
    data = bytearray(128)
    data[40:49] = b"Object01\0"
    struct.pack_into("<I", data, 12, 40)
    struct.pack_into("<I", data, 20, 40)
    rows = string_pointer_evidence(bytes(data), b"Object01\0")
    assert len(rows) == 1 and rows[0]["string_offset"] == 40
    assert rows[0]["aligned_ref_offsets"] == [12, 20]
    assert not string_pointer_evidence(bytes(data), b"Object01-node\0")
    assert bbox(np.array([[1, 2, 3], [3, 4, 5]], dtype=float))["centroid"] == [2, 3, 4]
    print("PASS synthetic offset reference / geometry regression (no owner IPA)")


def main() -> None:
    arg = argparse.ArgumentParser()
    arg.add_argument("--ipa", type=Path)
    arg.add_argument("--report", type=Path)
    arg.add_argument("--self-test", action="store_true")
    args = arg.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.ipa or not args.report:
        arg.error("actual source inspection requires --ipa and --report")
    report = inspect(args.ipa)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("UNDERWATER_AUX_2010_MESHES", report["source_mesh_names"])
    print("UNDERWATER_AUX_2010_RIG_NAMES", report["relevant_rig_nodes"])
    print("UNDERWATER_AUX_2010_STR_REFS", report["exact_string_pointer_evidence"])
    print("PASS source-only Object01 29v forensic report; attachment UNPROVEN, G8 untouched")


if __name__ == "__main__":
    main()
