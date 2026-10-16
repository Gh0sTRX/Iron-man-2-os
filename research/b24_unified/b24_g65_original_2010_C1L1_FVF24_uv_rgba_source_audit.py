#!/usr/bin/env python3
"""G65 reproducible CI audit: native 2010 BRES 24-byte vertex UV + RGBA.

Independent of copyrighted IPA pixel bytes. Reads owner B11 original BRES
source and the pre-existing G64 source GLB viewer artifact, checks original
face offsets, and categorizes every visible original triangle. Source PVR
decode and re-render are a separate LOCAL-only task, requiring owner IPA.
No generated UV, no Vita/VPK, no false touchHLE GPU emulation claim.
"""
from __future__ import annotations
import argparse, base64, collections, json, re, struct, zipfile
from pathlib import Path
import numpy as np
from b24_g64_source_original_C1L1_BRES_40_60_shader_sampler_recovery import decode as native_materials, STEMS

def tag(html, name):
    hit = re.search(r'<script id="' + re.escape(name) + r'"[^>]*>(.*?)</script>', html, re.S)
    if hit is None: raise ValueError('Missing G64 source HTML tag: ' + name)
    return hit.group(1)

def audit(b11zip, g64html, output):
    html = g64html.read_text(encoding='utf8')
    data = json.loads(tag(html, 'payload'))
    uv0 = np.frombuffer(base64.b64decode(tag(html,'rawuv')),dtype='<f4').reshape(-1,2).copy()
    pos = np.frombuffer(base64.b64decode(tag(html,'rawpositions')),dtype='<f4').reshape(-1,3)
    faces = np.frombuffer(base64.b64decode(tag(html,'rawindices')),dtype='<u4').reshape(-1,3)
    assert pos.shape == (37946,3) and uv0.shape == (37946,2) and faces.shape == (22919,3)
    assert len(data['batches']) == 386 and sum(b['tris'] for b in data['batches']) == 22441
    assert len(data['originalPVRs']) == 24
    present_atlases = {x['name'].casefold() for x in data['originalPVRs']}
    linked = collections.defaultdict(list)
    for b in data['batches']: linked[b['mesh']].append(b)
    audit_rows = []
    expected_new_atlases=set()
    counts=collections.Counter()
    original_vertices=0
    with zipfile.ZipFile(b11zip) as src:
        namespace={'__name__':'g65_original_bdae'}
        exec(compile(src.read('bdae_scene_parser.py'),'bdae_scene_parser.py','exec'),namespace)
        mesh_parser=namespace['parse']
        for stem in STEMS:
            raw=src.read('original_models/'+stem+'.bdae')
            mat_rows=native_materials(stem,raw)
            material_map={r['material']:r['original_TGA'] for r in mat_rows}
            meshes,_=mesh_parser(raw)
            for i,mesh in enumerate(meshes):
                name=stem+'_'+str(i)
                n=mesh['vertex_count']
                original_vertices+=n
                bb=linked.get(name)
                if not bb: continue
                fmin=bb[0]['start']//3
                fmax=(bb[-1]['start']+bb[-1]['count'])//3
                assert fmax-fmin==len(mesh['faces'])
                start=int(faces[fmin:fmax].min());end=start+n
                assert np.array_equal(faces[fmin:fmax],mesh['faces']+start), name+' true triangle topology'
                if mesh['stride']==24:
                    uv=np.ndarray((n,2),dtype='<f4',buffer=raw,offset=mesh['vertex_offset']+16,strides=(24,4)).copy()
                    col=np.ndarray((n,4),dtype=np.uint8,buffer=raw,offset=mesh['vertex_offset']+12,strides=(24,1)).copy()
                    assert np.isfinite(uv).all() and np.max(np.abs(uv))<1e4
                    assert np.all(col[:,3]==255)
                    assert np.all(uv0[start:end]==0)
                    counts['FVF24_meshes']+=1;counts['FVF24_vertices']+=n
                    source_has_uv=len(np.unique(uv,axis=0))>=2
                else:
                    source_has_uv=None
                for b in bb:
                    if b['original_uv_mesh_positive'] and b.get('tga'):
                        counts['already_original_PVR_UV_faces']+=b['tris']; continue
                    if mesh['stride']!=24:
                        raise AssertionError('unresolved non-FVF24 material source '+name)
                    atlas=material_map.get(b['material'])
                    if atlas is not None:
                        if atlas.casefold() not in present_atlases: expected_new_atlases.add(atlas.casefold())
                        if source_has_uv:
                            counts['new_source_UV_PVR_faces']+=b['tris']
                            mode='source UV plus native 40/60B atlas'
                        else:
                            counts['native_constant_UV_sampler_faces']+=b['tris']
                            mode='native constant UV with source atlas'
                    else:
                        counts['native_vertex_color_only_faces']+=b['tris']
                        mode='native source RGBA no verified sampler'
                    audit_rows.append({'source_mesh':name,'source_stride':mesh['stride'],
                                       'native_original_material':b['material'],
                                       'triangles':b['tris'],'native_sampler_atlas':atlas,
                                       'mode':mode})
    assert original_vertices==37946
    assert counts['FVF24_meshes']==128 and counts['FVF24_vertices']==2764
    assert counts['already_original_PVR_UV_faces']==20457
    assert counts['new_source_UV_PVR_faces']==1564
    assert counts['native_constant_UV_sampler_faces']==132
    assert counts['native_vertex_color_only_faces']==288
    assert sum(counts[k] for k in ['already_original_PVR_UV_faces','new_source_UV_PVR_faces',
                                  'native_constant_UV_sampler_faces','native_vertex_color_only_faces'])==22441
    assert len(expected_new_atlases)==7
    report={
        'stage':'G65','owner_original_2010_BRES_nodes_crosschecked':True,
        'source_triangles':22919,'linked_source_mesh_triangles':22441,
        'linked_source_meshes':296,'unlinked_small_special_meshes':74,
        'source_vertex_stride_24_bytes':{'position_offset':0,'color_RGBA8_offset':12,'UV_f32x2_offset':16},
        'counts':dict(counts),'real_original_UV_plus_PVR_source_faces':22021,
        'additional_source_atlas_names_to_extract_from_user_IPA':sorted(expected_new_atlases),
        'original_PVR_pixels_in_CI':False,'original_iOS_blend_alpha_shader_proven':False,
        'touchHLE_original_frame_in_this_CI':False,'new_VPK':False,
        'source_material_evidence':audit_rows,
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print('PASS G65 original BRES FVF24 authentic raw UV/color source audit:',
          dict(counts),'new native atlas refs',sorted(expected_new_atlases))
    print('No source meshes moved, no generated UV, no original renderer shader claim, NO VPK.')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--b11zip',type=Path,required=True)
    p.add_argument('--g64html',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    audit(args.b11zip,args.g64html,args.out)
