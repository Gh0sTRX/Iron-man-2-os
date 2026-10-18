#!/usr/bin/env python3
"""G217 source-authentic Iron Man 2 2010 iOS -> Vita-ready READ-ONLY
original state / AttackType / native StateTrack time marker table.

Input is G213B's fully decoded 2010 owner original 361393-byte
states binary, 55 groups, 1487 states, 379 exact authored AttackType
fields, 3658 true tracks. Exports precisely 4 owner-player StateSets
(IronMan, IronMan_suitcase, Warmachine, stealth) x 194 states each,
plus genuine 'attack'/'Attack'/'trail' track event raw time markers.
Never creates 'fire', projectiles, animations, damage, input mapping,
or extra guesses. NO VPK. Source-only C11 data for future G83/G169
integration after proper runtime evidence and user device tests.
"""
from __future__ import annotations
import argparse,json,collections
from pathlib import Path
ARMOR_NAMES=("IronMan","IronMan_suitcase","Warmachine","stealth")
HIT_NAMES=("attack","Attack","trail")
STATE_COUNT=194
def getp(st,key):
 return next((x["source_value_u32"] for x in st["source_original_state_params"] if x["name"]==key),None)
def emit(original:Path,out_dir:Path):
 d=json.loads(original.read_text())
 if (d["source_original_2010_StateSet_count"]!=55 or
     d["source_original_2010_StateData_count"]!=1487 or
     d["source_original_StateTrack_count"]!=3658 or
     d["source_original_AttackType_key_u32_value_count"]!=379 or
     d["source_original_named_Attack_attack_track_count"]!=369 or
     not d["source_original_all_bytes_consumed_exactly"]):
  raise ValueError("requires exact full original iOS G213B 55-set source file binary proof")
 groups={r["original_2010_StateSet_name"]:r for r in d["source_original_2010_state_sets_all"]}
 rows=[];events=[];armor_summaries={}
 for suit_no,name in enumerate(ARMOR_NAMES):
  records=groups[name]["source_authentic_2010_StateData"]
  if len(records)!=STATE_COUNT:raise ValueError("original owner player state count drift "+name)
  nt=sum(r["source_original_tracks_in_event_channels"] for r in records)
  if nt!=612:raise ValueError("original owner player StateTrack count drift "+name)
  na=0
  for index,st in enumerate(records):
   if st["source_original_state_record_index"]!=index:
    raise ValueError("original state native index mapping order changed")
   attack_values=st["source_original_attacktype_exact_definitions"]
   if len(attack_values)>1:raise ValueError("multiple original authored AttackType values for a state not expected")
   attacktype=attack_values[0]["value"] if attack_values else None
   if attacktype is not None:
    na+=1
    if not 0<=attacktype<=25:raise ValueError("original DoAttack selector source outside 26 native cases")
   rows.append({
    "original_owner_2010_armor_name":name,"native_original_suit_group_index":suit_no,
    "native_original_StateData_index":index,"original_2010_state_name":st["source_original_state_name"],
    "original_2010_attack_type_u32":attacktype,
    "original_2010_state_type_u32":getp(st,"type"),
    "original_2010_next_state_u32":getp(st,"next_state"),
    "original_2010_loop_u32":getp(st,"loop"),
    "original_2010_canChangeAtOnce_u32":getp(st,"canChangeAtOnce"),
    "source_original_StateTrack_count":st["source_original_tracks_in_event_channels"],
    "original_source_2010_state_data_record_absolute_offset":st["source_native_binary_record_start"],
    "original_2010_state_id_is_native_Lua_or_controller_button":False,
   })
   for ch in st["source_original_event_channels"]:
    for track in ch["source_2010_attached_track_records"]:
     if track["native_original_track_name"] not in HIT_NAMES:continue
     for entry in track["source_authentic_2010_event_records"]:
      events.append({
       "original_2010_owner_armor":name,"native_2010_armor_enum_source_only":suit_no,
       "original_state_native_index":index,
       "original_StateTrack_name":track["native_original_track_name"],
       "source_original_raw_event_start":entry["start_source_raw_integer"],
       "source_original_raw_event_duration":entry["duration_source_raw_integer"],
       "source_original_raw_event_end":entry["end_start_plus_duration"],
       "source_original_event_third_u32_UNCLASSIFIED":entry["third_u32_unknown_semantics"],
       "original_native_StateTrack_file_offset":entry["source_original_offset"],
       "confirmed_original_melee_hit_damage_or_projectile_fire_time":False,
      })
  if na!=56:raise ValueError("original player 56 AttackType rows expected "+name)
  armor_summaries[name]={"native_original_state_count":len(records),
    "original_native_attacks_with_AttackType":na,
    "original_full_StateTrack_count":nt,
    "original_source_named_attack_trail_events":sum(x["original_2010_owner_armor"]==name for x in events)}
 def found(suit,state):
  return next(x for x in rows if x["original_owner_2010_armor_name"]==suit and
              x["original_2010_state_name"]==state)
 actual={
  "IronMan":{"Attack_Float_idle":1,"Attack_M_Float_idle":2,"Attack_M_Ground_idle":2,
             "Attack_Ground_COMBO1":0,"Attack_Ground_Beam":4,"Attack_Float_Beam":4},
  "IronMan_suitcase":{"Attack_Float_idle":1,"Attack_M_Float_idle":2,"Attack_M_Ground_idle":2,
             "Attack_Ground_COMBO1":0,"Attack_Ground_Beam":4,"Attack_Float_Beam":4},
  "Warmachine":{"Attack_Float_idle":18,"Attack_M_Float_idle":25,"Attack_M_Ground_idle":25,
             "Attack_Ground_COMBO1":0,"Attack_Ground_Beam":4,"Attack_Float_Beam":4},
  "stealth":{"Attack_Float_idle":1,"Attack_M_Float_idle":2,"Attack_M_Ground_idle":2,
             "Attack_Ground_COMBO1":0,"Attack_Ground_Beam":4,"Attack_Float_Beam":4},
 }
 for suit,req in actual.items():
  for label,want in req.items():
   if found(suit,label)["original_2010_attack_type_u32"]!=want:
    raise ValueError("source 2010 original native state named AttackType changed "+suit+" "+label)
 # Presence of original G169/G195 authentic Beam clips, however, does
 # NOT by itself prove a 1:1 name/damage timestamp or override the G83
 # canonical animator. This export stays read-only until that proof.
 out_dir.mkdir(parents=True,exist_ok=True)
 meta={
  "source":"G217 real original 2010 iOS StateDatabase 55 original sets / 1487 StateData / 3658 StateTrack fully parsed G213B",
  "source_true_owner_2010_players":list(ARMOR_NAMES),
  "source_original_suit_state_count":len(rows),
  "source_original_suit_attack_trail_event_data_records":len(events),
  "source_2010_true_armor_counts":armor_summaries,
  "source_original_player_state_table":rows,
  "source_original_player_attack_trail_event_rows":events,
  "raw_event_time_unit_is_milliseconds_PROVEN":False,
  "source_named_original_attack_track_record_proves_HIT_DAMAGE_or_AIM_M_fire":False,
  "source_original_touch_joystick_control_binding_proven":False,
  "source_original_2010_hit_sound_weapon_projectile_spawn_timestamp_proven":False,
  "source_2010_original_2010_event_tracks_native_all_records_loaded_by_Parser":True,
  "G83_G169_live_Vita_animation_or_weapon_input_CHANGED":False,
  "NO_VPK":True}
 (out_dir/"G217_ORIGINAL_2010_4_SUITS_776_NATIVE_STATES_AND_ATTACK_EVENTS.json").write_text(
  json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
 header=[
  "/* G217 original owner iOS 2010 StateData source-only, G213B exact 55 state-set parse.",
  " * Real source AUTHORED data, no generated G83 action/weapon/damage behavior, no VPK.",
  " * Original 2010 raw event ticks have UNKNOWN unit; do not claim milliseconds.",
  " */",
  "#ifndef B24_G217_AUTHENTIC_2010_NATIVE_SOURCE_STATES_H",
  "#define B24_G217_AUTHENTIC_2010_NATIVE_SOURCE_STATES_H",
  "#include <stdint.h>",
  "#define B24G217_ARMOR_COUNT 4",
  "#define B24G217_SOURCE_STATES_PER_ARMOR 194",
  "#define B24G217_UNKNOWN_U32 UINT32_C(0xffffffff)",
  "typedef struct B24G217_SourceState {",
  "  const char *original_source_state_name;",
  "  uint32_t original_AttackType_or_UNKNOWN;",
  "  uint32_t original_next_state_or_UNKNOWN;",
  "  uint32_t original_state_type_or_UNKNOWN;",
  "  uint32_t original_loop_or_UNKNOWN;",
  "  uint16_t native_source_state_index;",
  "  uint16_t original_state_track_count;",
  "} B24G217_SourceState;",
  "typedef struct B24G217_SourceEvent {",
  "  const char *native_original_track_name;",
  "  uint32_t raw_original_2010_start;",
  "  uint32_t raw_original_2010_duration;",
  "  uint32_t raw_original_2010_third_field_UNCLASSIFIED;",
  "  uint16_t native_suit_group_index;",
  "  uint16_t native_original_state_index;",
  "} B24G217_SourceEvent;",
  "static const char *const b24g217_original_suit_source_names[4]={",
  ','.join(json.dumps(x) for x in ARMOR_NAMES)+"};",
  "static const B24G217_SourceState b24g217_true_2010_owner_states[4][194]={",
 ]
 for suit in ARMOR_NAMES:
  header.append("  { /* exact original source native StateSet: "+suit+" */")
  for r in [x for x in rows if x["original_owner_2010_armor_name"]==suit]:
   val=lambda key:"B24G217_UNKNOWN_U32" if r[key] is None else str(r[key])+"u"
   header.append("    {"+",".join([json.dumps(r["original_2010_state_name"]),
     val("original_2010_attack_type_u32"),val("original_2010_next_state_u32"),
     val("original_2010_state_type_u32"),val("original_2010_loop_u32"),
     str(r["native_original_StateData_index"])+"u",
     str(r["source_original_StateTrack_count"])+"u"])+"},")
  header.append("  },")
 header+=["};", "#define B24G217_TRUE_SOURCE_ATTACK_TRAIL_EVENT_COUNT "+str(len(events))]
 header.append("static const B24G217_SourceEvent b24g217_source_attack_trail_events["+str(len(events))+"]={")
 for e in events:
  header.append("  {"+",".join([json.dumps(e["original_StateTrack_name"]),
   str(e["source_original_raw_event_start"])+"u",
   str(e["source_original_raw_event_duration"])+"u",
   str(e["source_original_event_third_u32_UNCLASSIFIED"])+"u",
   str(e["native_2010_armor_enum_source_only"])+"u",
   str(e["original_state_native_index"])+"u"])+"},")
 header.extend(["};","#endif /* B24_G217_AUTHENTIC_2010_NATIVE_SOURCE_STATES_H */"])
 (out_dir/"b24_g217_AUTHENTIC_original_2010_iOS_source_states_ONLY_NO_VPK.h").write_text("\n".join(header)+"\n")
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 wanted=["Attack_Ground_COMBO1","Attack_Ground_COMBO2","Attack_Ground_COMBO3",
         "Attack_M_Ground_idle","Attack_M_Float_idle","Attack_Ground_Beam_out","Attack_Float_Beam_out"]
 suit="IronMan"; y=[];ticks=[]
 for state in wanted:
  record=found(suit,state)
  entry=[e for e in events if e["original_2010_owner_armor"]==suit and
         e["original_state_native_index"]==record["native_original_StateData_index"] and
         e["original_StateTrack_name"].lower()=="attack"]
  if not entry:raise ValueError("source original Attack timeline missing for "+state)
  y.append(state)
  ticks.append(entry[0]["source_original_raw_event_start"])
 fig,ax=plt.subplots(figsize=(11,5.8),dpi=140)
 for i,(label,start) in enumerate(zip(y,ticks)):
  ax.hlines(i,0,start,alpha=.25,linewidth=2)
  ax.plot([start],[i],"o",markersize=8)
  ax.text(start+15,i,str(start),va="center",fontsize=9)
 ax.set_yticks(list(range(len(y))),y)
 ax.invert_yaxis()
 ax.set_xlabel("Authentic 2010 StateTrack raw event start (unit not proven)")
 ax.set_title("Iron Man 2 iOS (2010) • original combat source StateTrack markers\nNot yet proven actual damage, projectile spawn, or millisecond values")
 ax.set_xlim(left=0,right=max(ticks)+135)
 ax.grid(axis="x",alpha=.15)
 fig.tight_layout()
 fig.savefig(out_dir/"G217_ORIGINAL_2010_REAL_MOVEMENT_COMBO_BEAM_ATTACK_MARKERS_STATIC.png")
 plt.close(fig)
 print("G217 source original 4 suits x194 states",len(rows),"true original 'attack/Attack/trail' event data",len(events))
 print("G217 source actual IRONMAN Combo1,Combo2,Combo3,Mground,Mfloat,BeamgroundOut,BeamfloatOut:",dict(zip(y,ticks)))
 print("G217 native original WM AttackType18 vs IM1 and WM25 vs IM2 preserved; real shot/hit/touch semantics UNKNOWN")
 print("G217 owner source-only C11 state header and noninteractive PNG done, never a VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--g213",required=True,type=Path)
 p.add_argument("--outdir",required=True,type=Path)
 a=p.parse_args()
 emit(a.g213,a.outdir)
