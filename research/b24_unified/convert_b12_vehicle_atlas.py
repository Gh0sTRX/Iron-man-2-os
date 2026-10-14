#!/usr/bin/env python3
"""Convert the USER'S PRIVATE original B12 decoded C1L1_Vehicles.png to
VitaGL-uploadable uncompressed atlas. This file must be run LOCALLY (or from
an explicitly authorized private B12 input); no B12 original texture pixels
are stored in GitHub source or CI artifacts. No Vita VPK is built.

B12 PVR->PNG recovery used an experimental PVRTC decoder; atlas association
was independently verified in a B12 22-vehicle textured GLB. Per-pixel
PVRTC reference fidelity and horizontal/vertical orientation still need
physical device/independent image checks, NOT claimed.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,struct,zipfile,io
from PIL import Image
ORIGINAL="decoded_textures/C1L1_Vehicles.png"
def build(archive:Path,out:Path,manifest:Path,flip_rows:bool=False):
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError("original B12 ZIP CRC mismatch")
        raw=z.read(ORIGINAL)
    im=Image.open(io.BytesIO(raw))
    im.load()
    if im.size!=(512,512) or im.mode!="RGBA":
        raise ValueError(f"not the verified B12 original 512x512 RGBA atlas: {im.size} {im.mode}")
    # PNG is top-first; GL texture memory uses the first supplied row as v=0.
    # Allow explicitly flipping the row order once original UV/atlas
    # orientation is verified. Default preserves original decoded bytes.
    rgba=im.tobytes()
    if flip_rows:
        row=512*4
        rgba=b"".join(rgba[k*row:(k+1)*row] for k in range(511,-1,-1))
    header=struct.pack("<4sIIII",b"C1TX",1,512,512,1 if flip_rows else 0)
    data=header+rgba
    assert len(data)==20+512*512*4
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(data)
    meta={"format":"C1TX v1 original B12 user-owned vehicle atlas",
      "source_member":ORIGINAL,
      "source_zip_sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),
      "source_png_sha256":hashlib.sha256(raw).hexdigest(),
      "output_sha256":hashlib.sha256(data).hexdigest(),
      "width":512,"height":512,"rgba_bytes":len(rgba),"total_bytes":len(data),
      "source_decoder":"B12 experimental PVRTC4 -> PNG",
      "flipped_rows_for_gl_v0":flip_rows,
      "original_texture_identification_verified":True,
      "pixel_exactness_vs_original_game_unverified":True,
      "physical_vita_orientation_unverified":True,
      "gameplay_vpk_built":False}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(meta,indent=2)+"\n")
    print("PASS authentic B12 C1L1_Vehicles.png -> C1TX 512x512 RGBA, no VPK")
    return meta
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--flip-rows",action="store_true",help="Explicit experimental OpenGL row inversion")
    a=p.parse_args()
    build(a.archive,a.out,a.manifest,a.flip_rows)
