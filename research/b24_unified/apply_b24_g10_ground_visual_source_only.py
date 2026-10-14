#!/usr/bin/env python3
"""G10 G9-real-hardware grounded suit feet fix, original C1L1 source only.

Must run AFTER all G9/ B14/B16 source patches. Does not alter C1WC original
wall geometry or create a synthetic floor. No new GPU pass; shift camera and
suit render root together in same native VitaGL stage using actual support
face Z and genuine armor model minimum. Base G9 untouched.
"""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];work=root/"work"
p=work/"b24/b24_unified/b24_gpu_runtime.c"
s=p.read_text()
def rep(a,b):
 global s
 if s.count(a)!=1:raise RuntimeError("G10 GPU ground source drift: "+str(s.count(a))+" "+a[:110])
 s=s.replace(a,b)
rep('#include "b24_gpu_boot_trace.h"',
'''#include "b24_gpu_boot_trace.h"
#include "b24_g10_original_foot_contact.h"''')
rep(''' float shoulder=1.f-g->camera_base.shoulder_to_chase;''',
''' /* The original 2010 C1L1 ground polygons are near Z=-.2473 at spawn.
    Previous G9 B14 target_z=0 put part of real armor below the visual road.
    Derive ONLY a visual rest adjustment from EXISTING original source
    C1G2 ground triangles (no fabricated plane or extra physics ticks).
    Keep both eye and target offset equal to preserve center reticle. */
 float g10_original_foot_dz=0.f;
 (void)b24_g10_foot_visual_source_offset(&r->city,m,c,
                                          &g10_original_foot_dz);
 cam.eye.z+=g10_original_foot_dz;
 cam.target.z+=g10_original_foot_dz;
 float shoulder=1.f-g->camera_base.shoulder_to_chase;''')
rep(''' r->frame_pose=(B24GpuSuitPose){c->player_x,c->player_y,c->player_z,
                 c->player_heading,g->visual_root.visual_pitch_rad,
                 g->visual_root.visual_roll_rad};''',
''' r->frame_pose=(B24GpuSuitPose){c->player_x,c->player_y,
                 c->player_z+g10_original_foot_dz,
                 c->player_heading,g->visual_root.visual_pitch_rad,
                 g->visual_root.visual_roll_rad};''')
p.write_text(s)
dst=work/"b24/b24_unified"
for f in ("b24_c1_true_source_floor.h","b24_c1_true_source_floor.c",
          "b24_g10_original_foot_contact.h","b24_g10_original_foot_contact.c"):
 shutil.copyfile(root/"research/b24_unified"/f,dst/f)
cmake=work/"CMakeLists.txt"
body=cmake.read_text()
needle="# G10_ORIGINAL_2010_C1L1_GROUNDED_ARMOR_VISUAL_SURFACE"
if needle in body:raise RuntimeError("double G10 scene support")
body+='''
# G10_ORIGINAL_2010_C1L1_GROUNDED_ARMOR_VISUAL_SURFACE
if(B24_ENABLE_GPU)
 target_sources(im2_beta PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_c1_true_source_floor.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_g10_original_foot_contact.c")
endif()
'''
cmake.write_text(body)
assert s.index('b24_g10_foot_visual_source_offset(')<s.index('b24_gpu_camera_matrices(')
assert 'g10_original_foot_dz' in s
print("PASS G10 real original 3280 triangle C1L1 ground source floor -> shared VitaGL eye/suit root; grounded only, no invented physics floors; G9 baseline untouched")
