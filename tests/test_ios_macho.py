#!/usr/bin/env python3
"""Synthetic safety regressions: no copyrighted IPA, no Vita hardware."""
import sys
from pathlib import Path
import struct
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_ios_macho import inspect_macho, feasibility


def command(cmd, body=b""):
    size = 8 + len(body)
    assert size % 4 == 0
    return struct.pack("<II", cmd, size) + body


def macho(commands, data=b""):
    body = b"".join(commands)
    return struct.pack("<IiiIIII", 0xFEEDFACE, 12, 9, 2, len(commands), len(body), 0) + body + data


def segment(fileoff=0, filesize=0, vmsize=0x1000, sections=0):
    return command(1, struct.pack("<16sIIIIiiII", b"__TEXT", 0x1000, vmsize,
                                  fileoff, filesize, 7, 5, sections, 0))


def dylib(path=b"/System/Library/Foo.dylib\0"):
    pad = (-len(path)) % 4
    return command(0xC, struct.pack("<IIII", 24, 0, 0, 0) + path + b"\0" * pad)


class MachoAuditTests(unittest.TestCase):
    def test_valid_macho(self):
        cmds = [segment(), dylib(), command(0x21, struct.pack("<III", 0, 0, 0)), command(5)]
        r = inspect_macho(macho(cmds))
        self.assertTrue(r["arm_cpu"] and r["executable"] and r["entry_command_present"])
        self.assertFalse(r["encrypted_on_disk"])
        self.assertEqual(r["dynamic_libraries"], ["/System/Library/Foo.dylib"])

    def test_fairplay_cryptid_blocker(self):
        r = inspect_macho(macho([segment(), command(0x21, struct.pack("<III", 0, 0, 1))]))
        self.assertTrue(r["encrypted_on_disk"])

    def test_short_header_and_fat_rejected(self):
        for item in (b"", b"\xCA\xFE\xBA\xBE" + b"\0" * 28):
            with self.assertRaises(ValueError):
                inspect_macho(item)

    def test_out_of_bounds_segment(self):
        with self.assertRaises(ValueError):
            inspect_macho(macho([segment(fileoff=999999, filesize=4)]))

    def test_out_of_bounds_dylib_name(self):
        with self.assertRaises(ValueError):
            inspect_macho(macho([command(0xC, struct.pack("<IIII", 1000, 0, 0, 0))]))

    def test_bad_command_length(self):
        raw = bytearray(macho([segment()]))
        struct.pack_into("<I", raw, 32, 3)
        with self.assertRaises(ValueError):
            inspect_macho(raw)

    def test_readiness_does_not_claim_runtime(self):
        r = inspect_macho(macho([segment(), command(5)]))
        r.update(known_2010_owner_executable=True, ipa_sha256_matches_known_2010_owner=True)
        f = feasibility(r)
        self.assertTrue(f["static_prerequisites_pass"])
        self.assertFalse(f["runtime_proven"])
        self.assertFalse(f["vita_compatible_proven"])


if __name__ == "__main__":
    unittest.main()
