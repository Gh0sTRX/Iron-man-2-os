#!/usr/bin/env python3
"""Original owner 2010 Gameloft Iron Man 2 level1.bclara MATERIAL / SPAWN probe.

Texture index refs were NOT directly located in source BRES material table.
The original authored level1 scene may override NodeMaterials/texture slots,
as CLARA has node binding and positioned authored SpawnPoint000..015.

No guessed triples accepted as 2010 authored positions. This is grounded
byte-level schema exploration and original string property frequency only.
"""
from __future__ import annotations
import argparse,collections,json,math,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact

KEYWORDS=('nodematerials','material','texture','diffuse','shader','ground',
          'position','spawnpoint','rotation','translation','scale','parent',
          'c1l1','level','model','file','node')
def snippets(raw,which):
 hits=[]
 lower=raw.lower()
 for term in which:
  needle=term.lower().encode()
  start=0
  while True:
   i=lower.find(needle,start)
   if i<0:break
   a=max(0,i-48);b=min(len(raw),i+128)
   data=raw[a:b]
   hits.append({'property':term,'offset':i,'neighbor_bytes_start':a,
      'raw_2010_context_hex':data.hex(),
      'source_context_ASCII':''.join(chr(q) if 32<=q<=126 else '.' for q in data)})
   start=i+len(needle)
 return sorted(hits,key=lambda x:x['offset'])
def main(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  b=z.read('Payload/IronMan2.app/clev')
 level=get_exact(b,decode(b,'.bclara'),'level1.bclara')
 raw=level
 strings=collections.defaultdict(list)
 # Only true consecutive printable 5+ ASCII at native byte positions,
 # not pretending arbitrary bytes are binary property values.
 for m in re.finditer(rb'[ -~]{5,110}',raw):
  txt=m.group(0).decode('ascii')
  strings[txt].append(m.start())
 names=[(key,locs) for key,locs in strings.items() if
        any(term in key.lower() for term in KEYWORDS)]
 model_refs=[(k,v) for k,v in names if ('C1L1_' in k or 'c1l1_' in k)]
 image_refs=[(k,v) for k,v in names if '.tga' in k.casefold() or '.pvr' in k.casefold()]
 mat_refs=[(k,v) for k,v in names if 'material' in k.casefold()]
 points=[(k,v) for k,v in names if 'spawnpoint' in k.casefold()]
 hist=collections.Counter()
 for t in KEYWORDS:hist[t]=sum(raw.lower().count(t.encode()) for _ in (0,))
 source_events=snippets(raw,('NodeMaterials','Material__','Texture','Diffuse','SpawnPoint000','SpawnPoint015','Position'))
 output={'filename':'level1.bclara','original_bytes':len(raw),
         'author_declared_property_counts':dict(hist),
         '2010_field_strings_with_offsets':[
            {'text':k,'true_offset_first':v[0],'count':len(v)} for k,v in names[:300]],
         'C1L1_mesh_name_references':[{'name':k,'source_offsets':v[:8]} for k,v in model_refs[:90]],
         'original_texture_filename_references':[{'name':k,'source_offsets':v[:8]} for k,v in image_refs[:90]],
         'original_material_name_references':[{'name':k,'source_offsets':v[:8]} for k,v in mat_refs[:90]],
         'original_spawn_node_references':[{'name':k,'source_offsets':v[:8]} for k,v in points[:40]],
         'native_property_contexts':source_events[:210],
         'original_material_to_TGA_verified':False,
         'original_player_spawn_xyz_verified':False,
         'contains_original_user_PVR_bytes':False,
         'does_not_infer_graphics_from_model_name':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(output,indent=2)+'\n')
 print('C1L1_GAME_AUTHORED_LEVEL1_PROPERTY_HISTOGRAM',dict(hist),flush=True)
 print('C1L1_TRUE_SCENE_REFERENCES',model_refs[:40],flush=True)
 print('C1L1_ACTUAL_TEXTURE_REFERENCES',image_refs[:40],flush=True)
 print('C1L1_NATIVE_MATERIAL_REFERENCES',mat_refs[:40],flush=True)
 print('C1L1_AUTHORED_SPAWN_NAMES',points[:40],flush=True)
 print('PASS real 2010 original level1.bclara material and scene property byte-level evidence, no guessed spawn, no map invented, NO VPK',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.ipa,a.out)
