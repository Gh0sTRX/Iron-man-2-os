#!/usr/bin/env python3
"""G277 isolated host unit fixture to prove instrumentation-only patch:
 No fake original game artifacts and NEVER a real Vita hardware result.
 Uses the checked-in ORIGINAL-sourced G75 conservative collision C, with
 only a macro adapter for the G159 real source floor alias. Verifies
 wall, absent floor, unsupported step, successful airborne sweep; all
 counters observational and no movement rules changed.
"""
from __future__ import annotations
import argparse,shutil,subprocess,tempfile
from pathlib import Path
import importlib.util

def run(root:Path):
 here=Path(__file__).resolve().parent
 main_py=here/"g277_install_original_G75_wall_floor_step_reject_probe_after_G229_NO_VPK.py"
 spec=importlib.util.spec_from_file_location("g277_source_patch",main_py)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 with tempfile.TemporaryDirectory(prefix="g277_true_collision_fixture_") as temp:
  fake=Path(temp);w=fake/"work";game=w/"b24/b24_unified"
  game.mkdir(parents=True)
  source=(root/"research/b24_unified/g75_device_qa/b24_g75_source_capsule.c").read_text()
  # Original G159 aliases genuine G66C support; isolated fixture uses
  # this EXACT fallback only. Full game G159 source path is used by G171.
  source=source.replace('#include "b24_g75_source_capsule.h"',
    '#include "b24_g75_source_capsule.h"\n'
    '#define g159_authoritative_first_native_then_source_road b24_g74_near_original_floor',1)
  source=source.replace("if(!b24_g74_near_original_floor(world,nx,ny,z,&h))continue;",
    "if(!g159_authoritative_first_native_then_source_road(world,nx,ny,z,&h))continue;",1)
  (game/"b24_g75_source_capsule.c").write_text(source)
  (w/"src").mkdir()
  (w/"src/main.c").write_text(
    '#include "../b24/b24_unified/b24_g227_vita_ground_world_render_probe.h"\n'
    'B24G229WalkWindow B24_G227_WALK_ROOT_DIAGNOSTIC;\n'
    'void fake(void){b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);\n'
    'b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx);\n'
    'b24_g75_capsule_reconcile(&city,0,0,0,0,0,0,0,.35f,2.24f,&x,&y,&z);\n'
    'b24_g227_probe.frame_num=(uint32_t)frame;}\n')
  (w/"CMakeLists.txt").write_text(
   'option(B24_G159_ROAD_FLOOR_CANDIDATE "source-only" ON)\n'
   'option(B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL "source-only" ON)\n')
  mod.patch(fake)
  patched=(game/"b24_g75_source_capsule.c").read_text()
  original=(root/"research/b24_unified/g75_device_qa/b24_g75_source_capsule.c").read_text()
  assert patched.count("b24_g75_capsule_reconcile(")==original.count("b24_g75_capsule_reconcile(")==1
  assert patched.count("g277_last.candidate_accepted") == 1
  assert not list(fake.rglob("*.vpk"))
  c='''#include "b24_g75_source_capsule.h"
#include "b24_g277_real_c1l1_ground_reject_reasons.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static void one(B24C1OriginalCollision *city,int grounded,
   B24G277CollisionReasons *result,float *endx){
 float x=.08f,y=0.f,z=0.f;
 assert(b24_g75_capsule_reconcile(city,0.f,0.f,0.f,.08f,0.f,0.f,
   grounded,.35f,2.24f,&x,&y,&z));
 assert(isfinite(x)&&isfinite(y)&&isfinite(z));
 *result=b24_g277_last_collision_reasons();
 *endx=x;
}
int main(void){
 B24C1OriginalCollision city={0};
 B24G277CollisionReasons q={0};float x=0.f;
 city.ready=1;
 one(&city,1,&q,&x);
 assert(q.candidate_no_source_support>=3u && q.candidate_accepted==0u);
 assert(fabsf(x)<.001f);
 one(&city,0,&q,&x);
 assert(q.candidate_no_source_support==0u&&q.candidate_accepted>=1u);
 assert(fabsf(x-.08f)<.001f);
 B24C1OriginalCollisionFace face={0};
 city.faces=&face;city.count=1u;
 const float original_wall[9]={.05f,-1.f,-1.f,.05f,1.f,-1.f,.05f,0.f,3.f};
 for(int i=0;i<9;i++)face.xyz[i]=original_wall[i];
 face.wall=1;face.minx=face.maxx=.05f;
 face.miny=-1.f;face.maxy=1.f;face.minz=-1.f;face.maxz=3.f;
 one(&city,1,&q,&x);
 assert(q.candidate_wall_reject>=3u&&q.candidate_accepted==0u);
 assert(fabsf(x)<.001f);
 const float low_floor[9]={-5.f,-5.f,-.4f,5.f,-5.f,-.4f,0.f,5.f,-.4f};
 for(int i=0;i<9;i++)face.xyz[i]=low_floor[i];
 face.wall=0;face.minx=-5.f;face.maxx=5.f;
 face.miny=-5.f;face.maxy=5.f;face.minz=face.maxz=-.4f;
 one(&city,1,&q,&x);
 assert(q.candidate_unsupported_step_height>=3u&&q.candidate_accepted==0u);
 assert(fabsf(x)<.001f);
 puts("G277 HOST FIXTURE PASS wall/floor/step/flight diagnostics. NOT original-world hardware QA, no VPK.");
 return 0;
}'''
  smoke=fake/"g277_fixture.c";smoke.write_text(c)
  exe=fake/"g277_fixture"
  command=["cc","-std=c11","-O2","-Wall","-Wextra","-Werror","-pedantic",
    "-DB24_G227_WALK_ROOT_DIAGNOSTIC=1",
    "-I",str(game),"-I",str(root/"research/b24_unified"),
    "-I",str(root/"research/b24_unified/g75_device_qa"),
    str(smoke),str(game/"b24_g75_source_capsule.c"),
    str(root/"research/b24_unified/b24_gpu_g68_collision.c"),
    str(root/"research/b24_unified/b24_c1_original_collision.c"),
    "-lm","-o",str(exe)]
  subprocess.run(command,check=True)
  subprocess.run([str(exe)],check=True)
  print("G277 source patched branch behavior unchanged except read-only diagnostics, three failure conditions reproducible")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[3])
 args=p.parse_args();run(args.root)
