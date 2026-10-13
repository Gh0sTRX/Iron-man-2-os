#!/usr/bin/env python3
"""B24-C1 original map asset staging, NOT yet a Vita render/mission port.

Input sources: private repo's B11 C1L1 original recovered archives.
Creates a deterministic manifest, exact environment GLB and collision raw data
for later GPU vertex/index and world collision conversion. Python stdlib only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import struct
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
ZIP_SCENE = ROOT / "research/B11_C1L1_Scene_GLBS.zip"
ZIP_ORIGINAL = ROOT / "research/B11_C1L1_Source_Parser.zip"
ENV = "exports/IronMan2_C1L1_Environment_Geometry.glb"
WITH_SUIT = "exports/IronMan2_C1L1_Original_Geometry_With_MarkVI.glb"
COLLISION = ("C1L1_col_01.bdae", "C1L1_building_col.bdae", "C1L1_floor_001.bdae")
MAP = ("C1L1_ground_001.bdae", "C1L1_obj_001.bdae", "C1L1_obj_002.bdae",
       "C1L1_obj_003.bdae", "C1L1_obj_004.bdae", "C1L1_car_01.bdae",
       "C1L1_car_02.bdae", "C1L1_light_001.bdae", "C1L1_light_002.bdae",
       "C1L1_light_003.bdae", "C1L1_sky_001.bdae")
BDAE_EXPECTED = 15


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def glb_info(data: bytes) -> dict:
    assert len(data) >= 20, "GLB header truncated"
    magic, version, length = struct.unpack_from("<4sII", data)
    assert magic == b"glTF", f"invalid GLB magic {magic!r}"
    assert version == 2, f"unexpected GLB version {version}"
    assert length == len(data), "GLB total file-length mismatch"
    pos, chunks = 12, {}
    while pos < len(data):
        assert len(data) - pos >= 8, "truncated chunk header"
        size, kind = struct.unpack_from("<I4s", data, pos)
        pos += 8
        assert pos + size <= len(data), "chunk OOB"
        assert size % 4 == 0, "chunk not 4-byte aligned"
        assert kind not in chunks, "duplicate chunk"
        chunks[kind] = data[pos:pos + size]
        pos += size
    assert pos == len(data), "trailing bytes"
    assert b"JSON" in chunks and b"BIN\x00" in chunks, "missing GLB JSON/BIN"
    doc = json.loads(chunks[b"JSON"].rstrip(b" \x00"))
    assert doc.get("asset", {}).get("version", "").startswith("2"), "not glTF 2"
    accessors = doc.get("accessors", [])
    primitives = [p for m in doc.get("meshes", []) for p in m.get("primitives", [])]
    vertex_count = 0
    triangle_count = 0
    for p in primitives:
        assert p.get("mode", 4) == 4, "non-triangle primitive not supported"
        idx = p.get("indices")
        assert isinstance(idx, int) and 0 <= idx < len(accessors)
        iacc = accessors[idx]
        assert iacc.get("componentType") in (5123, 5125), "need 16/32-bit indices"
        assert iacc["count"] % 3 == 0, "index count not triangular"
        attributes = p.get("attributes", {})
        position = attributes.get("POSITION")
        assert isinstance(position, int) and 0 <= position < len(accessors)
        pa = accessors[position]
        assert pa.get("type") == "VEC3" and pa.get("componentType") == 5126
        assert pa["count"] > 0
        vertex_count += pa["count"]
        triangle_count += iacc["count"] // 3
    return {"bytes": len(data), "sha256": sha(data), "meshes": len(doc.get("meshes", [])),
            "primitives": len(primitives), "accessor_vertices": vertex_count,
            "indexed_triangles": triangle_count, "nodes": len(doc.get("nodes", [])),
            "materials": len(doc.get("materials", [])), "world_up": "Y",
            "source_coordinate_frame": "original BDAE source Z-up; GLB export Y-up",
            "destination_b24_world_up": "Z",
            "required_transform": "inverse of B11 GLB Y-up export; validate before draw"}


def build(output: pathlib.Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    assert ZIP_SCENE.is_file() and ZIP_ORIGINAL.is_file(), "required original B11 sources absent"
    manifest = {"format": "B24-C1 source staging manifest, NOT PS Vita runtime map",
                "c1l1_to_level1_bclara_verified": False,
                "original_level_spawn_decoded": False,
                "gpu_renderer_integrated": False,
                "source_archives": {}}
    with zipfile.ZipFile(ZIP_SCENE) as z:
        assert z.testzip() is None, "scene ZIP CRC failure"
        names = set(z.namelist())
        assert ENV in names and WITH_SUIT in names
        scene = z.read(ENV)
        manifest["environment_glb"] = glb_info(scene)
        manifest["environment_glb"]["source_member"] = ENV
        manifest["environment_glb"]["contains_test_mark_vi"] = False
        assert manifest["environment_glb"]["primitives"] >= 300, "lost most original environment meshes"
        assert len(scene) < 32_000_000, "unreasonable scene size"
        (output / "C1L1_environment.glb").write_bytes(scene)
        manifest["source_archives"][ZIP_SCENE.name] = sha(ZIP_SCENE.read_bytes())
    with zipfile.ZipFile(ZIP_ORIGINAL) as z:
        assert z.testzip() is None, "source parser ZIP CRC failure"
        all_bdae = sorted(i.split("/")[-1] for i in z.namelist()
                          if i.startswith("original_models/C1L1_") and i.endswith(".bdae"))
        assert len(all_bdae) == BDAE_EXPECTED, f"expected {BDAE_EXPECTED} C1L1 models: {all_bdae}"
        assert set(COLLISION + MAP).issubset(set(all_bdae))
        originals = {}
        for name in COLLISION + MAP:
            blob = z.read("original_models/" + name)
            assert len(blob) > 128, f"broken BDAE {name}"
            originals[name] = {"bytes": len(blob), "sha256": sha(blob),
                               "role": "collision_candidate" if name in COLLISION else "visual_candidate"}
            (output / name).write_bytes(blob)
        manifest["original_bdae"] = originals
        manifest["source_archives"][ZIP_ORIGINAL.name] = sha(ZIP_ORIGINAL.read_bytes())
    # Converter deliberately stops before inventing original mission transform/spawn.
    manifest["next_steps"] = [
        "Decode C1L1 building/ground transform and use real wall/floor collision",
        "Transcode GLB primitives with correct inverse Y-up->B17 Z-up transform",
        "Upload actual GPU scene batches, avoid B17 CPU 121-tile raster",
        "Bind original C1L1 textures after verified per-submesh BDAE material map",
        "Test in unified B24 with Stage1/Stage2/RUSH and real ground contact",
    ]
    (output / "C1L1_source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=pathlib.Path, default=ROOT / "work" / "b24-c1-src")
    args = parser.parse_args()
    result = build(args.out)
    print(json.dumps({"environment": result["environment_glb"],
                      "model_count": len(result["original_bdae"]),
                      "collision_candidates": list(COLLISION),
                      "output": str(args.out)}, indent=2))
