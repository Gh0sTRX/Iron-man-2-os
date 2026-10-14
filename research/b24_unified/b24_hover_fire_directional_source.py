#!/usr/bin/env python3
"""2010-original hover strafe+fire clip family mapping and transition gate.

This script inventories ACTUAL recorded source animation names (B18/B15).
Names are evidence of source clips, not proof of a runtime weapon association.
No VPK build or G8 runtime modification. The emitted 2010 clips must still
be source-baked, checked against their matching rig and GPU-stream connected.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "research/B18_COMPLETE_304_PLAYER_ANIMATIONS_CATALOG_TR.md"
ROW = re.compile(r"^\| `([^|\n`]+\.anim)` \|\s*(\d+)\s*\|\s*(\d+)\s*\|", re.I | re.M)
DIRECTIONS = ("idle", "F", "B", "L", "R")
ARMOR_PREFIX = {"ironman": "IronMan", "warmachine": "Warmachine"}


def catalog(path: Path = CATALOG) -> dict[str, dict]:
    found = {}
    for name, ms, channels in ROW.findall(path.read_text(encoding="utf-8")):
        key = name.casefold()
        if key in found:
            raise ValueError("duplicate authentic source animation: " + name)
        found[key] = {"filename": name, "duration_ms": int(ms),
                      "source_named_tracks": int(channels)}
    return found


def expected_name(armor: str, mode: str, direction: str, firing: bool) -> str:
    if armor not in ARMOR_PREFIX or mode not in ("aim", "aim_m") or direction not in DIRECTIONS:
        raise ValueError("unknown armor / hover aim family / direction")
    prefix = ARMOR_PREFIX[armor]
    sub = "Aim_Float_" if mode == "aim" else "Aim_M_Float_"
    mid = "idle" if direction == "idle" else "move_" + direction
    return prefix + "_" + sub + mid + ("_Att" if firing else "") + ".anim"


@dataclass
class HoverInput:
    """One movement/attack tick, in actor-local XY before camera projection."""
    x: float
    forward: float
    firing: bool
    armor: str
    mode: str = "aim"


def choose_direction(x: float, forward: float, previous: str = "idle") -> str:
    """Dominant local direction with a small reentry/exit hysteresis.

    This is a NEW Vita movement decision heuristic, NOT decompiled iOS rules.
    Allow modest deadzone hysteresis to avoid instant L/R flicker on diagonals.
    """
    if not -1.01 <= x <= 1.01 or not -1.01 <= forward <= 1.01:
        raise ValueError("invalid normalized analog")
    mag = max(abs(x), abs(forward))
    enter, exit_ = 0.25, 0.18
    if mag < (exit_ if previous != "idle" else enter):
        return "idle"
    if previous in ("L", "R") and abs(x) > exit_ and abs(x) >= abs(forward) - 0.10:
        return "R" if x > 0 else "L"
    if previous in ("F", "B") and abs(forward) > exit_ and abs(forward) >= abs(x) - 0.10:
        return "F" if forward > 0 else "B"
    if abs(x) > abs(forward):
        return "R" if x > 0 else "L"
    return "F" if forward > 0 else "B"


def state_for(tick: HoverInput, previous_direction: str = "idle") -> tuple[str, str]:
    direction = choose_direction(tick.x, tick.forward, previous_direction)
    return expected_name(tick.armor, tick.mode, direction, tick.firing), direction


def source_matrix(records: dict[str, dict]) -> dict:
    out = {}
    for armor in ARMOR_PREFIX:
        for mode in ("aim", "aim_m"):
            rows = []
            for direction in DIRECTIONS:
                for firing in (False, True):
                    stem = expected_name(armor, mode, direction, firing)
                    source = records.get(stem.casefold())
                    rows.append({
                        "armor": armor, "source_mode_label": mode,
                        "local_direction": direction, "attack_named": firing,
                        "source_name_requested": stem,
                        "catalog_record": source,
                        "source_name_found": source is not None,
                        "raw_source_baked_for_G8": False,
                        "gameplay_state_connected_in_G8": False,
                        "2010_weapon_type_proven": False,
                    })
            out[armor + "_" + mode] = rows
    return out


def self_test() -> None:
    records = catalog()
    matrix = source_matrix(records)
    assert len(matrix) == 4
    assert all(len(rows) == 10 for rows in matrix.values())
    missing = [r["source_name_requested"] for rows in matrix.values()
               for r in rows if not r["source_name_found"]]
    assert not missing, "missing exact source hover records: " + repr(missing)
    assert state_for(HoverInput(-0.90, 0.04, True, "ironman")) == (
        "IronMan_Aim_Float_move_L_Att.anim", "L")
    assert state_for(HoverInput(0.90, 0, True, "warmachine")) == (
        "Warmachine_Aim_Float_move_R_Att.anim", "R")
    assert state_for(HoverInput(0, 0, False, "warmachine")) == (
        "Warmachine_Aim_Float_idle.anim", "idle")
    assert state_for(HoverInput(0.1, 0.88, True, "ironman")) == (
        "IronMan_Aim_Float_move_F_Att.anim", "F")
    assert choose_direction(0.22, 0.05, "R") == "R"
    assert choose_direction(0.1, 0.04, "R") == "idle"
    assert choose_direction(-0.97, 0.05, "R") == "L"
    assert expected_name("warmachine", "aim_m", "L", True) == (
        "Warmachine_Aim_M_Float_move_L_Att.anim")
    print("PASS 40 original named hover source states; L/R/F/B, hold+fire, idle, "
          "two separate aim families, 7 deterministic input tests")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--report", type=Path)
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
    if a.report:
        result = {
            "evidence": "source 2010 names, duration and track-label counts (not yet baked or runtime-connected)",
            "matrix": source_matrix(catalog()),
            "all_aim_m_weapon_missile_associations_proven": False,
            "real_original_transitions_recovered": False,
            "current_vita_g8_file_changed": False,
            "next": "Bake each source clip against actual original BRES skin and render source pose preview; then crossfade transitions and GPU-runtime mapping",
        }
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print("SOURCE_HOVER_CLIPS", sum(len(v) for v in result["matrix"].values()))


if __name__ == "__main__":
    main()
