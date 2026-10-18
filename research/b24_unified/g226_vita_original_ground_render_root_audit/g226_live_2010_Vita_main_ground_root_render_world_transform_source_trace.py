#!/usr/bin/env python3
"""G226 truthful Vita C1L1 walk-in-place diagnosis:
Read the single actually reconstructed G171/G218 Vita 'work/src/main.c'
and current B14 world model, native G66C/G108 source collsion integration,
and output line-number source windows for world tick, rendering matrix,
world coordinates, player pose, camera and input/grounded transitions.

Read ONLY (no generated VPK or hardware claim). Do not assume that host
B14 movement proves physical Vita walk. Emits actionable exact callsite
source evidence for subsequent ground render-transform bug patch.
"""
from pathlib import Path
import argparse,json,re
TOKENS=[
 ("physics",r"\bb14_world_tick\s*\("),
 ("render",r"\bglTranslatef\s*\(|\bglMultMatrixf\s*\(|\bglLoadMatrixf\s*\(|\bglPushMatrix\s*\("),
 ("model_matrix",r"\bmodel\b|\bworld\.x\b|\bworld\.y\b|\bworld\.z\b"),
 ("movement_controls",r"\bmove_x\b|\bmove_y\b|\bground_run\b|\bgrounded\b"),
 ("collision",r"\bb24_g75_capsule_reconcile\b|\bb24_g108_grid_clear\b|\bb24_g156\b"),
 ("source_anim",r"\bb24_g8_motion_tick_g84\b|\bb24_g218_observe_actually_loaded_G8_clip\b"),
 ("character",r"draw.*(armor|actor|character|model)|render.*(armor|hero|player)|\bglScalef\b")
]
def scan(path:Path):
 if not path.is_file():return {"exists":False}
 lines=path.read_text(errors="replace").splitlines()
 matches={}
 for label,rx in TOKENS:
  found=[i for i,s in enumerate(lines) if re.search(rx,s,re.IGNORECASE)]
  windows=[]
  # All 1-2 source render/movement windows; preserve enough context to
  # distinguish WORLD-B14 integration from VIEW matrix/actor local offset.
  for i in found[:45 if label in ("physics","render","collision","character") else 28]:
   windows.append({"line_1based":i+1,"source_context":[
     {"line":j+1,"code":lines[j].strip()[:400]}
     for j in range(max(0,i-5),min(len(lines),i+6))]})
  matches[label]={"total_original_source_mentions":len(found),
    "exact_context":windows}
 return {"exists":True,"line_count":len(lines),"sections":matches}
def run(out:Path):
 root=Path(__file__).resolve().parents[3]
 sources=[
  root/"work/src/main.c",
  root/"work/b24/b24_unified/b14_world.c",
  root/"work/b24/b24_unified/b14_pose.c",
  root/"work/src/b14_world.c",
  root/"work/src/b14_pose.c",
  root/"work/b24/b24_unified/b24_g8_live_original_motion.c",
  root/"work/b24/b24_unified/b24_g75_source_capsule.c",
  root/"work/b24/b24_unified/b24_g108_visible_original_wall_grid.c",
 ]
 result={"origin":"G226 original-source Vera Vita C1L1 B14 root movement-to-hero render dataflow audit only, NOT original 2010 mechanics",
  "source_actual_files":{}, "Vita_user_observed_walk_animation_not_world_translation_STILL_UNRESOLVED":True,
  "host_B14_ground_move_and_user_Vita_hardware_same_thing":False,
  "original_2010_iOS_world_to_actor_render_scale_PROVEN":False,
  "real_world_root_to_GPU_MVP_2010_original_equivalence_PROVEN":False,
  "runtime_culprit_identified_from_source_PROVEN":False,
  "gameplay_physics_or_C1L1_renderer_CHANGED":False,
  "NO_VPK":True}
 for path in sources:
  key=str(path.relative_to(root))
  result["source_actual_files"][key]=scan(path)
  d=result["source_actual_files"][key]
  if d["exists"]:
   print("G226 source",key,"TOTAL LINES",d["line_count"],flush=True)
   for group,details in d["sections"].items():
    print("G226 source category",key,group,"matches",details["total_original_source_mentions"],flush=True)
    for window in details["exact_context"][:12]:
     print("G226 actual line",key,group,window["line_1based"],
       "context",json.dumps(window["source_context"],ensure_ascii=False),flush=True)
 if not result["source_actual_files"]["work/src/main.c"]["exists"]:
  raise ValueError("G226 must run on assembled REAL original Vita main, no guessed alternate main source")
 data=result["source_actual_files"]["work/src/main.c"]["sections"]
 for label in ("physics","source_anim","render","movement_controls"):
  if data[label]["total_original_source_mentions"]==0:
   raise ValueError("G226 real final game missing "+label+" pathway, stop source diagnosis")
 result["source_2010_Vita_assembled_main_single_physics_tick_count"] = sum(
  "b14_world_tick" in row["code"] for win in data["physics"]["exact_context"]
  for row in win["source_context"] if row["line"]==win["line_1based"])
 if result["source_2010_Vita_assembled_main_single_physics_tick_count"]!=1:
  raise ValueError("G226 C1L1 live Vita main no unique B14 movement integrator")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("G226 PASS physical Vita ground walk unresolved: real single-main physics->collision->GPU player world matrix source audit READY; no fake movement fix, no VPK",flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.out)
