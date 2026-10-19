#!/usr/bin/env python3
"""G233 independent original 2010 iOS Mach-O symbol resolution of G232
actual DoAttack nested 0..3 ARM direct BL target addresses.
Only labels, canonical function VM and distances (NO proprietary raw opcodes).
Exact symbol-entry matches are distinguished from nearest-containing-symbol
heuristics, Thumb low-bit normalized, no guessed weapon or iOS input names.
"""
from __future__ import annotations
import argparse
import bisect
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

ORIGINAL_IPA_SIZE = 248613763
ORIGINAL_EXECUTABLE_SIZE = 7480208
ORIGINAL_EXECUTABLE = "Payload/IronMan2.app/IronMan2"
SOURCE_CALLS = {
    0: [(0xf6c48,0x7fd3c),(0xf6c58,0x7b36c),(0xf6c68,0xb1f14),
        (0xf6c74,0xab324),(0xf6c7c,0xab3ec),(0xf6ca4,0xc1078),(0xf6cb0,0xc2528)],
    1: [(0xf6ce8,0xb1d2c),(0xf6cf0,0xab324),(0xf6cf8,0xab3ec)],
    2: [(0xf6c48,0x7fd3c),(0xf6c58,0x7b36c),(0xf6d8c,0xf60ac)],
    3: [(0xf6c48,0x7fd3c),(0xf6c58,0x7b36c),(0xf6e04,0xf60ac)],
}
KNOWN_2010_UNIBEAM = 0xf60ac

def original_executable(ipa:Path)->bytes:
    if ipa.stat().st_size!=ORIGINAL_IPA_SIZE:
        raise ValueError("G233 original iOS owner IPA exact size mismatch")
    with zipfile.ZipFile(ipa) as z:
        if z.testzip() is not None:
            raise ValueError("G233 source IPA CRC failed")
        exe=z.read(ORIGINAL_EXECUTABLE)
    if len(exe)!=ORIGINAL_EXECUTABLE_SIZE:
        raise ValueError("G233 original 2010 Mach-O executable size mismatch")
    return exe

def canonical(value:int)->int:
    return value & ~1

def analyze(ipa:Path,out:Path,g196:Path|None=None)->dict:
    exe=original_executable(ipa)
    native=parse_macho(exe)
    entries=native["entries"]
    names=subprocess.run(["c++filt"],
        input="\n".join(x[0] for x in entries)+"\n",
        capture_output=True,text=True,check=True).stdout.splitlines()
    if len(names)!=len(entries):
        raise ValueError("G233 true Mach-O symbol count differs from c++filt")
    if native["nsyms"]<60000 or len(entries)<50000:
        raise ValueError("G233 symbol table unexpectedly incomplete")
    text_sections=[x for x in native["sections"] if x[3]=="__text"]
    if not text_sections:
        raise ValueError("G233 no 2010 original Mach-O __text")
    byaddr=collections.defaultdict(set)
    isa=collections.defaultdict(set)
    for entry,name in zip(entries,names):
        addr=canonical(entry[1])
        byaddr[addr].add(name)
        isa[addr].add("Thumb" if entry[1]&1 else "ARM")
    starts=sorted(addr for addr in byaddr if
        any(a<=addr<a+length for a,length,_,_,_ in text_sections))
    if not starts:
        raise ValueError("G233 authentic text symbol starts missing")
    if not any("MainCharacter::DoUniBeamAttack(" in s
               for s in byaddr.get(KNOWN_2010_UNIBEAM,())):
        raise ValueError("G233 native original UniBeam 0xf60ac exact entry drift")
    expected={}
    for event,edges in SOURCE_CALLS.items():
        for site,target in edges:
            if site in expected and expected[site]!=target:
                raise ValueError("G233 callsite ambiguous across source branches")
            expected[site]=target
    if g196 is not None:
        original=json.loads(g196.read_text())
        if len(original["source_original_entire_DoAttack_646_ARM_opcode_metadata"])!=646:
            raise ValueError("G233 original G196 owner instruction count drift")
        op={int(x["vm"],16):(x["mnemonic"].lower(),x["args"].lower())
            for x in original["source_original_entire_DoAttack_646_ARM_opcode_metadata"]}
        for site,target in expected.items():
            if op.get(site)!=("bl",f"#{target:#x}"):
                raise ValueError(f"G233 G196 original BL @{site:#x} is not {target:#x}: {op.get(site)}")
    callee={}
    for target in sorted(set(expected.values())):
        if not any(a<=target<a+size for a,size,_,_,_ in text_sections):
            raise ValueError(f"G233 callee {target:#x} not in genuine __text")
        j=bisect.bisect_right(starts,target)-1
        owner=starts[j] if j>=0 else None
        nxt=starts[j+1] if j+1<len(starts) else None
        same_section=bool(owner is not None and any(
            a<=owner<=target<a+size for a,size,_,_,_ in text_sections))
        exact=target in byaddr
        # An arbitrary address INSIDE a function must not be labelled as an
        # exact function entry, and nearest-preceding label is NOT proof.
        callee[target]={
            "direct_BL_target_VM":hex(target),
            "exact_original_native_symbol_entry":exact,
            "exact_original_2010_cpp_names":sorted(byaddr[target]) if exact else [],
            "exact_entry_native_ISA":sorted(isa[target]) if exact else [],
            "nearest_preceding_original_source_symbol_start":hex(owner) if same_section else None,
            "nearest_preceding_cpp_names":sorted(byaddr.get(owner,())) if same_section else [],
            "bytes_from_nearest_prior_symbol":target-owner if same_section else None,
            "next_original_symbol_VM":hex(nxt) if nxt is not None else None,
            "nearest_preceding_is_NOT_exact_method_identity":not exact,
            "gameplay_weapon_or_hit_semantics_proven":False,
        }
    per_event=[]
    for event,edges in sorted(SOURCE_CALLS.items()):
        per_event.append({
            "native_original_2010_event_value_candidate":event,
            "G232_static_paths_not_runtime_execution":True,
            "source_2010_direct_BL_calls":[{
                "callsite_VM":hex(site),
                "direct_callee_VM":hex(target),
                "exact_function_source_name":callee[target]["exact_original_2010_cpp_names"],
                "exact_match":callee[target]["exact_original_native_symbol_entry"],
                "method_name_not_equal_to_weapon_kind":True,
            }for site,target in edges],
            "actual_iOS_runtime_predicate_and_suit_effect_proven":False,
        })
    result={
        "source":"G233 authentic user supplied original iOS Iron Man 2 2010 Mach-O LC_SYMTAB verified via G76 parse_macho and c++filt",
        "original_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
        "real_native_MachO_symbol_count":native["nsyms"],
        "true_original_2010_direct_targets_resolution":[callee[t] for t in sorted(callee)],
        "original_per_0_1_2_3_event_static_BL_calls":per_event,
        "source_G196_independent_original_2010_BL_opcode_crosscheck_passed":g196 is not None,
        "exact_symbol_entries_are_not_automatically_original_weapon_effects":True,
        "event_0_1_2_3_full_runtime_semantics_PROVEN":False,
        "WarMachine_AimM_gatling_missile_mapping_PROVEN":False,
        "original_melee_hit_frame_or_damage_PROVEN":False,
        "actual_Vita_gameplay_controller_or_weapon_modified":False,
        "NO_VPK":True,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    for row in result["true_original_2010_direct_targets_resolution"]:
        print("G233 SOURCE CALL TARGET",row["direct_BL_target_VM"],
              "exact",row["exact_original_native_symbol_entry"],
              "true_names",row["exact_original_2010_cpp_names"],
              "nearest",row["nearest_preceding_original_source_symbol_start"],
              "nearest_names",row["nearest_preceding_cpp_names"][:3])
    print("G233 PASS real original 2010 MachO source C++ name lookup, no guessed weapons/Hit/Vita VPK")
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--ipa",required=True,type=Path)
    ap.add_argument("--g196",type=Path)
    ap.add_argument("--out",required=True,type=Path)
    a=ap.parse_args()
    analyze(a.ipa,a.out,a.g196)
