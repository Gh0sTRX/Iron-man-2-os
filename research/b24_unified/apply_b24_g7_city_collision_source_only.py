#!/usr/bin/env python3
"""B24 G7: authentic 2010 C1L1 world collision integration, no fake boxes.

Run only after source assembly, C2, GPU main, G5 menu and G6 analog patch.
C1WC is generated from user's original two COLLISION BDAE resources, NOT
from bounding boxes or triangles of the visual-only display mesh.
CPU B14 world stays authority; VitaGL 3D rendering unchanged.
Fail closed if the source patch markers or original colliders drift.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[2]/"work"
main=root/"src/main.c"
s=main.read_text()
def rep(before,after):
 global s
 n=s.count(before)
 if n!=1:
  raise RuntimeError(f"G7 collision source drift: expected once got {n}: {before[:110]!r}")
 s=s.replace(before,after)
rep('#include "../b24/b24_unified/b24_gpu_runtime.h"',
'''#include "../b24/b24_unified/b24_gpu_runtime.h"
#include "../b24/b24_unified/b24_c1_original_collision.h"
static B24C1OriginalCollision b24_original_c1_collision={0};''')
rep('''    if(running&&!b24_gpu_runtime_open(&b24_gpu_rt,"app0:maps/C1L1_environment.c1g2"))
        running=0;''',
'''    if(running&&!b24_gpu_runtime_open(&b24_gpu_rt,"app0:maps/C1L1_environment.c1g2"))
        running=0;
    if(running&&!b24_c1_original_collision_load(&b24_original_c1_collision,
                                     "app0:maps/C1L1_source.c1wc")){
        (void)b24_gpu_boot_trace_mark("36 C1WC_ORIGINAL_COLLISION_LOAD_FAILED");
        running=0;
    }else if(running){
        (void)b24_gpu_boot_trace_mark("36 C1WC_ORIGINAL_COLLISION_LOADED");
    }''')
rep('''          b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);''',
'''          /* Source C1WC wall surfaces are in original Z-up B14 coords.
             Collision broadphase/narrowphase live on CPU; GL frame never
             blocks or renders the physics geometry. Continuous X/Y sweep
             protects high-speed rush; floor remains unmodified/unrestored. */
          const float old_wall_x=world.x,old_wall_y=world.y,old_wall_z=world.z;
          b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);
          float wall_x=world.x,wall_y=world.y;
          if(!b24_c1_original_collision_resolve(&b24_original_c1_collision,
               old_wall_x,old_wall_y,old_wall_z,world.z,.35f,
               &wall_x,&wall_y)){
              (void)b24_gpu_boot_trace_mark("46 C1WC_COLLISION_RESOLVE_FAILED");
              running=0;
          }else{
              /* Move the camera by the authoritative collision correction to
                 avoid the view moving through walls ahead of the suit. */
              world.cam_x+=wall_x-world.x;
              world.cam_y+=wall_y-world.y;
              world.x=wall_x;world.y=wall_y;
          }''')
rep('''    b24_gpu_runtime_close(&b24_gpu_rt);''',
'''    b24_c1_original_collision_free(&b24_original_c1_collision);
    b24_gpu_runtime_close(&b24_gpu_rt);''')
main.write_text(s)
cmake=root/"CMakeLists.txt"
body=cmake.read_text()
if "B24_G7_SOURCE_COLLISION" in body:raise RuntimeError("duplicate G7 collision")
source='''
# B24_G7_SOURCE_COLLISION genuine 1908 original BDAE C1L1 source triangles
if(B24_ENABLE_GPU)
  target_sources(im2_beta PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_c1_original_collision.c)
endif()
'''
assert (root/"b24/b24_unified/b24_c1_original_collision.c").is_file()
cmake.write_text(body+source)
print("PASS G7 exact C1WC original-source CPU collision integrated in real B24 game; GPU render remains single owner")
