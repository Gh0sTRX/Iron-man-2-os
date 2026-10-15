#!/usr/bin/env python3
"""Physical G10 Vita feedback G11: NEVER combine sprint or stage2/rush with R.

One B14 source-authoritative movement decision is used for both B14 physics
and G10 original animation. The R hold is not a separate simulation. WM
accepted original repulsor shot gets source event even while B16 overlay
already runs. No new projectile or Vita VPK built by this patch.
"""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
work=root/'work'
p=work/'src/main.c'
s=p.read_text()
def rep(old,new):
 global s
 n=s.count(old)
 if n!=1:raise RuntimeError('G11 main source drift %d %r'%(n,old[:105]))
 s=s.replace(old,new)
rep('#include "../b24/b24_unified/b24_g10_practice_target.h"',
    '#include "../b24/b24_unified/b24_g10_practice_target.h"\n'
    '#include "../b24/b24_unified/b24_g11_combat_stage_policy.h"')
rep('''        b24_buttons|=b24_input_latched;
        b24_input_latched=0;''',
'''        b24_buttons|=b24_input_latched;
        b24_input_latched=0;
        /* G11 physical hardware feedback: stage R and movement are one
           decision, BEFORE the only authoritative B14 world tick.
           A real shot cannot coexist with sprint or Stage2/RUSH.
           Stage1 hover R is allowed and caps move stick at .82,
           below source B14 .96/.88 full-flight boundary. */
        B24G11CombatDecision g11_shot={0};
        const B24G11CombatInput g11_in={
            move_x,move_y,boost,trigger,
            b24_unified_paused(&b24_game),world.flying,
            world.flying?world.flight_stage:0};
        if(!b24_g11_combat_stage_policy(&g11_in,&g11_shot)){
            running=0;break;
        }
        move_x=g11_shot.move_x;
        move_y=g11_shot.move_y;
        boost=g11_shot.boost;
        world.rush=boost;''')
rep('''        const int ground_run=b24_gate.is_ground_running;''',
    '''        const int ground_run=b24_gate.is_ground_running &&
                             !g11_shot.force_walk;''')
rep('''        if(trigger){
          const unsigned palm=attack.palm_r;''',
    '''        if(trigger && !b24_unified_paused(&b24_game) &&
           b24_g11_stage_allows_hand_attack(world.flying,world.flight_stage)){
          const unsigned palm=attack.palm_r;''')
rep('''          if(fired>=0 && combat.mode==B16_REPULSOR && !attack.attack_active){
              b16_attack_begin(&attack,now,world.flying,0,0);
#ifdef B24_GPU_ENGINE
              /* Trigger on REAL accepted shot. Source _Att begins NEXT tick.
                 Existing B16 is fallback when exact IM2V is absent. */
              b24_g8_motion_repulsor_trigger(&b24_original_motion,(uint32_t)now);
#endif
          }''',
    '''          if(fired>=0 && combat.mode==B16_REPULSOR){
#ifdef B24_GPU_ENGINE
              /* WM G10 hardware: B16 limb overlay may already be active;
                 it MUST NOT silently eat a newly ACCEPTED source repulsor.
                 Real B16 shot event is the only trigger, not a fake bolt. */
              b24_g8_motion_repulsor_trigger(&b24_original_motion,(uint32_t)now);
#endif
              if(!attack.attack_active)
                  b16_attack_begin(&attack,now,world.flying,0,0);
          }''')
p.write_text(s)
dst=work/'b24/b24_unified'
for file in ('b24_g11_combat_stage_policy.h','b24_g11_combat_stage_policy.c'):
 shutil.copyfile(root/'research/b24_unified'/file,dst/file)
cm=work/'CMakeLists.txt'; body=cm.read_text()
if body.count('G11_NO_GROUND_SPRINT_OR_STAGE2_REPULSOR')!=0:
 raise RuntimeError('double G11 combat policy patch')
body+='''

# G11_NO_GROUND_SPRINT_OR_STAGE2_REPULSOR
if(B24_ENABLE_GPU)
 target_sources(im2_beta PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_g11_combat_stage_policy.c")
endif()
'''
cm.write_text(body)
assert s.index('b24_g11_combat_stage_policy(&g11_in')<s.index('b14_world_tick(&world,')
assert s.index('b24_g11_stage_allows_hand_attack(world.flying')<s.index('b16_combat_fire(&combat')
assert s.index('b16_combat_fire(&combat')<s.index('b24_g8_motion_tick(&b24_original_motion')
print('PASS G11 source actual G10 B14-world/ B16-fire original animation single-state source hook; no fake gun effects or VPK')
