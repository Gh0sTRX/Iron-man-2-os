#!/usr/bin/env python3
"""Read-only release/scope gate for the first authentic PS Vita C1L1 slice.

Source compilation or a host mock never counts as physical device proof.
This program produces no VPK and never sets readiness automatically.
"""
import argparse
import json
import re
from pathlib import Path

REQUIRED_IDS=(
    "world_visual","solid_collision","movement_combat","qte_ui",
    "audio_and_events","mission_complete","device_performance")
OPEN_STATES={"source_blocked","device_regression_open","not_measured","not_tested"}
CLOSED_STATE="passed"
SHA40=re.compile(r"^[a-fA-F0-9]{40}$")
DATE=re.compile(r"^\d{4}-\d{2}-\d{2}$")

def validate(m):
    if m.get("schema_version")!=1:
        raise ValueError("Unexpected first playable gate schema")
    if m.get("wip_limit")!=1:
        raise ValueError("Do not open multiple parallel workstreams; first playable WIP limit 1")
    if not m.get("active_workstream"):
        raise ValueError("Current one prioritized workstream missing")
    if len(m.get("criteria",[])) != len(REQUIRED_IDS):
        raise ValueError("Missing or extra mandatory first playable criteria")
    seen=set()
    for row in m["criteria"]:
        key=row.get("id")
        if key not in REQUIRED_IDS or key in seen:
            raise ValueError("Unknown or duplicate first playable criterion")
        seen.add(key)
        if row.get("mandatory") is not True:
            raise ValueError("Cannot demote mandatory first playable gate")
        if row.get("state") not in OPEN_STATES|{CLOSED_STATE}:
            raise ValueError("Unrecognized milestone state")
        if not row.get("acceptance") or not row.get("owner"):
            raise ValueError("Completion acceptance and owner required")
        if row["state"]==CLOSED_STATE:
            # A CI success or mocked host renderer is insufficient here.
            d=row.get("device_proof")
            if not isinstance(d,dict):
                raise ValueError(f"{key} cannot pass without actual handheld proof")
            if not SHA40.fullmatch(str(d.get("tested_commit",""))) or \
               not DATE.fullmatch(str(d.get("test_date",""))) or \
               not d.get("device_report_path") or \
               not d.get("observed_pass_criteria") or \
               d.get("hardware") != "PS Vita":
                raise ValueError(f"{key} has incomplete Vita device evidence")
    if seen!=set(REQUIRED_IDS):
        raise ValueError("Required first playable criteria changed")
    release=m.get("release",{})
    is_ready=all(row["state"]==CLOSED_STATE for row in m["criteria"])
    if release.get("ready") != is_ready:
        raise ValueError("Release readiness contradicts mandatory proof")
    if release.get("device_validation_passed") != is_ready:
        raise ValueError("Device QA status contradicts proof")
    if release.get("first_level_playable_claim_allowed") != is_ready:
        raise ValueError("Playable claim forbidden without all tested proof")
    if release.get("current_status") != ("READY" if is_ready else "BLOCKED"):
        raise ValueError("Release status contradicts mandatory proof")
    if release.get("candidate_vpk_auto_allowed") is not False:
        raise ValueError("Never auto-generate VPK just because source compiles")
    if m.get("policy",{}).get("source_build_is_not_device_proof") is not True:
        raise ValueError("Source build must not count as hardware QA")
    return is_ready

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,
      default=Path(__file__).with_name("first_playable_status.json"))
    ap.add_argument("--require-ready",action="store_true")
    a=ap.parse_args()
    doc=json.loads(a.manifest.read_text(encoding="utf-8"))
    ready=validate(doc)
    print("Iron Man 2 Vita C1L1 — first playable gate:", "READY" if ready else "BLOCKED")
    print("Current WIP:",doc["active_workstream"])
    for item in doc["criteria"]:
        print(" -",item["id"],":",item["state"])
    if a.require_ready and not ready:
        print("STOP: no release-ready first mission or automatic VPK; missing real Vita proofs.")
        raise SystemExit(2)
    print("Gate manifest internally valid; this validation is not a device test.")
if __name__=="__main__":
    main()
