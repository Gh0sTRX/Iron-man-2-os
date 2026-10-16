#!/usr/bin/env python3
"""G107 physical Vita owner feedback: visible authored 2010 C1L1
G68 has 22,441 triangles, loaded physics set only 1,910 faces. This
audit measures which *opaque/steep visible triangle CENTROIDS* lack a
nearby author COLLISION FACE AABB (not proof that they should be solid,
nor authorization to enable 22k fake colliders). No source mesh exported.
"""
import argparse,collections,json,math,struct,zipfile
from pathlib import Path
def run(p,out):
 with zipfile.ZipFile(p) as z:
  if z.testzip() is not None:raise ValueError('G107 needs verified G104 source VPK')
  mesh=z.read('assets/G66_city.g66m')
  col=z.read('assets/G66_original_collision.g66c')
  if mesh[:4]!=b'G66M' or struct.unpack_from('<4I',mesh,4)!=(1,67323,32,31):
   raise ValueError('Source owner visual mesh changed')
  if col[:4]!=b'G66C' or struct.unpack_from('<2I',col,4)!=(1,1910):
   raise ValueError('Source owner collision changed')
  batches=[struct.unpack_from('<4I',mesh,20+i*16) for i in range(32)]
  vis=memoryview(mesh)[20+32*16:]
  def v(i):return struct.unpack_from('<3f',vis,i*24)
  original_faces=[]
  for i in range(1910):
   f=struct.unpack_from('<9f',col,12+i*36)
   pts=[f[:3],f[3:6],f[6:9]]
   x0,x1=min(a[0] for a in pts),max(a[0] for a in pts)
   y0,y1=min(a[1] for a in pts),max(a[1] for a in pts)
   z0,z1=min(a[2] for a in pts),max(a[2] for a in pts)
   ax,ay,az=pts[0];bx,by,bz=pts[1];cx,cy,cz=pts[2]
   nx=(by-ay)*(cz-az)-(bz-az)*(cy-ay)
   ny=(bz-az)*(cx-ax)-(bx-ax)*(cz-az)
   nz=(bx-ax)*(cy-ay)-(by-ay)*(cx-ax)
   n=nx*nx+ny*ny+nz*nz
   steep=(nz*nz<.3364*n and z1-z0>.1)
   original_faces.append((x0,x1,y0,y1,z0,z1,steep))
  tiles=collections.defaultdict(list)
  def bins(lo,hi):
   lo=math.floor((lo-.8)/12.);hi=math.floor((hi+.8)/12.)
   return range(lo,hi+1)
  for i,(x0,x1,y0,y1,z0,z1,steep) in enumerate(original_faces):
   if not steep:continue
   for a in bins(x0,x1):
    for b in bins(y0,y1):
     tiles[a,b].append(i)
  stats=[]
  cutout={1,6,7,9,15,19,20}
  all_count=0;opaque_count=0;visible_steep=0
  close=0;far=0;examples=[]
  for group,(first,count,tex,flags) in enumerate(batches):
   row={'group':group,'source_material_atlas_id':tex,'opaque_source_atlas':tex not in cutout,
       'source_triangle_count':count//3,'visible_opaque_steep_triangles':0,
       'rough_opaque_steep_centroids_with_nearby_original_collision_wall_AABB':0,
       'rough_opaque_steep_centroids_with_no_nearby_original_collision_wall_AABB':0}
   for i in range(first,first+count,3):
    all_count+=1
    a,b,c=v(i),v(i+1),v(i+2)
    if tex in cutout or tex==0xffffffff:continue
    opaque_count+=1
    ab=(b[0]-a[0],b[1]-a[1],b[2]-a[2])
    ac=(c[0]-a[0],c[1]-a[1],c[2]-a[2])
    nx=ab[1]*ac[2]-ab[2]*ac[1]
    ny=ab[2]*ac[0]-ab[0]*ac[2]
    nz=ab[0]*ac[1]-ab[1]*ac[0]
    n=nx*nx+ny*ny+nz*nz
    if n<1e-7 or nz*nz>=.3364*n or max(a[2],b[2],c[2])-min(a[2],b[2],c[2])<=.1:
     continue
    visible_steep+=1;row['visible_opaque_steep_triangles']+=1
    x=(a[0]+b[0]+c[0])/3;y=(a[1]+b[1]+c[1])/3;z=(a[2]+b[2]+c[2])/3
    nearby=False
    for fidx in tiles.get((math.floor(x/12.),math.floor(y/12.)),()):
     x0,x1,y0,y1,z0,z1,_=original_faces[fidx]
     if x0-.8<=x<=x1+.8 and y0-.8<=y<=y1+.8 and z0-.8<=z<=z1+.8:
      nearby=True;break
    if nearby:
     close+=1;row['rough_opaque_steep_centroids_with_nearby_original_collision_wall_AABB']+=1
    else:
     far+=1;row['rough_opaque_steep_centroids_with_no_nearby_original_collision_wall_AABB']+=1
     if len(examples)<35:
      examples.append({'original_visual_sourced_group':group,
       'original_visual_triangle_number':i//3,
       'visual_wall_triangle_centroid_xyz_rounded':[round(x,2),round(y,2),round(z,2)],
       'not_proof_of_physically_solid_wall':True})
   stats.append(row)
 assert all_count==22441
 report={'source':'real original user-owned 2010 city actual Vita G104 VPK identical G68 resources',
  'visible_source_total_triangles':all_count,
  'visible_opaque_nontransparent_triangles':opaque_count,
  'existing_original_collision_faces':1910,
  'existing_source_steep_collision_walls':sum(f[6] for f in original_faces),
  'source_opaque_visual_steep_wall_triangles':visible_steep,
  'visual_opaque_steep_triangle_centroid_Near_AABB_existing_wall_rough_count':close,
  'visual_opaque_steep_triangle_centroid_No_AABB_existing_wall_rough_count':far,
  'original_source_material_groups':stats,
  'diagnostic_example_visual_centroids_not_matched':examples,
  'does_not_prove_original_world_mesh_physically_solid':True,
  'does_not_enable_invented_unproven_collision':True,
  'real_vita_hardware_collision_feedback_received':True,
  'requires_targeted_player_location_and_source_collision_mesh_authorship_check':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('G107 genuine original 2010 source collision coverage rough AABB count',visible_steep,close,far)
 print('G107 wall-group candidate gaps',sorted(
  [(a['group'],a['rough_opaque_steep_centroids_with_no_nearby_original_collision_wall_AABB']) for a in stats],
  key=lambda x:-x[1])[:12])
 print('G107 proof: 1910 original physics faces vs 22441 total visual 2010 original triangles; unverified decor MUST NOT auto become solid or ground')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--vpk',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
 o=a.parse_args();run(o.vpk,o.out)
