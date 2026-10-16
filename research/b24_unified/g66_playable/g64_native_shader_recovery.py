#!/usr/bin/env python3
"""G64 authentic 2010 BRES material record index decoding, 40B/60B property variants.

Native v0.0.0.133 BRES: 20B TGA table, 88B shader resource array,
variable 40B/60B shader property records, 64B material definitions.
The final u32 of each validated native property block identifies its
source-local TGA table index. No mesh UV or shader blending invented.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,zipfile
from pathlib import Path
SOURCES=('C1L1_ground_001','C1L1_obj_001','C1L1_obj_002','C1L1_obj_003','C1L1_obj_004','C1L1_car_01','C1L1_car_02','C1L1_light_001','C1L1_light_002','C1L1_light_003')
TARGETS=('c1l1_3building','Material__20','Material__21','Material__12','Material__17','Material__19','Material__46','Standard_16dd')
def u(b,p):
 return struct.unpack_from('<I',b,p)[0] if p is not None and 0<=p<=len(b)-4 else None
def st(b,p):
 if p is None or not 0<=p<len(b):return None
 e=b.find(b'\0',p,min(len(b),p+108))
 if e<0 or e-p<3:return None
 a=b[p:e]
 return a.decode('latin1') if all(32<=c<127 for c in a) else None

def parse(name,b):
 n=u(b,16);beg=u(b,20);end=u(b,24)
 assert n and 0<n<100000 and beg>=32 and end<len(b) and beg+4*n==end
 reloc={u(b,beg+4*i) for i in range(n)}
 # Game-authored native MAT64 contiguous records, 3 relocated string pointers.
 defs={}
 for p in range(32,len(b)-64,4):
  if not all(p+k in reloc for k in (0,4,12)):continue
  label=st(b,u(b,p));other=st(b,u(b,p+4));fx=st(b,u(b,p+12))
  if label and label==other and fx and fx.startswith('#') and label in fx and u(b,p+8)==0:
   defs[p]=label
 runs=[]
 for p in defs:
  if p-64 in defs:continue
  count=1
  while p+64*count in defs:count+=1
  runs.append((count,p))
 assert runs,(name,'MAT64')
 nmats,mat_base=max(runs)
 mats=[defs[mat_base+64*i] for i in range(nmats)]
 # Authentic 20-byte TGA resource lookup array.
 atlas_records={}
 for p in range(32,len(b)-20,4):
  if not all(p+k in reloc for k in (0,4,8)):continue
  three=[st(b,u(b,p+k)) for k in (0,4,8)]
  if all(three) and three[0].lower().endswith('.tga') and 'tga' in three[1].lower() and 'tga' in three[2].lower():
   atlas_records[p]=three[0]
 runs=[]
 for p in atlas_records:
  if p-20 in atlas_records:continue
  count=1
  while p+20*count in atlas_records:count+=1
  runs.append((count,p))
 assert runs,(name,'TGA20')
 ntga,tga_base=max(runs)
 atlas=[atlas_records[tga_base+20*i] for i in range(ntga)]
 # 88-byte SHADER entries, exact native author label order.
 shader_base=None
 for p in range(max(32,tga_base+ntga*20-200),min(len(b)-88,tga_base+ntga*20+600),4):
  if st(b,u(b,p))!=mats[0]+'-fx' or st(b,u(b,p+4))!=mats[0]:continue
  if all(st(b,u(b,p+88*i+4))==x for i,x in enumerate(mats)):
   shader_base=p;break
 assert shader_base is not None,(name,'SHADER88')
 prop_starts=[u(b,shader_base+i*88+12) for i in range(nmats)]
 assert prop_starts==sorted(prop_starts) and len(set(prop_starts))==nmats
 assert prop_starts[0]==shader_base+nmats*88
 # The final prop record is explicitly bounded by native MAT64 array.
 rows=[]
 for i,label in enumerate(mats):
  off=prop_starts[i]; nxt=prop_starts[i+1] if i+1<nmats else mat_base
  size=nxt-off
  assert size in (20,40,60) and off+size<=len(b),(name,label,size)
  vals=struct.unpack_from('<'+'I'*(size//4),b,off)
  # Value 0xFF959595 marks special 40/60B record start. An all-FV
  # 20B record only records shader constants (no sampler). In 40/60B
  # types the final u32 also carries an original atlas index; the 60B
  # type has an additional possible lightmap index at word 13.
  last=vals[-1]
  valid=(size in (40,60) and 0<=last<ntga and
         (vals[0]==0xFF959595 or vals[0]==1 or vals[0]==0xFF000000))
  tex=atlas[last] if valid else None
  rows.append({'source':name,'material':label,'record_offset':off,
      'native_property_size':size,'texture_id':last if valid else None,
      'native_atlas':tex,'source_structural_link_valid':valid,
      'native_property_first_u32':f'0x{vals[0]:08X}'})
 return {'source':name,'source_sha256':hashlib.sha256(b).hexdigest(),
         'author_atlas_count':len(atlas),'native_property_records':rows}

def run(input_zip,out):
 with zipfile.ZipFile(input_zip) as z:
  models=[parse(s,z.read('original_models/'+s+'.bdae')) for s in SOURCES]
 bysrc={x['source']:x for x in models}
 for s in ('C1L1_light_001','C1L1_light_002','C1L1_light_003'):
  byname={x['material']:x['native_atlas'] for x in bysrc[s]['native_property_records']}
  for m,t in [('Material__20','C1L1_earth02.tga'),('Material__21','C1L1_earth.tga'),
              ('Material__12','C1L1_earth03.tga'),('Material__17','c1l1_building2.tga'),
              ('Material__19','C1L1_ground_light.TGA'),('c1l1_3building','c1l1_building.tga')]:
   assert byname[m].casefold()==t.casefold(),(s,m,byname[m],t)
 assert sum(1 for s in SOURCES if any(r['material']=='c1l1_3building' and (r['native_atlas'] or '').lower()=='c1l1_building.tga' for r in bysrc[s]['native_property_records']))==7
 focus=[r for model in models for r in model['native_property_records'] if r['material'] in TARGETS]
 out_data={'stage':'G64','source_model_count':len(models),'models_sha256':{x['source']:x['source_sha256'] for x in models},
 'all_2010_original_property_source_evidence':focus,
 'native_source_proven_sphere_material_atlas':{'Material__20':'C1L1_earth02.tga','Material__21':'C1L1_earth.tga','Material__12':'C1L1_earth03.tga'},
 'native_source_proven_missing_building_mat':'c1l1_building.tga',
 'world_placement_unchanged':True,'native_sphere_UV_zero_and_shader_procedural_undecoded':True,
 'original_runtime_shader_and_blending_rebuilt':False,'no_new_vpk':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(out_data,ensure_ascii=False,indent=2)+'\n')
 print('PASS G64: native 20B/40B/60B property layouts; seven 3building BRES; triple-consistent material20/21 sphere atlas indices')
 print('source proofs',collections.Counter((r['material'],r['native_atlas']) for r in focus))
 return out_data
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zip',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
 run(a.zip,a.out)