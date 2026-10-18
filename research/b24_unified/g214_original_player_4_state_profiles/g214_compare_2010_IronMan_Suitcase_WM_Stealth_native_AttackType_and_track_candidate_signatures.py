#!/usr/bin/env python3
"""G214 compare genuine original 2010 *player* StateSet source profiles:
IronMan, IronMan_suitcase, Warmachine, stealth.

Inputs are three separately verified original source JSONs:
 G213C 55 exact native StateSet named intervals,
 G207 every original 'AttackType' key u32 value/file offset,
 G212 'Attack/attack' named track 12B candidate event data.

Compare exact ordered original serialized attack values, 22-value
frequencies, named event candidate raw count/order/signatures WITHOUT
claiming 2010 weapon bindings, identical movesets, missing/different
animation clips or real hit/damage time. Does not require original IPA
or transfer any licensed assets; host CI only. NO VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json
from pathlib import Path
NAMES=("IronMan","IronMan_suitcase","Warmachine","stealth")

def main(sets_path:Path,attacks_path:Path,events_path:Path,out:Path,png:Path):
 sets=json.loads(sets_path.read_text())
 attacks=json.loads(attacks_path.read_text())
 events=json.loads(events_path.read_text())
 original=sets["source_original_55_named_StateSet_archive_intervals"]
 if len(original)!=55 or not sets["source_55_group_names_exact_original_StateSetData_header_read_PROVEN"]:
  raise ValueError("need G213C source-proven all 55 original group intervals")
 byname={r["source_original_StateSet_name"]:r for r in original}
 if not all(name in byname for name in NAMES):raise ValueError("player original 2010 authored groups missing")
 if len(attacks["source_actual_attactype_key_records_with_named_nearby_animation_candidates"])!=379:
  raise ValueError("G207 owner source AttackType catalog incomplete")
 if len(events["source_original_native_Attack_named_12byte_event_candidates"])!=365:
  raise ValueError("G212 original raw candidate events incomplete")
 profiles={}
 for name in NAMES:
  section=byname[name];lo=section["source_original_StateSet_header_offset"]
  hi=section["source_original_StateSet_next_header_or_EOF"]
  rowlist=[
   r for r in attacks["source_actual_attactype_key_records_with_named_nearby_animation_candidates"]
   if lo<=r["owner_state_file_actual_AttackType_key_start_offset"]<hi]
  tracklist=[
   r for r in events["source_original_native_Attack_named_12byte_event_candidates"]
   if lo<=r["original_authored_source_name_prefixed_offset"]<hi]
  rowlist.sort(key=lambda r:r["owner_state_file_actual_AttackType_key_start_offset"])
  tracklist.sort(key=lambda r:r["original_authored_source_name_prefixed_offset"])
  assert len(rowlist)==section["source_original_AttackType_raw_key_count_in_set"]==56
  assert len(tracklist)==section["source_original_named_Attack_attack_raw_candidate_count_in_set"]==40
  values=[r["source_native_contiguous_original_u32_little_endian_value"] for r in rowlist]
  signatures=[{
     "name":r["source_original_track_name"],
     "u16_mode_unclassified":r["source_post_name_original_2byte_field_unclassified"],
     "event_triples":[[e["source_real_2010_start_raw_tick"],e["source_real_2010_duration_raw_tick"],
        e["original_2010_3rd_u32_field_UNCLASSIFIED"]]
        for e in r["source_original_2010_12byte_event_candidate_records"]],
   } for r in tracklist]
  profiles[name]={
   "owner_original_StateSet_name":name,
   "source_original_StateSet_header_start":lo,
   "source_original_StateSet_end":hi,
   "original_source_native_AttackType_key_count":len(values),
   "original_source_AttackType_value_order":values,
   "original_source_AttackType_value_distribution":{str(k):v for k,v in sorted(collections.Counter(values).items())},
   "authored_source_AttackType_record_offset_array":[
     r["owner_state_file_actual_AttackType_key_start_offset"] for r in rowlist],
   "original_source_AttackType_exact_56_values_SHA256":hashlib.sha256(bytes(values)).hexdigest(),
   "source_original_Attack_attack_event_candidates":len(signatures),
   "source_named_event_candidate_signature":signatures,
   "source_named_event_candidate_signature_SHA256":hashlib.sha256(
     json.dumps(signatures,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
   "source_event_candidates_confirmed_as_native_runtime_StateTrack":False,
   "source_which_source_armor_motion_bindings_proven":False,
  }
 names=list(NAMES)
 comparisons=[]
 for a in range(len(names)):
  for b in range(a+1,len(names)):
   one,two=profiles[names[a]],profiles[names[b]]
   valdiff=[i for i,(x,y) in enumerate(zip(one["original_source_AttackType_value_order"],
                                        two["original_source_AttackType_value_order"])) if x!=y]
   same_40=one["source_named_event_candidate_signature"]==two["source_named_event_candidate_signature"]
   comparisons.append({
    "source_original_group_A":names[a],"source_original_group_B":names[b],
    "source_raw_56_AttackType_u32_sequence_equal":len(valdiff)==0,
    "source_exact_AttackType_key_raw_numeric_order_diff_indices":valdiff,
    "source_raw_40_Attack_named_track_CANDIDATE_signature_equal":same_40,
    "native_original_runtime_weapon_input_or_animation_equivalent_PROVEN":False})
    # Even a byte-for-byte match in names/numbers may belong to different
    # active suit mesh, animation, button gating or source WeaponDB rules.
 result={
  "origin":"G214 crosscompare 4 authenticated 2010 original player StateSet groups via native G213C original boundaries, exact G207 u32 state values, G212 raw 12B candidate events",
  "source_original_source_groups_compared":list(NAMES),
  "source_4_native_set_profiles":profiles,
  "source_pairwise_player_state_profile_differences":comparisons,
  "original_4_player_state_set_group_names_exact_proven":True,
  "source_original_2010_ALL_player_StateData_cpp_parser_complete":False,
  "original_native_weapon_to_26_DA_attack_selector_values_PROVEN":False,
  "original_native_genuine_touch_controls_all_resolved":False,
  "Vita_input_or_gameplay_changed":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("G214 REAL SOURCE four original ARM player group 2010 AttackType")
 for name,v in profiles.items():
  print("G214 original",name,"attack keys",v["original_source_native_AttackType_key_count"],
   "attacks",v["original_source_AttackType_value_distribution"],
   "named event candidate groups",v["source_original_Attack_attack_event_candidates"],
   "source raw 56 SHA",v["original_source_AttackType_exact_56_values_SHA256"])
 for c in comparisons:
  print("G214 pairwise genuine source",c["source_original_group_A"],"vs",c["source_original_group_B"],
   "AttackType sequence same",c["source_raw_56_AttackType_u32_sequence_equal"],
   "differing indices",c["source_exact_AttackType_key_raw_numeric_order_diff_indices"],
   "raw event candidate same",c["source_raw_40_Attack_named_track_CANDIDATE_signature_equal"])
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 xs=sorted(set(int(x) for p in profiles.values() for x in p["original_source_AttackType_value_distribution"]))
 ys=[range(len(NAMES))]
 fig,ax=plt.subplots(figsize=(13,5.2),dpi=140)
 width=.19
 for j,name in enumerate(NAMES):
  dist=profiles[name]["original_source_AttackType_value_distribution"]
  ax.bar([i-.285+width*j for i in range(len(xs))],
         [dist.get(str(x),0) for x in xs],width=width,label=name)
 ax.set_xticks(range(len(xs)));ax.set_xticklabels([str(x) for x in xs])
 ax.set_xlabel("Original 2010 serialized AttackType u32 — NOT user controller key")
 ax.set_ylabel("Authentic record count")
 ax.set_title("Iron Man 2 iOS (2010) • source 4 player StateSet AttackType values\nActual authored 56 entries per set, unknown controller & weapon semantics")
 ax.legend(fontsize=9)
 ax.grid(axis="y",alpha=.15)
 fig.tight_layout()
 png.parent.mkdir(parents=True,exist_ok=True);fig.savefig(png);plt.close(fig)
 print("G214 static source player 4 StateSet original value distribution PNG",png.name,png.stat().st_size)
 print("G214 PASS all original true 56*4 values and 40*4 event candidates compared with no claimed Vita hit/damage or controller mappings")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for arg in ("g213c","g207","g212","out","png"):p.add_argument("--"+arg,type=Path,required=True)
 a=p.parse_args()
 main(a.g213c,a.g207,a.g212,a.out,a.png)
