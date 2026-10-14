#!/usr/bin/env python3
"""G7 original 2010 C1L1 collision-source integration in FULL existing B24.
Apply after G6 source fix. CPU owns physics; GPU owns rendering. Never changes
B14 input/flight physics, only corrected world X/Y after original wall sweep.
Test G7 separately from the user-confirmed G5/G6 game VPKs.
"""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[2]
W=ROOT/"work"
p=W/"src/main.c"
s=p.read_text()
def rep(a,b):
 global s
 n=s.count(a)
 if n!=1:raise RuntimeError(f"G7 drift {n} matches {a[:120]!r}")
 s=s.replace(a,b)
rep('''#include "../b24/b24_unified/b24_gpu_runtime.h"''',
'''#include "../b24/b24_unified/b24_gpu_runtime.h"
#include "../b24/b24_unified/b24_c1_original_collision.h"''')
rep("static B24GpuRuntime b24_gpu_rt={0};",
'''static B24GpuRuntime b24_gpu_rt={0};
static B24C1OriginalCollision b24_original_walls={0};''')
rep('''    if(running&&!b24_gpu_runtime_open(&b24_gpu_rt,"app0:maps/C1L1_environment.c1g2"))
        running=0;''',
'''    /* Exact 2010 iOS C1L1_col_01 + C1L1_building_col BDAE faces:
       source-owned original 1908 faces, 1690 steep candidates, Z-UP.
       Fail closed rather than showing a fake wall collider as working. */
    if(running&&!b24_c1_original_collision_load(&b24_original_walls,
                                               "app0:maps/C1L1_original_collision.c1wc")){
       (void)b24_gpu_boot_trace_mark("23 C1WC_ORIGINAL_COLLISION_LOAD_FAILED");
       running=0;
    }
    if(running)(void)b24_gpu_boot_trace_mark("23 C1WC_ORIGINAL_COLLISION_LOADED");
    if(running&&!b24_gpu_runtime_open(&b24_gpu_rt,"app0:maps/C1L1_environment.c1g2"))
        running=0;''')
rep('''          b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);
          world.orbit=b24_camera_recenter''',
'''#ifdef B24_GPU_ENGINE
          const float old_c1x=world.x,old_c1y=world.y,old_c1z=world.z;
#endif
          b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);
#ifdef B24_GPU_ENGINE
          const float proposed_c1x=world.x,proposed_c1y=world.y;
          /* Sub-frame genuine triangle sweep, original XY+Z collision.
             B14 drives normal walk, hover, Stage2 and RUSH the same way;
             only original wall contacts reconcile actor world XY.
             NO invented boxes and NO GL queries or per-frame heap allocation. */
          if(!b24_c1_original_collision_resolve(&b24_original_walls,
              old_c1x,old_c1y,old_c1z,world.z,.35f,&world.x,&world.y)){
              running=0;break;
          }
          float c1_follow=fminf(7.f*dt,1.f);
          world.cam_x+=(world.x-proposed_c1x)*c1_follow;
          world.cam_y+=(world.y-proposed_c1y)*c1_follow;
#endif
          world.orbit=b24_camera_recenter''')
rep('''    b24_gpu_runtime_close(&b24_gpu_rt);''',
'''    b24_c1_original_collision_free(&b24_original_walls);
    b24_gpu_runtime_close(&b24_gpu_rt);''')
assert 'C1L1_original_collision.c1wc' in s
p.write_text(s)
module=W/"b24/b24_unified/b24_c1_original_collision.c"
header=module.with_suffix(".h")
shutil.copyfile(ROOT/"research/b24_unified/b24_c1_original_collision.c",module)
shutil.copyfile(ROOT/"research/b24_unified/b24_c1_original_collision.h",header)
cm=W/"CMakeLists.txt"
b=cm.read_text()
marker="# B24_G7_GENUINE_CPU_WALLS_SOURCE"
if marker in b:raise RuntimeError("duplicate G7 wall module")
b+='''

# B24_G7_GENUINE_CPU_WALLS_SOURCE
if(B24_ENABLE_GPU)
 target_sources(im2_beta PRIVATE
   "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_c1_original_collision.c")
endif()
'''
cm.write_text(b)
print("PASS G7 real gameplay: original source C1L1 1908-triangle CPU wall sweeps integrated after B14 tick, GPU still only draws")
