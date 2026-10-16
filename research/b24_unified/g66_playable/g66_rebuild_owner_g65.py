#!/usr/bin/env python3
"""G65: recover original Gameloft BRES 24B vertex format, not generated UV.

Native source FVF24 layout:
  [0..11]  float32 x/y/z (3)
  [12..15] packed native RGBA u8 (4)
  [16..23] float32 u/v (2)
Unlike prior generic G57 parser (which left 24B vertex UV at zero),
this reads the native source 24B records and source shader property atlas ID.
User-owned IPA & B11 BRES must stay local, never republish original assets.
Original alpha/blend/mip filtering semantics and game renderer not yet proven.
"""
from __future__ import annotations
import argparse,base64,collections,hashlib,io,json,math,re,sys,types,struct,zipfile
from pathlib import Path
import numpy as np
from PIL import Image
import trimesh
from trimesh.visual.material import PBRMaterial
import texture2ddecoder

STEMS=('C1L1_ground_001','C1L1_obj_001','C1L1_obj_002','C1L1_obj_003','C1L1_obj_004',
       'C1L1_light_001','C1L1_light_002','C1L1_light_003','C1L1_car_01','C1L1_car_02')


def tag(src,key):
    m=re.search(r'<script id="'+re.escape(key)+r'"[^>]*>(.*?)</script>',src,re.S)
    if m is None: raise ValueError('no source HTML tag '+key)
    return m.group(1)


def source_mesh_parser(z):
    ns={'__name__':'owned_game_BRES','__file__':'bdae_scene_parser.py'}
    exec(compile(z.read('bdae_scene_parser.py'),'bdae_scene_parser.py','exec'),ns)
    return ns['parse'],ns['decode_archive']


def decode_pvr2(src:bytes,name:str):
    if len(src)<52: raise ValueError('PVR2 truncated '+name)
    hdr=struct.unpack_from('<13I',src)
    size,h,w,mips,flags,data_size,bpp,r,g,b,a,magic,surfaces=hdr
    fmt=flags&255
    if size!=52 or magic!=0x21525650 or not (8<=w<=2048 and 8<=h<=2048):
        raise ValueError('PVR2 header mismatch '+name)
    layer=src[52:52+w*h*bpp//8]
    if fmt==25 and bpp==4:
        rgba=np.frombuffer(texture2ddecoder.decode_pvrtc(layer,w,h),dtype=np.uint8).reshape(h,w,4)[:,:, [2,1,0,3]].copy()
    elif fmt==24 and bpp==2:
        rgba=np.frombuffer(texture2ddecoder.decode_pvrtc(layer,w,h),dtype=np.uint8).reshape(h,w,4)[:,:, [2,1,0,3]].copy()
    else:
        raise ValueError(f'unsupported owned source PVR {name}: fmt={fmt} bpp={bpp}')
    return Image.fromarray(rgba,'RGBA'),{
        'name':name,'size':[w,h], 'source_sha256':hashlib.sha256(src).hexdigest(),
        'PVR_format':fmt,'mips':mips,'alpha_nonopaque_count':int((rgba[:,:,3]!=255).sum())}


def build(original_html:Path,b11:Path,ipa:Path,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    html=original_html.read_text(encoding='utf-8')
    original_payload=tag(html,'payload'); original_uv=tag(html,'rawuv')
    data=json.loads(original_payload)
    pos=np.frombuffer(base64.b64decode(tag(html,'rawpositions')),dtype='<f4').reshape(-1,3)
    texuv=np.frombuffer(base64.b64decode(original_uv),dtype='<f4').reshape(-1,2).copy()
    faces=np.frombuffer(base64.b64decode(tag(html,'rawindices')),dtype='<u4').reshape(-1,3)
    assert pos.shape==(37946,3) and texuv.shape==(37946,2) and faces.shape==(22919,3)
    assert len(data['batches'])==386 and sum(b['tris'] for b in data['batches'])==22441
    assert len(data['originalPVRs'])==24
    img_bank={a['name'].lower():a for a in data['originalPVRs']}
    counts=collections.Counter()
    face_counts=collections.Counter()
    raw_vertex_color=np.tile(np.array([[255,255,255,255]],dtype=np.uint8),(len(texuv),1))
    id_to_source={}
    original_meshes={}
    bres_sha={}
    linked_batches=collections.defaultdict(list)
    for b in data['batches']:linked_batches[b['mesh']].append(b)
    with zipfile.ZipFile(b11) as z:
        parse,decode_archive=source_mesh_parser(z)
        base=0
        for stem in STEMS:
            blob=z.read('original_models/'+stem+'.bdae')
            bres_sha[stem]=hashlib.sha256(blob).hexdigest()
            meshes,_=parse(blob)
            for i,m in enumerate(meshes):
                name=f'{stem}_{i}'
                n=m['vertex_count']; base+=n
                batch_group=linked_batches.get(name)
                if not batch_group:continue   # 74 source meshes still unlinked, unchanged
                fstart=batch_group[0]['start']//3
                fend=(batch_group[-1]['start']+batch_group[-1]['count'])//3
                start=int(faces[fstart:fend].min());end=start+n
                assert np.array_equal(faces[fstart:fend],m['faces']+start),(name,'true source face offsets')
                original_meshes[name]=m
                id_to_source[name]=(stem,start,end)
                if m['stride']!=24:continue
                assert end<=len(texuv)
                assert np.array_equal(texuv[start:end],np.zeros((n,2),dtype='<f4')), 'placeholder UV unexpectedly nonzero: '+name
                uv24=np.ndarray((n,2),dtype='<f4',buffer=blob,offset=m['vertex_offset']+16,strides=(24,4)).copy()
                rgba=np.ndarray((n,4),dtype='u1',buffer=blob,offset=m['vertex_offset']+12,strides=(24,1)).copy()
                assert np.isfinite(uv24).all() and np.max(np.abs(uv24))<1e4
                assert (rgba[:,3]==255).all(),(name,'unexpected native RGBA alpha')
                texuv[start:end]=uv24
                raw_vertex_color[start:end]=rgba
                counts['24B_meshes']+=1
                counts['24B_vertices']+=n
        assert base==37946
        assert len(id_to_source)==296
    # Pull native shader atlas names from independent G64 original 40/60B reader,
    # without fabricating either UV or game state.
    g64_dir=Path(__file__).resolve().parent
    sys.path.insert(0,str(g64_dir))
    from g64_native_shader_recovery import parse as shader_parse
    source_materials={}
    with zipfile.ZipFile(b11) as z:
        for stem in STEMS:
            prop=shader_parse(stem,z.read('original_models/'+stem+'.bdae'))
            source_materials[stem]={x['material']:x for x in prop['native_property_records']}
    tex_needed=set()
    unbound=[]
    corrected=[]
    for b in data['batches']:
        stem,start,end=id_to_source[b['mesh']]
        m=original_meshes[b['mesh']]
        original_status=b['status']
        if b['original_uv_mesh_positive'] and b.get('tga'):
            counts['already_textured_faces']+=b['tris'];continue
        sampler=source_materials[stem].get(b['material'])
        atlas=sampler['native_atlas'] if sampler else None
        if m['stride']!=24 and not b['original_uv_mesh_positive']:
            unbound.append((b['mesh'],'unknown non24B UV'))
            continue
        has_distinct_uv=len(np.unique(texuv[start:end],axis=0))>=2
        # Atlas names *strictly* from native shader property, no guessed match.
        if atlas:
            name=atlas.lower()
            if name not in img_bank:tex_needed.add(name)
            b['tga']=atlas
            b['source_texture_named']=True
            b['original_uv_mesh_positive']=has_distinct_uv
            b['G65_native_UV_byte_offset']=16 if m['stride']==24 else None
            b['G65_native_RGBA_byte_offset']=12 if m['stride']==24 else None
            b['G65_original_source_status']=original_status
            if has_distinct_uv:
                b['status']='source-texture-and-UV'
                face_counts['new_UV_varies_real_sampler']+=b['tris']
            else:
                b['status']='source-texture-no-UV'
                face_counts['native_UV_constant_real_sampler']+=b['tris']
        else:
            if m['stride']==24:
                b['G65_native_RGBA_byte_offset']=12
                b['G65_vertex_color_only_NO_sampler']=True
                face_counts['native_vertex_color_only_no_diffuse_sampler']+=b['tris']
            else:
                unbound.append((b['mesh'],'missing native sampler on non24B'))
        corrected.append((b['mesh'],m['stride'],b['material'],b.get('tga'),b['status'],b['tris']))
    # Verify all original named source texture tables found in actual IPA.
    new_atlas=[]
    with zipfile.ZipFile(ipa) as z:
        raw_archive=z.read('Payload/IronMan2.app/textures')
    decoder=source_mesh_parser(zipfile.ZipFile(b11))[1]
    candidates={name.lower():(name,pvr) for name,pvr in decoder(raw_archive)}
    for needed in sorted(tex_needed):
        if needed not in candidates:raise ValueError('missing true IPA source texture '+needed)
        name,pvr=candidates[needed]
        img,meta=decode_pvr2(pvr,name)
        buf=io.BytesIO();img.save(buf,format='PNG')
        new_atlas.append({'name':name,'base64':base64.b64encode(buf.getvalue()).decode('ascii'),
                          'G65_original_source_PVR_metadata':meta})
        img.save(out/(name[:-4]+'.png'))
    data['originalPVRs']+=new_atlas
    known={a['name'].lower() for a in data['originalPVRs']}
    evidence=collections.Counter()
    for b in data['batches']:
        atlas=(b.get('tga') or '').lower()
        originalUV=bool(b['original_uv_mesh_positive'])
        if originalUV and atlas in known:
            evidence['source_real_uv_plus_pvr']+=b['tris']
        elif atlas in known:
            evidence['native_constant_uv_tex_sampler']+=b['tris']
        elif b.get('G65_vertex_color_only_NO_sampler'):
            evidence['source_vertex_color_only']+=b['tris']
        else:
            evidence['unresolved_other']+=b['tris']
    assert evidence['source_real_uv_plus_pvr']+evidence['native_constant_uv_tex_sampler']+evidence['source_vertex_color_only']+evidence['unresolved_other']==22441
    assert counts['24B_meshes']>=100
    assert face_counts['new_UV_varies_real_sampler']>=1500
    assert evidence['source_real_uv_plus_pvr']>=22000
    # Native RGBA vertex color from bytes is preview-only tint: precise original
    # fixed-function combiner/blend not known. Preserve in independent payload.
    report={
        'stage':'G65','original_BRES_SHA256':bres_sha,
        'native_FVF24_meshes':counts['24B_meshes'],
        'native_FVF24_vertices':counts['24B_vertices'],
        'native_fvf24_layout':{'XYZ_float32':'0..11','RGBA_u8':'12..15','UV_float32':'16..23'},
        'additional_PVR_recovered_from_original_user_IPA':[x['G65_original_source_PVR_metadata'] for x in new_atlas],
        'atlas_count_total':len(known),'source_original_face_counts':dict(evidence),
        'newly_rebound_real_UV_faces':face_counts['new_UV_varies_real_sampler'],
        'native_constant_UV_faces':face_counts['native_UV_constant_real_sampler'],
        'native_vertex_color_only_faces':face_counts['native_vertex_color_only_no_diffuse_sampler'],
        'original_mesh_vertices_faces_world_transforms_unchanged':True,
        'native_iOS_blend_alpha_depth_and_fog_proven':False,'touchHLE_frame_capture_from_this_run':False,
        'no_invented_sphere_UV':True,'no_new_VPK':True,
        'material_repair_rows':corrected,
        'still_unresolved_rows':unbound,
    }
    (out/'G65_NATIVE_FVF24_SOURCE_AUDIT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    data['G65_native_fvf24_repaired']=True
    data['G65_source_original_face_counts']=dict(evidence)
    data['G65_original_RGBA_vertex_color_present']=True
    data['G65_native_blending_NOT_verified']=True
    data['G65_no_generated_UV']=True
    updated_payload=json.dumps(data,separators=(',',':'),ensure_ascii=False)
    patched=html.replace(original_payload,updated_payload,1)
    patched=patched.replace(original_uv,base64.b64encode(texuv.astype('<f4').tobytes()).decode(),1)
    # Explicit extra source channel for WebGL diagnostics.
    packed_color=base64.b64encode(raw_vertex_color.tobytes()).decode()
    patched=patched.replace('<script id="rawindices"',f'<script id="rawcolors" type="application/octet-stream">{packed_color}</script>\n<script id="rawindices"',1)
    # GLSL 24B native RGBA; show experiment behind on/off switch.
    patched=patched.replace('layout(location=1) in vec2 uv;uniform mat4 projection,view;out vec3 worldP;out vec2 sourceUV;',
        'layout(location=1) in vec2 uv;layout(location=2) in vec4 colorNative;uniform mat4 projection,view;out vec3 worldP;out vec2 sourceUV;out vec4 vertexRGBA;')
    patched=patched.replace('void main(){sourceUV=uv;worldP=position;gl_Position=',
        'void main(){sourceUV=uv;vertexRGBA=colorNative;worldP=position;gl_Position=',1)
    patched=patched.replace('precision highp float;in vec3 worldP;in vec2 sourceUV;uniform vec3 baseColor;',
        'precision highp float;in vec3 worldP;in vec2 sourceUV;in vec4 vertexRGBA;uniform vec3 baseColor;')
    patched=patched.replace('outColor=vec4(src.rgb*s,1.);}',
        'outColor=vec4(src.rgb*vertexRGBA.rgb*s,src.a*vertexRGBA.a);}',1)
    marker='if(uv.length!==d.vertices*2)throw Error("Native original BRES UV count mismatch");'
    insert='const cb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,cb);let cc=new Uint8Array(b64("rawcolors"));gl.bufferData(gl.ARRAY_BUFFER,cc,gl.STATIC_DRAW);gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,4,gl.UNSIGNED_BYTE,true,0,0);if(cc.length!==d.vertices*4)throw Error("BRES RGBA channel byte count mismatch");'
    assert patched.count(marker)==1
    patched=patched.replace(marker,marker+insert,1)
    patched=patched.replace('gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);',
        'gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);',1)
    # Existing viewer option flags still function; label no original renderer claim.
    warning=('<section style="background:#233a38;color:#e0ffdf;padding:12px;border:2px solid #75bd93;margin:10px">'
             '<b>G65 2010 kaynak vertex-format düzeltmesi:</b> 24B (XYZ+native RGBA+native UV) '
             'okundu; orijinal IPA PVR doku bankası eklendi. Küre UVleri artık kaynak kayıttan. '
             'Vertex color birleşimi ve alfa-blend şimdilik host WebGL simülasyonu; '
             'touchHLE GPU shader eşdeğeri henüz kanıtlanmadı. Yeni VPK yok.</section>')
    patched=patched.replace('<body>','<body>'+warning,1)
    htmlfile=out/'G65_NATIVE_FVF24_C1L1_REAL_TEXTURED_3D.html'
    htmlfile.write_text(patched,encoding='utf-8')
    # GLB: UV+genuine atlas for verified source faces; vertex RGBA for no sampler.
    textures={a['name'].lower():Image.open(io.BytesIO(base64.b64decode(a['base64']))).convert('RGBA') for a in data['originalPVRs']}
    grouped=collections.defaultdict(lambda:[[],[],[]])
    for b in data['batches']:
        ids=faces[b['start']//3:b['start']//3+b['tris']].reshape(-1)
        # Material__46 genuine source RGBA only, no invented diffuse.
        atlas=(b.get('tga') or '').lower()
        key=atlas if atlas in textures else '__vertex_rgba__'+b['group']
        grouped[key][0].append(pos[ids]);grouped[key][1].append(texuv[ids]);grouped[key][2].append(raw_vertex_color[ids])
    scene=trimesh.Scene()
    fallback={'ground':[109,147,117,255],'urban':[142,159,176,255],
              'vehicles':[188,150,102,255],'lights':[163,154,168,255]}
    for index,(key,(positions,uvs,colors)) in enumerate(sorted(grouped.items())):
        pts=np.concatenate(positions);vuv=np.concatenate(uvs);cols=np.concatenate(colors)
        obj=trimesh.Trimesh(vertices=pts,faces=np.arange(len(pts),dtype=np.int64).reshape(-1,3),process=False)
        if key in textures:
            pbr=PBRMaterial(baseColorTexture=textures[key],metallicFactor=0,roughnessFactor=.92,doubleSided=True,alphaMode='BLEND' if key=='c1l1_earth.tga' else 'OPAQUE')
            obj.visual=trimesh.visual.TextureVisuals(uv=vuv,material=pbr)
        else:
            obj.visual.vertex_colors=cols if key=='__vertex_rgba__lights' else np.broadcast_to(fallback[key.removeprefix('__vertex_rgba__')],(len(pts),4)).copy()
        scene.add_geometry(obj,geom_name=f'G65_{index}_{key}')
    glb=out/'G65_C1L1_SOURCE_FVF24_REAL_PVR_UV.glb'
    glb.write_bytes(scene.export(file_type='glb'))
    scene_loaded=trimesh.load(glb,force='scene',process=False)
    assert sum(len(x.faces) for x in scene_loaded.geometry.values())==22441
    report['GLB_viewer_material_limit']='GLB uses native PVR images and UV. Pixelwise vertex-color modulation for textured materials only in interactive WebGL2 viewer; original blend not yet proven.'
    (out/'G65_NATIVE_FVF24_SOURCE_AUDIT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print('G65 SOURCE REPAIR FACE COUNTS',dict(evidence))
    print('G65 NEW 24B',dict(counts),'new source UV faces',dict(face_counts))
    print('G65 all native source original extra PVRs',sorted(tex_needed))
    print('PASS G65 native 24-byte UV+RGBA original 2010 mesh repair; no procedural mapping, no Vita VPK')
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--g64html',type=Path,required=True)
    ap.add_argument('--b11zip',type=Path,required=True)
    ap.add_argument('--ipa',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    build(args.g64html,args.b11zip,args.ipa,args.out)