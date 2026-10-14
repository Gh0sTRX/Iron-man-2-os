#!/usr/bin/env python3
"""2010 C1L1 exact pointer reference analysis: submesh author material -> TGA.

BRES original contains internal material labels and full original TGA strings.
Only assign diffuse if there is direct pointer evidence in same record.
"""
import collections,json,re,struct,zipfile
from pathlib import Path
from recover_c1l1_original_uv import BDAEZIP,SOURCES
from b24_g10_bres_material_pointer_probe import inspect

def forensic():
 with zipfile.ZipFile(BDAEZIP) as z:
  records=[]
  for bres_name in SOURCES:
   raw=z.read("original_models/"+bres_name+".bdae")
   labels=collections.Counter()
   for m in re.finditer(rb"[a-zA-Z0-9_./\\-]{3,120}\.tga\x00",raw,re.I):
    labels[m.group(0)[:-1].decode("latin1")].append(m.start()) if False else None
   tgas=collections.defaultdict(set)
   for m in re.finditer(rb"[a-zA-Z0-9_./\\-]{3,120}\.tga\x00",raw,re.I):
    tgas[m.group(0)[:-1].decode("latin1")].add(m.start())
   # Enumerate pointer positions that point exactly to 2010 TGA filename strings
   refs=collections.defaultdict(list)
   for off in range(0,len(raw)-3,4):
    pointer=struct.unpack_from("<I",raw,off)[0]
    for label,targets in tgas.items():
     if pointer in targets:
      refs[label].append(off)
   records.append({"original_bres":bres_name,
      "literal_tga_string_offsets":{x:sorted(v)[:7] for x,v in tgas.items()},
      "direct_native_pointer_references":{x:v[:25] for x,v in refs.items()},
      "total_pointer_hits":sum(map(len,refs.values())),
      "sampler_material_link_proven":False})
   print("2010_C1L1_TGA_DIRECT_POINTER_COUNTS",bres_name,
         {x:len(v) for x,v in refs.items() if v})
 return records
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 rec=forensic()
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps({"original":rec},indent=2)+"\n")
 print("PASS 2010 exact BRES material-to-TGA pointer reference enumeration; no asserted face mapping")
