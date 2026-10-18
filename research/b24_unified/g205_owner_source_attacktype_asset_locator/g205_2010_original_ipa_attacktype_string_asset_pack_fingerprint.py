#!/usr/bin/env python3
"""G205 owner-authentic 2010 Iron Man 2 iOS IPA original source data
pack discovery: locate the literal AttackType key in every original file
of the ZIP, including packed 'states', 'anims', 'clev', script, native
Mach-O and data files, with true decompressed offset for each hit.

This is an ASSET LOCATOR, not claim of executable state field parser or
source weapon enum value. No source raw binary or complete copyrighted
asset is emitted. Only path, asset size, hit offsets and small printable
surroundings (bounded 40 characters) for research provenance.

Never confuse native C++ key global constant in executable with actual
per-weapon ID numeric data in original game files. NO VPK.
"""
from __future__ import annotations
import argparse,collections,json,re,sys,zipfile,hashlib
from pathlib import Path

SIZE=248613763
NEEDLES=(b"AttackType",b"attacktype",b"ATTACKTYPE")
CHUNK=1024*512

def analyze(ipa:Path,out:Path):
 if ipa.stat().st_size!=SIZE:raise ValueError("not the genuine 2010 owner source IPA")
 rows=[]
 targets=[]
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("original ZIP integrity problem")
  for item in z.infolist():
   if item.is_dir():continue
   hits=[];bykind=collections.Counter()
   with z.open(item) as stream:
    context_prev=b"";position=0
    while True:
     chunk=stream.read(CHUNK)
     if not chunk:break
     data=context_prev+chunk
     base=position-len(context_prev)
     for needle in NEEDLES:
      start=0
      while True:
       found=data.find(needle,start)
       if found<0:break
       absolute=base+found
       # Overlapping sample chunk may repeat old hits; only report
       # match when its start is inside newly loaded chunk.
       if absolute>=position:
        lower=max(0,found-40);upper=min(len(data),found+len(needle)+40)
        around=data[lower:upper]
        sanitized="".join(chr(x) if 32<=x<=126 else "." for x in around)
        hits.append({"exact_original_needle":needle.decode("ascii"),
           "real_original_file_decompressed_byte_offset":absolute,
           "bounded_original_ascii_near_key":sanitized,
           "source_native_value_adjacent_byte_not_automatically_attack_enum":True})
        bykind[needle.decode("ascii")]+=1
       start=found+1
     # enough to resolve multi-chunk key; preserve up to 100 previous bytes
     context_prev=data[-100:]
     position+=len(chunk)
   if hits:
    targets.append({"original_owner_IPA_file":item.filename,
       "original_uncompressed_member_bytes":item.file_size,
       "real_original_key_hits":hits[:240],
       "hit_count":len(hits),
       "source_distinct_key_forms":dict(bykind),
       "source_genuine_binary_file_format_decoded_as_StateData":False})
    print("G205 ORIGINAL EXACT ATTACKTYPE FILE",item.filename,"size",item.file_size,
          "total",len(hits),"first offsets",[h["real_original_file_decompressed_byte_offset"] for h in hits[:18]],flush=True)
   rows.append({"owner_original_ZIP_member_path":item.filename,
       "original_member_bytes":item.file_size,
       "exact_original_AttackType_byte_match_count":len(hits)})
 hits_total=sum(r["hit_count"] for r in targets)
 report={
  "source":"Exact owner 2010 Iron Man 2 iOS 1.0.0 original IPA file decompressed textual key locations",
  "original_IPA_member_files_scanned":len(rows),
  "original_member_file_inventory":rows,
  "source_AttackType_exact_key_hit_count":hits_total,
  "source_asset_members_with_exact_attacktype":targets,
  "original_CPP_Actor_GetParam_key_is_AttackType":True,
  "source_native_Actor_StateData_file_loading_path_proven":False,
  "original_attack_type_id_to_weapon_damage_animation_proven":False,
  "original_states_55_Lua_programs_automatically_source_StateData_field":False,
  "original_touch_controls_ALL_recovered":False,
  "NO_SOURCE_ORIGINAL_BINARY_ASSETS_REPUBLISHED":True,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G205 ORIGINAL 2010 IPA files",len(rows),
       "EXACT AttackType hits",hits_total,
       "files",[x["original_owner_IPA_file"] for x in targets])
 print("G205 genuine AttackType asset offsets are NOT proof of int AttackType mapping; no controller remap, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 analyze(a.ipa,a.out)
