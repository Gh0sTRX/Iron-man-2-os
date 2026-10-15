#!/usr/bin/env python3
"""Real G10/G11 VitaGL app: original 2010 BRES C1MT 94 shaders to 39 real C1TX.

Prereq: prior proven apply_b24_map_first_original_material_batch_runtime_source_only
on assembled G10 original work/*. No VPK, no fabricated surfaces, no flight
combat additions. One GPU world draw per frame with index-sorted exact source
triangles, real 2010 source texture bank optional fail-closed to old renderer.

C1MT and c1l1_*.c1tx must be staged into app0:maps/ by a FUTURE user test
build from user's original 2010 IPA. This script generates only SOURCE.
"""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];w=root/'work'
src=w/'b24/b24_unified'
def patch(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:
  raise RuntimeError('G12 actual app source drift %d %s %s'%(s.count(a),str(path),a[:90]))
 path.write_text(s.replace(a,b))
h=src/'b24_gpu_runtime.h';c=src/'b24_gpu_runtime.c';owner=src/'b24_gpu_owner.h'
patch(h,'#include "b24_c1_material_batches.h"',
'''#include "b24_c1_material_batches.h"
#include "b24_c1_2010_diffuse_bank.h"
#include "b24_gpu_c1_2010_diffuse_upload.h"''')
patch(h,''' B24C1MaterialBatchPlan city_draw_material_plan; /* EXACT 2010 source 22919 faces sorted by source material, no fake diffuse */''',
''' B24C1MaterialBatchPlan city_draw_material_plan; /* original 22919 triangle stable material buckets */
 B24C1OriginalDiffuseBank city_original_diffuse; /* real owner 2010 shader88->property60->20B TGA→C1TX */
 int city_textured_ready; /* ONLY if source-authored original bank truly loaded + vitaGL images uploaded */''')
patch(owner,'#include "b24_c1_gpu_uv.h"',
'''#include "b24_c1_gpu_uv.h"
#include "b24_c1_material_batches.h"
#include "b24_c1_2010_diffuse_bank.h"''')
patch(owner,'''int b24_gpu_owner_scene_material(B24GpuOwner *owner,const B24GpuC1Mesh *scene,''',
'''int b24_gpu_owner_scene_original_2010(B24GpuOwner *owner,
 const B24GpuC1Mesh *scene,const B24C1UV *uv,
 const B24C1MaterialBatchPlan *plan,const B24C1OriginalDiffuseBank *bank);
int b24_gpu_owner_scene_material(B24GpuOwner *owner,const B24GpuC1Mesh *scene,''')
patch(c,''' r->verified_vehicle_atlas=0; /* B12 original atlas not packaged yet */''',
''' /* G12 source-authored 2010 sampler bank optional, never guessed ordinal.
    Native C1MT generated from true BRES shaders 88B→props60B→TGA20B.
    C1G2 source 22919 faces/UVs remain untouched, G10 fallback preserved. */
 if(r->city_draw_material_plan.ready && r->city_uv.loaded)
   (void)b24_c1_2010_diffuse_bank_load(&r->city_original_diffuse,
                              "app0:maps/C1L1_environment.c1mt");
 r->verified_vehicle_atlas=0; /* fallback original B12 atlas only */''')
patch(c,''' if(r->city_uv.loaded)
  (void)b24_gpu_c1_vehicle_atlas_open(&r->verified_vehicle_atlas,
                                      "app0:maps/C1L1_Vehicles.c1tx");''',
''' if(r->city_uv.loaded && r->city_draw_material_plan.ready &&
    r->city_original_diffuse.loaded)
  r->city_textured_ready=b24_gpu_c1_2010_diffuse_upload(
      &r->city_original_diffuse,&r->city_draw_material_plan,"app0:maps");
 if(r->city_uv.loaded && !r->city_textured_ready)
  (void)b24_gpu_c1_vehicle_atlas_open(&r->verified_vehicle_atlas,
                                      "app0:maps/C1L1_Vehicles.c1tx");''')
patch(c,''' if(!b24_gpu_owner_scene_material(&r->owner,&r->city,
            r->city_uv.loaded?&r->city_uv:NULL,
            r->verified_vehicle_atlas))return 0;''',
''' /* Exactly ONE true 2010 world scene draw: authenticated material bank
    takes over only with loaded real GPU source textures. Otherwise the
    previously tested G10 color geometry / original cars still works. */
 int city_scene_ok=0;
 if(r->city_textured_ready)
  city_scene_ok=b24_gpu_owner_scene_original_2010(
    &r->owner,&r->city,&r->city_uv,
    &r->city_draw_material_plan,&r->city_original_diffuse);
 else
  city_scene_ok=b24_gpu_owner_scene_material(&r->owner,&r->city,
    r->city_uv.loaded?&r->city_uv:NULL,r->verified_vehicle_atlas);
 if(!city_scene_ok)return 0;''')
patch(c,'''  b24_gpu_c1_vehicle_atlas_close(&r->verified_vehicle_atlas);
  b24_c1_material_batches_free(&r->city_draw_material_plan);''',
'''  b24_gpu_c1_2010_diffuse_release(&r->city_original_diffuse);
  b24_c1_2010_diffuse_bank_reset(&r->city_original_diffuse);
  b24_gpu_c1_vehicle_atlas_close(&r->verified_vehicle_atlas);
  b24_c1_material_batches_free(&r->city_draw_material_plan);''')
patch(c,''' b24_gpu_c1_vehicle_atlas_close(&r->verified_vehicle_atlas);
 b24_c1_material_batches_free(&r->city_draw_material_plan);
 b24_c1_material_source_free(&r->city_material);''',
''' b24_gpu_c1_2010_diffuse_release(&r->city_original_diffuse);
 b24_c1_2010_diffuse_bank_reset(&r->city_original_diffuse);
 b24_gpu_c1_vehicle_atlas_close(&r->verified_vehicle_atlas);
 b24_c1_material_batches_free(&r->city_draw_material_plan);
 b24_c1_material_source_free(&r->city_material);''')
for fname in (
 'b24_c1_2010_diffuse_bank.h','b24_c1_2010_diffuse_bank.c',
 'b24_gpu_c1_2010_diffuse_upload.h','b24_gpu_c1_2010_diffuse_upload.c',
 'b24_gpu_c1_2010_textured_material.h',
 'b24_gpu_c1_2010_textured_material_vitagl.c',
 'b24_gpu_owner_2010_material.c'):
 shutil.copyfile(root/'research/b24_unified'/fname,src/fname)
cm=w/'CMakeLists.txt';cs=cm.read_text()
if 'G12_SOURCE_2010_NATIVE_FULL_C1L1_MATERIAL_ATLAS_BRES_PER_TRI_GPU' in cs:raise RuntimeError('G12 already applied')
cs+='''

# G12_SOURCE_2010_NATIVE_FULL_C1L1_MATERIAL_ATLAS_BRES_PER_TRI_GPU
if(B24_ENABLE_GPU)
 target_sources(im2_beta PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_c1_2010_diffuse_bank.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_gpu_c1_2010_diffuse_upload.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_gpu_c1_2010_textured_material_vitagl.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_gpu_owner_2010_material.c")
endif()
'''
cm.write_text(cs)
data=c.read_text()
assert data.count('b24_gpu_owner_scene_original_2010(')==1
assert data.count('b24_gpu_owner_scene_material(')==1
assert data.count('b24_gpu_owner_scene_original_2010')==1
assert data.count('b24_gpu_c1_2010_diffuse_upload(')==1
assert data.count('b14_world_tick(')==0 # single CPU physics remains in main.c, unchanged
print('PASS G12 REAL ORIGINAL 2010 C1L1 shader material sampler 94-authored-world material VitaGL single scene GPU draw wired to G10; host and Vita ARM compile next, no owner IPA or VPK published')
