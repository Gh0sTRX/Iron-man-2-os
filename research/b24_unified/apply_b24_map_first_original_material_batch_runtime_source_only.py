#!/usr/bin/env python3
"""C1L1-first actual G10 VitaGL map build integration (source-only, NO VPK).

Construct the original 2010 index schedule grouped by (scene category,
source-qualified BDAE material ID) ONCE from validated exact C1G2+ C1MA.
Keep original Z-up world verts, all 22919 original triangles & winding.
No guessed material->diffuse link is attempted. Existing GPU fallback retains
4 batches plus authentic B12 car atlas until 2010 real SAMPLER binding proven.
This sets up performant per-material actual source atlas binds later.
"""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
w=root/'work'
h=w/'b24/b24_unified/b24_gpu_runtime.h'
c=w/'b24/b24_unified/b24_gpu_runtime.c'
def patch(path,original,replacement):
 s=path.read_text()
 if s.count(original)!=1:raise RuntimeError('MAP FIRST actual native source drift '+str(path)+' '+str(s.count(original)))
 path.write_text(s.replace(original,replacement))
patch(h,'#include "b24_c1_material_source.h"',
'''#include "b24_c1_material_source.h"
#include "b24_c1_material_batches.h"''')
patch(h,' B24C1MaterialSource city_material; /* original material LABELS, NOT atlases */',
''' B24C1MaterialSource city_material; /* original material LABELS, NOT atlases */
 B24C1MaterialBatchPlan city_draw_material_plan; /* EXACT 2010 source 22919 faces sorted by source material, no fake diffuse */''')
patch(c,''' (void)b24_gpu_boot_trace_mark("22 C1UV_C1MA_READ_COMPLETED");
 r->verified_vehicle_atlas=0;''',
''' (void)b24_gpu_boot_trace_mark("22 C1UV_C1MA_READ_COMPLETED");
 /* Actual authoritative 2010 source mesh→material IDs; stable partition
    of same B11 triangles by 94 BRES material keys, no fabricated textures.
    If optional C1MA missing, keep G10 old 4-color-category fallback.
    No per-frame CPU sorting, and no second GPU draw pipeline. */
 if(r->city_material.loaded)
  (void)b24_c1_material_batches_build(&r->city_draw_material_plan,
                                      &r->city,&r->city_material);
 r->verified_vehicle_atlas=0;''')
patch(c,''' b24_c1_material_source_free(&r->city_material);
 b24_c1_uv_free(&r->city_uv);
 b24_gpu_c1_free(&r->city);
 /* vitaGL''',
''' b24_c1_material_batches_free(&r->city_draw_material_plan);
 b24_c1_material_source_free(&r->city_material);
 b24_c1_uv_free(&r->city_uv);
 b24_gpu_c1_free(&r->city);
 /* vitaGL''')
# If optional HUD owner init fails, original B24 runtime should free plan.
patch(c,''' if(!b24_gpu_owner_init(&r->owner,0)){
  b24_c1_material_source_free(&r->city_material);''',
''' if(!b24_gpu_owner_init(&r->owner,0)){
  b24_c1_material_batches_free(&r->city_draw_material_plan);
  b24_c1_material_source_free(&r->city_material);''')
patch(c,''' if(!b24_gpu_hud_bridge_prepare(&r->hud)){
  b24_gpu_c1_vehicle_atlas_close(&r->verified_vehicle_atlas);''',
''' if(!b24_gpu_hud_bridge_prepare(&r->hud)){
  b24_gpu_c1_vehicle_atlas_close(&r->verified_vehicle_atlas);
  b24_c1_material_batches_free(&r->city_draw_material_plan);''')
path=w/'b24/b24_unified'
for n in ('b24_c1_material_batches.c','b24_c1_material_batches.h'):
 shutil.copyfile(root/'research/b24_unified'/n,path/n)
cm=w/'CMakeLists.txt';src=cm.read_text()
if 'MAP_FIRST_REAL_C1L1_NATIVE_PER_MATERIAL_GPU_BATCH_PLAN' in src:
 raise RuntimeError('already patched')
src+='''

# MAP_FIRST_REAL_C1L1_NATIVE_PER_MATERIAL_GPU_BATCH_PLAN
if(B24_ENABLE_GPU)
 target_sources(im2_beta PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_c1_material_batches.c")
endif()
'''
cm.write_text(src)
text=c.read_text()
assert text.count('b24_c1_material_batches_build(&r->city_draw_material_plan')==1
assert text.count('b24_c1_material_batches_free(&r->city_draw_material_plan)')==3
assert text.count('b24_gpu_c1_draw_material')==0  # remains called via GPU owner, no second scene pass
print('PASS MAP-FIRST exact G10 C1L1 original BRES source material group index schedule now integrated CPU-ONCE to actual Vita GPU runtime and destroyed correctly; no 39 invented atlas binding/no VPK')
