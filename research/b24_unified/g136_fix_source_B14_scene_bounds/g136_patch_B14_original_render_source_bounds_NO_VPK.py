#!/usr/bin/env python3
"""G136B fix previously masked G128: ONE actual B14 world tick still clamped
movement x[-324,330] and y[-351,254] even after G128 expanded G75
world collision to original full G66 geometry! Compute ACTUAL native 2010
render-source AABB from G66M 67,323 x 24-byte original vertices.
Plug into existing B14 x/y clamp with per-source-mesh exact floats under
separate opt-in macro; G75 polygon capsule remains final authority.
Do NOT claim bounding rectangle equals original 2010 authored play volume.
No full flight permission assumption, no new physics owner and NO VPK.
"""
from pathlib import Path
import math,struct
R=Path(__file__).resolve().parents[3];W=R/'work'
P=W/'src/b14_world.c';CM=W/'CMakeLists.txt';M=W/'src/main.c'
SCENE=W/'assets/G66_city.g66m'
def apply():
 for f in (P,CM,M,SCENE):
  if not f.is_file():raise FileNotFoundError('G136B exact original G134 source required '+str(f))
 source=P.read_text();cm=CM.read_text();main=M.read_text()
 assert main.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
 if 'G136_REAL_CITY_BOUND_B14_WORLD_SOURCE' in source:
  raise ValueError('G136B B14 world already patched')
 with SCENE.open('rb') as f:
  header=f.read(20+32*16)
  if len(header)!=20+512 or header[:4]!=b'G66M':
   raise ValueError('G136B original 2010 G66M native header missing')
  vers,count,nbatch,tex=struct.unpack_from('<IIII',header,4)
  if (vers,count,nbatch,tex)!=(1,67323,32,31):
   raise ValueError('G136B user authentic G66M format drift')
  v=f.read(count*24)
  if len(v)!=count*24 or f.read(1):
   raise ValueError('G136B original source vertex byte count unexpected')
  coords=[struct.unpack_from('<3f',v,i*24) for i in range(count)]
  if any(not all(math.isfinite(n) and abs(n)<100000 for n in xyz) for xyz in coords):
   raise ValueError('G136B original source non-finite scene')
 minx,maxx=min(p[0] for p in coords),max(p[0] for p in coords)
 miny,maxy=min(p[1] for p in coords),max(p[1] for p in coords)
 assert minx < -600 < maxx and miny < -700 < maxy and maxx>550 and maxy>500
 assert abs(minx+761.034)<.10 and abs(maxx-649.194)<.10
 assert abs(miny+773.51)<.10 and abs(maxy-586.695)<.10
 cap=.35
 xline='w->x=cl(w->x+w->authored_move_vx*dt,-324.f,330.f);'
 yline='w->y=cl(w->y+w->authored_move_vy*dt,-351.f,254.f);'
 if source.count(xline)!=1 or source.count(yline)!=1:
  raise ValueError("G136B B14 movement not 2026-10 G75 original-source line; refusing silent wrong patch")
 # B14 class and G75 source one mesh must use same physical source XY AABB;
 # radius inset is safe, G75 still supplies actual polygon collider.
 xreplace=f'''/* G136_REAL_CITY_BOUND_B14_WORLD_SOURCE: original 2010
    67,323 G66M source vertices measured X min/max, radius inset.
    Not an original scripted mission-playable zone / suit flight gate. */
#ifdef B24_G136_SOURCE_B14_WORLD_BOUNDS
w->x=cl(w->x+w->authored_move_vx*dt,{minx+cap:.7f}f,{maxx-cap:.7f}f);
#else
{xline}
#endif'''
 yreplace=f'''#ifdef B24_G136_SOURCE_B14_WORLD_BOUNDS
w->y=cl(w->y+w->authored_move_vy*dt,{miny+cap:.7f}f,{maxy-cap:.7f}f);
#else
{yline}
#endif'''
 source=source.replace(xline,xreplace,1).replace(yline,yreplace,1)
 cm+='''

# G136B: remove G75 original B14 central sandbox clamp; reconcile
# original real 2010 G66M full vertex XY source bounds + one G75 capsule.
option(B24_G136_SOURCE_B14_WORLD_BOUNDS "Full 2010 C1L1 G66 render-source bounds in B14 before G75 original capsule" OFF)
if(B24_G136_SOURCE_B14_WORLD_BOUNDS)
 if(NOT B24_G108_SOURCE_VISUAL_WALLS OR NOT B24_G75_SOURCE_CAPSULE)
  message(FATAL_ERROR "G136B full scene B14 source bounds requires G108 and G75 capsule")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G136_SOURCE_B14_WORLD_BOUNDS=1)
endif()
'''
 P.write_text(source);CM.write_text(cm)
 assert not list(W.rglob('*.vpk'))
 print(f"G136B original 2010 G66M measured x[{minx:.6f},{maxx:.6f}] y[{miny:.6f},{maxy:.6f}], B14 internal movement clamp fixed to genuine mesh radius .35 and same G75 world; NO VPK")
if __name__=='__main__':apply()
