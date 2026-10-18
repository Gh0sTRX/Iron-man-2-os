#!/usr/bin/env python3
"""G175 real 2010 owner's original iOS ARM Mach-O:
trace native Missile/UniBeam/WeaponDB/AttackType/game-animation method
edges without inventing original Aim_M controller transitions.

Only method names, addresses, bounded CALL-site metadata, and proven graph
edges are exported. No executable, instructions, assets, raw strings, or VPK.
An observed CALL EDGE cannot establish a concrete weapon-to-clip ID, true
animation state, frame hit time, muzzle socket or input binding by itself.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

OWNER_SIZE=248613763
TARGETS={
 "throw_missile":"MainCharacter::ThrowMissile(",
 "unibeam":"MainCharacter::DoUniBeamAttack(",
 "weapon_attack_lookup":"WeaponDB::GetAttackEntityByIndex(",
 "weapon_find_id":"WeaponDB::FindWeaponEntityById(",
 "weapon_attack_load":"AttackEntity::LoadFromFile(",
 "weapon_attack_fire":"AttackEntity::DoAttack(",
 "weapon_projectile":"AttackEntity::DoProjectileAttack(",
 "mission_attack_toggle":"SetAttackTypeEnabled",
 "melee":"MainCharacter::StartMeleeAttack(",
 "melee_update":"MainCharacter::UpdateMeleeAttackState(",
}
SCAN=re.compile(r"^(MainCharacter|WeaponDB|AttackEntity|ProjectileEntity|WeaponAccessory|"
                r"GamePlayUI|GS_GamePlay|StatesMgr|Anim|Animation|Model|"
                r"WeaponEntity|Lua|Script)",re.I)
ANIM=re.compile(r"anim|motion|state|pose|clip|sequence|blend|skeleton|rig",re.I)
WEAPON=re.compile(r"missile|beam|weapon|attack|fire|projectile|input|shot",re.I)

def canonical(a):
 return a & ~1
def is_direct_call(ins):
 if not ins.mnemonic.startswith(("bl","blx")):return None
 if not ins.operands or ins.operands[0].type!=ARM_OP_IMM:return None
 return canonical(ins.operands[0].imm)
def find_paths(start,end,graph,depth=3):
 # Static direct-call reachability, NOT proof of controller input or
 # selected source animation. Never follow virtual register BLX here.
 q=collections.deque([(start,[start])])
 while q:
  cur,path=q.popleft()
  if len(path)>depth:continue
  for nxt in graph.get(cur,()):
   if nxt in path:continue
   if nxt in end:yield path+[nxt]
   elif len(path)<depth:q.append((nxt,path+[nxt]))

def analyze(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("Not exact 2010 owner IPA length")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("source IPA CRC error")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("Original 2010 Mach-O size drift")
 native=parse_macho(exe)
 rows=native["entries"]
 names=subprocess.run(["c++filt"],input="\n".join(r[0] for r in rows)+"\n",
                      capture_output=True,text=True,check=True).stdout.splitlines()
 if len(names)!=len(rows):raise ValueError("Original symbol demangle mismatch")
 textsecs=[s for s in native["sections"] if s[3]=="__text"]
 addresses=sorted(set(canonical(r[1]) for r in rows))
 byaddr=collections.defaultdict(set)
 rawaddresses=collections.defaultdict(set)
 for row,name in zip(rows,names):
  addr=canonical(row[1]);byaddr[addr].add(name)
  rawaddresses[addr].add(row[1])
 target_matches={key:sorted([(hex(canonical(r[1])),name)
               for r,name in zip(rows,names) if prefix in name])
                 for key,prefix in TARGETS.items()}
 for key in ("throw_missile","unibeam","weapon_attack_lookup","weapon_attack_load"):
  if not target_matches[key]:raise ValueError("Missing original C++ symbol "+key)
 # Bound original 2010 names to actual method functions in __text.
 for key,expected in (("throw_missile","0xea850"),("unibeam","0xf60ac")):
  if expected not in {a for a,_ in target_matches[key]}:
   raise ValueError("original source native method address changed "+key)
 selected={}
 for addr,labels in byaddr.items():
  if any(SCAN.search(n) or "SetAttackTypeEnabled" in n for n in labels):
   selected[addr]=sorted(labels)
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for d in (arm,thumb):d.detail=True
 edges=[]
 analyzed=[]
 selectedgraph=collections.defaultdict(set)
 allcallcount=0
 missing=0
 for addr,labels in sorted(selected.items()):
  sec=next((s for s in textsecs if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:missing+=1;continue
  nextindex=bisect.bisect_right(addresses,addr)
  right=addresses[nextindex] if nextindex<len(addresses) else sec[0]+sec[1]
  length=min(right-addr,sec[0]+sec[1]-addr,8192)
  if length<4:continue
  ofs=sec[2]+addr-sec[0]
  if ofs<0 or ofs+length>len(exe):raise ValueError("source bounded method out of Mach-O")
  isthumb=all(bool(a&1) for a in rawaddresses[addr])
  decoder=thumb if isthumb else arm
  instructions=list(decoder.disasm(exe[ofs:ofs+length],addr))
  if not instructions:continue
  direct=[]
  indirect=0
  for i in instructions:
   if i.mnemonic.startswith(("bl","blx")):
    target=is_direct_call(i)
    allcallcount+=1
    if target is None:
     indirect+=1;continue
    selectedgraph[addr].add(target)
    exact=sorted(byaddr.get(target,()))
    edge={
      "original_caller_address":hex(addr),
      "original_caller_symbol":labels[:5],
      "original_callsite_VM":hex(i.address),
      "direct_callee_VM":hex(target),
      "direct_callee_symbol":exact[:5],
      "virtual_indirect_target_assumed":False,
    }
    # Report calls from weapon core and calls to useful weapon/animation
    # methods only; avoid huge unrelated subsystem dumps.
    important=any(WEAPON.search(l) for l in labels) or any(
                 (WEAPON.search(n) or ANIM.search(n)) for n in exact)
    if important:edges.append(edge)
    if len(direct)<200:direct.append({"native_callsite_hex":hex(i.address),
                                    "native_target_hex":hex(target),
                                    "target_symbols":exact[:4]})
  if any(WEAPON.search(l) or ANIM.search(l) for l in labels):
   analyzed.append({"native_address_hex":hex(addr),
                    "source_names":labels[:6],
                    "native_ISA":"THUMB" if isthumb else "ARM",
                    "bounded_bytes":length,
                    "source_instructions_decoded":len(instructions),
                    "direct_call_edges":direct,
                    "unresolved_blx_register_calls":indirect,
                    "original_method_body_semantics_fully_proven":False})
 # Static addresses only, no guessing what kind of animation 'M' is.
 core={name:{int(a,16) for a,_ in target_matches[name]}
       for name in TARGETS}
 animated={addr for addr,labels in byaddr.items()
           if any(ANIM.search(s) for s in labels) and addr in selected}
 path_summary={}
 for key in ("throw_missile","unibeam","weapon_attack_lookup","melee"):
  paths=[]
  for start in sorted(core[key]):
   for p in find_paths(start,animated,selectedgraph,3):
    paths.append([{"VM":hex(a),"names":sorted(byaddr.get(a,()))[:3]} for a in p])
    if len(paths)>=30:break
   if len(paths)>=30:break
  path_summary[key]=paths
 direct_target_edges={}
 for src in ("throw_missile","unibeam","weapon_attack_lookup","weapon_find_id","weapon_attack_fire"):
  direct_target_edges[src]={}
  for dest in ("unibeam","throw_missile","weapon_attack_lookup",
               "weapon_find_id","weapon_projectile","weapon_attack_fire"):
   count=sum(dst in core[dest] for s in core[src] for dst in selectedgraph.get(s,()))
   direct_target_edges[src][dest]=count
 # Source metadata proves labels and known callee addresses only.
 report={
   "project":"2010 owner iOS Iron Man 2 native weapon/animation bridge forensic G175",
   "verified_2010_arm_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
   "owner_iOS_arm_native_symbol_count":native["nsyms"],
   "original_native_method_target_matches":target_matches,
   "scanned_selected_CPP_text_methods":len(selected),
   "verified_bounded_selected_CPP_text_methods":len(analyzed),
   "selected_native_direct_and_indirect_call_total":allcallcount,
   "selected_native_functions_without_text":missing,
   "source_direct_weapon_animation_related_callsite_evidence":edges[:3500],
   "original_native_methods_selected_bounded_CALL_evidence":analyzed,
   "named_weapon_direct_function_edges":direct_target_edges,
   "named_weapon_to_any_animation_named_method_direct_chain_max3":path_summary,
   "original_2010_Aim_M_weapon_semantics_PROVEN":False,
   "original_2010_weaponID_to_Aim_M_clip_exact_native_transition_PROVEN":False,
   "original_2010_missile_weapon_kind_from_an_Aim_M_name_PROVEN":False,
   "original_2010_Unibeam_actual_native_B16_port_event_PROVEN":False,
   "original_2010_weapon_muzzle_Gun01_Gun04_proven":False,
   "original_2010_weapon_damage_frames_proven":False,
   "direct_call_edges_are_not_runtime_branch_reachability_or_argument_mapping":True,
   "no_proprietary_executable_or_raw_arm_machine_bytes_published":True,
   "NO_VPK":True,
 }
 out.mkdir(parents=True,exist_ok=True)
 dest=out/"G175_OWNER_2010_WEAPONDB_MISSILE_UNIBEAM_ANIMATION_NATIVE_CALLGRAPH_NO_VPK.json"
 dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G175 real ORIGINAL 2010 native Mach-O symbol total",native["nsyms"],
       "selected C++ methods",len(selected),"decoded",len(analyzed),
       "CALL opcodes",allcallcount)
 for name,matched in target_matches.items():
  print("G175 ORIGINAL NATIVE TARGET",name,matched[:10])
 for caller,row in direct_target_edges.items():
  print("G175 VERIFIED native direct method CALL sites from",caller,row)
 for source,paths in path_summary.items():
  print("G175 STATIC graph candidate routes",source,len(paths),
        [(p[-1]["VM"],p[-1]["names"]) for p in paths[:8]])
 print("G175 original Aim_M actual weapon mapping UNKNOWN unless original"
       " animation-state argument is decoded. NO G8/G83 fake missile hook; NO VPK.")

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--ipa",type=Path,required=True)
 ap.add_argument("--out",type=Path,required=True)
 a=ap.parse_args()
 analyze(a.ipa,a.out)
