#!/usr/bin/env python3
"""G27: static, source-authentic 2010 C1L1 Lua 5.1 global CALL opcode evidence.

Consumes owner's original scene bytes. Identifies calls through native GETGLOBAL,
LOADK, MOVE, LOADBOOL, CALL/TailCALL in native instructions. No bytecode
EXECUTION, no full control flow, NO guarantee instructions execute in listed
order or at all. False-positive numeric IDs are avoided by only binding known
entity-argument positions; camera timings/music/sfx/voice IDs are not entities.
"""
from __future__ import annotations
import argparse,collections,json,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_g10_original_lua51_state_and_bclara_record_decode import Parser,HEADER
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize

class NativeLua(Parser):
 def function(self,depth=0):
  if depth>15:raise ValueError("nested Lua 2010 source limit")
  source=self.string()
  line0=self.u32();line1=self.u32()
  nups=self.u8();nargs=self.u8();vararg=self.u8();stack=self.u8()
  n=self.size("bytecode",90000)
  code=[self.u32() for _ in range(n)]
  nconst=self.size("const",50000)
  constants=[]
  for _ in range(nconst):
   typ=self.u8()
   if typ==0:constants.append(None)
   elif typ==1:constants.append(bool(self.u8()))
   elif typ==3:constants.append(struct.unpack("<f",self.fetch(4))[0])
   elif typ==4:constants.append(self.string())
   else:raise ValueError("unexpected native Lua constant tag")
  children=[self.function(depth+1) for _ in range(self.size("prototypes",2048))]
  self.fetch(self.size("lineinfo",500000)*4)
  for _ in range(self.size("locals",90000)):
   self.string();self.u32();self.u32()
  for _ in range(self.size("upvalue_names",2048)):self.string()
  return {"native_function_code":code,"native_constants":constants,
    "original_child_functions":children,"native_source":source,
    "original_line_span":[line0,line1]}

ENTITY_ARGS={
 "SetCamera":(0,),"MoveEntityToEntity":(0,1),"FaceTo":(0,1),
 "PlayAnim":(0,),"SetState":(0,),"Enable":(0,),"Disable":(0,),
 "Show":(0,),"Hide":(0,),"KillSpawnpointEnemy":(0,),
 "DisplayEffect":(0,)
}
SUFFIXES=("_OnInteractComplete","_OnComplete","_OnDestroy","_OnEnter","_OnStart")
def calls(function,idmap):
 const=function["native_constants"]
 register={}
 output=[]
 code=function["native_function_code"]
 branch=0
 def RK(k):
  return const[k-256] if 256<=k<256+len(const) else register.get(k) if k<256 else None
 for pc,word in enumerate(code):
  op=word&63;A=(word>>6)&255;C=(word>>14)&511;B=(word>>23)&511;Bx=(word>>14)&262143
  if op==0:register[A]=register.get(B)
  elif op==1:register[A]=const[Bx] if Bx<len(const) else None
  elif op==2:register[A]=bool(B)
  elif op==3:
   for i in range(A,B+1):register[i]=None
  elif op==4:register[A]=None
  elif op==5:register[A]=("GLOBAL",const[Bx]) if Bx<len(const) else None
  elif op==6:register[A]=("TABLE",register.get(B),RK(C))
  elif op==11:register[A]=("METHOD",register.get(B),RK(C));register[A+1]=register.get(B)
  elif op in (28,29):
   current=register.get(A)
   name=current[1] if isinstance(current,tuple) and current[0]=="GLOBAL" else None
   if isinstance(name,str):
    args=[register.get(j) for j in range(A+1,A+B)] if B>0 else []
    links=[]
    for i,arg in enumerate(args):
     if i not in ENTITY_ARGS.get(name,()):continue
     if isinstance(arg,(int,float)) and not isinstance(arg,bool) and float(arg).is_integer():
      possible=idmap.get(int(arg),[])
      if len(possible)==1:
       node=possible[0]
       links.append({"argument_index":i,"original_source_typed_node_ID":int(arg),
         "original_node_name":node["original_name"],"source_class":node["original_class_name"]})
    output.append({"source_bytecode_PC":pc,"native_global_function":name,
      "literal_or_statically_tracked_arguments":args,
      "source_verified_named_entity_argument_candidates":links,
      "original_native_CALL_opcode":op,
      "static_analysis_not_executed":True})
   # Native CALL results clobber the function register.
   register[A]=None
   if C>1:
    for j in range(A+1,A+C-1):register[j]=None
  elif op in (22,23,24,25,26,27,32,33,34,35):branch+=1
  elif op in (12,13,14,15,16,17,18,19,20,21,31,36):register[A]=None
 return output,{"native_instructions":len(code),"native_branch_loop_related_opcodes":branch}
def report(raw):
 owner=summarize(raw)
 byname={x["original_name"]:x for x in owner["source_2010_typed_class_instances"]}
 byid=collections.defaultdict(list)
 for node in owner["source_2010_typed_class_instances"]:
  byid[node["original_numeric_name_id"]].append(node)
 offsets=[m.start() for m in re.finditer(re.escape(HEADER[:5]),raw)]
 if len(offsets)!=71:raise ValueError("not 71 real source Lua chunks")
 records=[]
 for offset in offsets:
  parser=NativeLua(raw,offset)
  if parser.fetch(12)!=HEADER:raise ValueError("incorrect original Lua 5.1 header")
  root=parser.function()
  label=root["native_constants"][0]
  suffix=next((s for s in SUFFIXES if isinstance(label,str) and label.endswith(s)),None)
  if not suffix or label[:-len(suffix)] not in byname:
   raise ValueError("original source callback name/class owner link failed")
  body=root["original_child_functions"][0] if root["original_child_functions"] else root
  original_calls,stats=calls(body,byid)
  records.append({"original_callback":label,"source_owner_node":label[:-len(suffix)],
     "original_source_callback_offset":offset,"source_native_chunk_bytes":parser.pos-offset,
     "original_static_global_CALL_sites":original_calls,"native_opcode_evidence":stats,
     "script_ran_in_original_game":False})
 totals=collections.Counter(e["native_global_function"] for r in records for e in r["original_static_global_CALL_sites"])
 count=sum(totals.values())
 if count!=1035:raise ValueError("independent owner source global CALL opcode count changed "+str(count))
 start=next(r for r in records if r["original_callback"]=="Mission000_OnStart")
 checks={("SetState",1062),("SetCamera",1864),("SetCamera",1868)}
 confirmed={(e["native_global_function"],int(e["literal_or_statically_tracked_arguments"][0]))
    for e in start["original_static_global_CALL_sites"]
    if e["literal_or_statically_tracked_arguments"] and
    isinstance(e["literal_or_statically_tracked_arguments"][0],float)}
 if not checks<=confirmed:raise ValueError("native first-level MC and 2 camera IDs no longer source backed")
 return {"source_game":"original 2010 Gameloft Iron Man 2 iOS level1.bclara",
   "original_2010_lua_callback_count":len(records),
   "original_native_Lua_GLOBAL_CALL_candidates":count,
   "source_global_native_CALL_site_counts":dict(totals),
   "source_lua_static_CALLBACK_instructions_and_id_links":records,
   "source_original_gameplay_execution_or_mission_flow_PROVEN":False,
   "source_camera_runtime_camera_transforms_PROVEN":False,
   "source_original_audio_anim_ID_to_file_binding_PROVEN":False,
   "source_no_guessed_node_ID_for_music_sfx_wait_duration":True,
   "source_statically_crosslinked_MC_and_CameraPreset_calls":True,
   "new_VPK":False}
def main(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  p=z.read("Payload/IronMan2.app/clev")
  raw=get_exact(p,decode(p,".bclara"),"level1.bclara")
 r=report(raw)
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
 print("G27 genuine first-level 2010 Lua global CALL opcodes",r["original_native_Lua_GLOBAL_CALL_candidates"])
 print("G27 exact source 71 callbacks native function frequency",sorted(r["source_global_native_CALL_site_counts"].items(),key=lambda x:-x[1])[:22])
 print("PASS source 2010 static native Lua GETGLOBAL+CALL registers and original classed camera/MC bindings; NO Lua executed or VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();main(a.ipa,a.out)
