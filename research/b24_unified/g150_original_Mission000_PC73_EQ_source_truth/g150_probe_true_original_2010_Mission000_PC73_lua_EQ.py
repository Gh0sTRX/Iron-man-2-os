#!/usr/bin/env python3
"""Inspect user's genuine Iron Man 2 iOS 2010 level1 Lua PC73 operands.

Requires user-owned original version 1.0.0 IPA. Produces only
small instruction metadata and constant *types* / boolean values;
does not export original game code, strings, PCM, meshes or IPA.
Never synthesizes a QTE completion, Lua branch, Vita VPK or input.
"""
import argparse
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))
from b24_owner_pack_extract import decode, get_exact
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua, HEADER, report as g27report

OP = {
    1:"LOADK",2:"LOADBOOL",5:"GETGLOBAL",22:"JMP",23:"EQ",
    26:"TEST",27:"TESTSET",28:"CALL",29:"TAILCALL",30:"RETURN",
}

def instruction(word):
    return {
        "op_num":word & 63,
        "opcode":OP.get(word & 63, "OTHER"),
        "a":(word >> 6) & 255,
        "b":(word >> 23) & 511,
        "c":(word >> 14) & 511,
        "sbx":((word >> 14) & 262143) - 131071,
    }

def operand(rk, constants):
    if rk < 256:
        return {"source_kind":"register","register":rk}
    idx = rk - 256
    if idx >= len(constants):
        raise ValueError("2010 source Lua 5.1 RK constant outside original proto")
    value = constants[idx]
    t = ("nil" if value is None else "boolean" if isinstance(value,bool)
         else "number" if isinstance(value,(float,int)) else "string")
    item = {"source_kind":"constant","index":idx,"type":t}
    if t == "boolean":
        item["value"] = value
    return item

def run(ipa, out):
    if ipa.stat().st_size != 248613763:
        raise ValueError("Original owner iOS 2010 1.0.0 exact IPA expected")
    with zipfile.ZipFile(ipa) as z:
        clev=z.read("Payload/IronMan2.app/clev")
        raw=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
    refs=g27report(raw)["source_lua_static_CALLBACK_instructions_and_id_links"]
    original=next(x for x in refs if x["original_callback"]=="Mission000_OnStart")
    p=NativeLua(raw,original["original_source_callback_offset"])
    if p.fetch(12) != HEADER:
        raise ValueError("G150 actual 2010 Lua header mismatch")
    original_prototype=p.function()
    fn=original_prototype["original_child_functions"][0]
    code=fn["native_function_code"]
    const=fn["native_constants"]
    if len(code) != 937:
        raise ValueError("G135 real Mission000 was 937 instructions")
    d={pc:instruction(code[pc]) for pc in (70,71,72,73,74,75,76,77,78,79)}
    if [d[71]["op_num"], d[72]["op_num"], d[73]["op_num"],
        d[74]["op_num"], d[78]["op_num"]] != [5,28,23,22,22]:
        raise ValueError("Original Lua PC71-74/78 no longer matches proven CALL/conditional loop")
    if d[74]["sbx"] != 4 or 74+1+d[74]["sbx"] !=79:
        raise ValueError("PC74 real jump target does not equal PC79")
    if d[78]["sbx"] != -8 or 78+1+d[78]["sbx"] !=71:
        raise ValueError("PC78 real retry target is not PC71")
    globalidx=(code[71] >> 14) & 262143
    if const[globalidx] != "IsTutConfirmed":
        raise ValueError("Source PC71 GETGLOBAL no longer maps IsTutConfirmed")
    if d[71]["a"] != d[72]["a"] or d[72]["c"] !=2:
        raise ValueError("Original PC72 CALL must produce one Lua return at function register")
    r={
        "source":"user original 2010 iOS level1.bclara/ Mission000_OnStart Lua5.1",
        "source_full_instructions":len(code),
        "native_query_PC71":{"opcode":"GETGLOBAL","global":"IsTutConfirmed","register":d[71]["a"]},
        "native_query_PC72":{"opcode":"CALL","return_register":d[72]["a"],"lua_return_count":d[72]["c"]-1},
        "source_PC73_EQ":{"a_expected":d[73]["a"],
            "operand_B":operand(d[73]["b"],const),
            "operand_C":operand(d[73]["c"],const),
            "potential_next_PCs":[74,75]},
        "source_PC74_JMP":{"jump_to_pc":79},
        "source_PC78_JMP":{"jump_to_pc":71},
        "source_UI_confirmed_callback_executed_in_Vita":False,
        "source_QTE_touch_gesture_verified":False,
        "source_original_PC73_boolean_branch_emulated":False,
        "new_vpk":False,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
    print("G150 original PC73 EQ source truthful A/B/C operands:",
          r["source_PC73_EQ"])
    print("G150 original PC74 ->79, PC78 ->71, PC71 global IsTutConfirmed")
    print("G150 source bytecode READ only, no gameplay auto-approval, NO VPK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.ipa,a.out)
