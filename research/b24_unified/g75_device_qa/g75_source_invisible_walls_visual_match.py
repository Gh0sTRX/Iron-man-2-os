#!/usr/bin/env python3
"""G75 read-only original G68 "invisible wall" collider-vs-render sampled
geometry alignment test. This is a SEARCH HEURISTIC, not a proof that
any face is fake: large triangles and physics proxy collision shells
naturally differ from texture mesh surfaces. No modified VPK.
"""
from pathlib import Path
import argparse,json,struct,zipfile
import numpy as np
from scipy.spatial import cKDTree
VRTX=np.dtype([('pos','<f4',(3,)),('uv','<f4',(2,)),('rgba','u1',(4,))])
def audit(vpk):
 with zipfile.ZipFile(vpk) as z:
  src=z.read('assets/G66_city.g66m')
  c=z.read('assets/G66_original_collision.g66c')
 version,n,b,t=struct.unpack_from('<4I',src,4)
 assert (version,n,b,t)==(1,67323,32,31)
 verts=np.frombuffer(src,dtype=VRTX,count=n,offset=20+b*16)['pos'].reshape(-1,3,3)
 coll=np.frombuffer(c,dtype='<f4',offset=12).reshape(-1,3,3)
 assert len(coll)==1910
 norms=np.cross(coll[:,1]-coll[:,0],coll[:,2]-coll[:,0])
 norm2=np.sum(norms*norms,axis=1)
 steep=(norms[:,2]*norms[:,2]<.3364*norm2)&(np.ptp(coll[:,:,2],axis=1)>.1)
 assert int(steep.sum())==1690
 sample=np.concatenate([verts.reshape(-1,3),verts.mean(axis=1),
          .5*(verts[:,0]+verts[:,1]),.5*(verts[:,1]+verts[:,2]),
          .5*(verts[:,0]+verts[:,2])],axis=0)
 tree=cKDTree(sample)
 result={'original_city_source_triangles':len(verts),'source_original_collision_triangles':len(coll),
  'real_steep_wall_triangles':int(steep.sum()),'real_ground_triangles':int((~steep).sum()),
  'method':'sample actual visible textured mesh 157087 vertex/edge-center/triangle-center XYZ points; original collision wall XY horizontal slices and nearest sampled visible point',
  'not_a_robust_exact_triangle_to_triangle_distance':True,
  'physics_only_invisible_face_proven':False,'original_colliders_to_delete_automatically':0,
  'wall_height_slices':[], 'suspect_source_face_IDs_needing_visual_debug_not_automatically_removed':[]}
 suspicion={}
 for level in (.8,2.,5.,12.,22.):
  xyz=[];ids=[]
  for i,f in enumerate(coll):
   if not steep[i] or f[:,2].min()>level or f[:,2].max()<level:continue
   pts=[]
   for k in range(3):
    a,b=f[k],f[(k+1)%3]
    if abs(float(a[2])-level)<.0001:pts.append(a[:2])
    if (a[2]<level<b[2]) or (a[2]>level>b[2]):
     alpha=(level-a[2])/(b[2]-a[2])
     pts.append(a[:2]+alpha*(b[:2]-a[:2]))
   if len(pts)<2:continue
   longest=0.;mid=None
   for p in range(len(pts)):
    for q in range(p+1,len(pts)):
     d=float(np.sum((pts[p]-pts[q])**2))
     if d>longest:longest=d;mid=(pts[p]+pts[q])*.5
   if mid is not None and longest>1.e-8:
    xyz.append([float(mid[0]),float(mid[1]),level]);ids.append(i)
  if not xyz:continue
  d,_=tree.query(xyz,workers=-1)
  j={'torso_height_z':level,'source_wall_faces_intersecting':len(d),
     'sampled_visible_distance_unit_percentile_p50_p75_p90_p95':
       np.percentile(d,[50,75,90,95]).round(4).tolist(),
     'count_nearest_visible_sample_gt_2_units':int((d>2).sum()),
     'count_nearest_visible_sample_gt_5_units':int((d>5).sum())}
  result['wall_height_slices'].append(j)
  if level==.8:
   best=np.argsort(d)[::-1][:35]
   suspicion={int(ids[k]):round(float(d[k]),4) for k in best if d[k]>5}
 result['suspect_source_face_IDs_needing_visual_debug_not_automatically_removed']=[
  {'source_original_collider_face_index':k,
   'centroid_nearest_render_sample_distance_at_z_0_8':v}
   for k,v in suspicion.items()]
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--vpk',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();j=audit(a.vpk)
 a.out.write_text(json.dumps(j,indent=2)+'\n')
 print('PASS G75 real G68 original 1690 walls nearest textured scene geometry sampling, source-only, NO automatic collision deletion')
 for x in j['wall_height_slices']:print(x)
