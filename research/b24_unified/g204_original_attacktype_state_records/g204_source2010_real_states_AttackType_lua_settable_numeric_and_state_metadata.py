#!/usr/bin/env python3
"""G204 genuine original Iron Man 2 iOS (2010) source 'states' Lua51
encoded programs. Decode real native Lua5.1 SETTABLE/SETGLOBAL records
whose EXACT key is AttackType and only PROVEN immediate numeric values.

StateData::GetParam("AttackType",-1) original C++ G203 source code
does not guarantee the game's binary 'states' Lua script pack actually
holds its StateData fields. This scanner therefore reports ZERO evidence
honestly if AttackType isn't in the 55 original Lua programs.

Never infer an AttackType number from a neighboring arbitrary constant,
a filename, or a SetAttackTypeEnabled mission Lua permission. No
executed Lua, no game controller/weapon mapping, no Vita VPK.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua, HEADER

OWNER_SIZE=248613763
def descend(root,path=()):
 yield path,root
 for n,child in enumerate(root["original_child_functions"]):
  yield from descend(child,path+(n,))

def parse_fn(chunk,source_offset,path):
 const=chunk["native_constants"]
 code=chunk["native_function_code"]
 regs={}
 writes=[]
 uses=[]
 numeric=[{"constant_index":i,"native_numeric_value":v} for i,v in enumerate(const)
          if isinstance(v,(float,int)) and not isinstance(v,bool)]
 def rk(n):
  if n>=256:
   j=n-256
   return ("constant",j,const[j]) if 0<=j<len(const) else ("out_of_bounds",j,None)
  return ("register",n,regs.get(n))
 for pc,word in enumerate(code):
  op=word&63
  A=(word>>6)&255;C=(word>>14)&511;B=(word>>23)&511;Bx=(word>>14)&262143
  if op==0:regs[A]=regs.get(B)                # MOVE
  elif op==1:regs[A]=const[Bx] if Bx<len(const) else None # LOADK
  elif op==2:regs[A]=bool(B)                   # LOADBOOL
  elif op==3:
   for i in range(A,B+1):regs[i]=None         # LOADNIL
  elif op==4:regs[A]=None                     # GETUPVAL
  elif op==5:regs[A]=("GLOBAL",const[Bx]) if Bx<len(const) else None
  elif op==6:regs[A]=("TABLE",regs.get(B),rk(C))
  elif op==7:                                  # SETGLOBAL: constant field
   label=const[Bx] if Bx<len(const) else None
   if label=="AttackType":
    uses.append({"kind":"SETGLOBAL","original_native_Lua_PC":pc,
                 "source_reg_A":A,
                 "source_register_static_value_candidate":regs.get(A),
                 "runtime_executed_PROVEN":False})
  elif op==9:                                   # SETTABLE A[B]=RK(C)
   bt,bi,bv=rk(B)
   ct,ci,cv=rk(C)
   if bv=="AttackType":
    value=(cv if isinstance(cv,(int,float)) and not isinstance(cv,bool) else None)
    row={
     "original_native_lua_PC":pc,
     "actual_key_operand_source":bt,
     "actual_key_constant_index":bi if bt=="constant" else None,
     "Lua_input_table_register_A":A,
     "actual_value_operand_source":ct,
     "actual_value_operand_index":ci,
     "original_authored_immediate_number":value if ct=="constant" else None,
     "unconditional_reachable_runtime_source_PROVEN":False,
     "Lua_register_indirect_number_equals_immediate_proven":False,
     "original_2010_native_attack_type_int_definition_proven":ct=="constant" and value is not None,
     "instruction_hex_not_exported":True,
    }
    writes.append(row)
  elif op in (10,11):
   regs[A]=None
   if op==11:regs[A+1]=None
  elif op in (28,29): # CALL/TAILCALL
   regs[A]=None
   if C>1:
    for j in range(A+1,A+C-1):regs[j]=None
  elif op in (12,13,14,15,16,17,18,19,20,21,31,36):
   regs[A]=None
 # Only Lua SETTABLE key matching exact string qualifies as authored
 # static numeric key assignment. Don't treat numeric const nearby.
 return {
   "source_owner_prototype_path":list(path),
   "original_lua_native_bytecode_instruction_count":len(code),
   "genuine_attacktype_constant_indices":[i for i,x in enumerate(const) if x=="AttackType"],
   "source_attacktype_SET_TABLE_entries":writes,
   "source_attacktype_SET_GLOBAL_uses":uses,
   "number_literals_in_this_prototype_without_proven_key_binding":numeric[:100],
 }

def analyze(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("Need exact user owned 2010 IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("authentic owner ZIP CRC failed")
  states=z.read("Payload/IronMan2.app/states")
 signatures=[m.start() for m in re.finditer(re.escape(HEADER[:5]),states)]
 if len(signatures)!=55:raise ValueError("Original 2010 owner states Lua51 signature count no longer 55")
 rows=[];matches=[];total_chunks=0
 for k,offset in enumerate(signatures):
  parser=NativeLua(states,offset)
  if parser.fetch(12)!=HEADER:raise ValueError("Source original state Lua header mismatch")
  root=parser.function()
  if parser.pos>len(states) or (k+1<len(signatures) and parser.pos>signatures[k+1]):
   raise ValueError("Native 2010 state Lua program overruns next")
  total_chunks+=1
  records=[]
  for path,fn in descend(root):
   record=parse_fn(fn,offset,path)
   if record["genuine_attacktype_constant_indices"] or record["source_attacktype_SET_TABLE_entries"] or record["source_attacktype_SET_GLOBAL_uses"]:
    records.append(record)
    matches.append((offset,path,record))
  row={
    "original_lua_state_chunk_number":k,
    "original_2010_binary_source_offset":offset,
    "original_2010_lua_program_original_byte_length":parser.pos-offset,
    "original_2010_source_chunk_SHA256":hashlib.sha256(states[offset:parser.pos]).hexdigest(),
    "source_original_lua51_root_native_proto_count":sum(1 for _ in descend(root)),
    "original_attacktype_name_found_in_lua_bytecode":bool(records),
    "source_2010_attacktype_name_and_assignment_opcodes":records,
    "source_2010_actual_numerical_state_Asset_AttackType_semantics_proven":False,
  }
  rows.append(row)
  print("G204 original 2010 Lua state",k,"offset",offset,"proto",row["source_original_lua51_root_native_proto_count"],"has exact AttackType",bool(records),flush=True)
  for record in records:
   print("G204 genuine AttackType Lua opcode",offset,record["source_owner_prototype_path"],"key",record["genuine_attacktype_constant_indices"],"SETTABLE",record["source_attacktype_SET_TABLE_entries"],"SETGLOBAL",record["source_attacktype_SET_GLOBAL_uses"],flush=True)
 # Lua-only source program evidence; do not label a matched constant
 # as real serialized StateData unless link through native loader is proven.
 report={
  "origin":"G204 exact original 2010 user-owned state Lua5.1 source programs; native StateData key AttackType from G203",
  "source_original_states_archive_bytes":len(states),
  "source_original_states_Lua51_signatures":len(signatures),
  "original_complete_source_Lua_programs_parsed":total_chunks,
  "original_exact_AttackType_lua_prototype_hits":len(matches),
  "source_original_state_lua_meta":rows,
  "native_StateData_GetParam_original_key":"AttackType",
  "native_original_Actor_StateData_AttackType_values_PROVEN":False,
  "g204_original_state_Lua_prototype_contains_native_Actor_StateData_definition_PROVEN":False,
  "original_touch_event_to_26_DoAttack_switchID_mapping_PROVEN":False,
  "original_weapon_to_G83_animation_mapping_PROVEN":False,
  "No_original_Lua_program_executed":True,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G204 original Lua 'states' scripts",total_chunks,"exact AttackType prototype hits",len(matches))
 print("G204 StateData real C++ AttackType is NOT automatically Lua states script AttackType. NO VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 args=p.parse_args()
 analyze(args.ipa,args.out)
