#!/usr/bin/env python3
"""G195 original user-owned 2010 Iron Man 2 (iOS) six Mark VI Uni-Beam
source .anim clips x REAL B13 BDAE matrix hierarchy. Per-frame
Dummy_Chest (native ID14) & Dummy_Foot_L (native ID33) positions AND
authentic authored 802-vertex BRES skinned armor mesh. Produce GIFs and
PNG from ORIGINAL source only; NOT gameplay, no invented keyframes.
No VPK, new Vita executable, or original unlicensed assets exported.
"""
from __future__ import annotations
import argparse,json,hashlib,math,sys,tempfile,zipfile
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13
from b24_hover_fire_authentic_pose_preview import source_meshes,prepare

MODEL="Iron_man_mark6.bdae"
SOCKETS={14:("Dummy_Chest","Dummy_Chest-node","Bip01_Spine1-node"),
         33:("Dummy_Foot_L","Dummy_Foot_L-node","Bip01_L_Foot-node")}
BEAM={
 "ground":[("IronMan_Aim_Ground_Beam1.anim",400),
           ("IronMan_Aim_Ground_Beam2.anim",400),
           ("IronMan_Aim_Ground_Beam3.anim",1000)],
 "hover":[("IronMan_Aim_Float_Beam1.anim",600),
          ("IronMan_Aim_Float_Beam2.anim",400),
          ("IronMan_Aim_Float_Beam3.anim",1266)],
}
OWNER_SIZE=248613763
def source_frames(ipa:Path,g193:Path):
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("G195 needs genuine owner 2010 1.0.0 IPA")
 proven=json.loads(g193.read_text())
 if not proven.get("native_original_source_name_mapping_PROVEN"):
  raise ValueError("original 2010 dummy 14/33 name mapping has not been source proven")
 for k,(name,_,_) in SOCKETS.items():
  if proven.get(f"original_native_scene_group{k}_named_source_key")!=name:
   raise ValueError("original source native SceneImpl dummy key/name drift")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner original 2010 IPA CRC mismatch")
  models=z.read("Payload/IronMan2.app/models")
  animation=z.read("Payload/IronMan2.app/anims")
 models_index=decode(models,".bdae")
 animations_index=decode(animation,".anim")
 raw_model=get_exact(models,models_index,MODEL)
 actual=source_meshes(raw_model)
 meshes=[m for m in actual if len(m["positions"])==802]
 if len(meshes)!=1:raise ValueError("original MarkVI authored skin 802 vertices ambiguous")
 mesh=meshes[0]
 faces=np.asarray(mesh["faces"]).reshape(-1,3).astype(int)
 if len(faces)<500 or np.any(faces<0) or np.any(faces>=802):
  raise ValueError("original 2010 skin mesh faces invalid")
 with tempfile.TemporaryDirectory(prefix="g195_original_2010_sockets_") as temp:
  bake=load_original_b13(Path(temp))
  setup,err,nodes,palette=prepare(bake,raw_model,np.asarray(mesh["positions"],dtype=np.float64))
  rig=setup["nodes"]
  if nodes!=96:raise ValueError("MarkVI true rig expected original 96 nodes")
  if not np.isfinite(err) or err>=2e-4:raise ValueError("2010 BRES inverse-bind source original failed")
  byname={n["name"]:n for n in rig}
  for k,(name,rig_node,parent) in SOCKETS.items():
   if rig_node not in byname or byname[rig_node]["parent"]!=parent:
    raise ValueError(f"native real source 2010 authored {k} rig parent mismatch")
  rest=bake.worlds(rig)
  reference={
    str(k):{"authored_node":node,"parent":parent,
       "source_rest_world_matrix":np.asarray(rest[node]).tolist(),
       "source_rest_position_xyz":np.asarray(rest[node])[:3,3].tolist()}
       for k,(name,node,parent) in SOCKETS.items()}
  result={}
  for mode,clips in BEAM.items():
   staged=[]
   global_start=0
   for phase,(clip,duration) in enumerate(clips,1):
    track=bake.decode_anim(get_exact(animation,animations_index,clip))
    if track.duration_ms!=duration:
     raise ValueError(f"2010 source {clip} duration drift {track.duration_ms} vs {duration}")
    if len(track.names)<20:
     raise ValueError("2010 original UniBeam source has missing bone channels "+clip)
    # Each native source phase is separate original animation with own timeline.
    # End time included for trajectory integrity and source motion interpolation.
    samples=sorted(set([0,duration]+list(range(0,duration,100))))
    for t in samples:
     matrices=bake.worlds(rig,track,t)
     sockets={}
     for k,(label,node,parent) in SOCKETS.items():
      mat=np.asarray(matrices[node],dtype=np.float64)
      if mat.shape!=(4,4) or not np.isfinite(mat).all():
       raise ValueError("invalid original 2010 animation socket matrix")
      pos=mat[:3,3]
      if np.max(np.abs(pos))>1000:raise ValueError("original world rest coordinate excessive")
      sockets[str(k)]={"actual_2010_animated_rig_position_xyz":[float(v) for v in pos],
        "actual_2010_animated_rig_world_matrix":mat.tolist()}
     verts=bake.bake_pose(setup,track,t)
     if verts.shape!=(802,3) or not np.isfinite(verts).all():
      raise ValueError("genuine 2010 authored skin animation invalid")
     staged.append({"phase":phase,"source_clip":clip,"source_animation_duration_ms":duration,
      "source_time_ms":t,"sequence_time_ms":global_start+t,
      "source_original_bres_socket_matrices":sockets,
      "vertices":verts})
    global_start+=duration
   result[mode]={
    "duration_ms":global_start,
    "source_original_frames":staged}
  return result,reference,faces,err,palette

def render_samples(modes,faces,output:Path):
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 from matplotlib.animation import PillowWriter,FuncAnimation
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 output.mkdir(parents=True,exist_ok=True)
 for mode,info in modes.items():
  frames=info["source_original_frames"]
  allvertices=np.concatenate([f["vertices"] for f in frames],axis=0)
  # Bounds only from actually measured original source geometry.
  limmin=np.min(allvertices,axis=0)
  limmax=np.max(allvertices,axis=0)
  mid=(limmin+limmax)*.5
  radius=max(float(np.max(limmax-limmin))*.59,.1)
  fig=plt.figure(figsize=(6.7,5.5),facecolor="#0e1725")
  ax=fig.add_subplot(111,projection="3d",facecolor="#0e1725")
  ax.set_xlim(mid[0]-radius,mid[0]+radius)
  ax.set_ylim(mid[1]-radius,mid[1]+radius)
  ax.set_zlim(mid[2]-radius,mid[2]+radius)
  ax.set_box_aspect((1,1,1))
  ax.view_init(elev=7,azim=-65)
  ax.set_axis_off()
  # Keep ALL original source BRES triangles (not a sparse perforated subset), original skinned frames.
  polygon=Poly3DCollection(frames[0]["vertices"][faces],
   facecolor="#a1b6c8",edgecolors=(.11,.17,.26,.13),linewidths=.08)
  ax.add_collection3d(polygon)
  pts={k:ax.scatter([],[],[],s=65,marker="x",linewidths=3,
      color=("#ffae38" if k=="14" else "#59e5a8"),depthshade=False)
      for k in ("14","33")}
  text=ax.text2D(.03,.97,"",transform=ax.transAxes,va="top",fontsize=10,color="white")
  legend=ax.text2D(.03,.04,
   "Orange = #14 Dummy_Chest  |  Green = #33 Dummy_Foot_L\n"
   "REAL source 2010 rig + animation (host) • NOT Vita gameplay",
   transform=ax.transAxes,va="bottom",fontsize=8,color="#ebecf2")
  # Retain all original source-timeline samples; no invented in-between poses.
  display=frames
  def frame_update(f):
   polygon.set_verts(f["vertices"][faces])
   for k,scatter in pts.items():
    xyz=f["source_original_bres_socket_matrices"][k]["actual_2010_animated_rig_position_xyz"]
    scatter._offsets3d=([xyz[0]],[xyz[1]],[xyz[2]])
   text.set_text(f"IRON MAN 2 iOS • ORIGINAL MARK VI • {mode.upper()}\n"
     f"Uni-Beam phase {f['phase']}  t={f['source_time_ms']} ms\n{f['source_clip']}")
   return polygon,*pts.values(),text,legend
  output_name=output/f"G195_REAL_2010_MARKVI_{mode.upper()}_UNIBEAM_ANIMATED_DUMMY14_33.gif"
  anim=FuncAnimation(fig,frame_update,frames=display,interval=130,blit=False,repeat=True)
  anim.save(output_name,writer=PillowWriter(fps=8))
  plt.close(fig)
  print("G195 real original 2010 skinned source GIF",output_name.name,"frames",len(display),
        "bytes",output_name.stat().st_size,flush=True)
 # PNG source 3D socket trajectories for side by side comparisons
 fig=plt.figure(figsize=(13,6),dpi=130,facecolor="white")
 for j,(mode,info) in enumerate(modes.items()):
  ax=fig.add_subplot(1,2,j+1,projection="3d")
  for k,col in (("14","darkorange"),("33","seagreen")):
   pos=np.asarray([f["source_original_bres_socket_matrices"][k]["actual_2010_animated_rig_position_xyz"]
                   for f in info["source_original_frames"]])
   ax.plot(pos[:,0],pos[:,1],pos[:,2],color=col,linewidth=2,label=f"Original {k}")
   ax.scatter(pos[0,0],pos[0,1],pos[0,2],s=35,color=col)
  ax.set_title(f"2010 Mark VI {mode} 3 native Uni-Beam phases\nB13 original animated socket trajectory",fontsize=10)
  ax.set_xlabel("BDAE local X")
  ax.set_ylabel("BDAE local Y")
  ax.set_zlabel("BDAE local Z")
  ax.legend()
 fig.text(.5,.015,"REAL 2010 BDAE + .anim keyframes | source-rig-local, NOT the Vita / original game's particle emitter",
  ha="center",fontsize=9)
 fig.tight_layout(rect=(0,.045,1,1))
 p=output/"G195_ORIGINAL_2010_MARKVI_GROUND_HOVER_DUMMY14_33_SOURCE_MOTION_TRAJECTORIES.png"
 fig.savefig(p)
 plt.close(fig)
 print("G195 source trajectory PNG",p.name,p.stat().st_size,flush=True)

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--ipa",required=True,type=Path)
 parser.add_argument("--g193",required=True,type=Path)
 parser.add_argument("--out",required=True,type=Path)
 a=parser.parse_args()
 modes,rest,faces,err,palette=source_frames(a.ipa,a.g193)
 a.out.mkdir(parents=True,exist_ok=True)
 render_samples(modes,faces,a.out)
 report={
  "source":"2010 original owned IPA BDAE authored Mark VI BRES rig + six genuine .anim G169 UniBeam clips",
  "original_native_dummy_names":{"14":"Dummy_Chest","33":"Dummy_Foot_L"},
  "source_original_armor_bdae":MODEL,"source_original_skin_vertices":802,
  "source_original_skin_triangles":len(faces),
  "source_original_inverse_rest_bind_residual":err,
  "source_original_skin_palette_size":palette,
  "source_original_rest_socket_matrices":rest,
  "source_phase_timeline_ms":{mode:info["duration_ms"] for mode,info in modes.items()},
  "source_original_sampled_sequences":{
    mode:[{k:v for k,v in f.items() if k!="vertices"}
          for f in info["source_original_frames"]]
    for mode,info in modes.items()},
  "original_2010_beam_native_attack_event_frame_mapping_PROVEN":False,
  "original_2010_phase33_conditions_PROVEN":False,
  "original_game_or_Vita_scene_world_actor_transform_PROVEN":False,
  "Vita_active_particle_emitter_world_position_integrated":False,
  "Vita_real_UNIBEAM_hit_detection_or_damage_changed":False,
  "static_and_GIF_previews_are_HOST_source_only_NOT_Vita_gameplay":True,
  "NO_VPK":True
 }
 (a.out/"G195_REAL_2010_MARKVI_UNIBEAM_ANIMATED_CHEST_FOOT_SOURCE_MANIFEST.json").write_text(
    json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 for mode,info in modes.items():
  p=np.asarray([f["source_original_bres_socket_matrices"]["14"]["actual_2010_animated_rig_position_xyz"]
                 for f in info["source_original_frames"]])
  f=np.asarray([f["source_original_bres_socket_matrices"]["33"]["actual_2010_animated_rig_position_xyz"]
                 for f in info["source_original_frames"]])
  print("G195 original source mode",mode,"frames",len(p),"chest motion range",np.ptp(p,axis=0),
       "foot motion range",np.ptp(f,axis=0),flush=True)
 print("G195 PASS native 2010 original MarkVI 6 UniBeam animated BRES socket matrices and source skinned mesh GIF/PNG generated; NO VPK")
if __name__=="__main__":main()
