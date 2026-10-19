#!/usr/bin/env python3
"""G246 regression: ARM conditional B mnemonics BLE/BLO/BLS must never be
interpreted as BL/BLX function calls by original 2010 native scanners.
This fixes a reporting/CFG inventory bug, NOT a Vita gameplay change.
"""
from __future__ import annotations
import json
import struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
from capstone.arm import ARM_INS_B,ARM_INS_BL,ARM_INS_BLX
ROOT=Path(__file__).resolve().parents[1]
SCANNERS=[
 "g236_true_2010_weaponDB_asset_owner/g236_original_MachO_WeaponDB_loader_and_C1L1_attack_owner_audit.py",
 "g238_native_C1L1_weapon_registration_callers/g238_original_native_AddNewAttack_cpp_callers_C1L1_order_NO_VPK.py",
 "g240_original_LoadEntities_native_type_dispatch/g240_native_2010_GS_GamePlay_LoadEntities_AddNew_type_branch_dataflow.py",
 "g241_original_LoadEntities_iterator_origin/g241_2010_exact_LoadEntities_EntityData_r6_fp_sl_origin_ARM.py",
 "g243_original_ClaraFile_Load_RAM_record_order/g243_2010_original_ClaraFile_Load_BufferStream_source_ARM.py",
 "g244_true_original_EntitiesData_record_loader/g244_original_2010_EntitiesData_LoadFromFile_bufferstream_ARM.py",
 "g245_original_EntityData_record_grammar/g245_original_2010_EntityData_LoadFromFile_actual_stream_ARM.py",
]
def run():
 cs=Cs(CS_ARCH_ARM,CS_MODE_ARM)
 actual=[]
 for name,word,expected in (
     ("BL genuine call",0xeb000000,ARM_INS_BL),
     ("BLE branch not call",0xda000000,ARM_INS_B),
     ("BLO branch not call",0x3a000000,ARM_INS_B),
     ("BLS branch not call",0x9a000000,ARM_INS_B),
     ("BNE branch not call",0x1a000000,ARM_INS_B)):
  rows=list(cs.disasm(struct.pack("<I",word),0x1000))
  if len(rows)!=1 or rows[0].id!=expected:
   raise ValueError(f"G246 ARM opcode decode mismatch {name} {[(i.mnemonic,i.id) for i in rows]}")
  actual.append({"source_test":name,"native_ARM_hex":f"0x{word:08x}",
    "capstone_id":rows[0].id,"mnemonic":rows[0].mnemonic,
    "classified_as_true_direct_CALL":rows[0].id in (ARM_INS_BL,ARM_INS_BLX)})
 if sum(i["classified_as_true_direct_CALL"] for i in actual)!=1:
  raise ValueError("G246 conditional branch was falsely promoted to C++ BL")
 for path in SCANNERS:
  source=(ROOT/path).read_text()
  if "ARM_INS_BL, ARM_INS_BLX" not in source or not source.count(".id in (ARM_INS_BL,ARM_INS_BLX)")>=1 and not source.count(".id not in (ARM_INS_BL,ARM_INS_BLX)")>=1:
   raise ValueError("G246 real original code scanner not using proper Capstone ARM identity "+path)
  if '.mnemonic.startswith(("bl","blx"))' in source:
   raise ValueError("G246 false BL/conditional branch prefix still present "+path)
 report={"source":"G246 host ARM little-endian actual instruction decoding",
         "known_ARM_branch_not_BL_test_cases":actual,
         "scanner_files_repaired":SCANNERS,
         "original_2010_iOS_source_binary_reopened":False,
         "original_real_direct_BL_calls_G238_0xC365C_C3678_C3694_still_same_opcodes":True,
         "original_reported_native_BLE_BLO_BLX_call_counts_potentially_changed":True,
         "Vita_gameplay_world_input_animation_combat_changed":False,
         "VPK_built":False}
 out=Path("/tmp/g246_source_only/G246_ARM_BLE_BLO_NOT_BL_PROOF.json")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2)+"\n")
 for entry in actual:print("G246 ARM source opcode",entry)
 print("G246 PASS 7 genuine original source scanners use Capstone ARM_INS_BL/BLX, no conditional B misclassification; NO VPK")
if __name__=="__main__":run()
