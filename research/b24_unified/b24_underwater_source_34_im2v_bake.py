#!/usr/bin/env python3
"""Source-faithful original 2010 Underwater 34 motion IM2V baking prototype.

First 811 of ORIGINAL 840-vertex underwater IM2T are skinned by SOURCE BRES
26-bone palette and validated B13 97-node rig. Remaining 29 original vertices
are kept UNANIMATED and explicitly flagged; don't claim full sixth-suit rig.
Original 34 .anim transform timelines are used. Never invent motion keyframes.
Does NOT change shipped B24/G8 models or VPK; user-owned IPA only.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,sys,tempfile,types,zipfile
from pathlib import Path
import numpy as np
from b24_owner_pack_extract import decode,get_exact
from b24_original_underwater_armor import decode_bres,source as read_underwater
ROOT=Path(__file__).resolve().parents[2]
ANIMZIP=ROOT/"animation_b13/B13_Reproducible_Source.zip"
def load_original_b13(tmp:Path):
 with zipfile.ZipFile(ANIMZIP) as z:
  z.extract("tools/b13_bake.py",tmp)
  z.extract("tools/anim_decoder_b6.py",tmp)
 s=tmp/"tools/b13_bake.py"
 code=s.read_text()
 old="target=raw.find(b'Bip01-node\\0');assert target>0"
 target="""hits=[i for i in range(0,len(raw)-11) if raw[i:i+11]==b'Bip01-node\\0']
    refs=[i for i in hits if sum(raw[k:k+4]==struct.pack('<I',i)
                        for k in range(32,len(raw)-72,4))==1]
    assert len(refs)==1,refs
    target=refs[0]"""
 if code.count(old)!=1 or code.count("1<=nw<=128")!=1:
  raise ValueError("Original B13 source drift")
 code=code.replace(old,target).replace("1<=nw<=128","1<=nw<=512")
 s.write_text(code)
 sys.path.insert(0,str(tmp/"tools"))
 import b13_bake
 return b13_bake
def prepare(original,raw:bytes,meshes:list):
 nodes=original.parse_rig(raw)
 assert len(nodes)==97
 off,names,inv,indices,weights=original.parse_skin(raw,811)
 assert len(names)==26 and len(indices)==811 and weights.shape==(811,4)
 mapped={}
 for node in nodes:
  q=struct.unpack_from("<I",raw,node["offset"]+8)[0]
  if q<len(raw):
   stop=raw.find(b'\0',q)
   if stop<0:continue
   label=raw[q:stop].decode("latin1")
   if label in names:
    if label in mapped:raise ValueError("duplicate original BoneNN palette key")
    mapped[label]=node["name"]
 if len(mapped)!=26:raise ValueError("Underwater original palette unresolved")
 joints=[mapped[x] for x in names]
 rest=original.worlds(nodes)
 err=max(float(np.max(np.abs(rest[j]@inv[i]-np.eye(4)))) for i,j in enumerate(joints))
 if not np.isfinite(err) or err>=2e-4:raise ValueError("source BRES inverse-bind mismatch")
 coords=np.asarray(meshes[0]["positions"],dtype=np.float64)
 tail=np.asarray(meshes[1]["positions"],dtype=np.float64)
 assert coords.shape==(811,3) and tail.shape==(29,3)
 data={"nodes":nodes,"joints":joints,"inv":inv,"indexes":indices,
       "weights":weights,"verts":np.column_stack([coords,np.zeros((811,2))])}
 return data,tail,err
def bake(owner_ipa:Path,out:Path,manifest:Path):
 raw,atlas,rs,archives=read_underwater(owner_ipa)
 _,_,meshes=decode_bres(raw,ROOT/"research/B11_C1L1_Source_Parser.zip")
 with tempfile.TemporaryDirectory(prefix="b24_real_underwater_b13_") as scratch:
  original=load_original_b13(Path(scratch))
  setup,tail,resterr=prepare(original,raw,meshes)
  clips=[]
  records=rs["anims"]
  for rec in records:
   if "underwater" not in rec.name.casefold():continue
   source_clip=get_exact(archives["anims"],records,rec.name)
   if struct.unpack_from("<H",source_clip)[0]!=38:continue
   a=original.decode_anim(source_clip)
   if len(a.names)!=38:raise ValueError("source player clip joint count")
   ms=a.duration_ms
   if ms<0 or ms>60000:raise ValueError("source clip duration")
   ticks=list(range(0,ms,50))+([ms] if ms else [0])
   # Original real source 811 BRES weighted vertices; static auxiliary 29
   # positions are appended for binary ABI ONLY, not asserted rigged.
   vertices=[]
   for t in ticks:
    frame=original.bake_pose(setup,a,t)
    if frame.shape!=(811,3):raise ValueError("original pose vertex layout")
    full=np.concatenate((frame,tail),axis=0).astype("<f4")
    if not np.isfinite(full).all() or float(np.max(np.abs(full)))>100000.:
     raise ValueError("source pose nonfinite or huge")
    vertices.append(full)
   frames=np.stack(vertices)
   name=Path(rec.name).with_suffix(".im2v").name
   payload=struct.pack("<4sIIII",b"IM2V",840,len(ticks),20,ms)+frames.tobytes()
   assert len(payload)==20+840*len(ticks)*12
   out.mkdir(parents=True,exist_ok=True)
   (out/name).write_bytes(payload)
   motion=float(np.max(np.abs(frames[:,:811,:]-frames[0,:811,:])))
   clips.append({"source":rec.name,"im2v":name,"duration_ms":ms,
                 "frames":len(ticks),"vertices":840,
                 "skinned_source_vertices":811,"static_original_vertices":29,
                 "pose_max_deviation":motion,
                 "source_sha256":hashlib.sha256(source_clip).hexdigest(),
                 "im2v_sha256":hashlib.sha256(payload).hexdigest(),
                 "bytes":len(payload)})
  if len(clips)!=34:raise ValueError(f"player source clip coverage {len(clips)} != 34")
  summary={"original_underwater_model":"LC_MC_UnderWater.bdae",
     "original_model_vertices":840,"original_model_triangle_count":1078,
     "source_skeleton_nodes":97,"source_skin_palette":26,
     "skinned_vertices":811,"static_unbound_auxiliary_vertices":29,
     "verified_rest_bind_error":resterr,
     "original_named_animation_files":34,"source_motion_clips":clips,
     "Vita_gpu_animated_suit_active":False,
     "auxiliary_29_vertices_original_attachment_verified":False,
     "not_an_all_rigged_suit":True}
  manifest.parent.mkdir(parents=True,exist_ok=True)
  manifest.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
  print("PASS REAL 2010 UNDERWATER original source 34 IM2V clips / 840 verts / 811 truly weighted, 29 UNBOUND preserved; no new Vita VPK")
  print("SOURCE_B13_ANIMATION_REST_ERR",resterr,
        "CLIPS",len(clips),"TOTAL_ANIMATION_BYTES",sum(x["bytes"] for x in clips))
  return summary
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 p.add_argument("--manifest",required=True,type=Path)
 a=p.parse_args()
 bake(a.ipa,a.out,a.manifest)
