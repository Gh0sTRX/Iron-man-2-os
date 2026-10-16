#!/usr/bin/env python3
"""G68: owner-only original 2010 Mark V Suitcase + selected authored animation
frames, packaged for isolated G67-derived first-level gameplay candidate.
Never uploads original IPA or raw source assets to Git history.
"""
import argparse,hashlib,json,struct,sys,tempfile,zipfile
from pathlib import Path
import numpy as np
from b24_owner_pack_extract import decode,get_exact
from b24_hover_fire_authentic_pose_preview import source_meshes,prepare
from b24_underwater_source_34_im2v_bake import load_original_b13
from b24_g11_original_2010_city_texture_and_window_ui_contact import pvr_pixels

TARGET="suitcase.bdae"
ATLAS="MC_SuitCase.tga"
# Exact original clip identities; these are selected for a Vita gameplay
# state-machine prototype, NOT a proof of original level1 control bindings.
CLIPS=[
 ("idle","IronMan_Ground_Idel.anim"),
 ("walk","IronMan_Aim_Ground_move_F.anim"),
 ("fire","Ironman_Aim_Ground_idle_Att.anim"),
 ("hover","IronMan_Aim_Float_idle.anim"),
 ("rush","Ironman_Fly_F_RUSH.anim"),
 ("melee","IronMan_Ground_Combo_1.anim"),
 ("land","IronMan_Air_land.anim"),
]
def owner_parts(ipa):
 with zipfile.ZipFile(ipa) as z:
  prefix='Payload/IronMan2.app/'
  models=z.read(prefix+'models')
  textures=z.read(prefix+'textures')
  animations=z.read(prefix+'anims')
 model=get_exact(models,decode(models,'.bdae'),TARGET)
 atlas=get_exact(textures,decode(textures,'.tga'),ATLAS)
 return model,atlas,animations

def write(out,model,atlas,animations):
 from pathlib import Path
 out.mkdir(parents=True,exist_ok=True)
 meshes=source_meshes(model)
 mains=[m for m in meshes if len(m['positions'])==629]
 if len(mains)!=1:raise ValueError('Authentic source Suitcase 629-vtx skin ambiguous')
 main=mains[0]
 image,tex_meta=pvr_pixels(atlas,ATLAS)
 if image.size!=(512,512):raise ValueError('Owner original Mark V atlas dimension mismatch')
 pixel=image.tobytes()
 (out/'G66_armor_tex_00.g66t').write_bytes(b'G66T'+struct.pack('<III',1,512,512)+pixel)
 geom=[];mapping=[];batches=[];total_triangles=0
 for m in meshes:
  points=np.asarray(m['positions'],dtype=np.float32)
  uv=np.asarray(m['uv'],dtype=np.float32)
  faces=np.asarray(m['faces'],dtype=np.int64).reshape(-1)
  if not len(points) or not len(faces):continue
  if uv.shape!=(len(points),2) or np.any(faces<0) or np.any(faces>=len(points)):
   raise ValueError('Suitcase authentic source face/UV layout drift')
  if not np.isfinite(points).all() or not np.isfinite(uv).all():
   raise ValueError('Suitcase source nonfinite UV/geometry')
  off=sum(len(k) for k in geom)
  rows=np.empty((len(faces),),dtype=[
   ('p','<f4',(3,)),('uv','<f4',(2,)),('rgba','u1',(4,))])
  rows['p']=points[faces];rows['uv']=uv[faces];rows['rgba']=255
  geom.append(rows)
  mapping.extend(faces.astype(np.uint16).tolist() if m is main else [65535]*len(faces))
  batches.append((off,len(faces),0,0))
  total_triangles+=len(faces)//3
 if not geom or total_triangles<=0 or len(mapping)>65535:
  raise ValueError('Suitcase face coverage outside Vita contract')
 packed=np.concatenate(geom)
 (out/'G66_armor.g66m').write_bytes(
  b'G66M'+struct.pack('<4I',1,len(packed),len(batches),1)+
  b''.join(struct.pack('<4I',*b) for b in batches)+packed.tobytes())
 (out/'G68_armor_mapping.g68i').write_bytes(
  struct.pack('<4sII',b'G68I',1,len(mapping))+
  np.asarray(mapping,dtype='<u2').tobytes())
 with tempfile.TemporaryDirectory(prefix='g68_owner_b13_') as tmp:
  original=load_original_b13(Path(tmp))
  setup,error,nodes,bones=prepare(original,model,np.asarray(main['positions']))
  if error>=2e-4:raise ValueError('Original Mark V inverse bind mismatch')
  animation_records=decode(animations,'.anim')
  clips=[]
  anim_bytes=bytearray(struct.pack('<4sIII',b'G68A',1,629,len(CLIPS)))
  for alias,name in CLIPS:
   raw=get_exact(animations,animation_records,name)
   track=original.decode_anim(raw)
   duration=int(track.duration_ms)
   if not (0<duration<=12000):raise ValueError('Source clip duration unexpected '+name)
   times=list(range(0,duration,50))+[duration]
   if len(times)>300:raise ValueError('Unexpected source clip sample count')
   pose=[]
   for ms in times:
    xyz=np.asarray(original.bake_pose(setup,track,ms),dtype='<f4')
    if xyz.shape!=(629,3) or not np.isfinite(xyz).all() or np.abs(xyz).max()>1.e5:
     raise ValueError('Native suit motion invalid '+name)
    pose.append(xyz)
   samples=np.stack(pose)
   key=alias.encode('ascii')
   anim_bytes.extend(struct.pack('<16sII',key,len(times),duration))
   anim_bytes.extend(samples.tobytes())
   clips.append({'alias':alias,'original_anim':name,'frames':len(times),
      'duration_ms':duration,'authored_keyframes_source_SHA256':hashlib.sha256(raw).hexdigest(),
      'frame0_delta_max':float(np.abs(samples-samples[0]).max())})
 (out/'G68_suitcase_motion.g68a').write_bytes(anim_bytes)
 report={
  'stage':'G68', 'original_player_BRES':TARGET,'original_atlas':ATLAS,
  'source_model_SHA256':hashlib.sha256(model).hexdigest(),
  'source_texture_SHA256':hashlib.sha256(atlas).hexdigest(),
  'native_atlas_pvr':tex_meta,'authentic_mesh_count':len(meshes),
  'source_original_triangles':total_triangles,'source_flat_vertices':len(mapping),
  'genuine_weighted_body_vertices':629,'source_rig_nodes':nodes,
  'source_skin_bone_palette':bones,'source_inverse_bind_error':error,
  'original_authored_motion_clips':clips,
  'scene_original_Lua_interpreter_ported':False,
  'mission_camera_audio_original_timeline_ported':False,
  'Vita_device_tested':False
 }
 (out/'G68_MARK_V_SOURCE_PROVENANCE.json').write_text(json.dumps(report,indent=2)+'\n')
 print('G68 Mark V real original Suitcase BRES',len(meshes),'meshes',
       total_triangles,'triangles, 629 animated vertices,',len(CLIPS),
       'native 2010 motion clips',flush=True)
 return report

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args()
 write(a.out,*owner_parts(a.ipa))
if __name__=='__main__':main()
