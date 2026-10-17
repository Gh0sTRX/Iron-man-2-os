#!/usr/bin/env python3
"""2010 owner Iron Man 2 iOS Mach-O Lua Wait native function pointer
forensics. Read-only from private original IPA; output metadata ONLY.
An absent paired registration does not justify guessing time units.
"""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

KNOWN={
    "ShowTut":0x18818,
    "IsTutConfirmed":0x187BC,
    "PauseMusic":0x17ECC,
    "PlayMusic":0x18000,
    "PlayVoice":0x18A04,
}
NAMES=("Wait","IsTutConfirmed","ShowTut","PauseMusic","PlayMusic","PlayVoice","StopVoice")
def u32(buf,i):
    if i<0 or i+4>len(buf):
        return None
    return struct.unpack_from('<I',buf,i)[0]

def segments(buf):
    if u32(buf,0)!=0xFEEDFACE:
        raise ValueError("owner original Mach-O must be 32bit little-endian")
    ncmds=u32(buf,16)
    cursor=28
    result=[]
    for _ in range(ncmds):
        cmd=u32(buf,cursor)
        size=u32(buf,cursor+4)
        if not size or size<8 or cursor+size>len(buf):
            raise ValueError("Mach-O load command OOB")
        if cmd==1:
            fields=struct.unpack_from('<II16sIIIIiiII',buf,cursor)
            name=fields[2].rstrip(b'\0').decode('ascii','replace')
            vm,vms,fileoff,filesize=fields[3:7]
            if fileoff+filesize>len(buf):
                raise ValueError("Mach-O segment outside owner binary")
            result.append({"name":name,"vmaddr":vm,"vmsize":vms,
                           "fileoff":fileoff,"filesize":filesize})
        cursor+=size
    if not result:
        raise ValueError("Original Mach-O has no LC_SEGMENT")
    return result

def offset_to_vm(segs,offset):
    for s in segs:
        if s['fileoff']<=offset<s['fileoff']+s['filesize']:
            return s['vmaddr']+offset-s['fileoff']
    return None

def vm_to_offset(segs,vm):
    for s in segs:
        if s['vmaddr']<=vm<s['vmaddr']+s['filesize']:
            return s['fileoff']+vm-s['vmaddr']
    return None

def exact_ascii_offsets(binary,name):
    needle=name.encode('ascii')+b'\0'
    p=0;result=[]
    while True:
        pos=binary.find(needle,p)
        if pos<0:
            return result
        prev=binary[pos-1] if pos else 0
        if not ((48<=prev<=57) or (65<=prev<=90) or (97<=prev<=122) or prev==95):
            result.append(pos)
        p=pos+1

def refs_of_u32(buf,value):
    b=struct.pack('<I',value)
    offsets=[]
    pos=0
    while True:
        x=buf.find(b,pos)
        if x<0:
            return offsets
        if x%4==0:
            offsets.append(x)
        pos=x+1

def run(ipa,out):
    if ipa.stat().st_size!=248613763:
        raise ValueError("owner v1.0.0 248613763-byte original IPA required")
    with zipfile.ZipFile(ipa) as z:
        executable=z.read('Payload/IronMan2.app/IronMan2')
    if len(executable)!=7480208:
        raise ValueError('owner v1.0.0 Mach-O executable size drift')
    segs=segments(executable)
    textseg=next((s for s in segs if s['name']=='__TEXT'),None)
    if textseg is None:
        raise ValueError('original ARM Mach-O TEXT segment missing')
    matches={}
    records={}
    for name in NAMES:
        occurrences=exact_ascii_offsets(executable,name)
        values=[]
        for loc in occurrences:
            vm=offset_to_vm(segs,loc)
            if vm is None:
                continue
            for ref in refs_of_u32(executable,vm):
                near=[]
                for delta in (-16,-12,-8,-4,4,8,12,16):
                    addr=u32(executable,ref+delta)
                    # exclude string/data pointers; require address in actual
                    # executable __TEXT file-backed range, label only as
                    # candidate until independently verified.
                    if (addr is not None and
                        textseg['vmaddr']<=addr<textseg['vmaddr']+textseg['filesize']):
                        near.append({"delta":delta,"candidate_code_vm":addr})
                values.append({"ascii_file_offset":loc,"ascii_vm":vm,
                               "name_pointer_file_offset":ref,
                               "nearby_code_pointers":near[:12]})
        records[name]={"ascii_matches_count":len(occurrences),
                       "pointer_reference_count":len(values),
                       "references":values[:32]}
    # Look for *paired* known registration (name ptr, known native
    # handler) to validate table stride/order before using a candidate
    # Wait address. If native code emits registrations directly and no
    # pair is found, return INCONCLUSIVE rather than inventing semantics.
    checked=[]
    for name,knownfunc in KNOWN.items():
        for row in records[name]["references"]:
            for candidate in row["nearby_code_pointers"]:
                if candidate["candidate_code_vm"] in (knownfunc,knownfunc|1):
                    checked.append({
                        "known":name,"function_vm":knownfunc,
                        "registration_ref":row["name_pointer_file_offset"],
                        "pointer_delta":candidate["delta"]})
    offsets={x["pointer_delta"] for x in checked}
    reliable_offsets={
        dx for dx in offsets if sum(1 for x in checked if x['pointer_delta']==dx)>=2
    }
    wait=[]
    for row in records["Wait"]["references"]:
        for candidate in row["nearby_code_pointers"]:
            if candidate["delta"] in reliable_offsets:
                wait.append({"wait_name_ref":row["name_pointer_file_offset"],
                    "native_candidate_vm":candidate["candidate_code_vm"],
                    "established_registration_delta":candidate["delta"]})
    result={
        "source":"user original 2010 Iron Man 2 iOS 1.0.0 Mach-O",
        "source_executable_bytes":len(executable),
        "source_sha256":hashlib.sha256(executable).hexdigest(),
        "segments":segs,
        "known_native_ARM_lua_handlers":KNOWN,
        "paired_registration_anchors":checked[:35],
        "cross_confirmed_pointer_deltas":sorted(reliable_offsets),
        "wait_handler_candidates_table_provenance":wait[:24],
        "registration_confirmed":bool(reliable_offsets),
        "wait_time_unit_proven":False,
        "original_Wait10_runtime_executed":False,
        "new_vpk":False,
        "string_pointer_references":records}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print("G154 native Mach-O source Wait registration references",
          records['Wait']['pointer_reference_count'])
    print("G154 independently paired known native handlers:",checked[:12])
    print("G154 matched registration strides",sorted(reliable_offsets))
    print("G154 native Wait candidates",wait[:15])
    print("G154 source only; time units unknown until native handler logic proved, no VPK")

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--ipa',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    run(a.ipa,a.out)
