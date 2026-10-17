#!/usr/bin/env python3
"""G111 in actual B24 single game source: original 2010 named EntityData
GetParamValue, Actor::CanAttack and MainCharacter::IsInMeleeAttackState
evidence gates wired INTO original B24 G82 contact/damage coordinator.
Run after G75/G84/G85/G87/G92 and optional G106/G108.
Never create VPK. No extra physics, animation, attack or dummy owner.
"""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
W=R/'work';D=W/'b24/b24_unified';CM=W/'CMakeLists.txt';M=W/'src/main.c'
def apply():
 for p in (CM,M,D/'b24_g82_original_combat_coordinator.c',
    D/'b24_g82_original_combat_coordinator.h'):
  if not p.exists():raise FileNotFoundError('G111 after G84 authentic G82 required '+str(p))
 cm=CM.read_text();main=M.read_text()
 if 'B24_G111_NATIVE_SOURCE_GATES' in cm:raise ValueError('G111 already staged')
 if main.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')!=1:
  raise ValueError('G111 never adds own physics owner')
 if main.count('b24_g8_motion_tick_g84(')!=1:raise ValueError('G111 keeps one source pose streamer')
 assert 'B24_G111_NATIVE_SOURCE_GATES' in (D/'b24_g82_original_combat_coordinator.c').read_text()
 assert 'original_2010_attack_entitydata' in (D/'b24_g82_original_combat_coordinator.h').read_text()
 for category,name in (
    ('g111_original_game_combat_gates','b24_g111_original_source_entitydata_and_combat_permission.h'),
    ('g111_original_game_combat_gates','b24_g111_original_source_entitydata_and_combat_permission.c'),
    ('g103_partial_original_actor_attack_permission','b24_g103_verified_original_actor_attack_classification.h'),
    ('g103_partial_original_actor_attack_permission','b24_g103_verified_original_actor_attack_classification.c'),
    ('g89_original_combo_native_flow','b24_g89_real_2010_melee_state_predicates.h'),
    ('g89_original_combo_native_flow','b24_g89_real_2010_melee_state_predicates.c')):
  shutil.copyfile(R/'research/b24_unified'/category/name,D/name)
 cm+='''
# G111 2010 native source ARM actual EntityData::GetParamValue string+memcpy,
# Actor::CanAttack actor type+0x2B8, IsInMeleeAttackState +0x824.
# Compile into EXISTING G82 contact/damage source owner only, default OFF.
option(B24_G111_NATIVE_SOURCE_GATES "Require original 2010 typed entitydata and actor permission in EXISTING B24 G82 combat" OFF)
if(B24_G111_NATIVE_SOURCE_GATES)
 if(NOT B24_G84_ORIGINAL_MOVESET_ROUTER)
  message(FATAL_ERROR "G111 requires real G84 G82 single-game attack owner")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G111_NATIVE_SOURCE_GATES=1)
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g111_original_source_entitydata_and_combat_permission.c"
  "b24/b24_unified/b24_g103_verified_original_actor_attack_classification.c"
  "b24/b24_unified/b24_g89_real_2010_melee_state_predicates.c")
endif()
'''
 CM.write_text(cm)
 assert not list(W.rglob('*.vpk'))
 print('G111 applied REAL original 2010 named property/native actor/native melee gates to existing G82 contact engine source; no fake Damage values, NO VPK')
if __name__=='__main__':apply()
