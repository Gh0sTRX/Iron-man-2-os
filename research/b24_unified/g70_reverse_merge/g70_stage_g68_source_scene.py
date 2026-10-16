#!/usr/bin/env python3
"""G70: extract ONLY already-Vita-tested G68 original C1L1 city/collision
source products from owner's existing successful VPK. Do not reconstruct
different scene transforms, lighting, atlas UVs or enemy/player model.
The source original .ipa and all iOS proprietary archives stay out of Git.
"""
from pathlib import Path
import argparse,hashlib,json,struct,zipfile

def stage(vpk:Path,out:Path):
 out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(vpk) as z:
  if z.testzip(): raise ValueError("Damaged prior owner VPK")
  names=set(z.namelist())
  scene=z.read("assets/G66_city.g66m")
  if scene[:4]!=b"G66M" or struct.unpack_from("<4I",scene,4)!=(1,67323,32,31):
   raise ValueError("G68 hardware-proven scene ABI/geometry changed")
  groups=[struct.unpack_from("<4I",scene,20+i*16) for i in range(32)]
  assert len(scene)==20+32*16+67323*24
  cursor=0
  for first,count,tid,flags in groups:
   if first!=cursor or count==0 or count%3 or (tid!=0xffffffff and tid>=31):
    raise ValueError("G68 map source batch layout changed")
   cursor+=count
  if cursor!=67323:raise ValueError("Source city missing faces")
  collision=z.read("assets/G66_original_collision.g66c")
  if collision[:4]!=b"G66C" or struct.unpack_from("<2I",collision,4)!=(1,1910):
   raise ValueError("G68 original 1910 triangle collision drift")
  if len(collision)!=12+1910*36:raise ValueError("G68 native collision bytes changed")
  staged={"G66_city.g66m":scene,"G66_original_collision.g66c":collision}
  for i in range(31):
   name="G66_city_tex_%02d.g66t"%i
   b=z.read("assets/"+name)
   if b[:4]!=b"G66T":raise ValueError("Corrupted city texture "+name)
   version,w,h=struct.unpack_from("<3I",b,4)
   if version!=1 or not (8<=w<=1024 and 8<=h<=1024) or len(b)!=16+w*h*4:
    raise ValueError("Unexpected G68 city atlas size "+name)
   staged[name]=b
  for name,b in staged.items():(out/name).write_bytes(b)
 result={"owner_previously_tested_VPK":vpk.name,
   "geometry_2010_original_triangles":22441,
   "original_source_collision_triangles":1910,
   "city_texture_count":31,
   "GPU_scene_source_sha256":hashlib.sha256(scene).hexdigest(),
   "collision_source_sha256":hashlib.sha256(collision).hexdigest(),
   "files":{n:{"size":len(b),"sha256":hashlib.sha256(b).hexdigest()} for n,b in staged.items()},
   "legacy_B24_gameplay_animation_replaced":False,
   "G68_standalone_update_loop_included":False,
   "hardware_merge_verified":False}
 (out/"G70_CITY_SNAPSHOT_PROVENANCE.json").write_text(json.dumps(result,indent=2)+"\n")
 print("PASS G70 staged exactly the real G68 Vita map, 22441 source polygons, 31 PVR atlases and 1910 original CPU collider triangles")
 return result
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--vpk",type=Path,required=True);ap.add_argument("--out",type=Path,required=True)
 a=ap.parse_args();stage(a.vpk,a.out)
