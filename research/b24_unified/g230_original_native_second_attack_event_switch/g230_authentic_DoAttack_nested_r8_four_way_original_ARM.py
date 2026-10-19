#!/usr/bin/env python3
"""G230 original 2010 iOS MainCharacter::DoAttack r8 nested 0..3 ARM table.
Inputs: source-authenticated G196 whole method and G221 original StateTrack
event rows. NO guesses about rockets, melee hits or player inputs.
NO Vita patch / VPK. All instruction evidence must match original artifact.
"""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path


def analyze(g196: Path, g221: Path, out: Path) -> dict:
    source = json.loads(g196.read_text())
    bridge = json.loads(g221.read_text())
    opcodes = source["source_original_entire_DoAttack_646_ARM_opcode_metadata"]
    if (source["native_source_method_VM"] != "0xf64f8"
        or len(opcodes) != 646
        or not source["source_2010_original_native_dispatch_cmp_r5_25_jump_table_proven"]):
        raise ValueError("G230 needs original 646-instruction 2010 DoAttack native source")
    if (bridge["source_original_event_array_third_u32_READ_by_ACTOR_VM"] != "0xdb6a4"
        or bridge["source_original_event_third_u32_loaded_in_ARM_r2"] is not True
        or bridge["original_2010_vtable_dynamic_dispatch_VM"] != "0xdb6d8"):
        raise ValueError("G230 needs genuine original Actor::UpdateStateAttack r2 proof")
    op = {int(x["vm"], 16): (x["mnemonic"].lower(), x["args"].lower()) for x in opcodes}
    if len(op) != len(opcodes):
        raise ValueError("duplicate ARM addresses in authentic DoAttack")
    mandatory = {
        0xf650c: ("mov", "r5, r1"),
        0xf6518: ("mov", "r8, r2"),
        0xf6524: ("cmp", "r5, #0x19"),
        0xf6528: ("addls", "pc, pc, r5, lsl #2"),
        0xf65a0: ("mov", "r2, r8"),
        0xf69dc: ("mov", "r2, r8"),
        0xf6a30: ("cmp", "r8, #3"),
        0xf6a34: ("addls", "pc, pc, r8, lsl #2"),
    }
    for addr, instruction in mandatory.items():
        if op.get(addr) != instruction:
            raise ValueError(f"G230 genuine native ARM opcode drift {addr:#x}: {op.get(addr)} != {instruction}")
    sw = source["source_original_2010_attack_id_switch_0_to_25"]
    if len(sw) != 26 or sw["1"]["original_target_VM"] != "0xf6930" or sw["18"]["original_target_VM"] != "0xf6930":
        raise ValueError("original 2010 outer AttackType=1/18 switch destination drift")
    # Original ARM PC in ADDLS points to (instruction_address + 8).
    # The default/fallthrough opcode is at 0xF6A38, table indexes 0..3 at
    # 0xF6A3C + 4*event, not 0xF6A38 or the outer 26-way AttackType jump.
    nested = []
    for event in range(4):
        addr = 0xf6a3c + 4*event
        inst = op.get(addr)
        if inst is None:
            raise ValueError(f"missing original nested ARM instruction @{addr:#x}")
        mn, arg = inst
        target = None
        if mn == "b" and arg.startswith("#0x"):
            target = hex(int(arg.removeprefix("#"), 16))
        nested.append({
            "original_StateTrack_event_third_u32_candidate": event,
            "original_ARM_jump_table_entry_VM": hex(addr),
            "source_original_ARM_instruction": {"mnemonic": mn, "args": arg},
            "direct_branch_target_VM_if_provable": target,
            "weapon_missile_combo_or_hit_effect_proven": False,
        })
    # This is a LOCAL register-write analysis, not a complete path-sensitive
    # interprocedural C++ proof. The original method reuses r8 elsewhere:
    # 0xF66B0 LDR r8,[sp,...] belongs to a different assembly region.
    near = [x for x in opcodes if 0xf6930 <= int(x["vm"],16) <= 0xf6a34]
    def direct_write_r8(row):
        args = row["args"].lower()
        first = args.split(",",1)[0].strip()
        return first == "r8" and not row["mnemonic"].lower().startswith(
            ("cmp", "tst", "teq", "str", "stm", "b", "swp"))
    local_writes = [
        {"vm": x["vm"], "mnemonic": x["mnemonic"], "args": x["args"]}
        for x in near if direct_write_r8(x)
    ]
    if local_writes:
        raise ValueError("G230 original r8 is overwritten inside candidate 1/18 branch span: " + str(local_writes))
    rows = bridge["source_original_2010_AttackType_associated_named_attack_event_rows"]
    groups = ("IronMan", "IronMan_suitcase", "Warmachine", "stealth")
    hist = {name: collections.Counter() for name in groups}
    per_outer = collections.defaultdict(collections.Counter)
    for item in rows:
        armor = item["real_source_2010_armor"]
        if armor not in hist:
            continue
        ev = item["original_event_record_third_u32_PASSABLE_TO_VIRTUAL"]
        outer = item["source_authored_AttackType"]
        if not isinstance(ev, int) or not isinstance(outer, int):
            raise ValueError("source authored event contains non-integer field")
        hist[armor][ev] += 1
        per_outer[(armor, outer)][ev] += 1
    for name in groups:
        known = bridge["source_actual_native_2010_event_original_armor_values"][name]
        expected = {int(k): v for k,v in known["original_2010_event_third_u32_value_frequencies"].items()}
        if dict(hist[name]) != expected:
            raise ValueError("G230 native StateTrack original event histogram drift: " + name)
    report = {
        "method": "G230 original 2010 iOS native ARM source-only 4-entry r8 dispatch candidate",
        "real_original_iOS_DoAttack_VM": "0xf64f8",
        "exact_original_opcode_total": len(opcodes),
        "original_source_actor_r2_event_proven": True,
        "original_DoAttack_saves_event_argument_in_r8_VM": "0xf6518",
        "original_outer_AttackType_1_and_18_entry_VM": "0xf6930",
        "original_nested_cmp_r8_3_VM": "0xf6a30",
        "original_nested_addls_PC_r8_LSL2_VM": "0xf6a34",
        "original_nested_fallthrough_VM_if_r8_greater_than_3": "0xf6a38",
        "original_nested_event_0_1_2_3_instructions": nested,
        "original_r8_direct_writes_in_local_F6930_F6A34_span": local_writes,
        "local_source_has_no_r8_direct_overwrite_in_that_span": True,
        "local_span_proves_all_runtime_paths_enter_with_original_r8": False,
        "original_maincharacter_event_third_u32_source_histogram_by_armor": {
            name: dict(sorted(hist[name].items())) for name in groups},
        "event_distribution_per_original_armor_AttackType": [
            {"armor": name, "AttackType": attack, "event_value_histogram": dict(sorted(vals.items()))}
            for (name,attack),vals in sorted(per_outer.items())
        ],
        "G230_event_values_0_1_2_3_mean_specific_weapon_or_hit_window_PROVEN": False,
        "G230_real_user_touch_to_ARM_native_attack_semantics_PROVEN": False,
        "G230_native_ARM_full_interprocedural_CFG_or_virtual_return_PROVEN": False,
        "Vita_gameplay_armor_animation_damage_or_input_CHANGED": False,
        "NO_VPK": True,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("G230 2010 source method 646 ARM instructions; nested original r8 four-entry source opcode map:")
    for item in nested:
        print("G230 original native candidate",item)
    print("G230 histogram",report["original_maincharacter_event_third_u32_source_histogram_by_armor"])
    print("G230 LOCAL not interprocedural r8 overwrite",local_writes)
    print("G230 PASS original 2010 nested source branch proven, unknown original per-case effects; NO VPK")
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--g196",type=Path,required=True)
    ap.add_argument("--g221",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a = ap.parse_args()
    analyze(a.g196,a.g221,a.out)
