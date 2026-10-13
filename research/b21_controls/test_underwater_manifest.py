#!/usr/bin/env python3
"""Regression tests for original Underwater ship capitalization and 0ms pose handling.
Host-only, no Vita build; imports actual adjacent manifest generator.
"""
import csv
import io
import unittest
import underwater_manifest as audit

FIELDS=["name","source_character","nominal_family","duration_ms",
        "joint_labels","animated_translations","animated_rotations","raw_sha256"]
SCENE=[
    ("underwater_bomb_idle.anim",7),
    ("underwater_cannon_attack.anim",5),
    ("underwater_cannon_idle.anim",5),
    ("Underwater_ship02_fall.anim",4),
    ("Underwater_ship02_idle.anim",4),
    ("Underwater_ship02_shake.anim",4),
    ("Underwater_ship_fall.anim",4),
    ("Underwater_ship_idle.anim",4),
    ("Underwater_ship_shake.anim",4),
]
def fixture():
    buf=io.StringIO()
    writer=csv.DictWriter(buf,fieldnames=FIELDS)
    writer.writeheader()
    for i in range(929):
        writer.writerow(dict(name=f"Unrelated_{i:03}.anim",duration_ms=1000,
                             joint_labels=6,raw_sha256="0"*64))
    for i in range(32):
        writer.writerow(dict(name=f"Underwater_Aim_Float_{i:02}.anim",
                             duration_ms=1600,joint_labels=38,raw_sha256="1"*64))
    for name in ("Underwater_Dead_Float_idle.anim","Underwater_Dead_Swim_idle.anim"):
        writer.writerow(dict(name=name,duration_ms=0,joint_labels=38,raw_sha256="2"*64))
    for name,joints in SCENE:
        writer.writerow(dict(name=name,duration_ms=0 if "idle" in name else 3500,
                             joint_labels=joints,raw_sha256="3"*64))
    return buf.getvalue().encode("utf-8-sig")

class TestUnderwaterOriginalMetadata(unittest.TestCase):
    def test_actual_ship_casing(self):
        manifest=audit.build(fixture())
        self.assertEqual(manifest["underwater_count"],43)
        suits=[x for x in manifest["clips"] if x["requires_original_rig"]]
        scenes=[x for x in manifest["clips"] if x["category"]=="scene_object"]
        self.assertEqual(len(suits),34)
        self.assertEqual(len(scenes),9)
        self.assertTrue(all(x["joint_labels"]==38 for x in suits))
        self.assertEqual({x["source"] for x in scenes},{name for name,_ in SCENE})
        self.assertEqual(len([x for x in suits if not x["safe_bake"]]),2)
        self.assertFalse(manifest["underwater_model_verified"])
        self.assertFalse(manifest["vita_bake_verified"])
    def test_reject_incomplete_source(self):
        src=fixture().decode("utf-8-sig")
        corrupted="\n".join(src.splitlines()[:-1])+"\n"
        with self.assertRaises(AssertionError):
            audit.build(corrupted.encode("utf-8-sig"))
    def test_refuse_non_underwater_file(self):
        with self.assertRaises(ValueError):
            audit.classify("Drone_Army_Attack.anim")

if __name__=="__main__":
    unittest.main()
