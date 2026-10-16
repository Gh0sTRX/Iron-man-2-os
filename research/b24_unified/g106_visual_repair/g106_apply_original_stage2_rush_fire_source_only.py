#!/usr/bin/env python3
"""G106 new real-Vita feedback: no source air-fire pose in stage2/rush.
2010 USER IPA's 248 original MarkV source bank independently VERIFIES:
suitcase_ironman_fly_att_s 1600ms/33 original G85 frames, and fly_att_m
separate. Preserve identical accepted real B16 repulsor event, existing
single original G8 pose owner and native C G83 full-body flight router.
Only experimental hypothesized association of original *_fly_att_s with
repulsor; original 2010 per-weapon dispatch not yet reverse-proven.
Zero invented keyframes, no new shot/damage.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/'work'
G8=W/'b24/b24_unified/b24_g8_live_original_motion.c'
CM=W/'CMakeLists.txt'
def once(text,a,b):
 count=text.count(a)
 if count!=1:raise ValueError('G106 exact source G85 flight route drift '+str(count)+' '+a[:65])
 return text.replace(a,b,1)
def patch():
 if not G8.is_file() or not CM.is_file():raise FileNotFoundError('G106 must patch AFTER G75/G84/G85/G87/G92')
 c=G8.read_text();cm=CM.read_text()
 if 'G106_REAL_ORIGINAL_FLIGHT_ATTACK_CLIP' in c:raise ValueError('G106 flight attack already staged')
 anchor='''   shot=b24_g8_motion_repulsor_clip(0,mode,left_x,forward);
 }
#endif'''
 new='''   shot=b24_g8_motion_repulsor_clip(0,mode,left_x,forward);
#ifdef B24_G106_SOURCE_FLY_ATTACK_MARKV
   /* G106_REAL_ORIGINAL_FLIGHT_ATTACK_CLIP: Mark V original 2010
    * source-owner 1600ms fly_att_s for stage2/rush, not legacy B16's
    * incompatible hover arm overlay on a forward-flight rig.
    * '_s' IS NOT proof of the native weapon ID; only the actual 2010
    * source pose and its period are certain. Never invent damage. */
   if(mode==B24M_CRUISE||mode==B24M_RUSH)
     shot="ironman_ironman_fly_att_s";
#endif
 }
#endif'''
 c=once(c,anchor,new)
 cm+='''
# G106 original Mark V 2010 flight attack source is ACTUAL baked 629v,
# but mapping from native weapon/attack_type to fly_att_s is provisional.
# User physical Vita trial of stage2/rush B16 repulsor mismatch.
option(B24_G106_SOURCE_FLY_ATTACK_MARKV "Opt-in real 2010 MarkV fly_att_s source full-body for accepted stage2/rush B16 fire" OFF)
if(B24_G106_SOURCE_FLY_ATTACK_MARKV)
 if(NOT B24_G85_NATIVE_MARKV_629 OR NOT B24_G84_ORIGINAL_MOVESET_ROUTER)
  message(FATAL_ERROR "G106 requires actual G85 single original MarkV rig and G83 flight")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G106_SOURCE_FLY_ATTACK_MARKV=1)
endif()
'''
 if not (W/'animations/suitcase_ironman_fly_att_s.im2v').is_file():
  raise ValueError('Missing G106 original source 2010 fly_att_s asset')
 import struct
 raw=(W/'animations/suitcase_ironman_fly_att_s.im2v').read_bytes()
 if struct.unpack_from('<4sIIII',raw)!=(b'IM2V',629,33,20,1600):
  raise ValueError('G106 source fly attack must be REAL 1600ms owner 2010 629v')
 G8.write_text(c);CM.write_text(cm)
 print('G106 SOURCE corrected MarkV stage2/rush accepted B16 repulsor to ORIGINAL authored suitcase_ironman_fly_att_s 629v/33f, continuous G83 full-body, NO guessed weapon stat')
if __name__=='__main__':patch()
