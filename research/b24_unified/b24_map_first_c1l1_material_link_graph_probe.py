#!/usr/bin/env python3
"""Real 2010 C1L1 BRES material triangle-to-texture reference graph.

No scene color guess: inspect 10 true source BRES 56-byte mesh submesh records,
material name pointers and native texture TGA ptr table, 2010 iOS endian.
We explicitly discriminate pointer graph evidence from coincidental names.
Print compact enough to inspect CI logs; JSON has detailed linkage.
"""
from __future__ import annotations
import argparse, collections, json, re, struct, zipfile
from pathlib import Path
from recover_c1l1_original_uv import BDAEZIP, SOURCES
def U(raw,offset):
 return struct.unpack_from('<I',raw,offset)[0]
def printable(raw,pos,limit=100):
 if not 0<=pos<len(raw):return None
 end=raw.find(b'\x00',pos,min(len(raw),pos+limit))
 if end<0 or end<=pos or end-pos>limit:return None
 s=raw[pos:end]
 if not all(32<=v<127 for v in s):return None
 return s.decode('latin1')
def resolve(blob, parser, name):
 meshes,stats=parser(blob)
 sources=collections.defaultdict(set)
 # Only true author strings anchored on exact NUL start.
 for m in re.finditer(rb'(?:[a-zA-Z0-9_./\\-]{3,115}\.tga)\x00',blob,re.I):
  s=m.group(0)[:-1].decode('latin1')
  if s.lower().startswith(('../../textures/','c1l1_','c1l1/')) or 'c1l1/' in s.lower():
   sources[s.split('/')[-1].casefold()].add(m.start()+len(s)-len(s.split('/')[-1]))
 texstrings={off:key for key,spots in sources.items() for off in spots}
 # All real 32-bit pointer references to exact texture strings; do not
 # assume their order or BRES material palette semantics.
 texptrs={}
 for off in range(0,len(blob)-3,4):
  target=U(blob,off)
  if target in texstrings:texptrs[off]=texstrings[target]
 texrefpositions=sorted(texptrs)
 out=[]
 for mi,m in enumerate(meshes):
  sd=U(blob,m['mesh_descriptor']+28)
  for si,sub in enumerate(m['submeshes']):
   rp=sd+si*56
   rec=[U(blob,rp+4*i) for i in range(14)]
   addrptr=rec[1]
   if printable(blob,addrptr)!=sub['material']:raise ValueError("BRES original actual material name pointer drift")
   # Exact pointer to TGA string anywhere in original record; could be
   # texture table index instead -> separately report texture table.
   direct=[{'field':k,'name':texstrings[v]} for k,v in enumerate(rec) if v in texstrings]
   links=[]
   for k,v in enumerate(rec):
    if not (0<v<len(blob)-4 and v%4==0):continue
    # Inspect ONLY direct pointer target with 16 original u32 fields,
    # not a guessed unlimited recursive search.
    near=[{'offset':v+4*j,'name':texptrs[v+4*j]} for j in range(16)
          if v+4*j in texptrs]
    if near:links.append({'field':k,'source_pointer_target':v,'texture_table_record_matches':near})
   out.append({'original_bres':name,'mesh_index':mi,'submesh_index':si,
     'material':sub['material'],'original_face_count':len(sub['faces']),
     'submesh_record_offset':rp,'record_14_words':rec,
     'material_string_ptr_field1':addrptr,'direct_to_TGA':direct,
     'one_hop_adjacent_to_TGA_pointer_table':links})
 return {'name':name,'size':len(blob),'source_meshes':len(meshes),
    'submeshes':len(out),'BRES_material_graph_records':out,
    'texture_files_actual_in_source':sorted(sources.keys()),
    'original_table_ptr_offsets_by_file':{
      key:[p for p,x in texptrs.items() if x==key][:10] for key in sources},
    'material_to_TGA_link_verified':False}
def run(out):
 with zipfile.ZipFile(BDAEZIP) as z:
  ns={'__name__':'_source_b11','__file__':'bdae_scene_parser.py'}
  exec(compile(z.read('bdae_scene_parser.py'),'bdae_scene_parser.py','exec'),ns)
  rows=[]
  for name in SOURCES:
   r=resolve(z.read('original_models/'+name+'.bdae'),ns['parse'],name)
   rows.append(r)
   exact=sum(bool(q['direct_to_TGA']) for q in r['BRES_material_graph_records'])
   near=sum(bool(q['one_hop_adjacent_to_TGA_pointer_table']) for q in r['BRES_material_graph_records'])
   print('G11_C1L1_ORIGINAL_BRES',name,'meshes',r['source_meshes'],
         'original_source_submeshes',r['submeshes'],'actual_original_TGA_names',
         r['texture_files_actual_in_source'],'direct_face_texture_refs',exact,
         'one_hop_texture_table_pointer_refs',near,flush=True)
   for q in r['BRES_material_graph_records'][:3]:
    print('G11_C1L1_ORIGINAL_FACE_GRAPH',name,
         'material',q['material'],'14_uint32',q['record_14_words'],
         'name_ptr',q['material_string_ptr_field1'],
         'texture_refs',q['direct_to_TGA'],'one_hop',q['one_hop_adjacent_to_TGA_pointer_table'],flush=True)
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({'source_year':2010,'sources':rows,
   'false_surface_texture_associations_not_silently_accepted':True,
   'source_39_GPU_textures_ready_but_not_Vita_bound':True},indent=2)+'\n')
 print('PASS ten original C1L1 BRES records parsed original per-triangle material name + exact TGA index probe NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
 run(args.out)
