#!/usr/bin/env python3
"""Build real owner-derived G65 scene + armored Mark VI + original C1L1 collision
for an intentionally separate PSVita playable hardware alpha.
No original IPA/assets in Git source. Requires user-supplied source files locally.
C1L1 source scene drawn as original-world coordinates, not center/guessed moves.
"""
import argparse,collections,hashlib,json,struct
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image

MAGIC=b'G66M'

def load_flat_scene(path):
    scene=trimesh.load(path,force='scene',process=False)
    # Dump with per-node world transforms applied. G65 scene objects are already
    # source-positioned; do not re-center or re-normalize the whole map.
    return scene.dump(concatenate=False)

def visual_image(mesh):
    if mesh.visual.kind != 'texture': return None
    mat=mesh.visual.material
    img=getattr(mat,'baseColorTexture',None)
    if img is None: img=getattr(mat,'image',None)
    return img.convert('RGBA') if img is not None else None

def pack_geometry(src,out,actor=False):
    meshes=load_flat_scene(src)
    batches=[]; verts=[]; atlases=[]; found={}
    tris=0
    for n,m in enumerate(meshes):
        assert m.faces.shape[1]==3
        image=visual_image(m)
        if image is not None:
            buf=image.tobytes();key=hashlib.sha256(image.width.to_bytes(4,'little')+image.height.to_bytes(4,'little')+buf).hexdigest()
            if key not in found:
                idx=len(atlases)
                found[key]=idx
                atlases.append({'name':f'G66_{"armor" if actor else "city"}_tex_{idx:02d}.g66t','width':image.width,'height':image.height,'pixels':buf})
            tid=found[key]
        else:tid=-1
        ids=np.array(m.faces.reshape(-1), dtype=np.int64)
        coords=np.asarray(m.vertices,dtype='<f4')[ids]
        if m.visual.kind=='texture' and len(m.visual.uv)==len(m.vertices):
            uv=np.asarray(m.visual.uv,dtype='<f4')[ids]
        else: uv=np.zeros((len(ids),2),dtype='<f4')
        if m.visual.kind=='vertex' and len(m.visual.vertex_colors)==len(m.vertices):
            color=np.asarray(m.visual.vertex_colors,dtype=np.uint8)[ids]
        else: color=np.ones((len(ids),4),dtype=np.uint8)*255
        # 24B interleaved XYZ+UV+RGBA, VitaGL compatible with GL_UNSIGNED_BYTE
        packed=np.empty((len(ids),),dtype=np.dtype([('p','<f4',(3,)),('uv','<f4',(2,)),('rgba','u1',(4,))]))
        packed['p']=coords;packed['uv']=uv;packed['rgba']=color
        start=sum(len(x) for x in verts)//24
        verts.append(packed.tobytes())
        batches.append((start,len(ids),tid,1 if 'earth' in str(getattr(getattr(m.visual,'material',None),'name','')).lower() else 0))
        tris+=len(m.faces)
    binary=MAGIC+struct.pack('<4I',1,sum(x[1] for x in batches),len(batches),len(atlases))
    binary+=b''.join(struct.pack('<4I',start,count,tid if tid>=0 else 0xffffffff,flags) for start,count,tid,flags in batches)
    binary+=b''.join(verts)
    out.mkdir(parents=True,exist_ok=True)
    target=out/('G66_armor.g66m' if actor else 'G66_city.g66m')
    target.write_bytes(binary)
    for atlas in atlases:
        (out/atlas['name']).write_bytes(b'G66T'+struct.pack('<3I',1,atlas['width'],atlas['height'])+atlas['pixels'])
    return {'file':target.name,'meshes':len(meshes),'triangles':tris,'vertices':sum(x[1] for x in batches),
            'textures':[{k:v for k,v in t.items() if k!='pixels'} for t in atlases],
            'sha256':hashlib.sha256(binary).hexdigest()}

def pack_colliders(src,out):
    meshes=load_flat_scene(src)
    tris=np.concatenate([np.asarray(m.vertices,dtype='<f4')[m.faces] for m in meshes],axis=0)
    assert len(tris)==1910 and np.isfinite(tris).all()
    bb=tris.reshape(-1,3)
    assert bb[:,0].min()<-300 and bb[:,0].max()>300
    assert bb[:,1].min()<-340 and bb[:,1].max()>250
    (out/'G66_original_collision.g66c').write_bytes(b'G66C'+struct.pack('<II',1,len(tris))+tris.astype('<f4').tobytes())
    return {'triangles':len(tris),'bounds':np.stack((bb.min(axis=0),bb.max(axis=0))).tolist(),
            'sha256':hashlib.sha256(tris.tobytes()).hexdigest()}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--g65glb',type=Path,required=True)
    ap.add_argument('--mark6glb',type=Path,required=True)
    ap.add_argument('--collisionglb',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    scene=pack_geometry(a.g65glb,a.out)
    assert scene['triangles']==22441 and scene['meshes']==32
    armor=pack_geometry(a.mark6glb,a.out,actor=True)
    assert armor['triangles']==970
    collision=pack_colliders(a.collisionglb,a.out)
    manifest={'stage':'G66','scene':scene,'mark6':armor,'colliders':collision,
              'true_original_skin_animation_loaded':False,
              'source_render_scene_world_coordinates_unchanged':True,
              'collision_mesh_coordinates_unchanged':True,
              'device_fps_measured':False,'device_tested':False}
    (a.out/'G66_manifest.json').write_text(json.dumps(manifest,indent=2))
    print('SOURCE PACK',json.dumps(manifest,default=str)[:2000])
if __name__=='__main__':main()