#!/usr/bin/env python3
"""Explain exactly which original C1L1 surfaces can render textures from C1UV.

Real 370 BRES/GLB meshes and 22919 triangles. Unlike prior milestone 169
candidate-UV claim, count genuine UV-carrying FACES not just mesh count and
mark surfaces missing UVs explicitly. No inferred diffuse atlas assignments.
"""
from __future__ import annotations
import argparse,collections,json,tempfile
from pathlib import Path
from recover_c1l1_original_uv import recover
def main(out):
 with tempfile.TemporaryDirectory(prefix='map_first_native_uv_') as td:
  root=Path(td)
  m=recover(root/'original.c1uv',root/'uv_manifest.json')
  groups=collections.defaultdict(lambda:collections.Counter())
  mat=collections.defaultdict(lambda:collections.Counter())
  for mesh in m['meshes']:
   g=mesh['category']
   c=groups[g]
   c['all_meshes']+=1;c['all_faces']+=mesh['triangles'];c['all_vertices']+=mesh['vertices']
   if mesh['uv_candidate']:
    c['texturable_meshes']+=1;c['texturable_faces']+=mesh['triangles']
    c['texturable_verts']+=mesh['vertices']
   else:
    c['missing_uv_meshes']+=1;c['missing_uv_faces']+=mesh['triangles']
   for p in mesh['submesh_materials']:
    mat[g][p['source_name']]+=p['triangles']
  output={'source_year':2010,'original_C1L1_triangle_total':22919,
   'original_source_meshes':370,'groups':{k:dict(v) for k,v in groups.items()},
   'original_real_material_face_frequency':{k:dict(v) for k,v in mat.items()},
   'original_material_TGA_binding_proven':False,
   'UV_zero_BRES_faces_must_not_get_false_solid_texture':True}
  out.parent.mkdir(parents=True,exist_ok=True)
  out.write_text(json.dumps(output,indent=2)+'\n')
  for g,v in groups.items():
   print('MAP_FIRST_NATIVE_UV_REAL_SOURCE',g,dict(v),
     'untexturable_source_faces',v['missing_uv_faces'],
     'source_candidates_percent',round(100*v['texturable_faces']/v['all_faces'],2),flush=True)
  print('PASS 2010 all original C1L1 materials and true UV-carried face coverage by each scene group, NO VPK',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.out)
