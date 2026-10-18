#!/usr/bin/env python3
"""G176 infer only if directly encoded: original iOS 2010 native UniBeam
Object3D::GetDummyAbsolutePosition(int,int) call arguments.

Input is G97 source-authentic original ARM 2010 disassembled opcode METADATA
(not the private IPA), and G175 original direct native call evidence.
No 'chest' assertion without source dummy-ID/parent and FX assignment proof.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
UNI="MainCharacter::DoUniBeamAttack("
CALLSITE=0xF611C
TARGET=0x159C4

def recent_source_arg(opcodes,i,reg):
 # Conservative ARM AAPCS register argument classification. A previous
 # BL/BLX may clobber r0-r3; an unresolved branch/memory producer makes
 # actual argument UNKNOWN. Do not infer original source socket id.
 before=opcodes[max(0,i-32):i]
 for entry in reversed(before):
  m=entry["mnemonic"].lower()
  args=entry["operand_register_or_literal"]
  if m.startswith(("bl","blx")):
   return {"register":reg,"proof":"UNKNOWN_CLOBBER_BY_PRIOR_CALL"}
  if m in ("b","bx") or m.startswith(("beq","bne","bgt","ble","bge","blt","bhi","bls")):
   return {"register":reg,"proof":"UNKNOWN_CONTROL_FLOW"}
  operands=[p.strip().lower() for p in args.split(",")]
  if not operands or operands[0]!=reg:continue
  if m in ("mov","movs") and len(operands)>1 and operands[1].startswith("#"):
   try: value=int(operands[1][1:],0)
   except ValueError:return {"register":reg,"proof":"UNKNOWN_IMMEDIATE"}
   if 0<=value<0x100000:
    return {"register":reg,"proof":"DIRECT_IMMEDIATE_LAST_WRITER_SAME_BASIC_BLOCK",
            "native_direct_int":value,
            "original_ARM_instruction_PC":entry["pc_hex"]}
  return {"register":reg,"proof":"UNKNOWN_NOT_DIRECT_IMMEDIATE",
          "original_ARM_instruction_PC":entry["pc_hex"],
          "native_opcode":m}
 return {"register":reg,"proof":"UNKNOWN_NO_SAME_BLOCK_WRITER"}

def main(g97:Path,g175:Path,out:Path):
 r=json.loads(g97.read_text())
 g=json.loads(g175.read_text())
 assert r["NO_VPK"] and g["NO_VPK"]
 target=[m for m in r["original_CPP_methods"]
          if m.get("original_symbol_found") and m["source_method"].startswith(UNI)]
 if len(target)!=1:raise ValueError("G176 requires exactly one genuine original UniBeam native method")
 u=target[0]
 assert u["original_ARM_address_hex"]=="0xf60ac"
 calls=[e for e in g["source_direct_weapon_animation_related_callsite_evidence"]
        if e["original_caller_address"]=="0xf60ac"
        and e["original_callsite_VM"]==hex(CALLSITE)
        and e["direct_callee_VM"]==hex(TARGET)
        and any("Object3D::GetDummyAbsolutePosition(int, int)"==n for n in e["direct_callee_symbol"])]
 if len(calls)!=1:raise ValueError("G176 native source call edge changed or wrong method")
 ops=u["full_bounded_original_source_opcode_metadata_NOT_machine_bytes"]
 hits=[i for i,x in enumerate(ops) if int(x["pc_hex"],16)==CALLSITE]
 if len(hits)!=1 or not ops[hits[0]]["mnemonic"].startswith(("bl","blx")):
  raise ValueError("G176 requires EXACT original ARM instruction site")
 i=hits[0]
 candidates=[{"original_arm_vm":x["pc_hex"],"mnemonic":x["mnemonic"],
              "native_assembler_operands":x["operand_register_or_literal"]}
             for x in ops[max(0,i-26):i+1]]
 origin=[recent_source_arg(ops,i,"r1"),recent_source_arg(ops,i,"r2")]
 # Presence of one immediate argument alone does not give the semantic
 # meaning of that argument (node index vs suit/bone vs object index).
 complete=all(x["proof"]=="DIRECT_IMMEDIATE_LAST_WRITER_SAME_BASIC_BLOCK" for x in origin)
 item={
  "origin":"Owner iOS 2010 1.0.0 original ARM Machine Code via authenticated G97 opcode metadata and G175 verified source direct CALL",
  "method_original":"MainCharacter::DoUniBeamAttack(int, Actor*, float, float, vector3d const&)",
  "method_original_ARM_VM":"0xf60ac",
  "source_dummy_lookup_callsite_VM":hex(CALLSITE),
  "actual_native_target":"Object3D::GetDummyAbsolutePosition(int, int)",
  "original_function_VM":hex(TARGET),
  "preceding_original_ARM_opcode_2010_source_evidence_NOT_machine_bytes":candidates,
  "arm_AAPCS_method_argument_r1_r2_last_write_provenance":origin,
  "source_same_basic_block_two_immediates_visible":complete,
  "source_dummy_id_with_correct_semantics_PROVEN":False,
  "source_chest_dummy_node_binding_to_original_2010_rig_PROVEN":False,
  "source_UniBeam_particle_muzzle_world_position_proven":False,
  "original_2010_game_weapon_semantics_PROVEN":False,
  "2010_native_original_source_member_function_direct_CALL_PROVEN":True,
  "NO_NEW_VITA_VFX_OR_DAMAGE":True,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(item,ensure_ascii=False,indent=2)+"\n")
 print("G176 ORIGINAL 2010 UniBeam ARM owner source",hex(CALLSITE),"->",hex(TARGET))
 for p in candidates:print("G176 NATIVE SOURCE",p["original_arm_vm"],p["mnemonic"],p["native_assembler_operands"])
 for x in origin:print("G176 ARG PROOF",x)
 print("G176 chest gun socket claim remains",item["source_chest_dummy_node_binding_to_original_2010_rig_PROVEN"],
       "native callsite is real, no invented emitter/named attachment, NO VPK")
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--g97",type=Path,required=True)
 ap.add_argument("--g175",type=Path,required=True)
 ap.add_argument("--out",type=Path,required=True)
 a=ap.parse_args()
 main(a.g97,a.g175,a.out)
