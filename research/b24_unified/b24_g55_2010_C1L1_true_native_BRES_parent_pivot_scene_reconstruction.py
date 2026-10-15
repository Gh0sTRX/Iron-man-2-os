#!/usr/bin/env python3
"""G55 authoritative source-only reconstruction of Iron Man 2 (2010) C1L1
BRES v0.0.0.133 real node->pivot/mesh native TRS chains.

Native 2010 node record layout, proven by original offsets and links:
  +00 u32 first name reference (length-prefixed original ASCII)
  +04 u32 second name reference
  +08 u32 third name reference
  +12 XYZ float32[3]
  +24 quaternion xyzw float32[4]
  +40 scale float32[3]
  +52 direct child count u32
  +56 first child record pointer u32
The earlier G51 test interpreted +56 as count and +60 as child;
this was off by one dword and missed hundreds of real source links.

We require SAME-STEM exact source '-node' -> '-node_PIVOT' pointer
before composing local TRS. Nonmatched meshes remain unchanged/unplaced.
Full runtime root/world matrix, shader, visibility are NOT proven.
Never build a Vita VPK or claim live original engine output.
"""
from __future__ import annotations
import argparse
import collections
import contextlib
import hashlib
import io
import json
import math
import re
import struct
import zipfile
from pathlib import Path
import numpy as np

SOURCES = ['C1L1_ground_001','C1L1_obj_001','C1L1_obj_002',
           'C1L1_obj_003','C1L1_obj_004','C1L1_light_001',
           'C1L1_light_002','C1L1_light_003','C1L1_car_01','C1L1_car_02']


def original_string(raw:bytes,ptr:int):
    if ptr<4 or ptr>=len(raw): return None
    n=struct.unpack_from('<I',raw,ptr-4)[0]
    if n<3 or n>115 or ptr+n>len(raw): return None
    b=raw[ptr:ptr+n]
    if not all(32<=c<=126 for c in b):return None
    s=b.decode('ascii')
    if not re.fullmatch(r'[A-Za-z0-9_.:/\-\[\] ]{3,115}',s):return None
    return s


def parse_node(raw:bytes,off:int):
    if off<0 or off%4 or off+60>len(raw):return None
    ptr=struct.unpack_from('<III',raw,off)
    names=[original_string(raw,p) for p in ptr]
    # Presence in the FIRST reference prevents 4-byte shifted alias records.
    if not names[0] or '-node' not in names[0]:return None
    vec=struct.unpack_from('<10f',raw,off+12)
    if not all(math.isfinite(x) for x in vec):return None
    if max(abs(x) for x in vec[:3])>5000:return None
    if abs(sum(x*x for x in vec[3:7])-1)>0.012:return None
    if any(abs(x)<.0001 or abs(x)>100 for x in vec[7:10]):return None
    cc,child=struct.unpack_from('<II',raw,off+52)
    if cc>300 or (cc and (child%4 or child>=len(raw))):return None
    return {'offset':off,'name':names[0],'names':names,
            'xyz':[float(x) for x in vec[:3]],
            'qxyzw':[float(x) for x in vec[3:7]],
            'scale':[float(x) for x in vec[7:10]],
            'native_child_count':cc,'native_child_ptr':child}


def find_native_nodes(raw:bytes):
    words=np.frombuffer(raw[:len(raw)//4*4],dtype='<u4')
    records={}
    for mo in re.finditer(rb'[A-Za-z0-9_]+(?:-node(?:_PIVOT)?|_PIVOT)',raw):
        loc=mo.start()
        if loc<4:continue
        for hit in np.flatnonzero((words==loc)|(words==loc+4)):
            for slot in (0,1,2):
                off=int(hit)*4-slot*4
                if off<0 or off in records:continue
                r=parse_node(raw,off)
                if r:records[off]=r
    return records


def rotation_matrix(qxyzw):
    x,y,z,w=np.asarray(qxyzw,dtype=float)
    l=math.sqrt(x*x+y*y+z*z+w*w)
    if l<1e-8:raise ValueError('zero quaternion')
    x,y,z,w=x/l,y/l,z/l,w/l
    return np.asarray([
        [1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
        [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
        [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)],
    ],dtype=np.float64)


def apply_trs(points:np.ndarray,node:dict):
    v=np.asarray(points,dtype=np.float64)
    s=np.asarray(node['scale'],dtype=np.float64)
    t=np.asarray(node['xyz'],dtype=np.float64)
    r=rotation_matrix(node['qxyzw'])
    return (v*s)@r.T+t


def _short_floats(xs):return [round(float(x),6) for x in xs]


def reconstruct(source_zip:Path,output_json:Path,output_glb:Path|None=None,output_png:Path|None=None):
    summary=collections.Counter()
    report=[]
    preview=[]
    scene=None
    if output_glb:
        import trimesh
        scene=trimesh.Scene()
    with zipfile.ZipFile(source_zip) as z:
        env={'__name__':'bdae_owned_source_geometry','__file__':'bdae_scene_parser.py'}
        exec(compile(z.read('bdae_scene_parser.py'),'bdae_scene_parser.py','exec'),env)
        for stem in SOURCES:
            raw=z.read('original_models/'+stem+'.bdae')
            nodes=find_native_nodes(raw)
            names=collections.defaultdict(list)
            for rec in nodes.values():names[rec['name']].append(rec)
            with contextlib.redirect_stdout(io.StringIO()):
                meshes,_=env['parse'](raw)
            rows=[]
            for m in meshes:
                mesh_name=m['name'];base=mesh_name.removesuffix('-mesh')
                p=names.get(base+'-node',[])
                q=names.get(base+'-node_PIVOT',[])
                candidate=[(parent,pivot) for parent in p for pivot in q
                           if parent['native_child_count']>=1 and
                              parent['native_child_ptr']==pivot['offset']]
                row={'mesh':mesh_name,'source_vertices':int(m['vertex_count']),
                     'source_triangles':len(m['faces']),
                     'native_same_name_parent_records':[x['offset'] for x in p],
                     'native_same_name_pivot_records':[x['offset'] for x in q],
                     'native_exact_same_name_parent_pivot_edges':len(candidate)}
                summary['source_meshes']+=1
                summary['source_triangles']+=len(m['faces'])
                if len(candidate)==1:
                    parent,pivot=candidate[0]
                    v=np.asarray(m['positions'],dtype=np.float64)
                    transformed=apply_trs(apply_trs(v,pivot),parent)
                    assert np.isfinite(transformed).all()
                    raw_bb=np.r_[v.min(axis=0),v.max(axis=0)]
                    world_bb=np.r_[transformed.min(axis=0),transformed.max(axis=0)]
                    row.update({
                        'corrected_source_native_link':True,
                        'native_parent_offset':parent['offset'],
                        'native_pivot_offset':pivot['offset'],
                        'native_parent_xyz':_short_floats(parent['xyz']),
                        'native_pivot_xyz':_short_floats(pivot['xyz']),
                        'original_raw_mesh_bounds':_short_floats(raw_bb),
                        'source_node_chain_bounds':_short_floats(world_bb),
                        'source_node_chain_centroid_of_bbox':_short_floats((world_bb[:3]+world_bb[3:])/2),
                        'native_parent_xyzw':_short_floats(parent['qxyzw']),
                        'native_pivot_xyzw':_short_floats(pivot['qxyzw']),
                        'native_parent_scale':_short_floats(parent['scale']),
                        'native_pivot_scale':_short_floats(pivot['scale']),
                    })
                    summary['exact_linked_meshes']+=1
                    summary['exact_linked_triangles']+=len(m['faces'])
                    summary['exact_linked_vertices']+=len(v)
                    preview.append((stem,mesh_name,transformed,np.asarray(m['faces'],dtype=np.int64)))
                    if scene is not None:
                        tr=trimesh.Trimesh(vertices=transformed,
                                           faces=np.asarray(m['faces'],dtype=np.int64),
                                           process=False)
                        c=([110,145,170,255] if 'obj' in stem
                           else [120,155,128,255] if 'ground' in stem
                           else [187,143,87,255] if 'car' in stem
                           else [168,147,177,255])
                        tr.visual.face_colors=c
                        scene.add_geometry(tr,geom_name=stem+'__'+mesh_name)
                else:
                    row['corrected_source_native_link']=False
                    summary['unresolved_meshes']+=1
                rows.append(row)
            summary['native_source_nodes']+=len(nodes)
            print('G55',stem,'source_meshes',len(meshes),'valid_named_nodes',len(nodes),
                  'mesh exact parent-pivot',sum(x['corrected_source_native_link'] for x in rows))
            report.append({'source_BRES':stem,'source_sha256':hashlib.sha256(raw).hexdigest(),
                           'mesh_count':len(meshes),'validated_correct_native_TRS_nodes':len(nodes),
                           'exact_parent_pivot_mesh_links':sum(x['corrected_source_native_link'] for x in rows),
                           'meshes':rows})
    assert summary['source_meshes']==370,summary
    assert summary['exact_linked_meshes']==296,summary
    assert summary['native_source_nodes']>=670,summary
    assert sum(x['exact_parent_pivot_mesh_links'] for x in report if 'ground' in x['source_BRES'])==16
    assert sum(x['exact_parent_pivot_mesh_links'] for x in report if '_obj_' in x['source_BRES'])==121
    assert sum(x['exact_parent_pivot_mesh_links'] for x in report if '_car_' in x['source_BRES'])==22
    final={'stage':'G55_source_only','exact_native_node_record_format':{
               'name_pointers':0,'XYZ':12,'quaternion_xyzw':24,'scale':40,
               'child_count':52,'first_child_record_pointer':56,
               'overrides_G51_incorrect_child_offsets':[56,60]},
           'totals':dict(summary),'sources':report,
           'original_source_3d_rigged_parent_pivot_mesh_trs_recomposed':True,
           'source_geom_world_candidate_not_runtime_verified':True,
           'gameplay_visibility_shader_blend_and_scene_root_unresolved':True,
           'NO_VPK_AND_NO_NATIVE_DEVICE_TEST':True}
    output_json.parent.mkdir(parents=True,exist_ok=True)
    output_json.write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n')
    if scene is not None:
        output_glb.parent.mkdir(parents=True,exist_ok=True)
        scene.export(str(output_glb),file_type='glb')
    if output_png:
        source_scene_preview(preview,output_png)
    print('PASS G55',json.dumps(dict(summary),sort_keys=True))
    return final


def source_scene_preview(preview,output_png:Path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig,ax=plt.subplots(figsize=(15,11),dpi=125)
    ax.set_facecolor('#151c25');fig.patch.set_facecolor('#111820')
    cols={'ground':'#71967b','obj':'#7f9ab1','car':'#d6a05f','light':'#b59fb9'}
    tri_list=[];colors=[]
    for stem,name,vertices,faces in preview:
        kind='ground' if 'ground' in stem else 'car' if 'car' in stem else 'light' if 'light' in stem else 'obj'
        if len(faces)==0:continue
        polys=vertices[faces][:,:,:2]
        tri_list.extend(polys)
        colors.extend([cols[kind]]*len(polys))
    coll=PolyCollection(tri_list,facecolors=colors,edgecolors='none',alpha=.78,rasterized=True)
    ax.add_collection(coll)
    vertices=np.vstack([v for _,_,v,_ in preview]);xmin,ymin=vertices[:,:2].min(axis=0);xmax,ymax=vertices[:,:2].max(axis=0)
    dx=xmax-xmin;dy=ymax-ymin
    ax.set_xlim(xmin-.04*dx,xmax+.04*dx);ax.set_ylim(ymin-.04*dy,ymax+.04*dy);ax.set_aspect('equal')
    ax.grid(alpha=.15,color='white',linewidth=.5);ax.tick_params(colors='white')
    for spine in ax.spines.values():spine.set_color('#425466')
    ax.set_title('Iron Man 2 (2010) | C1L1 | G55 Native BRES Parent + Pivot Source Chain',color='white',fontsize=15,pad=20)
    ax.set_xlabel('Native source X',color='white');ax.set_ylabel('Native source Y',color='white')
    ax.text(.02,.02,'296/370 source meshes linked. Not original iOS runtime camera, visibility or PVR materials.\nGround 16 | Urban 121 | Vehicles 22 | Special lights 137',transform=ax.transAxes,color='white',fontsize=9,va='bottom')
    output_png.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(output_png,facecolor=fig.get_facecolor(),bbox_inches='tight')
    plt.close(fig)


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--zip',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--glb',type=Path)
    ap.add_argument('--png',type=Path)
    a=ap.parse_args()
    reconstruct(a.zip,a.out,a.glb,a.png)