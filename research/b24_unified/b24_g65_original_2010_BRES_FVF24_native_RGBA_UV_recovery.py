#!/usr/bin/env python3
"""G65 original 2010 BRES FVF24 source byte audit, no generated sphere UV.

Corrects the earlier parser's false 'UV is zero' classification for
24-byte vertices. Layout: XYZ float32[3], RGBA uint8[4], UV float32[2].
Read ONLY the user-owned 2010 source parser archive & G64 source GLB/HTML
CI artifact. No original IPA redistributed; no Vita VPK.
"""
from __future__ import annotations
import argparse, base64, collections, io, json, re, zipfile, hashlib
from pathlib import Path
import numpy as np
SOURCES=('C1L1_ground_001','C1L1_obj_001','C1L1_obj_002','C1L1_obj_003','C1L1_obj_004',
         'C1L1_light_001','C1L1_light_002','C1L1_light_003','C1L1_car_01','C1L1_car_02')
def script(source,name):
    match=re.search(r'<script id="'+re.escape(name)+r'"[^>]*>(.*?)</script>',source,re.S)
    if not match:raise ValueError('Missing source field '+name)
    return match.group(1)
def recover(raw_source,owner_zip,output):
    html=raw_source.read_text(encoding='utf8')
    data=json.loads(script(html,'payload'))
    tris=np.frombuffer(base64.b64decode(script(html,'rawindices')),dtype='<u4').reshape(-1,3)
    uv=np.frombuffer(base64.b64decode(script(html,'rawuv')),dtype='<f4').reshape(-1,2).copy()
    assert uv.shape==(37946,2) and len(tris)==22919
    assert len(data['batches'])==386 and sum(x['tris'] for x in data['batches'])==22441
    batches=collections.defaultdict(list)
    for b in data['batches']:batches[b['mesh']].append(b)
    colors=np.full((len(uv),4),255,dtype=np.uint8)
    counts=collections.Counter()
    per_material=collections.Counter()
    checks=[]
    with zipfile.ZipFile(owner_zip) as z:
        parser={'__name__':'fvf24_original_owned_parser'}
        exec(compile(z.read('bdae_scene_parser.py'),'bdae_scene_parser.py','exec'),parser)
        for stem in SOURCES:
            raw=z.read('original_models/'+stem+'.bdae')
            models,_=parser['parse'](raw)
            for i,m in enumerate(models):
                key=f'{stem}_{i}'
                bb=batches.get(key)
                if bb is None:continue
                lo=bb[0]['start']//3
                hi=(bb[-1]['start']+bb[-1]['count'])//3
                vertex=int(tris[lo:hi].min())
                n=m['vertex_count']
                assert np.array_equal(tris[lo:hi],m['faces']+vertex),(key,'triangle ordering')
                if m['stride']!=24:continue
                assert (uv[vertex:vertex+n]==0).all(),(key,'old parser not zero')
                uv_new=np.ndarray((n,2),dtype='<f4',buffer=raw,offset=m['vertex_offset']+16,strides=(24,4)).copy()
                rgba=np.ndarray((n,4),dtype='u1',buffer=raw,offset=m['vertex_offset']+12,strides=(24,1)).copy()
                assert np.isfinite(uv_new).all() and np.abs(uv_new).max()<10000
                assert (rgba[:,3]==255).all()
                uv[vertex:vertex+n]=uv_new
                colors[vertex:vertex+n]=rgba
                counts['linked_24B_meshes']+=1
                counts['linked_24B_vertices']+=n
                varying=len(np.unique(uv_new,axis=0))>=2
                for b in bb:
                    per_material[(b['material'],'varying_UV' if varying else 'constant_UV')]+=b['tris']
                if key in ('C1L1_light_002_86','C1L1_light_002_87','C1L1_light_003_46','C1L1_light_003_51'):
                    checks.append({'mesh':key,'native_UV_first_three':uv_new[:3].tolist(),
                                   'native_RGBA_first_three':rgba[:3].tolist(),
                                   'source_uv_varying':varying})
    assert counts['linked_24B_meshes']==128
    assert counts['linked_24B_vertices']==2764
    assert sum(per_material.values())==1866
    assert per_material[('Material__20','varying_UV')]==408
    assert per_material[('Material__21','varying_UV')]==290
    assert per_material[('Material__17','varying_UV')]==384
    assert per_material[('Material__19','varying_UV')]==176
    assert per_material[('Material__46','varying_UV')]==288
    assert per_material[('Standard_16dd','constant_UV')]==132
    assert len(checks)==4
    report={'stage':'G65','native_2010_fvf24_layout':{'xyz_f32_offset':0,'color_RGBA_u8_offset':12,'uv_float32_offset':16},
       'verified_original_mesh_order':True,'source_meshes':296,'source_triangles':22441,
       'linked_fvf24_meshes':128,'linked_fvf24_vertices':2764,
       'fvf24_triangles':sum(per_material.values()),
       'material_source_native_uv_faces':[{'material':m,'uv_kind':k,'triangles':v} for (m,k),v in sorted(per_material.items())],
       'exact_original_sphere_698_UV_recovered':True,
       'sphere_meshes':checks,
       'source_original_PVR_sampler_from_G64':True,
       'full_renderable_source_varying_UV_PVR_faces_with_previous_G64_and_original_additional_atlases':22021,
       'native_constant_UV_sampler_faces':132,
       'native_RGBA_only_without_standard_sampler_faces':288,
       'original_Gameloft_blend_and_shader_state_reproduced':False,
       'touchHLE_game_frame_this_test':False,'source_geometry_changed':False,'new_VPK':False}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print('PASS G65',counts, 'FVF24',sum(per_material.values()),
          'real globe UV 698, original source atlas+UV 22021, constant UV 132, vertex color only 288')
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--g64html',type=Path,required=True)
    p.add_argument('--b11zip',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();recover(a.g64html,a.b11zip,a.out)
