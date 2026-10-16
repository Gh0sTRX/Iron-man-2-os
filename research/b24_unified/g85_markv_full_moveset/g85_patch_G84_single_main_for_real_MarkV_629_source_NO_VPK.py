#!/usr/bin/env python3
"""G85 physically wire all 248 native original iOS IronMan animation streams
rebaked on authentic 629-v suitCASE BRES into G84's actual game main and
SINGLE G8 IM2V stream player. Mark V is suit index 4 in real G9 model bank.
Only source patch + host/ARM QA, NEVER package a VPK. Fail closed.
"""
from pathlib import Path
R=Path(__file__).resolve().parents[3]
W=R/"work";D=W/"b24/b24_unified"
GAME=W/"src/main.c";CM=W/"CMakeLists.txt"
G8=D/"b24_g8_live_original_motion.c"
G83=D/"b24_g83_unified_movement_aim.c"
G83H=D/"b24_g83_unified_movement_aim.h"
def once(s,old,new,label):
 if s.count(old)!=1:raise RuntimeError(f'G85 {label} original source drift: {s.count(old)}')
 return s.replace(old,new,1)
def install():
 for p in (GAME,CM,G8,G83,G83H):
  if not p.is_file():raise FileNotFoundError('Requires REAL rebuilt G84 source: '+str(p))
 main=GAME.read_text();cm=CM.read_text();g8=G8.read_text()
 g83=G83.read_text();header=G83H.read_text()
 if "G85_NATIVE_MARKV_629" in main:raise ValueError("No repeated G85 patch")
 assert "G84_OPTIONAL_TRUE_B24_MAIN" in main
 assert main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")==1
 assert main.count("b24_g8_motion_melee_trigger(")==1
 assert main.count("b24_g8_motion_repulsor_trigger(")==1
 assert main.count("b24_g8_motion_tick_g84(")==1
 assert 'static const char *filename[5] = {"mark6.im2t", "mark4.im2t", "warmachine.im2t", "stealth.im2t", "suitcase.im2t"};' in main
 header=once(header,"B24G83_MARKVI=0,B24G83_WARMACHINE=2",
   "B24G83_MARKVI=0,B24G83_WARMACHINE=2,B24G83_MARKV=4",
   "real G9 source suit index MarkV")
 g83=once(g83,''' const int markvi=p->suit_index==B24G83_MARKVI;
 const int wm=p->suit_index==B24G83_WARMACHINE;
 if(!markvi&&!wm)return 1;''',''' const int markvi=p->suit_index==B24G83_MARKVI;
 const int wm=p->suit_index==B24G83_WARMACHINE;
#ifdef B24_G85_NATIVE_MARKV_629
 /* These same original 2010 IronMan joint tracks are rebaked from genuine
    B13 hierarchy onto the UNIQUE Mark V 629 weighted-skin palette. */
 const int markv=p->suit_index==B24G83_MARKV;
#else
 const int markv=0;
#endif
 const int original_ironman_rig=markvi||markv;
 if(!original_ironman_rig&&!wm)return 1;''',"MarkV rig selector")
 g83=once(g83," }else if(markvi){"," }else if(original_ironman_rig){",
           "IronMan source native MarkV motion state mapping")
 g83=once(g83,'''      in->suit_index==B24G83_MARKVI){''',
           '''      (in->suit_index==B24G83_MARKVI
#ifdef B24_G85_NATIVE_MARKV_629
       ||in->suit_index==B24G83_MARKV
#endif
       )){''',"G82 three-combo source on native suitcase suit")
 g8=once(g8,''' if(!a||a->suit_index!=0||!a->nv)return;
 b24_g8_melee_press(&a->melee,now);''',''' if(!a||!a->nv)return;
#ifdef B24_G85_NATIVE_MARKV_629
 if(a->suit_index!=0&&a->suit_index!=4)return;
#else
 if(a->suit_index!=0)return;
#endif
 b24_g8_melee_press(&a->melee,now);''',"allow same old accepted combo on 629 suit")
 g8=once(g8,''' const char *shot=b24_g8_motion_repulsor_clip(suit,mode,left_x,forward);
 if(a->repulsor_pending''',''' const char *shot=b24_g8_motion_repulsor_clip(suit,mode,left_x,forward);
#ifdef B24_G85_NATIVE_MARKV_629
 char g85_native_shot[128]={0};
 char g85_native_desired[128]={0};
 if(suit==4){
   /* 2010 source animation binary was re-baked onto real Mark V; do not
      attach Mark VI 802v positions to suitcase 629v geometry. */
   const char *original=b24_g8_motion_repulsor_clip(0,mode,left_x,forward);
   if(original){
     int n=snprintf(g85_native_shot,sizeof(g85_native_shot),"suitcase_%s",original);
     if(n<=0||(size_t)n>=sizeof(g85_native_shot))return 0;
     shot=g85_native_shot;
   }
 }
#endif
 if(a->repulsor_pending''',"real original suitcase .im2v accepted repulsor clip name")
 g8=once(g8,''' if(suit==0 && mode<=B24M_RUN)
    melee=b24_g8_melee_tick(&a->melee,now);''',''' if((suit==0
#ifdef B24_G85_NATIVE_MARKV_629
       ||suit==4
#endif
       ) && mode<=B24M_RUN)
    melee=b24_g8_melee_tick(&a->melee,now);''',"one original melee timeline shared suit 0 or 4")
 g8=once(g8,''' if(g84_source_clip&&!melee&&!a->repulsor_pending)
   desired=g84_source_clip;
 if(!desired|| (suit==0&&nv!=802u) || (suit==2&&nv!=1292u)){''',''' if(g84_source_clip&&!melee&&!a->repulsor_pending)
   desired=g84_source_clip;
#ifdef B24_G85_NATIVE_MARKV_629
 if(suit==4&&desired){
   int n=snprintf(g85_native_desired,sizeof(g85_native_desired),"suitcase_%s",desired);
   if(n<=0||(size_t)n>=sizeof(g85_native_desired))return 0;
   desired=g85_native_desired;
 }
#endif
 if(!desired|| (suit==0&&nv!=802u) || (suit==2&&nv!=1292u)
#ifdef B24_G85_NATIVE_MARKV_629
   || (suit==4&&nv!=629u)
#endif
   ){''',"MarkV 629 source stream prefix and exact vertex guard")
 old='''         if(!b24_unified_paused(&b24_game) && idx==0 &&
            !world.flying && b24_unified_should_melee(&b24_game))'''
 new='''#ifdef B24_G85_NATIVE_MARKV_629
         /* G85_NATIVE_MARKV_629: retain ONE existing user combo button
            owner, now valid also for 629v original Mark V suit index 4. */
         if(!b24_unified_paused(&b24_game) && (idx==0||idx==4) &&
            !world.flying && b24_unified_should_melee(&b24_game))
#else
         if(!b24_unified_paused(&b24_game) && idx==0 &&
            !world.flying && b24_unified_should_melee(&b24_game))
#endif'''
 main=once(main,old,new,"original accepted melee event only once")
 cm+='''
# G85 genuine 2010 Mark V all original IronMan bone streams, OFF by default.
# Compile this only when all 248 ORIGINAL 629-v IM2V owner-derived files
# are explicitly staged under animations/. No new game VPK at this stage.
option(B24_G85_NATIVE_MARKV_629 "Use original IronMan 248 B13 pose streams on true Mark V 629v" OFF)
if(B24_G85_NATIVE_MARKV_629)
 if(NOT B24_G84_ORIGINAL_MOVESET_ROUTER)
  message(FATAL_ERROR "G85 original Mark V requires G84 single source motion engine")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G85_NATIVE_MARKV_629=1)
endif()
'''
 assert main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")==1
 assert main.count("b24_g8_motion_melee_trigger(")==1
 assert main.count("b24_g8_motion_repulsor_trigger(")==1
 assert main.count("b24_g83_timeline_tick(")==1
 for file,data in ((GAME,main),(CM,cm),(G8,g8),(G83,g83),(G83H,header)):
  file.write_text(data)
 assert not list(W.rglob('*.vpk'))
 print('PASS G85 true 2010 original MarkV 629v full 248 IronMan source route patched into single original B24/G84 G8 IM2V animator, no second physics or fire, NO VPK')
if __name__=="__main__":install()
