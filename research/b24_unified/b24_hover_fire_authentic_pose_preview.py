#!/usr/bin/env python3
"""SOURCE-ONLY actual owner iOS hover L/R and attack skinned-pose contact sheets.

The image panels are off-console diagnostic geometry renders, *not* Vita GPU
screenshots, not the original game's material shader. No fabricated poses:
every vertex is baked from original BRES weights and original .anim tracks.
Fail closed when rig attachment/vertex counts cannot be proven.
"""
from __future__ import annotations

import argparse
import json
import struct
import tempfile
import zipfile
from pathlib import Path
import sys

import numpy as np

from b24_hover_fire_directional_source import catalog, expected_name
from b24_owner_pack_extract import decode, get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13

ROOT = Path(__file__).resolve().parents[2]
TARGETS = {
    "ironman": ("Iron_man_mark6.bdae", 802),
    "warmachine": ("warmachine.bdae", 1292),
}
SCENES = [("L", False), ("L", True), ("R", False), ("R", True)]


def source_meshes(raw: bytes):
    """Reuse exact B11 mesh parser; no synthetic replacement topology."""
    with zipfile.ZipFile(ROOT / "research/B11_C1L1_Source_Parser.zip") as z:
        src = z.read("bdae_scene_parser.py")
    env = {"__name__": "b24_actual_hover_original_bres", "__file__": "bdae_scene_parser.py"}
    exec(compile(src, "bdae_scene_parser.py", "exec"), env)
    meshes, stats = env["parse"](raw)
    return meshes


def prepare(original, raw: bytes, verts: np.ndarray):
    nodes = original.parse_rig(raw)
    offset, names, inv, indices, weights = original.parse_skin(raw, len(verts))
    bones = {}
    for node in nodes:
        q = struct.unpack_from("<I", raw, node["offset"] + 8)[0]
        if q >= len(raw):
            continue
        end = raw.find(b"\0", q)
        if end < 0:
            continue
        key = raw[q:end].decode("latin1")
        if key in names:
            if key in bones:
                raise ValueError("duplicate genuine source bone palette")
            bones[key] = node["name"]
    if set(bones) != set(names):
        raise ValueError(f"source BRES bone mapping incomplete: {len(bones)}/{len(names)}")
    joints = [bones[name] for name in names]
    rest = original.worlds(nodes)
    error = max(float(np.max(np.abs(rest[j] @ inv[i] - np.eye(4))))
                for i, j in enumerate(joints))
    if error >= 2e-4 or not np.isfinite(error):
        raise ValueError(f"source inverse bind rest mismatch {error}")
    v = np.asarray(verts, dtype=np.float64)
    assert v.shape[1] == 3
    setup = {
        "nodes": nodes, "joints": joints, "inv": inv, "indexes": indices,
        "weights": weights,
        "verts": np.column_stack([v, np.zeros((len(v), 2))]),
    }
    return setup, error, len(nodes), len(names)


def bake(original, setup: dict, raw: bytes):
    a = original.decode_anim(raw)
    if not a.names:
        raise ValueError("no original joint tracks")
    tick = a.duration_ms // 2 if a.duration_ms else 0
    vertices = original.bake_pose(setup, a, tick)
    if vertices.shape != (len(setup["verts"]), 3) or not np.isfinite(vertices).all():
        raise ValueError("invalid original bone skin resulting vertices")
    return vertices, a, tick


def contact_sheet(armor: str, frames: list[dict], dst: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(14, 5.8), dpi=130, facecolor="#0b1424")
    fig.suptitle(
        f"2010 ORIGINAL SOURCE ANIMATION - {armor.upper()} | HOST B13 SKIN POSES",
        color="white", fontsize=13, y=0.99)
    all_verts = np.concatenate([x["verts"] for x in frames])
    mid = (all_verts.max(axis=0) + all_verts.min(axis=0)) / 2
    radius = max(float(np.max(np.ptp(all_verts, axis=0))), 0.1) * .58
    for i, f in enumerate(frames):
        ax = fig.add_subplot(1, 4, i + 1, projection="3d", facecolor="#101c2c")
        verts = f["verts"]
        face = f["faces"]
        # Real 2010 author triangles, downsampled only for readable host clay preview.
        polys = verts[face[::2]]
        collection = Poly3DCollection(polys, linewidths=0.02,
                                     edgecolors=(0.10, 0.16, 0.21, 0.16),
                                     facecolors=("#9cb7be" if armor == "ironman" else "#a5aeb7"),
                                     alpha=1)
        ax.add_collection3d(collection)
        for k in range(3):
            lo, hi = float(mid[k]-radius), float(mid[k]+radius)
            (ax.set_xlim, ax.set_ylim, ax.set_zlim)[k](lo, hi)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=8, azim=-68)
        ax.set_axis_off()
        direction, firing = f["direction"], f["firing"]
        ax.set_title(f"{direction} | {'ATTACK' if firing else 'MOVE'}\n"
                     f"{f['source_name']}\n"
                     f"source t={f['tick_ms']}ms",
                     fontsize=7, color="white", pad=5)
    fig.text(.5, .014,
             "DIAGNOSTIC CLAY VIEW - real source BRES mesh and animation, "
             "NOT textured in-game Vita renderer; zero invented poses",
             ha="center", color="#c7d1e4", fontsize=10)
    dst.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dst, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ipa", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    evidence = catalog()
    with zipfile.ZipFile(args.ipa) as z:
        prefix = "Payload/IronMan2.app/"
        models = z.read(prefix + "models")
        anims = z.read(prefix + "anims")
    model_records = decode(models, ".bdae")
    animation_records = decode(anims, ".anim")
    summary = {}
    with tempfile.TemporaryDirectory(prefix="b24_hover_actual_original_") as td:
        original = load_original_b13(Path(td))
        for armor, (model_name, nv) in TARGETS.items():
            model = get_exact(models, model_records, model_name)
            meshlist = source_meshes(model)
            matched = [m for m in meshlist if len(m["positions"]) == nv]
            if len(matched) != 1:
                raise ValueError(f"{armor} author skin topology mismatch: "
                                 f"want {nv}, got {[len(m['positions']) for m in meshlist]}")
            mesh = matched[0]
            coords = np.asarray(mesh["positions"])
            faces = np.asarray(mesh["faces"]).reshape(-1, 3).astype(int)
            if np.any(faces < 0) or np.any(faces >= nv):
                raise ValueError("source BRES triangle indices invalid")
            setup, rest_error, nnodes, npalette = prepare(original, model, coords)
            shots = []
            for direction, firing in SCENES:
                lookup = expected_name(armor, "aim", direction, firing)
                spec = evidence.get(lookup.casefold())
                if spec is None:
                    raise ValueError("original 2010 source not cataloged: " + lookup)
                raw = get_exact(anims, animation_records, spec["filename"])
                v, animation, tick = bake(original, setup, raw)
                shots.append(dict(direction=direction, firing=firing,
                                  source_name=spec["filename"],
                                  duration_ms=animation.duration_ms,
                                  tick_ms=tick,
                                  bone_track_count=len(animation.names),
                                  verts=v, faces=faces))
            output = args.out / f"HOST_2010_{armor}_hover_LR_attack.png"
            contact_sheet(armor, shots, output)
            summary[armor] = {
                "source_bres": model_name, "original_source_vertices": nv,
                "original_mesh_triangles": len(faces),
                "source_rig_nodes": nnodes, "source_skin_palette": npalette,
                "source_inverse_bind_residual": rest_error,
                "preview_png": output.name,
                "pose_sources": [{
                    "name": x["source_name"], "duration_ms": x["duration_ms"],
                    "sample_time_ms": x["tick_ms"], "bone_track_count": x["bone_track_count"]
                } for x in shots],
                "real_vita_execution_proven": False,
            }
            print("PASS ACTUAL SOURCE HOVER POSE", armor, "vertices", nv,
                  "triangles", len(faces), "rest_error", rest_error,
                  "image", output.name)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "SOURCE_HOVER_PREVIEW_MANIFEST.json").write_text(
        json.dumps(summary, indent=2) + "\n")
    print("PASS 8 genuine original 2010 iOS player movement/attack poses, no VPK")


if __name__ == "__main__":
    main()
