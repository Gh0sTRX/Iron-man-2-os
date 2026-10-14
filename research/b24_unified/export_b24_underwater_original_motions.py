#!/usr/bin/env python3
"""Reconstruct ALL 34 original Underwater player animations from 2010 owner IPA.
Not a rig-retarget: safe IM2A translation+quaternion tracks for separate future
Vita skinning. Nine other underwater-named clips are cannons/bombs/ships and
are NOT player animations. No guessed keyframes or blended animations.
Uses verified B6 original Gameloft decoder + exporter from archived source.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,struct,sys,types,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
ARCH=Path("research/B6_Animation_Decoder_Runtime.zip")
def source_modules():
 with zipfile.ZipFile(ARCH) as z:
  code=z.read("anim_decoder_b6.py")
  export=z.read("export_im2a.py")
 m=types.ModuleType("anim_decoder_b6")
 m.__file__="original_verified_B6_anim_decoder_b6.py"
 sys.modules[m.__name__]=m
 exec(compile(code,m.__file__,"exec"),m.__dict__)
 e=types.ModuleType("original_B6_IM2A_export")
 e.__file__="original_verified_B6_export_im2a.py"
 e.__name__="original_B6_IM2A_export"
 exec(compile(export,e.__file__,"exec"),e.__dict__)
 return m.decode_anim,e.encode_clip
def convert(ipa:Path,destination:Path,manifest:Path):
 decode_anim,encode_clip=source_modules()
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner IPA integrity")
  pack=z.read("Payload/IronMan2.app/anims")
 records=decode(pack,".anim")
 rows=[r for r in records if "underwater" in r.name.casefold()]
 if len(rows)!=43:raise ValueError(f"2010 original underwater clip count {len(rows)} != 43")
 player=[]
 for r in rows:
  source=get_exact(pack,records,r.name)
  if struct.unpack_from("<H",source)[0]==38: player.append((r,source))
 if len(player)!=34:raise ValueError(f"original 38-bone player clips {len(player)} != 34")
 result=[]
 palette=None
 for r,raw in player:
  clip=decode_anim(raw)
  if len(clip.names)!=38:raise ValueError(f"player clip {r.name} bone count drift")
  if len(set(clip.names))!=38:raise ValueError(f"duplicate source rig names {r.name}")
  if palette is None:palette=tuple(clip.names)
  # Original Gameloft 2010 animations legitimately order bone track names
  # differently. IM2A stores EACH original name with its track: matching
  # by numeric track index would be a serious animation skinning defect.
  # Preserve native order per-clip. Do not invent a single rigid track order.
  unique_names=set(clip.names)
  # Some original Gameloft clips encode a long original authoring path
  # among name records. Do not replace it with a guessed Bip01 bone.
  # Preserve that exact source label; flag compatibility for later rig QA.
  matching_names=(unique_names==set(palette))
  data=encode_clip(clip)
  header=struct.unpack_from("<4sHHi",data)
  if header!=(b"IM2A",1,38,clip.duration_ms):raise ValueError("IM2A header integrity")
  if not 0<=clip.duration_ms<=60000:raise ValueError("source clip runtime unsafe")
  name=Path(r.name).with_suffix(".im2a").name
  destination.mkdir(parents=True,exist_ok=True)
  (destination/name).write_bytes(data)
  result.append({"original":r.name,"output":name,"joint_count":38,
                 "duration_ms":clip.duration_ms,"samples":clip.sample_count,
                 "original_source_sha256":hashlib.sha256(raw).hexdigest(),
                 "im2a_sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data),
                 "palette_same_bone_set_as_first_clip":matching_names,
                 "palette_order_same_as_first_clip":tuple(clip.names)==palette,
                 "bone_names_in_original_order":list(clip.names),
                 "new_or_missing_bones":sorted(unique_names ^ set(palette)),
                 "bip01_named_tracks":sum(n.startswith("Bip01") for n in clip.names)})
 if len(result)!=34:raise AssertionError("unreachable")
 out={"provenance":"User-provided real Gameloft Iron Man 2 iOS v1.0.0 IPA 2010 Underwater 38-bone .anim",
      "clips":result,"original_underwater_name_matches":43,
      "original_underwater_player_clips":34,"original_underwater_nonplayer":9,
      "palette_joints":list(palette),
      "all_34_clips_same_bone_name_set":all(x["palette_same_bone_set_as_first_clip"] for x in result),
      "all_34_clips_same_bone_order":all(x["palette_order_same_as_first_clip"] for x in result),
      "all_keyframe_data_true_original":True,
      "Vita_IM2A_tracks_decoded":True,
      "Vita_underwater_rig_skin_weights_verified":False,
      "Vita_animated_underwater_playable":False}
 manifest.parent.mkdir(parents=True,exist_ok=True)
 manifest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 print("PALETTE_SOURCE_COMPARISON same_bone_set",sum(x["palette_same_bone_set_as_first_clip"] for x in result),
       "same_order",sum(x["palette_order_same_as_first_clip"] for x in result),
       "bip01_named_tracks_min",min(x["bip01_named_tracks"] for x in result),
       "bip01_named_tracks_max",max(x["bip01_named_tracks"] for x in result))
 for x in result:
  if not x["palette_same_bone_set_as_first_clip"]:
   print("ORIGINAL_CLIP_NAMES_DIFFER",x["original"],"symmetric_diff",x["new_or_missing_bones"][:14])
 print("PASS 34 genuine 2010 Underwater player motions decoded to original B6 IM2A; 38 named source tracks preserved per clip; NOT playable skinned sixth suit yet")
 return out
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 a.add_argument("--manifest",type=Path,required=True)
 x=a.parse_args()
 convert(x.ipa,x.out,x.manifest)
