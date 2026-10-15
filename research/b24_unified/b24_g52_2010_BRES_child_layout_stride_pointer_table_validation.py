#!/usr/bin/env python3
"""G52: source-only, fail-closed sibling layout search for 2010 C1L1 BRES.

Reuses the exact 370-mesh/382-record G51 evidence. A parent record's +56
count and +60 address may describe a direct first child, a table of pointers,
or contiguous child records. This tool tests these *separately*, never turns
a heuristic into a world transform, and never edits mesh coordinates.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import struct
import tempfile
import zipfile
from pathlib import Path

from b24_g50_original_2010_C1L1_BRES_mesh_name_node_PIVOT_inverse_center_hierarchy import SOURCES
from b24_g51_original_2010_BRES_named_node_child_pointer_graph import (
    original_string,
    run as g51_run,
)


def extended_named_record(raw: bytes, off: int):
    """Structure-qualified possible child; weaker than a fully indexed G51 node."""
    if off < 0 or off % 4 or off + 64 > len(raw):
        return None
    refs = struct.unpack_from("<III", raw, off)
    names = [original_string(raw, p) for p in refs]
    if not any(names) or (not names[0] and not names[1]):
        return None
    xyz_q_scale = struct.unpack_from("<10f", raw, off + 12)
    if not all(map(math.isfinite, xyz_q_scale)):
        return None
    if max(map(abs, xyz_q_scale[:3])) > 5000:
        return None
    if abs(sum(x * x for x in xyz_q_scale[3:7]) - 1) > 0.012:
        return None
    if any(abs(x) < 0.0001 or abs(x) > 100 for x in xyz_q_scale[7:10]):
        return None
    count, child_ptr = struct.unpack_from("<II", raw, off + 56)
    if count > 300 or (count and (child_ptr >= len(raw) or child_ptr % 4)):
        return None
    return {
        "offset": off,
        "names": names,
        "xyz": [round(x, 6) for x in xyz_q_scale[:3]],
        "count": count,
        "first_child_field": child_ptr,
    }


def child_layout_evidence(raw: bytes, parent: dict, anchors: set[int], cache: dict):
    count = parent["source_native_direct_child_count_field"]
    addr = parent["source_native_direct_child_pointer_field"]
    off = parent["source_native_node_record_offset"]
    if count == 0 or addr == 0 or addr % 4 or addr >= len(raw):
        return None

    def valid(target: int):
        if target not in cache:
            cache[target] = extended_named_record(raw, target)
        return cache[target]

    direct = valid(addr)
    result = {
        "parent_offset": off,
        "parent_name": next((s for s in parent["source_author_names"] if s), None),
        "original_count_field": count,
        "original_address_field": addr,
        "exact_first_child_named_struct": (
            {"offset": addr, "names": direct["names"],
             "also_G51_anchor": addr in anchors} if direct else None
        ),
        "pointer_array_full_validation": None,
        "packed_record_stride_full_validation": [],
        "diagnostic_adjacent_fields_matching_anchor_offsets": [],
    }

    # These are concrete raw references, but their semantics are unknown.
    for rel in (52, 64, 68, 72, 76, 80, 84, 88, 92, 96):
        if off + rel + 4 <= len(raw):
            ptr = struct.unpack_from("<I", raw, off + rel)[0]
            if ptr in anchors and ptr != off:
                result["diagnostic_adjacent_fields_matching_anchor_offsets"].append(
                    {"byte_offset_relative_to_parent": rel, "target_node_offset": ptr}
                )

    # Only validate a WHOLE table, never cherry-pick matching individual words.
    if 2 <= count <= 32 and addr + 4 * count <= len(raw):
        table = struct.unpack_from("<" + "I" * count, raw, addr)
        if len(set(table)) == count and all(valid(x) for x in table):
            result["pointer_array_full_validation"] = [
                {"node_offset": x, "name": next(
                    (n for n in valid(x)["names"] if n), None),
                 "also_G51_anchor": x in anchors}
                for x in table
            ]

    # Hypothesis only: a regular stride may be incidental; no engine layout
    # claim or transform will be made from this probe alone.
    if 2 <= count <= 16:
        for stride in range(64, 257, 4):
            if addr + (count - 1) * stride + 64 > len(raw):
                continue
            hits = [valid(addr + i * stride) for i in range(count)]
            if all(hits):
                result["packed_record_stride_full_validation"].append({
                    "hypothetical_stride": stride,
                    "named_struct_offsets": [h["offset"] for h in hits],
                    "all_in_G51_anchor_set": all(h["offset"] in anchors for h in hits),
                })
    return result


def analyze(zpath: Path, outpath: Path):
    with tempfile.TemporaryDirectory() as td:
        g51path = Path(td) / "g51.json"
        g51_run(zpath, g51path)
        g51 = json.loads(g51path.read_text())
    assert g51["source_authentic_original_source_meshes"] == 370
    assert g51["original_source_first_child_exact_node_pointer_edges"] >= 4
    source_models = {
        x["original_BRES"]: x
        for x in g51["source_original_10_BRES_real_native_node_records_graph"]
    }

    totals = collections.Counter()
    sources = []
    with zipfile.ZipFile(zpath) as archive:
        for stem in SOURCES:
            raw = archive.read("original_models/" + stem + ".bdae")
            orig = source_models[stem]
            parents = orig["original_native_node_TRS_records"]
            known = {p["source_native_node_record_offset"] for p in parents}
            cache = {}
            results = []
            for p in parents:
                ev = child_layout_evidence(raw, p, known, cache)
                if ev is None:
                    continue
                results.append(ev)
                totals["parent_nodes_with_child_fields"] += 1
                if ev["exact_first_child_named_struct"]:
                    totals["direct_first_child_struct_valid"] += 1
                    if not ev["exact_first_child_named_struct"]["also_G51_anchor"]:
                        totals["additional_named_child_struct_not_G51_anchor"] += 1
                if ev["pointer_array_full_validation"]:
                    totals["complete_valid_pointer_arrays"] += 1
                    totals["children_in_complete_arrays"] += len(
                        ev["pointer_array_full_validation"]
                    )
                if ev["packed_record_stride_full_validation"]:
                    totals["possible_packed_layout_parents"] += 1
                if ev["diagnostic_adjacent_fields_matching_anchor_offsets"]:
                    totals["nodes_with_additional_adjacent_raw_refs"] += 1
            sources.append({
                "original_BRES": stem,
                "sha256_original_owned_source": hashlib.sha256(raw).hexdigest(),
                "G51_known_named_records": len(known),
                "G51_original_meshes": orig["real_original_source_meshes"],
                "original_nodes_with_nonzero_child_fields": len(results),
                "child_layout_candidates": results,
            })
            totals["meshes"] += orig["real_original_source_meshes"]
            totals["G51_nodes"] += len(known)

    report = {
        "stage": "G52",
        "source_only_no_vpk_no_geometry_shift": True,
        "source_BRES_v133_files": len(sources),
        "totals": dict(totals),
        "per_source": sources,
        "interpretation": {
            "direct": "Address itself parses as a native named TRS record; explicit source field, parent semantics still need runtime confirmation.",
            "pointer_array": "EVERY u32 element of declared count resolves to a separately validated source named TRS record.",
            "packed_stride": "Every addressed stride position parses as a named TRS record. Multiple strides or unknown field semantics mean diagnostic only.",
            "adjacent_fields": "Literal pointers to known nodes found near a record, not yet proven parent/sibling pointers.",
            "world_matrix_proven": False,
            "shader_visibility_proven": False,
            "native_scene_modified": False,
        },
    }
    assert totals["meshes"] == 370
    assert totals["G51_nodes"] >= 370
    assert totals["direct_first_child_struct_valid"] >= 4
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print("G52 source-only counts", json.dumps(dict(totals), sort_keys=True))
    for s in sources:
        active = s["child_layout_candidates"]
        print(s["original_BRES"], "G51 nodes", s["G51_known_named_records"],
              "child fields", len(active),
              "direct", sum(bool(x["exact_first_child_named_struct"]) for x in active),
              "pointer arrays", sum(bool(x["pointer_array_full_validation"]) for x in active),
              "stride candidates", sum(bool(x["packed_record_stride_full_validation"]) for x in active))
    print("PASS G52 original BRES native child representation census; no world-transform claims")


def self_test():
    raw = bytearray(4096)

    def label(off, s):
        b = s.encode("ascii")
        struct.pack_into("<I", raw, off - 4, len(b))
        raw[off:off + len(b)] = b
        return off

    a = label(301, "parent-node")
    b = label(401, "one-node_PIVOT")
    c = label(501, "two-node_PIVOT")
    def node(off, ptr, count=0, first=0):
        struct.pack_into("<III", raw, off, ptr, ptr, 0)
        struct.pack_into("<10f", raw, off + 12,
                         0, 0, 0, 0, 0, 0, 1, 1, 1, 1)
        struct.pack_into("<II", raw, off + 56, count, first)

    node(64, a, 2, 800)
    node(128, b)
    node(192, c)
    struct.pack_into("<II", raw, 800, 128, 192)
    parent = {
        "source_native_node_record_offset": 64,
        "source_author_names": ["parent-node", "parent-node", None],
        "source_native_direct_child_count_field": 2,
        "source_native_direct_child_pointer_field": 800,
    }
    result = child_layout_evidence(bytes(raw), parent, {64, 128, 192}, {})
    assert result["pointer_array_full_validation"] is not None
    assert [x["node_offset"] for x in result["pointer_array_full_validation"]] == [128, 192]
    assert result["exact_first_child_named_struct"] is None
    node(64, a, 1, 128)
    parent["source_native_direct_child_count_field"] = 1
    parent["source_native_direct_child_pointer_field"] = 128
    result = child_layout_evidence(bytes(raw), parent, {64, 128, 192}, {})
    assert result["exact_first_child_named_struct"]["offset"] == 128
    print("PASS G52 synthetic direct and pointer-table classification; source files not used")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
    else:
        if not args.zip or not args.out:
            ap.error("--zip and --out required except --self-test")
        analyze(args.zip, args.out)
