#!/usr/bin/env python3
"""Verified 2010 Gameloft Iron Man 2 iOS named resource-pack decoder.
The caller must provide their OWN original IPA bytes; never fetch or publish
the IPA from this module. Source-only until asset conversion is verified.
Index: u16 N, N u32 offsets relative to END of index table;
       first offset 0; second offset is end of (u16 count + names),
       offsets[i+1:i+3] cover resource i, name count N-2.
No guessed source asset names, silent corruption or fuzzy records.
"""
from __future__ import annotations
from dataclasses import dataclass
import struct
from typing import List
@dataclass(frozen=True)
class Resource:
    name: str
    start: int
    end: int
def decode(data:bytes,expected_type:str="") -> List[Resource]:
    if len(data)<18:raise ValueError("Gameloft pack truncated")
    n=struct.unpack_from("<H",data)[0]
    if not 2<n<5000:raise ValueError("resource count invalid")
    base=2+4*n
    if base+2>len(data):raise ValueError("index truncated")
    offsets=struct.unpack_from("<"+str(n)+"I",data,2)
    if offsets[0]!=0 or offsets[-1]!=len(data)-base:
        raise ValueError("packed archive base/end invalid")
    if any(a>=b for a,b in zip(offsets,offsets[1:])):
        raise ValueError("record offsets not monotonic")
    count=struct.unpack_from("<H",data,base)[0]
    if count!=n-2:raise ValueError("name count mismatch")
    pos=base+2
    rows=[]
    names=set()
    for i in range(count):
        if pos+2>base+offsets[1]:raise ValueError("name size OOB")
        strlen=struct.unpack_from("<H",data,pos)[0]
        pos+=2
        if not 1<=strlen<=255 or pos+strlen>base+offsets[1]:
            raise ValueError("name truncated or overlong")
        name=data[pos:pos+strlen].decode("utf-8")
        pos+=strlen
        if name in names:raise ValueError("name collision")
        names.add(name)
        start,end=base+offsets[i+1],base+offsets[i+2]
        if start>=end or end>len(data):raise ValueError("resource outside archive")
        rows.append(Resource(name,start,end))
    if pos!=base+offsets[1]:
        raise ValueError("name table not exact original offset")
    if expected_type and any(not r.name.lower().endswith(expected_type.lower()) for r in rows):
        raise ValueError("mismatched packed asset file type")
    return rows
def get_exact(data:bytes,records:List[Resource],name:str)->bytes:
    matches=[r for r in records if r.name==name]
    if len(matches)!=1:raise KeyError("exact original resource not present: "+name)
    r=matches[0]
    return data[r.start:r.end]
