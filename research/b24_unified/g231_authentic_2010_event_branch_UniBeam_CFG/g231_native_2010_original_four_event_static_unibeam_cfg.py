#!/usr/bin/env python3
"""G231: source-only, CONSERVATIVE structural ARM CFG for four original
2010 DoAttack second-event candidate branch roots. No touch/weapon meaning.
Graph ignores branch predicates: reachability NEVER proves runtime behavior.
"""
from __future__ import annotations
import argparse
import collections
import json
import re
from pathlib import Path

ROOTS = {0:0xf6c60,1:0xf6ce0,2:0xf6d58,3:0xf6d98}
G196_UNIBEAM = {0xf6638:14,0xf6d8c:14,0xf6e04:33}
CONDITION = r"(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)"
BRANCH_RE = re.compile(r"^b(?:" + CONDITION + r")?$")


def run(g196:Path,out:Path)->dict:
    source=json.loads(g196.read_text())
    ops=source["source_original_entire_DoAttack_646_ARM_opcode_metadata"]
    if len(ops)!=646 or source["native_source_method_VM"]!="0xf64f8":
        raise ValueError("G231 real 2010 native DoAttack source unavailable")
    orig={int(x["vm"],16):(x["mnemonic"].lower(),x["args"].lower()) for x in ops}
    if len(orig)!=646:raise ValueError("duplicated native ARM VMs")
    verified={0xf6a30:("cmp","r8, #3"),0xf6a34:("addls","pc, pc, r8, lsl #2")}
    for addr,inst in verified.items():
        if orig.get(addr)!=inst:raise ValueError("genuine r8 source four-entry dispatch changed")
    for event,root in ROOTS.items():
        branch=orig.get(0xf6a3c+event*4)
        if branch!=("b",f"#{root:#x}"):
            raise ValueError(f"original 2010 native r8 branch {event} source mismatch: {branch}")
    for call,dummy in G196_UNIBEAM.items():
        mn,args=orig.get(call,(None,None))
        if mn!="bl" or args!="#0xf60ac":
            raise ValueError(f"G231 source native DoUniBeamAttack call {call:#x} mismatch {mn,args}")
        reported={int(o["source_uniBeam_direct_CALL_VM"],16):o["actual_source_native_integer_dummy_group"]
                  for o in source["original_unibeam_callsite_14_14_33_in_source"]}
        if reported.get(call)!=dummy:
            raise ValueError("G196 native dummy source callsite mismatch")
    adj=collections.defaultdict(list)
    direct_calls={}
    unresolved=[]
    for vm,(mn,arg) in sorted(orig.items()):
        next_vm=vm+4
        if mn=="bl" or mn=="blx":
            direct_calls[vm]={"mnemonic":mn,"target":arg}
            if next_vm in orig: adj[vm].append((next_vm,"call-return-assumed"))
            continue
        if mn=="bx" or "pc" in arg and (
            arg.split(",",1)[0].strip()=="pc"
            or "{pc" in arg
            or re.search(r"[, ]pc[},]",arg)
        ):
            unresolved.append({"vm":hex(vm),"mnemonic":mn,"args":arg})
            # indirect branch and function returns are not traversed
            continue
        if BRANCH_RE.fullmatch(mn):
            try:
                target=int(arg.lstrip("#"),16)
            except ValueError:
                unresolved.append({"vm":hex(vm),"mnemonic":mn,"args":arg})
                continue
            if target in orig:
                adj[vm].append((target,"branch-target-predicate-not-resolved"))
            else:
                unresolved.append({"vm":hex(vm),"mnemonic":mn,"args":arg})
            if mn!="b" and next_vm in orig:
                adj[vm].append((next_vm,"conditional-fallthrough"))
            continue
        if mn.startswith("add") and arg.startswith("pc,"):
            unresolved.append({"vm":hex(vm),"mnemonic":mn,"args":arg})
            continue
        if next_vm in orig:adj[vm].append((next_vm,"linear"))
    results=[]
    for selector,root in ROOTS.items():
        visited={root}
        prev={}
        queue=collections.deque([root])
        while queue:
            u=queue.popleft()
            for v,k in adj[u]:
                if v in visited:continue
                visited.add(v)
                prev[v]=(u,k)
                queue.append(v)
        calls=[]
        for site,group in G196_UNIBEAM.items():
            if site not in visited:continue
            route=[site]
            kinds=[]
            while route[-1]!=root:
                parent,edge=prev[route[-1]]
                route.append(parent)
                kinds.append(edge)
            route.reverse();kinds.reverse()
            calls.append({
                "original_UniBeam_call_VM":hex(site),
                "2010_original_dummy_group":group,
                "original_dummy_group_name":"Dummy_Chest" if group==14 else "Dummy_Foot_L",
                "static_CFG_structurally_reachable":True,
                "path_VM":list(map(hex,route)),
                "path_edge_types":kinds,
                "branch_predicates_resolved":False,
                "original_real_gameplay_execution_proven":False,
                "Vita_effect_or_suit_weapon_binding_proven":False,
            })
        indirect=[x for x in unresolved if int(x["vm"],16) in visited]
        results.append({
            "original_event_third_u32_candidate":selector,
            "branch_entry_VM":hex(root),
            "structurally_reachable_ARM_instructions":len(visited),
            "reachable_original_DoUniBeamAttack_calls":calls,
            "reachable_original_direct_BL_call_inventory":[
                {"source_native_callsite_VM":hex(site),
                 "source_original_called_VM_string":instruction["target"],
                 "cpp_method_identity_authenticated_as_DoUniBeamAttack":
                    instruction["target"]=="#0xf60ac",
                 "2010_gameplay_effect_or_weapon_input_proven":False}
                for site,instruction in sorted(direct_calls.items()) if site in visited
            ],
            "unresolved_indirect_or_control_flow_sites":indirect[:32],
            "original_ARM_CFG_is_predicate_and_virtual_indirect_incomplete":True,
        })
    report={
        "source":"G231 actual original 2010 source 646 ARM DoAttack ops with G196 verified 14/33 UniBeam calls",
        "four_authentic_event_arg_selector_ARM_targets":{str(k):hex(v) for k,v in ROOTS.items()},
        "original_source_14_33_do_unibeam_VM":"0xf60ac",
        "source_only_conditional_branch_structural_cfg":True,
        "branch_predicate_satisfiability_proven":False,
        "runtime_original_iOS_suit_weapon_semantics_proven":False,
        "per_event_arm_static_paths":results,
        "changed_Vita_animation_weapons_input_or_physics":False,
        "NO_VPK":True,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    for item in results:
        print("G231 source original event",item["original_event_third_u32_candidate"],
              "branch",item["branch_entry_VM"],
              "static UniBeam callsites",[(c["original_UniBeam_call_VM"],c["2010_original_dummy_group"])
              for c in item["reachable_original_DoUniBeamAttack_calls"]],
              "visited",item["structurally_reachable_ARM_instructions"],
              "source BL calls",[(a["source_native_callsite_VM"],a["source_original_called_VM_string"])
               for a in item["reachable_original_direct_BL_call_inventory"]])
    print("G231 PASS actual original ARM structural CFG; runtime predicates/suit/weapon effects still UNKNOWN, no VPK")
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--g196",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    opts=parser.parse_args()
    run(opts.g196,opts.out)
