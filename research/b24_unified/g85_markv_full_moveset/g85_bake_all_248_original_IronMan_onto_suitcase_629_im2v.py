#!/usr/bin/env python3
"""G85: Re-bake *all 248 authentic 2010 Iron Man native joint animations*
onto the ORIGINAL Mark V suitcase.bdae 629-vertex weighted source mesh.
Not an animation retarget by guessed bone name: it uses Gameloft's actual
B13 hierarchical 2010 rig, original skin palette and inverse bind matrices.
Output streamed 20Hz IM2V (same engine format as G8) on disk only.
NO game packaging, gameplay event timing, VPK, or source IPA publication.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,sys,tempfile,zipfile,time,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_hover_fire_authentic_pose_preview import source_meshes,prepare
from b24_underwater_source_34_im2v_bake import load_original_b13
ROOT=Path(__file__).resolve().parents[3]
def bake(ipa:Path,out:Path,manifest:Path,limit:int=0):
 with zipfile.ZipFile(ipa) as z:
  original_model=z.read("Payload/IronMan2.app/models")
  anim_pack=z.read("Payload/IronMan2.app/anims")
 mesh=get_exact(original_model,decode(original_model,'.bdae'),'suitcase.bdae')
 models=source_meshes(mesh)
 mains=[m for m in models if len(m['positions'])==629]
 if len(mains)!=1:raise ValueError('2010 owner source original Mark V skinned 629 mesh ambiguous')
 coordinates=np.asarray(mains[0]['positions'],dtype=np.float64)
 records=decode(anim_pack,'.anim')
 im=[x for x in records if x.name.casefold().startswith('ironman_')]
 if len(im)!=248:raise ValueError(f"Expected authentic original 248 IronMan source clips, got {len(im)}")
 if limit and not(1<=limit<=248):raise ValueError('Smoke testing limit 1..248 only')
 selected=im[:limit] if limit else im
 out.mkdir(parents=True,exist_ok=True)
 start=time.monotonic()
 summary=[];missing=[];total_bytes=0
 with tempfile.TemporaryDirectory(prefix="g85_original_2010_markv_") as t:
  native=load_original_b13(Path(t))
  source_data,inverse_error,nodes,palette=prepare(native,mesh,coordinates)
  if inverse_error>=2e-4:raise ValueError('Mark V source 2010 inverse-bind bones invalid')
  for rec in selected:
   source_raw=get_exact(anim_pack,records,rec.name)
   a=native.decode_anim(source_raw)
   ms=int(a.duration_ms)
   if not(0<=ms<=120000):raise ValueError(f'Original 2010 clip duration invalid {rec.name} {ms}')
   ticks=list(range(0,ms,50))+([ms] if ms else [0])
   if len(ticks)>4000:raise ValueError('2010 IM2V source runtime maximum frames exceeded')
   clip_name='suitcase_'+rec.name.removesuffix('.anim').casefold()
   if len(clip_name)>119:raise ValueError('Source filename too long')
   dest=out/(clip_name+'.im2v')
   sha=hashlib.sha256()
   with dest.open('wb') as output:
    header=struct.pack('<4sIIII',b'IM2V',629,len(ticks),20,ms)
    output.write(header);sha.update(header)
    largest_delta=0.0;first=None
    for tick in ticks:
     frame=np.asarray(native.bake_pose(source_data,a,tick),dtype='<f4')
     if frame.shape!=(629,3) or not np.isfinite(frame).all() or np.abs(frame).max()>1.e5:
      raise ValueError('Invalid original Mark V 2010 joint pose '+rec.name)
     if first is None:first=frame.copy()
     else:largest_delta=max(largest_delta,float(np.abs(frame-first).max()))
     payload=frame.tobytes(order='C')
     sha.update(payload);output.write(payload)
   expected=20+len(ticks)*629*3*4
   if dest.stat().st_size!=expected:raise ValueError('Native streamed 2010 IM2V size')
   total_bytes+=expected
   summary.append({'original_2010_clip':rec.name,'vita_stream_name':dest.name,
    'duration_ms':ms,'source_joint_tracks':len(a.names),
    'sample_frames_20hz':len(ticks),'true_original_weighted_vertices':629,
    'source_original_anim_sha256':hashlib.sha256(source_raw).hexdigest(),
    'baked_source_im2v_sha256':sha.hexdigest(),'bytes':expected,
    'max_baked_pose_delta_from_first_frame':largest_delta,
    'source_hit_active_frames_verified':False,'original_input_transition_verified':False})
   if len(summary)%24==0:
    print('G85 TRUE ORIGINAL MARKV B13 BAKED',len(summary),'/',len(selected),
       'MB',round(total_bytes/1048576,2),'elapsed_s',round(time.monotonic()-start,1),flush=True)
 report={'proof':'Original Gameloft 2010 owner IPA native suitcase.bdae skin + original ironman ANIM',
   'original_2010_anim_bank_IronMan_count':len(im),
   'original_native_MarkV_weighted_verts':629,
   'original_source_model_sha256':hashlib.sha256(mesh).hexdigest(),
   'inverse_bind_max_error':inverse_error,
   'original_skin_rig_node_count':nodes,
   'original_skin_bone_palette_count':palette,
   'genuine_IronMan_source_clips_baked_as_MarkV':len(summary),
   'source_only_smoke_subset':bool(limit),
   'genuine_all_248_complete':len(summary)==248,
   'g85_streamed_bytes':total_bytes,
   'baked_motion_files':summary,
   'source_original_gameplay_input_mapping_verified':False,
   'original_2010_attack_active_hit_frames_verified':False,
   'full_game_Vita_audio_AI_and_combat_integrated':False,
   'new_VPK_generated':False}
 manifest.parent.mkdir(parents=True,exist_ok=True)
 manifest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print('PASS G85 authentic 2010 Mark V B13 skin +',len(summary),
       'real ironman anims -> 629v stream','source-weight mismatch',inverse_error,
       'total_MB',round(total_bytes/1048576,2),'NO VPK',flush=True)
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 p.add_argument('--manifest',required=True,type=Path)
 p.add_argument('--limit',type=int,default=0)
 args=p.parse_args()
 bake(args.ipa,args.out,args.manifest,args.limit)
