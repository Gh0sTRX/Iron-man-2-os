#!/usr/bin/env python3
"""Bake the exact 40 original 2010 iOS player hover/aim/attack motion streams.

Includes aim and aim_m families, 2 armors x (idle,F,B,L,R) x (move,attack).
Uses owner original BRES bone weights and individual named .anim tracks, not
any invented animation or vertex retargeting. SOURCE-ONLY: no VPK and NO
runtime mapping, combat/weapon roles remain unverified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import tempfile
import zipfile
from pathlib import Path

import numpy as np

from b24_hover_fire_directional_source import catalog, expected_name, DIRECTIONS
from b24_hover_fire_authentic_pose_preview import TARGETS, source_meshes, prepare
from b24_owner_pack_extract import decode, get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13


def run(ipa: Path, out: Path):
    cat = catalog()
    with zipfile.ZipFile(ipa) as z:
        models = z.read("Payload/IronMan2.app/models")
        anims = z.read("Payload/IronMan2.app/anims")
    model_items = decode(models, ".bdae")
    anim_items = decode(anims, ".anim")
    out.mkdir(parents=True, exist_ok=True)
    result = {"format": "IM2V", "fps_nominal": 20,
              "original_owner_iOS_game_version": "1.0.0",
              "original_source_player_clip_count": 40,
              "g8_vita_gameplay_connected": False,
              "all_2010_weapon_mode_roles_recovered": False,
              "no_new_vpk": True, "models": {}, "clips": []}
    with tempfile.TemporaryDirectory(prefix="b24_original_hover_skin_") as tmp:
        original = load_original_b13(Path(tmp))
        for armor, (model_name, expected_nv) in TARGETS.items():
            source = get_exact(models, model_items, model_name)
            meshlist = source_meshes(source)
            matches = [m for m in meshlist if len(m["positions"]) == expected_nv]
            if len(matches) != 1:
                raise ValueError(f"source model {model_name} topology mismatch")
            setup, rest_err, node_count, palette_count = prepare(
                original, source, np.asarray(matches[0]["positions"]))
            result["models"][armor] = {
                "source": model_name, "vertices": expected_nv,
                "rig_nodes": node_count, "skin_palette_bones": palette_count,
                "inverse_bind_rest_error": rest_err,
            }
            for mode in ("aim", "aim_m"):
                for direction in DIRECTIONS:
                    for firing in (False, True):
                        requested = expected_name(armor, mode, direction, firing)
                        spec = cat.get(requested.casefold())
                        if spec is None:
                            raise ValueError("2010 original clip absent: " + requested)
                        raw = get_exact(anims, anim_items, spec["filename"])
                        clip = original.decode_anim(raw)
                        if len(clip.names) != spec["source_named_tracks"]:
                            raise ValueError("2010 source track names disagree for " + requested)
                        ms = clip.duration_ms
                        if ms <= 0 or ms > 30000 or ms != spec["duration_ms"]:
                            raise ValueError("2010 source clip timing drift: " + requested)
                        ticks = list(range(0, ms, 50)) + [ms]
                        frames = []
                        low, high = np.inf, -np.inf
                        for t in ticks:
                            frame = np.asarray(original.bake_pose(setup, clip, t),
                                               dtype=np.float64)
                            if frame.shape != (expected_nv, 3) or not np.isfinite(frame).all():
                                raise ValueError("original source skin output invalid: " + requested)
                            low = min(low, float(frame.min()))
                            high = max(high, float(frame.max()))
                            if high > 100000 or low < -100000:
                                raise ValueError("original pose contains outlier")
                            frames.append(frame.astype("<f4", copy=False))
                        binary = (struct.pack("<4sIIII", b"IM2V",
                                              expected_nv, len(ticks), 20, ms)
                                  + np.stack(frames).astype("<f4", copy=False).tobytes())
                        if len(binary) != 20 + len(ticks) * expected_nv * 12:
                            raise ValueError("IM2V source animation stream corrupted")
                        dest = armor + "_" + Path(spec["filename"]).stem.casefold() + ".im2v"
                        (out / dest).write_bytes(binary)
                        result["clips"].append({
                            "armor": armor, "source_animation": spec["filename"],
                            "source_animation_sha256": hashlib.sha256(raw).hexdigest(),
                            "output": dest, "im2v_sha256": hashlib.sha256(binary).hexdigest(),
                            "frames": len(ticks), "duration_ms": ms,
                            "tracks": len(clip.names), "source_original_vertices": expected_nv,
                            "bytes": len(binary),
                            "source_pose_min": low, "source_pose_max": high,
                            "mesh_rig_identity_verified": True,
                            "B24_gameplay_and_weapon_verified": False,
                        })
            print("PASS ORIGINAL 2010 HOVER", armor, "verts", expected_nv,
                  "original rig", node_count, "clips", 20)
    if len(result["clips"]) != 40:
        raise ValueError("source clip coverage unexpectedly changed")
    result["total_baked_bytes"] = sum(x["bytes"] for x in result["clips"])
    (out / "B24_G8_ORIGINAL_40_HOVER_FIRE_MOTION_MANIFEST.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print("PASS 40 original user-owned BRES+ANIM -> IM2V streams",
          "total_bytes", result["total_baked_bytes"], "NO VPK")
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ipa", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    run(a.ipa, a.out)


if __name__ == "__main__":
    main()
