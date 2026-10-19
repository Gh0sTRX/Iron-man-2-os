#!/usr/bin/env python3
"""G234 original 2010 ARM callsite argument-provenance windows: GetWeapon,
GetAssistantWeapon, WeaponDB/GetAttackEntityByIndex and WeaponEntity::DoAttack.
Consumes source-authenticated G196 ARM metadata and G233 exact MachO symbols;
no fabricated original touch / missile / gatling / damage semantics.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

CALLS = {
    0xf6c68:(0xb1f14, "WeaponMgr::GetWeapon(int)"),
    0xf6ce8:(0xb1d2c, "WeaponMgr::GetAssistantWeapon(int)"),
    0xf6c74:(0xab324, "WeaponDB::GetInstance()"),
    0xf6cf0:(0xab324, "WeaponDB::GetInstance()"),
    0xf6c7c:(0xab3ec, "WeaponDB::GetAttackEntityByIndex(int)"),
    0xf6cf8:(0xab3ec, "WeaponDB::GetAttackEntityByIndex(int)"),
    0xf6ca4:(0xc1078, "WeaponEntity::DoAttack("),
}
ARM_ARGS=("r0","r1","r2","r3")

def run(g196:Path,g233:Path,out:Path)->dict:
    g=json.loads(g196.read_text());n=json.loads(g233.read_text())
    records=g["source_original_entire_DoAttack_646_ARM_opcode_metadata"]
    if len(records)!=646 or g["native_source_method_VM"]!="0xf64f8":
        raise ValueError("G234 only original 2010 G196 646-opcode data accepted")
    if not n["source_G196_independent_original_2010_BL_opcode_crosscheck_passed"]:
        raise ValueError("G234 native G233 source must have crosschecked G196")
    if n["real_native_MachO_symbol_count"]<60000:
        raise ValueError("G234 original MachO symbol inventory incomplete")
    names={int(x["direct_BL_target_VM"],16):x for x in n["true_original_2010_direct_targets_resolution"]}
    op={int(x["vm"],16):x for x in records}
    index={int(x["vm"],16):i for i,x in enumerate(records)}
    selected=[]
    for site,(callee,required) in sorted(CALLS.items()):
        row=op.get(site)
        if not row or row["mnemonic"].lower()!="bl" or row["args"].lower()!=f"#{callee:#x}":
            raise ValueError(f"G234 authentic original BL callsite drift at {site:#x}")
        info=names.get(callee)
        if not info or not info["exact_original_native_symbol_entry"]:
            raise ValueError(f"G234 original direct callee exact source symbol missing {callee:#x}")
        labels=info["exact_original_2010_cpp_names"]
        if not any(required in name for name in labels):
            raise ValueError(f"G234 real native callee name mismatch {callee:#x}: {labels}")
        i=index[site]
        # The window can contain branches, returns, or other calls. Those are
        # HINTS only; a near instruction does not necessarily execute.
        before=records[max(0,i-14):i]
        after=records[i+1:min(len(records),i+13)]
        writes=[]
        for x in before:
            args=x["args"].lower().split(",",1)
            mn=x["mnemonic"].lower()
            if args[0].strip() not in ARM_ARGS:
                continue
            if mn.startswith(("cmp","tst","teq","str","stm","bl","bne","beq","b")):
                continue
            writes.append({"source_VM":x["vm"],"source_opcode":mn,
                           "target_register":args[0].strip(),
                           "other_operands":args[1].strip() if len(args)>1 else ""})
        selected.append({
            "original_iOS_ARM_BL_callsite_VM":hex(site),
            "original_iOS_arm_direct_callee_VM":hex(callee),
            "genuine_native_exact_Cpp_method_names":labels,
            "source_14_instructions_before":before,
            "source_12_instructions_after":after,
            "source_nearby_candidate_argument_register_writes":writes,
            "nearby_writes_do_NOT_prove_runtime_branch_or_final_call_args":True,
            "original_iOS_touch_or_specific_WeaponDB_ID_PROVEN":False,
        })
    result={
        "source":"G234 original iOS 2010 native G196 entire 646 DoAttack ARM metadata + genuine 2010 MachO G233 exact method labels",
        "verified_original_native_callsite_and_Cpp_identity_count":len(selected),
        "original_source_WeaponMgr_weapon_and_assistant_paths_distinct_functions":True,
        "original_source_GetAttackEntityByIndex_shared_by_both_paths":True,
        "source_real_Cpp_callsite_argument_neighborhoods":selected,
        "original_WeaponMgr_GetWeapon_int_runtime_value_PROVEN":False,
        "original_WeaponMgr_GetAssistantWeapon_int_runtime_value_PROVEN":False,
        "original_WM_missile_gatling_which_Index_and_button_PROVEN":False,
        "original_iOS_StateTrack_event_is_main_weapon_or_assistant_every_runtime_PROVEN":False,
        "Vita_input_damage_melee_weapon_or_G8_engine_modified":False,
        "NO_VPK":True,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    for record in selected:
        print("G234 genuine original ARM site",record["original_iOS_ARM_BL_callsite_VM"],
              "calls",record["genuine_native_exact_Cpp_method_names"],
              "candidate argument writes",record["source_nearby_candidate_argument_register_writes"][-8:])
        print("G234 prior 14",record["source_14_instructions_before"])
    print("G234 PASS exact original 2010 C++ source attack callee + adjacent ARM argument candidates, no guessed input/VPK")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--g196",type=Path,required=True)
    p.add_argument("--g233",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.g196,a.g233,a.out)
