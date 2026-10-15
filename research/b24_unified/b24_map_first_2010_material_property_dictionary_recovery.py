#!/usr/bin/env python3
"""Find Gameloft 2010 BRES declaration -> original material diffuse reference.

Cross-check public old Gameloft BDAE binary template v0.0.0.779 against the
user's real iOS 2010 game BRES (nearby v0.0.0.764). Unlike prior scans of
56-byte SUBMESH geometric records this scans independent authored material
DEFINITIONS and their property tables.

Source template:
https://github.com/lOlbas/Game-Engines-Filetypes-Reverse-Engineering/
  engines/Gameloft/bdae/v0.0.0.779/templates/BDAE.bt

DO NOT assign any texture until source exact native ID/pointer linking proven.
"""
from __future__ import annotations
import argparse,collections,json,re,struct,zipfile
from pathlib import Path
BDAEZIP=Path(__file__).resolve().parents[2]/'research/B11_C1L1_Source_Parser.zip'
SOURCES=('C1L1_ground_001','C1L1_obj_001','C1L1_obj_002',
         'C1L1_obj_003','C1L1_obj_004','C1L1_car_01','C1L1_car_02',
         'C1L1_light_001','C1L1_light_002','C1L1_light_003')

def u(b,p):
 return struct.unpack_from('<I',b,p)[0] if 0<=p<=len(b)-4 else None
def string(b,p):
 if p is None or not 0<=p<len(b):return None
 j=b.find(b'\x00',p,min(len(b),p+110))
 if j<0 or j-p<3:return None
 v=b[p:j]
 if not all(32<=c<127 for c in v):return None
 return v.decode('latin1')
def lookup(b,offset,window=48):
 left=max(0,offset-window)
 return [{"offset":k,"value":u(b,k),"points_to":string(b,u(b,k)) if u(b,k) is not None and
           u(b,k)<len(b) else None}
         for k in range((left+3)//4*4,min(len(b)-4,offset+window),4)]
def analyze(name,b):
 names=collections.defaultdict(list)
 for m in re.finditer(rb'(?:Standard_[A-Za-z0-9_]+|Material__[0-9]+|Water|orig_Material__[0-9]+|c1l1_3building)\x00',b):
  names[m.group(0)[:-1].decode('latin1')].append(m.start())
 rows=[]
 pointers=collections.defaultdict(list)
 for at in range(0,len(b)-3,4):
  ptr=u(b,at)
  if ptr is not None and 0<ptr<len(b) and ptr%4==0:
   pointers[ptr].append(at)
 for mname,positions in sorted(names.items())[:60]:
  for pos in positions[:4]:
   refs=pointers.get(pos,[])
   # Original SUBMESH uses 56-byte records; material declaration tables
   # should have other references to same exact name string pointer.
   details=[]
   for ref in refs[:22]:
    neighborhood=lookup(b,ref,24)
    candidates=[e for e in neighborhood if e['points_to'] is not None]
    details.append({"field_offset":ref,
                    "pointer_neighbors":candidates[:15],
                    "nearby_words": [(e['offset'],e['value']) for e in neighborhood]})
   rows.append({"material":mname,"true_name_start":pos,
     "all_native_ref_offsets":refs[:32],"ref_count":len(refs),
     "reference_contexts":details})
 header=[u(b,p) for p in range(0,min(len(b),128),4)]
 return {"original_bres":name,"file_bytes":len(b),"header_32_u32":header,
         "unique_original_material_strings":len(names),"material_pointer_inspections":rows}
def main(out):
 all=[]
 with zipfile.ZipFile(BDAEZIP) as z:
  for name in SOURCES:
   b=z.read("original_models/"+name+".bdae")
   d=analyze(name,b)
   all.append(d)
   print("G11_DAEMAT_2010",name,"FILE_FIRST_24_U32",
         d['header_32_u32'][:24],"MATERIAL_NAMES",d["unique_original_material_strings"],flush=True)
   for row in d['material_pointer_inspections'][:14]:
    print("G11_DAEMAT_DEF",name,row['material'],
          "name_offset",row['true_name_start'],
          "native_references",row['all_native_ref_offsets'][:20],
          "nearby_referenced_strings",
          [r['pointer_neighbors'] for r in row['reference_contexts'][:3]],flush=True)
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({"original_2010_BRES_material_declaration_reference_graph":all,
   "authoritative_diffuse_material_tex_pair_confirmed":False,
   "template_version_779_not_assumed_compatible_2010_764":True},indent=2)+"\n")
 print("PASS 2010 owner BRES material declarations scanned, distinguish SUBMESH from MATERIAL PROPS no VPK")
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.out)
