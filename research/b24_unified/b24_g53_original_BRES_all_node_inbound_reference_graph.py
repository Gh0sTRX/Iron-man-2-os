#!/usr/bin/env python3
"""G53: reverse-reference original BRES native node pointers across entire files.

G52 shows only 4/382 indexed native records expose a nonzero child field,
so repeating +56/+60 record walks cannot rebuild the scene graph.
This script searches ALL 4-byte aligned original source words for exact
pointers to individually validated G51 native TRS record starts. It
separates references within a node record from external archive tables,
and reports contiguous/dense pointer runs. It does NOT infer world matrices
or assume an external reference is necessarily a parent link.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

import numpy as np

from b24_g50_original_2010_C1L1_BRES_mesh_name_node_PIVOT_inverse_center_hierarchy import SOURCES
from b24_g51_original_2010_BRES_named_node_child_pointer_graph import run as g51_run


def index_refs(raw: bytes, known: dict[int, dict]):
    anchors = sorted(known)
    if not anchors:
        return {"external_references": [], "internal_references": [], "groups": []}
    wordbuf = np.frombuffer(raw[:len(raw) & ~3], dtype="<u4")
    wanted = np.asarray(anchors, dtype="<u4")
    sites = np.flatnonzero(np.isin(wordbuf, wanted)).tolist()
    external, internal = [], []
    for slot in sites:
        site = slot * 4
        target = int(wordbuf[slot])
        # The 64-byte native G51 record is the only established size.
        i = bisect.bisect_right(anchors, site) - 1
        owning = anchors[i] if i >= 0 and site < anchors[i] + 64 else None
        row = {
            "original_source_ref_word_offset": site,
            "original_source_exact_target_node_record_offset": target,
            "target_native_names": known[target]["source_author_names"],
        }
        if owning is not None:
            row["within_known_node_record"] = owning
            row["owner_field_byte_offset"] = site - owning
            internal.append(row)
        else:
            external.append(row)
    groups = []
    for row in external:
        if groups and row["original_source_ref_word_offset"] == (
            groups[-1]["last_word_offset"] + 4
        ):
            g = groups[-1]
            g["last_word_offset"] = row["original_source_ref_word_offset"]
            g["node_offsets"].append(
                row["original_source_exact_target_node_record_offset"]
            )
        else:
            groups.append({
                "first_word_offset": row["original_source_ref_word_offset"],
                "last_word_offset": row["original_source_ref_word_offset"],
                "node_offsets": [
                    row["original_source_exact_target_node_record_offset"]
                ],
            })
    return {"external_references": external, "internal_references": internal,
            "groups": groups}


def probe(zip_path: Path, outfile: Path):
    with tempfile.TemporaryDirectory() as tmp:
        g51path = Path(tmp) / "g51.json"
        g51_run(zip_path, g51path)
        src = json.loads(g51path.read_text())
    assert src["source_authentic_original_source_meshes"] == 370
    bystem = {x["original_BRES"]: x for x in
              src["source_original_10_BRES_real_native_node_records_graph"]}
    totals = collections.Counter()
    out = []
    with zipfile.ZipFile(zip_path) as zf:
        for stem in SOURCES:
            raw = zf.read("original_models/" + stem + ".bdae")
            model = bystem[stem]
            known = {r["source_native_node_record_offset"]: r
                     for r in model["original_native_node_TRS_records"]}
            refs = index_refs(raw, known)
            inbound = collections.Counter(
                r["original_source_exact_target_node_record_offset"]
                for r in refs["external_references"])
            multi = [g for g in refs["groups"] if len(g["node_offsets"]) >= 2]
            # Report all source exact locations; no guess about parent semantics.
            external_rows = refs["external_references"]
            out.append({
                "source_original_BRES": stem,
                "source_file_sha256": hashlib.sha256(raw).hexdigest(),
                "named_TRS_anchors_G51": len(known),
                "external_exact_u32_node_refs": len(external_rows),
                "external_distinct_target_nodes": len(inbound),
                "inside_native_record_exact_u32_refs": len(refs["internal_references"]),
                "inside_native_node_ref_fields": refs["internal_references"],
                "external_exact_node_ref_fields": external_rows,
                "contiguous_external_pointer_runs_min2": multi,
                "all_external_reference_targets": sorted(
                    [{"node_offset": k, "inbound_count": v,
                      "source_names": known[k]["source_author_names"]}
                     for k, v in inbound.items()],
                    key=lambda x: (-x["inbound_count"], x["node_offset"])),
            })
            totals["native_BRES_models"] += 1
            totals["original_meshes"] += model["real_original_source_meshes"]
            totals["G51_nodes"] += len(known)
            totals["external_exact_node_refs"] += len(external_rows)
            totals["distinct_nodes_with_external_refs"] += len(inbound)
            totals["internal_exact_node_refs"] += len(refs["internal_references"])
            totals["contiguous_external_pointer_runs_min2"] += len(multi)
            totals["nodes_in_contiguous_external_runs"] += sum(
                len(g["node_offsets"]) for g in multi)
            print("G53", stem, "original named nodes", len(known),
                  "outside-node raw pointer refs", len(external_rows),
                  "distinct nodes", len(inbound),
                  "contiguous pointer runs", len(multi))
    result = {
        "stage": "G53", "original_data": "owner's BRES 2010 v0.0.0.133",
        "totals": dict(totals), "per_BRES": out,
        "raw_exact_offsets_not_semantics": True,
        "all_original_mesh_vertices_unchanged": True,
        "cumulative_world_matrices_reconstructed": False,
        "confirmed_parent_sibling_edges_from_external_refs": 0,
        "no_vpk_no_performance_work": True,
    }
    assert totals["original_meshes"] == 370
    assert totals["G51_nodes"] == src["source_original_explicit_named_native_TRS_nodes"]
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print("G53 TOTALS", json.dumps(dict(totals), sort_keys=True))
    print("PASS G53 original absolute pointer reverse-index, no guessed hierarchy")


def selftest():
    raw = bytearray(512)
    # 2 known 64-byte node records, 2 external table references and one
    # actual reference within the first native node body.
    np.frombuffer(raw, dtype="<u4")[25:27] = [128, 256]
    np.frombuffer(raw, dtype="<u4")[34] = 256
    known = {128: {"source_author_names": ["one-node"]},
             256: {"source_author_names": ["two-node"]}}
    r = index_refs(bytes(raw), known)
    assert len(r["external_references"]) == 2
    assert len(r["internal_references"]) == 1
    assert len([g for g in r["groups"] if len(g["node_offsets"]) >= 2]) == 1
    assert r["internal_references"][0]["owner_field_byte_offset"] == 8
    print("PASS G53 synthetic exact reverse-pointer classification, no BRES asserted")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        selftest()
    else:
        if not args.zip or not args.out:
            ap.error("Real archive --zip and report --out required")
        probe(args.zip, args.out)
