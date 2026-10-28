#!/usr/bin/env python3
"""Read-only iOS ARM Mach-O feasibility report. Never executes or patches game code."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile

MAGIC = 0xFEEDFACE
CPU_TYPE_ARM = 12
MH_EXECUTE = 2
LC_SEGMENT = 1
LC_LOAD_DYLIB = {0xC, 0x18, 0x1F, 0x23}
LC_ENCRYPTION_INFO = 0x21
LC_ENCRYPTION_INFO_64 = 0x2C
LC_UNIXTHREAD = 5
LC_MAIN = 0x28
LC_SYMTAB = 2
KNOWN_EXE_SHA256 = "3ba6337a23ab7e08f2e025ec9731c53a7990e8d611b59eac07ba00cb63acc629"
KNOWN_IPA_SHA256 = "4c338c71cdd2817afb10099b90834c911d3c82e94adc477f24a9f9f4e0479c94"
GAME_PATH = "Payload/IronMan2.app/IronMan2"


def inspect_macho(data):
    if len(data) < 28:
        raise ValueError("Truncated Mach-O header")
    magic, cpu, subtype, filetype, count, size, flags = struct.unpack_from("<IiiIIII", data)
    if magic != MAGIC:
        raise ValueError("Expected little-endian 32-bit Mach-O (not ELF, FAT or ARM64)")
    if count > 10000 or size > len(data) - 28 or count * 8 > size:
        raise ValueError("Invalid Mach-O load command table")
    offset, end = 28, 28 + size
    segments, libraries, encryption = [], [], []
    entry = False
    symbol_table = False
    for _ in range(count):
        if offset + 8 > end:
            raise ValueError("Truncated load command")
        cmd, cmdsize = struct.unpack_from("<II", data, offset)
        if cmdsize < 8 or cmdsize % 4 or offset + cmdsize > end:
            raise ValueError("Invalid load command bounds/alignment")
        kind = cmd & 0x7FFFFFFF
        if kind == LC_SEGMENT:
            if cmdsize < 56:
                raise ValueError("Truncated segment")
            rawname, vmaddr, vmsize, fileoff, filesize, maxprot, initprot, nsects, sflags = struct.unpack_from(
                "<16sIIIIiiII", data, offset + 8)
            if nsects > (cmdsize - 56) // 68 or filesize > len(data) or fileoff > len(data) - filesize or filesize > vmsize:
                raise ValueError("Invalid segment section/file size")
            segments.append(dict(name=rawname.split(b"\0", 1)[0].decode("ascii", "replace"),
                                 vmaddr=vmaddr, vmsize=vmsize, file_bytes=filesize,
                                 executable=bool(initprot & 4)))
        elif kind in LC_LOAD_DYLIB:
            if cmdsize < 24:
                raise ValueError("Truncated dylib command")
            nameoff = struct.unpack_from("<I", data, offset + 8)[0]
            if not 24 <= nameoff < cmdsize:
                raise ValueError("Invalid dylib name offset")
            raw = data[offset + nameoff:offset + cmdsize]
            if b"\0" not in raw:
                raise ValueError("Unterminated dylib path")
            libraries.append(raw.split(b"\0", 1)[0].decode("utf-8", "replace"))
        elif kind in (LC_ENCRYPTION_INFO, LC_ENCRYPTION_INFO_64):
            if cmdsize < (24 if kind == LC_ENCRYPTION_INFO_64 else 20):
                raise ValueError("Truncated encryption info")
            cryptoff, cryptsize, cryptid = struct.unpack_from("<III", data, offset + 8)
            if cryptsize > len(data) or cryptoff > len(data) - cryptsize:
                raise ValueError("Invalid encryption range")
            encryption.append(dict(cryptid=cryptid, cryptoff=cryptoff, cryptsize=cryptsize))
        elif kind in (LC_UNIXTHREAD, LC_MAIN):
            entry = True
        elif kind == LC_SYMTAB:
            symbol_table = True
        offset += cmdsize
    if offset != end:
        raise ValueError("Load command size does not match header")
    return dict(format="Mach-O 32-bit little-endian", arm_cpu=(cpu == CPU_TYPE_ARM),
                cpu_type=cpu, cpu_subtype=subtype & 0xFF, executable=(filetype == MH_EXECUTE),
                load_commands=count, entry_command_present=entry,
                symbol_table_present=symbol_table, segments=segments,
                dynamic_libraries=libraries, encryption_commands=encryption,
                encrypted_on_disk=any(x["cryptid"] != 0 for x in encryption),
                file_backed_segment_bytes=sum(x["file_bytes"] for x in segments))


def inspect_ipa(path):
    # Only read one bounded executable member. Never unpack or re-publish IPA assets.
    with zipfile.ZipFile(path) as z:
        item = z.getinfo(GAME_PATH)
        if item.file_size > 64 * 1024 * 1024:
            raise ValueError("Game executable exceeds diagnostic safety bound")
        data = z.read(item)
    result = inspect_macho(data)
    result["executable_sha256"] = hashlib.sha256(data).hexdigest()
    result["known_2010_owner_executable"] = result["executable_sha256"] == KNOWN_EXE_SHA256
    result["ipa_sha256_matches_known_2010_owner"] = file_sha256(path) == KNOWN_IPA_SHA256
    return result


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def feasibility(report):
    issues = []
    if not report["arm_cpu"] or not report["executable"]:
        issues.append("Not an ARM Mach-O main executable")
    if report["encrypted_on_disk"]:
        issues.append("cryptid is nonzero; decrypted owner executable required")
    if not report["entry_command_present"]:
        issues.append("No LC_MAIN/LC_UNIXTHREAD; inspect startup method")
    if not report["segments"]:
        issues.append("No LC_SEGMENT mappings")
    if not report["known_2010_owner_executable"]:
        issues.append("Executable differs from known Iron Man 2 1.0.0 sample")
    if not report["ipa_sha256_matches_known_2010_owner"]:
        issues.append("IPA differs from verified owner sample")
    return dict(static_prerequisites_pass=(len(issues) == 0), blockers_or_unknowns=issues,
                runtime_proven=False, vita_compatible_proven=False,
                still_required=["ARM relocation/rebase audit", "import symbol and ObjC framework shim inventory",
                                "global constructors and threading audit", "Vita memory/render/audio runtime test"])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ipa", type=Path, required=True, help="Local owner IPA outside Git")
    p.add_argument("--out", type=Path, help="Optional JSON report outside Git")
    a = p.parse_args()
    result = inspect_ipa(a.ipa)
    result["feasibility"] = feasibility(result)
    blob = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(blob, encoding="utf-8")
    else:
        print(blob, end="")


if __name__ == "__main__":
    main()
