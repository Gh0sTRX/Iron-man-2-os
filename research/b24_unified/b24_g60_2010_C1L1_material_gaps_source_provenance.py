#!/usr/bin/env python3
"""G60: verify original C1L1 texture gaps from authentic G57 CI artifact.

Never elevate an atlas visual candidate or fabricated planar UV to an
authentic iOS binding. This audit is source-only and does not alter meshes.
"""
import argparse
import base64
import collections
import json
import re
import struct
from pathlib import Path

def tag(html, name):
    m=re.search(r'<script id="'+re.escape(name)+r'"[^>]*>(.*?)</script>',html,re.S)
    if not m: raise ValueError('missing source HTML field '+name)
    return m.group(1)

def run(source, output):
    html=source.read_text(encoding='utf8')
    d=json.loads(tag(html,'payload'))
    uv=base64.b64decode(tag(html,'rawuv'))
    indices=base64.b64decode(tag(html,'rawindices'))
    assert len(uv)==37946*2*4 and len(indices)==22919*3*4
    assert len(d['originalPVRs'])==24
    batches=d['batches']
    assert len(batches)==386
    atlas={x['name'].lower() for x in d['originalPVRs']}
    classes=collections.Counter()
    for b in batches:classes[b['status']]+=b['tris']
    assert sum(classes.values())==22441
    assert classes['source-texture-and-UV']==18568
    assert classes['expo']==206
    expo=[b for b in batches if b['status']=='expo']
    assert len(expo)==1 and expo[0]['material']=='orig_07___Default'
    assert expo[0]['tga'].lower()=='cahp01_c_expo_building.tga'
    assert expo[0]['original_uv_mesh_positive'] and expo[0]['tga'].lower() in atlas
    building=[b for b in batches if b['material']=='c1l1_3building' and b['status']=='UV-no-source-diffuse']
    assert sum(b['tris'] for b in building)==1683
    assert all(b['original_uv_mesh_positive'] and not b['tga'] for b in building)
    poles=[b for b in batches if b['status']=='source-texture-no-UV']
    assert sum(b['tris'] for b in poles)==132
    assert all(b['material']=='Standard_16dd' and b['tga'].lower()=='c1l1_road.tga'
               for b in poles)
    # Direct native G32/G57 UV bytes and indices, not just a status label:
    count=0
    for batch in poles:
        a=batch['start']//3
        for f in range(a,a+batch['tris']):
            for k in range(3):
                vertex=struct.unpack_from('<I',indices,4*(3*f+k))[0]
                u,v=struct.unpack_from('<ff',uv,8*vertex)
                if u!=0. or v!=0.:raise ValueError('source pole native UV nonzero')
            count+=1
    assert count==132
    verified_original=classes['source-texture-and-UV']+classes['expo']
    assert verified_original==18774
    result={
        'stage':'G60',
        'input_native_meshes':296,
        'input_source_triangles':22441,
        'original_PVR_and_original_UV_verified_triangles':verified_original,
        'expo_206_faces_ALREADY_original_texture_not_missing':True,
        'c1l1_3building_faces_with_UV_but_no_proven_atlas':1683,
        'building_same_game_PVR_test_candidates':['c1l1_building.tga','c1l1_build2.tga','c1l1_building4.tga'],
        'any_building_candidate_proven_native_binding':False,
        'road_132_source_triangle_UVs_exactly_zero':True,
        'road_projection_if_used_is_non_native_experiment':True,
        'unknown_original_material_triangles':22441-verified_original,
        'source_meshes_or_indices_modified':False,
        'gameloft_original_shader_or_alpha_recovered':False,
        'source_only_no_new_VPK':True,
        'source_status':dict(classes),
    }
    assert all(x in atlas for x in result['building_same_game_PVR_test_candidates'])
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS G60: original expo actually textured; missing 1683 3building atlas unresolved;',
          '132 road native zero UV; no fake iOS asset binding')

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--g57html',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    run(a.g57html,a.out)
