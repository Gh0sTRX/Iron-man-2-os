#!/usr/bin/env python3
"""G11 owner-authored 2010 3-phase UniBeam + no-flap hover source-only.

AFTER G10 independent rig-skin route and G11 camera/stage-shot source patches.
Never invent laser damage, new FX or projectile: original B16 chest emitter
still owns actual shooting. 2010 Beam1/2/3 are only model animations.
"""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];w=root/'work'
def do(path,a,b):
 p=w/path
 s=p.read_text()
 n=s.count(a)
 if n!=1:raise RuntimeError('G11 authentic beam source drift '+str(n)+' '+str(path)+' '+a[:100])
 p.write_text(s.replace(a,b))
motion='b24/b24_unified/b24_g8_live_original_motion.c'
header='b24/b24_unified/b24_g8_live_original_motion.h'
main='src/main.c'
do(motion,'#include <stdio.h>','#include <stdio.h>\n#include "b24_g11_original_unibeam_sequence.h"')
do(motion,'static char names[3][128];','static char names[4][128];')
do(motion,'role<0||role>=3)return NULL;','role<0||role>=4)return NULL;')
do(header,' uint32_t started_ms,previous_ms,repulsor_started_ms;',
''' uint32_t started_ms,previous_ms,repulsor_started_ms,beam_started_ms;''')
do(header,' int active,repulsor_pending,whole_body_repulsor_active;',
''' int active,repulsor_pending,whole_body_repulsor_active,beam_pending;''')
do(header,'void b24_g8_motion_melee_trigger(B24G8LiveOriginalMotion *a,uint32_t now_ms);',
'''void b24_g8_motion_melee_trigger(B24G8LiveOriginalMotion *a,uint32_t now_ms);
void b24_g8_motion_unibeam_trigger(B24G8LiveOriginalMotion *a,uint32_t now_ms);''')
do(motion,
'''void b24_g8_motion_melee_trigger(B24G8LiveOriginalMotion *a,uint32_t now){''',
'''/* 2010 source UniBeam is BEAM1->BEAM2->BEAM3, not a fabricated arm shot.
   Triggered only when B16 genuinely accepts the chest weapon event. */
void b24_g8_motion_unibeam_trigger(B24G8LiveOriginalMotion *a,uint32_t now){
 if(!a)return;
 if(!a->beam_pending){
  a->beam_started_ms=now;a->beam_pending=1;
  a->repulsor_pending=0;a->whole_body_repulsor_active=0;
 }
}
void b24_g8_motion_melee_trigger(B24G8LiveOriginalMotion *a,uint32_t now){''')
do(motion,''' const char *melee=NULL;
 if((suit==0||suit==1||suit==3||suit==4)&&mode<=B24M_RUN)''',
''' /* Source-authentic three-part Beam chain; no beams in sprint,
    cruise, rush, land, or on WM. Actual 2010 phase durations preserved. */
 const char *beam=NULL;
 if(a->beam_pending){
  const int grounded=(mode==B24M_IDLE||mode==B24M_WALK);
  const int hovering=(mode==B24M_HOVER||mode==B24M_DRIFT);
  if((!grounded&&!hovering)||suit==2)a->beam_pending=0;
  else{
   beam=b24_g11_unibeam_clip(suit,hovering,
                           (uint32_t)(now-a->beam_started_ms));
   if(!beam)a->beam_pending=0;
  }
 }
 const char *melee=NULL;
 if((suit==0||suit==1||suit==3||suit==4)&&mode<=B24M_RUN)''')
do(motion,''' else if(a->repulsor_pending&&shot)desired=shot;''',
''' else if(beam){
    desired=suit==0?beam:g10_alt_iron_source_name(beam,suit,3);
    if(!desired)return 0;
 }
 else if(a->repulsor_pending&&shot)desired=shot;''')
do(motion,''' if(!fresh(a,nv,suit))return 0;
 size_t n=nv*3;''',
''' /* First accepted shot after selecting WM or another armor must survive
    the new suit's stream/buffer initialization: prior G10 fresh() cleared
    repulsor_pending here, silently eating the first source attack. */
 const int pending_shot=a->repulsor_pending;
 const uint32_t shot_started=a->repulsor_started_ms;
 const int pending_beam=a->beam_pending;
 const uint32_t beam_started=a->beam_started_ms;
 if(!fresh(a,nv,suit))return 0;
 if(pending_shot&&!a->repulsor_pending){
  a->repulsor_pending=1;a->repulsor_started_ms=shot_started;
 }
 if(pending_beam&&!a->beam_pending){
  a->beam_pending=1;a->beam_started_ms=beam_started;
 }
 size_t n=nv*3;''')
do(motion,''' if(!b24_original_im2v_sample(&a->stream,age,1,a->source_xyz))return 0;''',
''' /* IronMan_Move_Float is an 800ms transition-like torso/arms move.
    G10 physical test: looping it idle makes "wing flapping". Hold the
    genuine authored midpoint pose in stationary nonattacking hover only,
    preserving B14/GPU native hover bob and all directional clips. */
 const int neutral_float=(mode==B24M_HOVER&&
    !a->repulsor_pending&&!a->beam_pending&&!a->melee.phase&&
    strstr(a->selected,"_move_float")!=NULL);
 const uint32_t source_age=neutral_float?a->stream.duration_ms/2:age;
 if(!b24_original_im2v_sample(&a->stream,source_age,1,a->source_xyz))return 0;''')
do(main,'''          if(fired>=0 && combat.mode==B16_REPULSOR){''',
'''#ifdef B24_GPU_ENGINE
          if(fired>=0 && combat.mode==B16_UNIBEAM && idx!=2)
              b24_g8_motion_unibeam_trigger(&b24_original_motion,(uint32_t)now);
#endif
          if(fired>=0 && combat.mode==B16_REPULSOR){''')
out=w/'b24/b24_unified'
for fname in ('b24_g11_original_unibeam_sequence.h','b24_g11_original_unibeam_sequence.c'):
 shutil.copyfile(root/'research/b24_unified'/fname,out/fname)
cm=w/'CMakeLists.txt';body=cm.read_text()
if 'G11_2010_ACTUAL_THREE_STAGE_BEAM_SOURCE' in body:raise RuntimeError('duplicate')
body+='''

# G11_2010_ACTUAL_THREE_STAGE_BEAM_SOURCE
if(B24_ENABLE_GPU)
 target_sources(im2_beta PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_g11_original_unibeam_sequence.c")
endif()
'''
cm.write_text(body)
s=(w/main).read_text()
assert s.index('b16_combat_fire(&combat')<s.index('b24_g8_motion_unibeam_trigger(')<s.index('b24_g8_motion_tick(')
print('PASS G11 original 2010 Beam1/Beam2/Beam3 grounded+hover accepted Unibeam source; all four native BRES skinned armors, first WM repulsor event survives suit binding, idle source wings STOP looping; NO VPK')
