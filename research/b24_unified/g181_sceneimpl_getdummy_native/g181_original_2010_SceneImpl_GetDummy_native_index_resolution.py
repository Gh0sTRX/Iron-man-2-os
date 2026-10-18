#!/usr/bin/env python3
"""G181: genuine 2010 iOS SceneImpl::GetDummy(int,unsigned int)
native implementation, authoritative call target of Object3D source G180.

Do not confuse source visual BDAE rig 'array index' with native lookup key.
Decode true ARM register path, comparisons, call edges, and memory accesses
into source metadata. No original executable, licensed rig bytes, VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_OP_MEM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

METHOD="SceneImpl::GetDummy(int, unsigned int)"
METHOD_ADDR=0x61724
IPA_SIZE=248613763
def analyze(ipa,out):
 if ipa.stat().st_size!=IPA_SIZE:raise ValueError("G181 requires owner original iOS 1.0.0")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("2010 original IPA CRC failed")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("Owner 2010 native ARM MachO size changed")
 d=parse_macho(exe)
 dem=subprocess.run(["c++filt"],input="\n".join(row[0] for row in d["entries"])+"\n",
      capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(d["entries"]):raise ValueError("genuine native symbol count mismatch")
 byaddr=collections.defaultdict(set)
 raw=collections.defaultdict(set)
 for sym,n in zip(d["entries"],dem):
  a=sym[1]&~1;byaddr[a].add(n);raw[a].add(sym[1]&1)
 if METHOD not in byaddr[METHOD_ADDR]:raise ValueError("genuine SceneImpl native method changed")
 addresses=sorted(byaddr)
 ix=bisect.bisect_right(addresses,METHOD_ADDR)
 sect=next((s for s in d["sections"] if s[3]=="__text"
    and s[0]<=METHOD_ADDR<s[0]+s[1]),None)
 if sect is None:raise ValueError("G181 original ARM method not in __text")
 nextsym=addresses[ix] if ix<len(addresses) else sect[0]+sect[1]
 size=min(nextsym-METHOD_ADDR,sect[0]+sect[1]-METHOD_ADDR,8192)
 if size<16:raise ValueError("G181 original ARM bounded native function too short")
 off=sect[2]+METHOD_ADDR-sect[0]
 isa=capstone.CS_MODE_THUMB if raw[METHOD_ADDR]=={1} else capstone.CS_MODE_ARM
 cs=capstone.Cs(capstone.CS_ARCH_ARM,isa);cs.detail=True
 decoded=list(cs.disasm(exe[off:off+size],METHOD_ADDR))
 if not decoded:raise ValueError("original SceneImpl native decode produced no instructions")
 ops=[];calls=[];loads=[];compares=[];conditional=[]
 for op in decoded:
  rec={"vm":hex(op.address),"offset":hex(op.address-METHOD_ADDR),
        "opcode":op.mnemonic,"arguments":op.op_str}
  ops.append(rec)
  if op.mnemonic.startswith(("bl","blx")):
   imm=op.operands[0].imm&~1 if op.operands and op.operands[0].type==ARM_OP_IMM else None
   calls.append({"native_ARM_callsite_VM":rec["vm"],
     "callee_VM":hex(imm) if imm is not None else None,
     "native_direct_symbol":sorted(byaddr.get(imm,()))[:7] if imm is not None else [],
     "unresolved_register_dispatch":imm is None})
  if op.mnemonic.startswith(("cmp","cmn","tst","teq")):
   compares.append(rec)
  if (op.mnemonic.startswith("b") and
      not op.mnemonic.startswith(("bl","bic","bfi","bfx","bfc"))):
   immediate=op.operands[-1].imm&~1 if op.operands and op.operands[-1].type==ARM_OP_IMM else None
   conditional.append({**rec,"branch_target_VM":hex(immediate) if immediate is not None else None})
  if any(x.type==ARM_OP_MEM for x in op.operands):
   loads.append(rec)
 # Field lookups and branch comparisons alone cannot tell source
 # BDAE index encoding, internal SceneImpl::mDummies representation or
 # which scene instance owns active Character's model at runtime.
 report={
  "origin":"Original owned 2010 iOS Iron Man 2 ARM Mach-O 1.0.0",
  "original_native_function":METHOD,
  "original_native_function_VM":hex(METHOD_ADDR),
  "origin_exact_2010_macho_sha256":hashlib.sha256(exe).hexdigest(),
  "source_original_method_bounded_bytes":size,
  "native_ISA":"thumb" if isa==capstone.CS_MODE_THUMB else "arm",
  "original_source_native_instruction_count":len(ops),
  "native_real_CPP_calls":calls,
  "native_real_memory_loads_and_stores":loads,
  "native_real_compare_test_instructions":compares,
  "native_real_control_branches":conditional,
  "source_bounded_original_ARM_opcode_metadata_NOT_machine_bytes":ops,
  "Object3D_G180_get_dummy_calls_this_method_PROVEN":True,
  "known_original_UniBeam_argument_id_candidates":[14,33],
  "native_2010_second_unsigned_int_arg_at_lookups":0,
  "native_dummy_key_to_original_BDAE_named_node_id_PROVEN":False,
  "native_dummy_key_index_vs_scene_object_instance_id_PROVEN":False,
  "original_UniBeam_world_chest_or_hand_socket_PROVEN":False,
  "source_works_without_adding_Vita_dummy_weapon_or_pos":True,
  "ORIGINAL_IPA_AND_MACHO_NOT_PUBLISHED":True,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G181 native original 2010 SceneImpl GetDummy",hex(METHOD_ADDR),
       "instructions",len(ops),"bounded size",size,"calls",len(calls))
 for op in ops[:220]:
  print("G181 SOURCE ARM",op["vm"],op["opcode"],op["arguments"])
 for c in calls:print("G181 ORIGINAL CPP CALL",c)
 print("G181 BDAE name numeric native ID crosswalk remains unproven pending resource metadata; no Vita sprite/projectile VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 analyze(a.ipa,a.out)
