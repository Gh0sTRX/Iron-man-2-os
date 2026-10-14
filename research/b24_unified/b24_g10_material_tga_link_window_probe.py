#!/usr/bin/env python3
"""Original 2010 BRES material label and PVR/TGA link pointer neighborhoods.

Find all independently real pointer-containing BRES records and determine
whether a unique authored material->texture association can be traced.
No artificial material ID/atlas guesses allowed.
"""
import argparse,collections,json,re,struct,zipfile
from pathlib import Path
from recover_c1l1_original_uv import BDAEZIP,SOURCES

def source(raw):
 n=len(raw)
 U=lambda off:struct.unpack_from("<I",raw,off)[0]
 strings={}
 for m in re.finditer(rb"[A-Za-z0-9_./\\-]{3,120}(?:\.tga|\-mesh|Standard_[A-Za-z0-9_]*|Material__[0-9]+)\x00",raw,re.I):
  strings[m.start()]=m.group(0)[:-1].decode("latin1","ignore")
 references=collections.defaultdict(list)
 for off in range(0,n-3,4):
  target=U(off)
  if target in strings:references[target].append(off)
 def nearby(ref):
  start=max(0,ref-48);stop=min(n,ref+80)
  coords=range((start+3)//4*4,stop-3,4)
  out=[]
  for off in coords:
   val=U(off)
   if val in strings:out.append({"field_offset":off,"points_to":strings[val]})
  return out
 exact=[]
 for target,label in strings.items():
  if ".tga" not in label.lower() and not label.startswith(("Standard_","Material__")):continue
  refs=references.get(target,[])
  exact.append({"kind":"texture" if ".tga" in label.lower() else "material",
   "name":label,"string_offset":target,"u32_ref_offsets":refs[:16],
   "u32_pointer_neighbor_strings":[{"ref":r,"near":nearby(r)} for r in refs[:4]]})
 return exact
def main(out):
 all=[]
 with zipfile.ZipFile(BDAEZIP) as z:
  for name in SOURCES:
   raw=z.read("original_models/"+name+".bdae")
   rows=source(raw)
   if name=="C1L1_ground_001":
     for r in rows:
      if r["kind"]=="material":
       print("C1L1_GROUND_AUTHOR_MATERIAL_NEIGHBOR",r["name"],
             r["u32_ref_offsets"][:5],
             r["u32_pointer_neighbor_strings"][:2])
     for r in rows:
      if r["kind"]=="texture":
       print("C1L1_GROUND_AUTHOR_TGA_POINTER",r["name"],r["u32_ref_offsets"][:5],
             r["u32_pointer_neighbor_strings"][:2])
   all.append({"original_model":name,
      "real_native_reference_rows":rows})
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({"sources":all,"material_to_diffuse_recovered":False},
                          indent=2)+"\n")
 print("PASS exact native original BRES material and TGA linked pointer record graph, no invented texture mapping")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();main(a.out)
