#!/usr/bin/env python3
"""G180 native iOS 2010 Object3D::GetDummyAbsolutePosition(int,int)
and real owner BDAE rig source crosswalk, without assigning unproven semantics.

Read original user-owned IPA only in ephemeral Actions; extract original native
CALL/ARM memory/control flow and real authored rig-node order and parents.
The numeric UniBeam args 14/33 are *function input ints*, NOT yet native
BDAE list indices/bone names, muzzle emitters or verified socket transforms.
No new original game binary, image asset, Vita patch, projectile, or VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,hashlib,re,subprocess,sys,tempfile,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_OP_MEM
from b24_owner_pack_extract import decode,get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13
from g76_original_combat.g76_2010_native_arm_combat_method_provenance import parse_macho

OWNER_SIZE=248613763
NATIVE_ADDR=0x159c4
LOOKUP_NAME="Object3D::GetDummyAbsolutePosition(int, int)"
UNIBEAM_ARGS=(14,33)

def main(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("G180 requires exact original owner iOS IPA size")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("Source original iOS 2010 ZIP CRC mismatch")
  executable=z.read("Payload/IronMan2.app/IronMan2")
  models=z.read("Payload/IronMan2.app/models")
 if len(executable)!=7480208:raise ValueError("Original 2010 ARM executable unexpectedly changed")
 origin=parse_macho(executable)
 labels=subprocess.run(["c++filt"],input="\n".join(x[0] for x in origin["entries"])+"\n",
                        text=True,capture_output=True,check=True).stdout.splitlines()
 if len(labels)!=len(origin["entries"]):raise ValueError("native original 2010 C++ symbol parse mismatch")
 symbols=collections.defaultdict(set)
 rawflags=collections.defaultdict(set)
 for rec,name in zip(origin["entries"],labels):
  loc=rec[1]&~1
  symbols[loc].add(name)
  rawflags[loc].add(rec[1]&1)
 if LOOKUP_NAME not in symbols[NATIVE_ADDR]:
  raise ValueError("Native Object3D dummy method address/name mismatch")
 sec=next((s for s in origin["sections"] if s[3]=="__text"
           and s[0]<=NATIVE_ADDR<s[0]+s[1]),None)
 if sec is None:raise ValueError("Original dummy lookup ARM not in code")
 addresses=sorted(symbols)
 ix=bisect.bisect_right(addresses,NATIVE_ADDR)
 nxt=addresses[ix] if ix<len(addresses) else sec[0]+sec[1]
 size=min(nxt-NATIVE_ADDR,sec[0]+sec[1]-NATIVE_ADDR,4096)
 if size<16:raise ValueError("Original GetDummyAbsolutePosition source truncated")
 ofs=sec[2]+NATIVE_ADDR-sec[0]
 decoder=capstone.Cs(capstone.CS_ARCH_ARM,
                    capstone.CS_MODE_THUMB if rawflags[NATIVE_ADDR]=={1} else capstone.CS_MODE_ARM)
 decoder.detail=True
 instructions=list(decoder.disasm(executable[ofs:ofs+size],NATIVE_ADDR))
 if len(instructions)<5:raise ValueError("Original dummy function native instructions missing")
 entries=[];direct=[];mem=[];compares=[];branches=[]
 for k,op in enumerate(instructions):
  r={"vm":hex(op.address),"offset":hex(op.address-NATIVE_ADDR),
     "mnemonic":op.mnemonic,"args":op.op_str}
  entries.append(r)
  if op.mnemonic.startswith(("bl","blx")):
   target=op.operands[0].imm&~1 if op.operands and op.operands[0].type==ARM_OP_IMM else None
   direct.append({"site":hex(op.address),"target":hex(target) if target is not None else None,
       "direct_native_symbol":sorted(symbols.get(target,set()))[:8] if target is not None else [],
       "unresolved_indirect_virtual_dispatch":target is None})
  if op.mnemonic.startswith(("cmp","cmn","tst","teq")):
   compares.append(r)
  if op.mnemonic.startswith("b") and not op.mnemonic.startswith(("bl","bic","bfi","bfx")):
   target=op.operands[-1].imm&~1 if op.operands and op.operands[-1].type==ARM_OP_IMM else None
   branches.append({**r,"direct_target":hex(target) if target is not None else None})
  if any(operand.type==ARM_OP_MEM for operand in op.operands):
   mem.append(r)
 # Do not mislabel BRES parsed-order index as original native Dummy ID.
 records=decode(models,".bdae")
 selected=[rec for rec in records if re.search(
  r"iron.?man|mark.?[456]|suitcase|warmachine|war_machine|stealth",rec.name,re.I)]
 with tempfile.TemporaryDirectory(prefix="g180_source_b13_") as temp:
  b13=load_original_b13(Path(temp))
  candidates=[]
  for rec in selected:
   raw=get_exact(models,records,rec.name)
   try:
    rig=b13.parse_rig(raw)
   except (ValueError,AssertionError,KeyError,IndexError,TypeError) as e:
    candidates.append({"original_owner_resource":rec.name,
        "authored_rig_nodes_parsed":False,"parser_error":type(e).__name__+": "+str(e)[:160]})
    continue
   if len(rig)>1000 or len(rig)<1:raise ValueError("invalid original model rig length")
   parsed=[]
   for k,n in enumerate(rig):
    name=n.get("name")
    if not isinstance(name,str):raise ValueError("source node name corrupt "+rec.name)
    parsed.append({
      "B13_parser_traversal_ordinal_NOT_NATIVE_DUMMY_ID":k,
      "source_original_rig_name":name,
      "source_bres_record_offset":n.get("offset"),
      "original_source_parent_name":n.get("parent"),
      "name_contains_dummy":bool(re.search("dummy",name,re.I)),
    })
   neighbors={}
   for numeric in UNIBEAM_ARGS:
    if 0<=numeric<len(parsed):
     neighbors[str(numeric)]=[parsed[i] for i in range(max(0,numeric-2),min(len(parsed),numeric+3))]
    else:neighbors[str(numeric)]=[]
   candidates.append({"original_owner_resource":rec.name,
    "authored_rig_nodes_parsed":True,"source_authored_node_count":len(rig),
    "B13_source_list_order_only_UNVERIFIED_native_idx":neighbors,
    "native_dummy_id_to_node_resolution_PROVEN":False,
    "real_source_named_dummy_node_entries":[x for x in parsed if x["name_contains_dummy"]][:60],
    "original_resource_sha256":hashlib.sha256(raw).hexdigest()})
 if not any(x["original_owner_resource"]=="warmachine.bdae"
            and x.get("source_authored_node_count")==112 for x in candidates):
  raise ValueError("Previously proven authentic 2010 WarMachine 112-node rig was not parsed")
 report={
 "source":"owner iOS 2010 original native ARM Object3D::GetDummyAbsolutePosition and owner BDAE rig data",
 "original_native_method":LOOKUP_NAME,"original_native_VM":hex(NATIVE_ADDR),
 "source_original_instruction_count":len(instructions),
 "source_original_direct_or_indirect_method_calls":direct,
 "native_real_memory_operand_instructions":mem,
 "native_real_compare_instructions":compares,
 "native_real_branch_instructions":branches,
 "native_original_bounded_ARM_opcode_METADATA_not_bytes":entries,
 "original_2010_real_model_archive_candidates":candidates,
 "confirmed_UniBeam_DoAttack_passed_int_values":[14,14,33],
 "native_original_id_lookup_mechanism_under_analysis":True,
 "BRES_rig_array_order_is_actual_native_DummyId_mapping_PROVEN":False,
 "source_14_33_actual_model_dummy_node_or_bone_name_PROVEN":False,
 "original_2010_particle_muzzle_transform_PROVEN":False,
 "native_Vita_2010_feature_auto_integrated":False,
 "no_owner_asset_or_executable_export":True,
 "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G180 SOURCE 2010 Object3D GetDummyAbsolutePosition",hex(NATIVE_ADDR),
       "bounded native ARM instructions",len(instructions),"calls",len(direct))
 for c in direct:print("G180 NATIVE CALL",c)
 for item in entries[:100]:print("G180 ARM SOURCE",item["vm"],item["mnemonic"],item["args"])
 for c in candidates:
  print("G180 REAL ORIGINAL RIG",c["original_owner_resource"],c.get("source_authored_node_count"),
        "DUMMY SOURCE NAMES",[e["source_original_rig_name"] for e in c.get("real_source_named_dummy_node_entries",[])[:24]])
  for num,around in c.get("B13_source_list_order_only_UNVERIFIED_native_idx",{}).items():
   print("G180 ORDINAL IS NOT DUMMY ID",c["original_owner_resource"],num,
         [e["source_original_rig_name"] for e in around])
 print("G180 Native BRES Dummy ID crosswalk is NOT proven by matching arbitrary B13 parse order; no VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 main(a.ipa,a.out)
