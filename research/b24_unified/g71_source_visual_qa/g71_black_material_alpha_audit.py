#!/usr/bin/env python3
"""G71 sourced G68->G70 city RGBA transparent/opaque audit.
Only counts pixels and geometry batches; no original texture data exported.
Artifact itself belongs to owner and stays ephemeral in CI.
"""
from pathlib import Path
import argparse,collections,hashlib,json,struct,zipfile
def audit(vpk):
 with zipfile.ZipFile(vpk) as z:
  assert z.testzip() is None
  data=z.read("assets/G66_city.g66m")
  assert data[:4]==b"G66M" and struct.unpack_from("<4I",data,4)==(1,67323,32,31)
  batches=[struct.unpack_from("<4I",data,20+i*16) for i in range(32)]
  assert len(data)==20+32*16+67323*24
  src_rgba=data[20+32*16:]
  assert all(src_rgba[i]==255 for i in range(23,len(src_rgba),24)), "native geometry vertex alpha drift"
  textures=[]
  for idx in range(31):
   buf=z.read(f"assets/G66_city_tex_{idx:02d}.g66t")
   assert buf[:4]==b"G66T"
   version,w,h=struct.unpack_from("<III",buf,4)
   assert version==1 and len(buf)==16+w*h*4
   a=buf[19::4]
   assert len(a)==w*h
   translucent=sum(alpha<255 for alpha in a)
   cutout=sum(alpha==0 for alpha in a)
   part=sum(0<alpha<255 for alpha in a)
   textures.append({"index":idx,"alpha":int(translucent>0),
    "transparent_pixels":translucent,"cutout_pixels":cutout,
    "partially_transparent_pixels":part,"w":w,"h":h,
    "mip0_bytes":w*h*4})
  transparent_ids=[t["index"] for t in textures if t["alpha"]]
  alpha_groups=[i for i,x in enumerate(batches) if x[2] in transparent_ids]
  counts={"translucent_ids":transparent_ids,
   "transparent_source_groups":alpha_groups,
   "transparent_triangles":sum(batches[i][1]//3 for i in alpha_groups),
   "opaque_triangles":sum(x[1]//3 for i,x in enumerate(batches) if i not in alpha_groups),
   "all_source_triangles":sum(x[1]//3 for x in batches),
   "scene_mip0_rgba_bytes":sum(x["mip0_bytes"] for x in textures),
   "source_geometry_packed_bytes":67323*24,
   "gpu_scene_sha256":hashlib.sha256(data).hexdigest(),
   "gpu_source_pvr_alpha_preserved":True,
   "source_iOS_native_blend_shader_recovered":False,
   "two_pass_device_visually_verified":False}
  assert counts["translucent_ids"]==[1,6,7,9,15,19,20],counts
  assert counts["transparent_triangles"]==1282
  assert counts["opaque_triangles"]==21159
  assert counts["all_source_triangles"]==22441
  return counts
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--vpk",required=True,type=Path)
 a.add_argument("--out",type=Path)
 q=a.parse_args();report=audit(q.vpk)
 if q.out:q.out.write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
