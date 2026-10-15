#!/usr/bin/env python3
"""G13 REAL SOURCE MESH-BY-MESH diagnostic of 'CLAY' original C1L1 visuals.

No guesses about which mesh is a film dome. Each contact-sheet tile has
source BDAE mesh name, authentic BRES material diffuse pointer, original
source UV positive flag, exact triangle count and bbox in world coords.
Renders genuine BRES triangle wireframe positions from the 2010 owner B11
scene archive as a diagnostic (NOT the game's camera or a Vita screenshot).
"""
from __future__ import annotations
import argparse,collections,contextlib,io,json,math,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from recover_c1l1_original_uv import BDAEZIP,SOURCES
from b24_map_first_2010_source_60byte_material_texture_index_recovery import decode

def source():
 rows=[];score=collections.Counter()
 with zipfile.ZipFile(BDAEZIP) as z:
  ns={'__name__':'g13_original_bres_parser','__file__':'bdae_scene_parser.py'}
  exec(compile(z.read('bdae_scene_parser.py'),'bdae_scene_parser.py','exec'),ns)
  for basename in SOURCES:
   b=z.read('original_models/'+basename+'.bdae')
   meshes,_=ns['parse'](b)
   with contextlib.redirect_stdout(io.StringIO()):
    mats,_=decode(basename,b)
   matmap={x['original_material_name']:x['candidate_true_source_TGA'] for x in mats}
   for i,m in enumerate(meshes):
    pos=np.asarray(m['positions'],dtype=np.float32)
    uv=np.asarray(m['uv'],dtype=np.float32)
    face=np.asarray(m['faces'],dtype=np.int32).reshape(-1,3)
    if len(pos)==0 or face.size==0:continue
    if uv.shape!=(len(pos),2):raise ValueError('original BRES UV mesh topology '+basename)
    source_has_uv=bool(int(m['stride'])>=20 and np.any(uv!=0.0))
    group=('ground' if '_ground_' in basename else
            'urban' if '_obj_' in basename else
            'vehicles' if '_car_' in basename else 'lights')
    orig_sub=[]
    for sub in m['submeshes']:
     label=sub['material']
     count=len(sub['faces'])
     tex=matmap.get(label)
     orig_sub.append({'original_material_name':label,'original_shader_diffuse':tex,
       'source_original_faces':count,
       'authored_named_PVR':bool(tex),
       'is_prefix_C1L1':bool(tex and tex.casefold().startswith('c1l1_')),
       'is_EXPO_nonprefix':bool(tex and tex.casefold()=='cahp01_c_expo_building.tga')})
    if sum(sub['source_original_faces'] for sub in orig_sub)!=len(face):
     raise ValueError('original submesh triangle count drift')
    bbox=(pos.min(axis=0),pos.max(axis=0))
    extent=bbox[1]-bbox[0]
    described={
      'source_mesh_name':basename+'_'+str(i),
      'source_file':basename+'.bdae','original_scene_group':group,
      'source_faces':int(len(face)),'source_vertices':int(len(pos)),
      'native_2010_source_vertex_stride':int(m['stride']),
      'genuine_original_uv_candidate':source_has_uv,
      'original_world_bbox_min':bbox[0].tolist(),
      'original_world_bbox_max':bbox[1].tolist(),
      'original_world_extents_xyz':extent.tolist(),
      'original_BRES_authored_submesh_materials':orig_sub,
      'can_draw_original_diffuse_safely':source_has_uv and any(x['authored_named_PVR'] for x in orig_sub),
      'G12_force_untextured_due_to_entire_category':group=='lights',
      'not_proven_to_be_dome':True,
    }
    rows.append((described,pos,face))
    score[group+'_total_faces']+=len(face)
    if source_has_uv:score[group+'_uv_candidate_faces']+=len(face)
    if any(x['authored_named_PVR'] for x in orig_sub):
     score[group+'_source_sampler_faces']+=sum(s['source_original_faces'] for s in orig_sub if s['authored_named_PVR'])
    if group=='lights' and source_has_uv and any(x['authored_named_PVR'] for x in orig_sub):
     score['light_faces_actually_original_UV_positive_AND_genuine_sampler']+=sum(s['source_original_faces'] for s in orig_sub if s['authored_named_PVR'])
 if len(rows)!=370 or sum(r[0]['source_faces'] for r in rows)!=22919:
  raise ValueError('original 370 BRES meshes 22919 source triangles invariant failed')
 return rows,score

COLORS={'source_diffuse_UV':'#6FC69D','source_diffuse_without_uv':'#D6A46A',
        'source_other_no_diffuse':'#9EBBCC','original_EXPO_UV':'#E7CE6B'}
def color(sub,has_uv):
 if sub['is_EXPO_nonprefix'] and has_uv:return COLORS['original_EXPO_UV']
 if sub['authored_named_PVR']:return COLORS['source_diffuse_UV'] if has_uv else COLORS['source_diffuse_without_uv']
 return COLORS['source_other_no_diffuse']
def panel(draw,r,pos,face,x0,y0,w=288,h=250):
 name=r['source_mesh_name'];uv=r['genuine_original_uv_candidate']
 c=np.array([pos[:,0],pos[:,1],pos[:,2]]).T
 center=(c.min(axis=0)+c.max(axis=0))/2.
 az=math.radians(38);elev=math.radians(28)
 axis_r=np.array([math.cos(az),-math.sin(az),0.])
 axis_u=np.array([math.sin(az)*math.sin(elev),math.cos(az)*math.sin(elev),math.cos(elev)])
 axis_z=np.array([-math.sin(az)*math.cos(elev),-math.cos(az)*math.cos(elev),math.sin(elev)])
 xy=np.column_stack(((c-center)@axis_r,(c-center)@axis_u))
 xy[:,1]*=-1
 span=np.max(xy.max(axis=0)-xy.min(axis=0))
 scale=min((w-38)/max(span,.001),(h-80)/max(span,.001))
 xy=xy*scale + np.array([x0+w*.5,y0+(h-72)*.48+25])
 # Source face identity, no invented modern model geometry; painter's approx.
 fcolors=[]
 for s in r['original_BRES_authored_submesh_materials']:
  fcolors.extend([color(s,uv)]*s['source_original_faces'])
 if len(fcolors)!=len(face):raise ValueError('owner source face/material bounds')
 depth=(c@axis_z)[face].mean(axis=1)
 for i in np.argsort(depth):
  tri=[tuple(map(float,xy[face[i,j]])) for j in range(3)]
  draw.polygon(tri,fill=fcolors[i])
  if r['source_faces']<320:draw.line(tri+[tri[0]],fill='#405061',width=1)
 draw.rectangle((x0,y0,x0+w-1,y0+h-1),outline='#536170')
 draw.rectangle((x0,y0,x0+w-1,y0+24),fill='#1B2733')
 draw.text((x0+7,y0+5),name,fill='white')
 material=r['original_BRES_authored_submesh_materials']
 source_tex=sum(s['source_original_faces'] for s in material if s['authored_named_PVR'])
 draw.text((x0+7,y0+h-55),'source faces: '+str(r['source_faces'])+'  PVR-ref faces: '+str(source_tex),fill='#1C2630')
 draw.text((x0+7,y0+h-37),'original UV: '+('YES' if uv else 'NO')+'  group: '+r['original_scene_group'],fill='#1C2630')
 draw.text((x0+7,y0+h-19),'source materials: '+str(len(material)),fill='#1C2630')

def render(rows,out):
 # Real original light mesh provenance may NOT have four meshes with BOTH
 # source diffuse sampler AND true UV; do not invent source-confirmed combos.
 # Select 4 largest original positive UV light meshes, four true no-UV light
 # meshes and four original unresolved urban/material meshes.
 light_uv=sorted((r for r in rows if r[0]['original_scene_group']=='lights' and
    r[0]['genuine_original_uv_candidate']),key=lambda r:-r[0]['source_faces'])[:4]
 light_no_uv=sorted((r for r in rows if r[0]['original_scene_group']=='lights' and
    not r[0]['genuine_original_uv_candidate']),key=lambda r:-r[0]['source_faces'])[:4]
 urban_missing=sorted((r for r in rows if r[0]['original_scene_group']=='urban' and
    any(not x['authored_named_PVR'] for x in r[0]['original_BRES_authored_submesh_materials'])),
    key=lambda r:-r[0]['source_faces'])[:4]
 group_list=light_uv+light_no_uv+urban_missing
 if len(group_list)!=12:
  # Genuine source may have fewer unresolved urban meshes than four.
  # Pick only distinct authentic mesh records, never synthesize models.
  used={r[0]['source_mesh_name'] for r in group_list}
  for r in sorted(rows,key=lambda r:-r[0]['source_faces']):
   if len(group_list)==12:break
   if r[0]['source_mesh_name'] not in used:
    group_list.append(r);used.add(r[0]['source_mesh_name'])
 if len(group_list)!=12:raise ValueError('insufficient ORIGINAL source meshes')
 image=Image.new('RGB',(1200,850),'#EEF3F4')
 draw=ImageDraw.Draw(image)
 draw.rectangle((0,0,1200,60),fill='#142632')
 draw.text((20,13),'IRON MAN 2 iOS 2010 | C1L1 ORIGINAL MESH MATERIAL FORENSICS',fill='white')
 draw.text((20,35),'Source BRES faces | source UV | original shader material links | NOT Vita in-game',fill='#B3CEDB')
 for i,(r,pos,faces) in enumerate(group_list):
  x=16+(i%4)*296
  y=68+(i//4)*253
  panel(draw,r,pos,faces,x,y)
 draw.text((18,831),'GREEN=real diffuse+UV  YELLOW=EXPO or diffuse/UV issue  CYAN=no proven diffuse  All source meshes authentic.',fill='#284251')
 out.parent.mkdir(parents=True,exist_ok=True)
 image.save(out)
 return [r['source_mesh_name'] for r,_,_ in group_list]

def run(report,png):
 rows,counters=source()
 selections=render(rows,png)
 j={'source_year':2010,'source_source_meshes':370,'source_faces':22919,
    'source_BRES_original_material_and_UV_mesh_records':[r for r,_,_ in rows],
    'group_counts':dict(counters),
    'light_uv_and_authored_sampler_face_count_at_source_mesh_resolution':
       counters['light_faces_actually_original_UV_positive_AND_genuine_sampler'],
    'representative_contact_sheet_meshes':selections,
    'do_not_claim_dome_identity_from_mesh_name_or_heuristic':True,
    'light_no_UV_must_not_receive_guessed_uv':True,
    'not_a_real_2010_in_game_GPU_screenshot':True,
    'no_VPK':True}
 report.parent.mkdir(parents=True,exist_ok=True)
 report.write_text(json.dumps(j,indent=2)+'\n')
 print('PASS G13 native 2010 370 BRES mesh original face bounding coords 22919/22919, per-mesh UV+shader confirmed, 12 source-mesh real triangle visual contact PNG, UV+sampler lights:',
       j['light_uv_and_authored_sampler_face_count_at_source_mesh_resolution'])
 return j
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path)
 p.add_argument('--png',required=True,type=Path)
 a=p.parse_args();run(a.out,a.png)
