#!/usr/bin/env python3
"""G84 source-only real G75/G70/G9 B24 main loop integration: one B14
physics owner, one G8 original IM2V pose owner and existing B16 fire source.
Enable by explicit CMake flag only AFTER further original-combat validation.
NEVER create a new game VPK. Fail closed if old callsite changes.
"""
from pathlib import Path
R=Path(__file__).resolve().parents[3]
W=R/"work";D=W/"b24/b24_unified"
GAME=W/"src/main.c";CM=W/"CMakeLists.txt"
G8C=D/"b24_g8_live_original_motion.c"
G8H=D/"b24_g8_live_original_motion.h"
def rep(src,needle,sub,label):
 if src.count(needle)!=1:raise ValueError(f"G84 {label} source changed: {src.count(needle)}")
 return src.replace(needle,sub,1)
def apply():
 for f in (GAME,CM,G8C,G8H):
  if not f.exists():raise FileNotFoundError(f)
 game=GAME.read_text();cm=CM.read_text()
 g8=G8C.read_text();h=G8H.read_text()
 assert "G75_SOURCE_ONLY_GAMEPLAY_RECOVERY" in game
 assert game.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")==1
 assert "G84_OPTIONAL_TRUE_B24_MAIN" not in game
 assert game.count("b24_g8_motion_melee_trigger(")==1
 assert game.count("b24_g8_motion_repulsor_trigger(")==1
 h=rep(h,"#endif",'''/* G84 single real G8 original IM2V owner, optional source route */
int b24_g8_motion_tick_g84(B24G8LiveOriginalMotion *a,const char *dir,
 void *vertices,size_t stride,size_t nv,int suit,B24MotionStage mode,
 float left_x,float forward,uint32_t now,const char *source_clip);
#endif''',"G8 header")
 g8=rep(g8,"int b24_g8_motion_tick(B24G8LiveOriginalMotion *a,const char *dir,",
    "int b24_g8_motion_tick_g84(B24G8LiveOriginalMotion *a,const char *dir,",
    "G8 function")
 g8=rep(g8,"uint32_t now){\n if(!a||!dir||!vertices",
    "uint32_t now,const char *g84_source_clip){\n if(!a||!dir||!vertices",
    "G8 argument")
 g8=rep(g8," if(!desired|| (suit==0&&nv!=802u) || (suit==2&&nv!=1292u)){",
  ''' /* G84 only selects source animation when G8 native melee and B16's
  already accepted repulsor have NOT taken ownership. */
 if(g84_source_clip&&!melee&&!a->repulsor_pending)desired=g84_source_clip;
 if(!desired|| (suit==0&&nv!=802u) || (suit==2&&nv!=1292u)){''',
 "G8 clip owner priority")
 g8+='''
/* Keep old API for all other projects with byte-identical routing. */
int b24_g8_motion_tick(B24G8LiveOriginalMotion *a,const char *dir,
 void *vertices,size_t stride,size_t nv,int suit,B24MotionStage mode,
 float left_x,float forward,uint32_t now){
 return b24_g8_motion_tick_g84(a,dir,vertices,stride,nv,suit,mode,
                               left_x,forward,now,NULL);
}
'''
 game=rep(game,'#include "../b24/b24_unified/b24_g75_source_capsule.h"',
 '''#include "../b24/b24_unified/b24_g75_source_capsule.h"
#ifdef B24_G84_ORIGINAL_MOVESET_ROUTER
#include "../b24/b24_unified/b24_g83_authentic_timed_router.h"
/* G84_OPTIONAL_TRUE_B24_MAIN */
static B24G83Timeline g84_time={0};
static int g84_previous_suit=-1;
static B24G83Dir g84_last_flight_dir=B24G83_DIR_IDLE;
#endif''',"GPU include")
 old='''          if(!b24_g8_motion_tick(&b24_original_motion,
                "app0:animations",
                model.vertices,sizeof(IM2Vertex),model.nv,idx,
                original_stage,move_x,move_y,(uint32_t)now)){
             running=0;break;
          }'''
 new='''#ifdef B24_G84_ORIGINAL_MOVESET_ROUTER
          /* B14 ticked ONCE before this point; G8 is sole original
             source IM2V animator. Existing G8 melee and accepted B16
             repulsor have priority; NO second weapon event is created.
             L aims in this PROTOTYPE controller; original iOS L semantics
             still need touchHLE validation. */
          if(g84_previous_suit!=idx){
             b24_g83_timeline_reset(&g84_time);
             g84_last_flight_dir=B24G83_DIR_IDLE;
             g84_previous_suit=idx;
          }
          B24G83Input g84_input={0};
          g84_input.suit_index=idx;
          g84_input.motion=!world.flying?B24G83_GROUND:
             world.flight_stage>=3?B24G83_RUSH:
             world.flight_stage==2?B24G83_FLIGHT:B24G83_HOVER;
          g84_input.aim=(b24_buttons&IM2_BT_L)&&
             combat.mode==B16_REPULSOR?B24G83_AIM_HAND:B24G83_AIM_NONE;
          g84_input.axis_x=clip(move_x,-1.f,1.f);
          g84_input.axis_y=clip(move_y,-1.f,1.f);
          g84_input.run=ground_run;
          g84_input.previous_flight_dir=g84_last_flight_dir;
          g84_input.accepted_weapon_event=0; /* sole accepted B16->G8 */
          g84_input.grounded_contact_verified=0;
          B24G83Selection g84_route={0};
          if(!b24_g83_timeline_tick(&g84_time,NULL,(uint32_t)now,
                &g84_input,&g84_route)){running=0;break;}
          g84_last_flight_dir=world.flying?g84_route.direction:B24G83_DIR_IDLE;
          if(!b24_g8_motion_tick_g84(&b24_original_motion,
                "app0:animations",model.vertices,sizeof(IM2Vertex),
                model.nv,idx,original_stage,move_x,move_y,
                (uint32_t)now,g84_route.stem)){running=0;break;}
#else
'''+old+'''
#endif'''
 game=rep(game,old,new,"actual real B24 G8 frame call")
 assert game.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")==1
 assert game.count("b24_g8_motion_melee_trigger(")==1
 assert game.count("b24_g8_motion_repulsor_trigger(")==1
 assert game.count("b24_g83_timeline_tick(")==1
 originals=[
 ("g76_original_combat","b24_g76_original_native_damage_math.c"),
 ("g76_original_combat","b24_g76_original_native_damage_math.h"),
 ("g77_original_weapon_db","b24_g77_melee_source_radius.c"),
 ("g77_original_weapon_db","b24_g77_melee_source_radius.h"),
 ("g82_original_combat","b24_g82_original_combat_coordinator.c"),
 ("g82_original_combat","b24_g82_original_combat_coordinator.h"),
 ("g83_full_motion_aim","b24_g83_unified_movement_aim.c"),
 ("g83_full_motion_aim","b24_g83_unified_movement_aim.h"),
 ("g83_full_motion_aim","b24_g83_authentic_timed_router.c"),
 ("g83_full_motion_aim","b24_g83_authentic_timed_router.h"),
 ("g83_full_motion_aim","b24_g83_authentic_2010_source_durations.h")]
 files={}
 for folder,name in originals:
  file=R/"research/b24_unified"/folder/name
  source=file.read_text()
  for p in ("../g82_original_combat/","../g76_original_combat/",
            "../g77_original_weapon_db/","../"):
   # Narrow: don't rewrite other potential relative includes needlessly.
   pass
  source=source.replace('#include "../b24_g8_melee_source_chain.h"',
                        '#include "b24_g8_melee_source_chain.h"')
  for directory in ("g82_original_combat","g76_original_combat",
                    "g77_original_weapon_db"):
   source=source.replace('#include "../'+directory+'/',
                         '#include "')
  files[name]=source
 cm+='''
# G84 source-only source integration: opt-in, DEFAULT OFF.
option(B24_G84_ORIGINAL_MOVESET_ROUTER "G83 authored move selector through sole G8 source animator" OFF)
if(B24_G84_ORIGINAL_MOVESET_ROUTER)
 if(NOT B24_ENABLE_GPU)
  message(FATAL_ERROR "G84 requires old G8 original VitaGL animation owner")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G84_ORIGINAL_MOVESET_ROUTER=1)
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g76_original_native_damage_math.c"
  "b24/b24_unified/b24_g77_melee_source_radius.c"
  "b24/b24_unified/b24_g82_original_combat_coordinator.c"
  "b24/b24_unified/b24_g83_unified_movement_aim.c"
  "b24/b24_unified/b24_g83_authentic_timed_router.c")
endif()
'''
 for filename,body in files.items():(D/filename).write_text(body)
 GAME.write_text(game);CM.write_text(cm);G8C.write_text(g8);G8H.write_text(h)
 assert not list(W.rglob("*.vpk"))
 print("PASS G84 real G75 G68 source & live B24 main G83 optional route wired to ONE G8 source pose and B14 movement, B16 combat preserved, NO VPK")
if __name__=="__main__":apply()
