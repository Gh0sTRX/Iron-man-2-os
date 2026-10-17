#!/usr/bin/env python3
"""G165 one G83/G8 Vita animator: War Machine directional original-source
fallback for otherwise empty grounded idle/walk and RUSH clip selection.

G161 hardware feedback says WM animations incomplete. Current G83 had a
NULL stem on WM ground when AIM_NONE; WM RUSH also yielded NULL.
Original 2010 named WM directional aimed-ground and aim_fly_m exist, but
are NOT known to be native neutral/RUSH clips. Opt-in temporary fallback.
"""
from pathlib import Path
R=Path(__file__).resolve().parents[3];W=R/"work"
G83=W/"b24/b24_unified/b24_g83_unified_movement_aim.c"
M=W/"src/main.c";CM=W/"CMakeLists.txt"
def once(s,a,b):
 n=s.count(a)
 if n!=1:raise ValueError("G165 source WM route drift: "+str(n)+" "+a[:110])
 return s.replace(a,b,1)
def patch():
 for p in (G83,M,CM):
  if not p.is_file():raise FileNotFoundError(str(p))
 c=G83.read_text();cm=CM.read_text();main=M.read_text()
 if "B24_G165_WM_SOURCE_DIRECTIONAL_FALLBACK" in cm:raise ValueError("already G165")
 if "B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY" not in cm:
  raise ValueError("G165 patches AFTER G164 sky and G163 aim")
 if main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1 or main.count("b24_g83_timeline_tick(")!=1:
  raise ValueError("G165 must retain one source G83 and B14 physics owner")
 a=''' }else if(wm){
  if(ground){
   if(aim!=B24G83_AIM_NONE){'''
 b=''' }else if(wm){
  if(ground){
#ifdef B24_G165_WM_SOURCE_DIRECTIONAL_FALLBACK
   /* Genuine original warmachine_warmachine_aim_ground_move_*
    * source clips ALREADY play while L aim is held. Without L, the
    * old route returned NULL, falling back to unrelated G8 motions.
    * Actual original WM relaxed-neutral stance has not been proven.
    * Reuse named 2010 aimed-ground directional locomotion as
    * EXPERIMENTAL presentational fallback, not authentic neutral. */
   if(aim==B24G83_AIM_NONE)stem=wm_ground_aim[dir];
   else
#endif
   if(aim!=B24G83_AIM_NONE){'''
 c=once(c,a,b)
 a='''  } /* WM native RUSH absent: preserve prior G8 fallback */
 }'''
 b='''  }
#ifdef B24_G165_WM_SOURCE_DIRECTIONAL_FALLBACK
  else if(rush){
   /* Original 2010 WM RUSH-only source clip NOT decoded.
    * Reuse true original wm aim_fly_m flight posture rather than
    * old G8 fallback ground run, explicitly TEMPORARY. */
   stem="warmachine_warmachine_aim_fly_m";
  }
#endif
  /* Source-authored WM RUSH-only motion remains unverified. */
 }'''
 c=once(c,a,b)
 cm+="""
# G165 original 2010 War Machine named aimed ground source exists.
# Neutral stance and dedicated WM rush source clip remain UNKNOWN.
# Experimental directional fallback uses NO fabricated keyframes,
# weapon action, projectile or additional rig tick.
option(B24_G165_WM_SOURCE_DIRECTIONAL_FALLBACK "Original WM directional aimed source clips reused experimentally for neutral ground and WM flight pose in rush" OFF)
if(B24_G165_WM_SOURCE_DIRECTIONAL_FALLBACK)
 if(NOT B24_G84_ORIGINAL_MOVESET_ROUTER OR NOT B24_G85_NATIVE_MARKV_629)
  message(FATAL_ERROR "G165 requires single G83/G8 source player")
 endif()
 target_compile_definitions(im2_beta PRIVATE
  B24_G165_WM_SOURCE_DIRECTIONAL_FALLBACK=1)
endif()
"""
 G83.write_text(c);CM.write_text(cm)
 if list(W.rglob("*.vpk")):raise ValueError("G165 no new VPK before multiple feedback issues fixed")
 print("G165 original 2010 WM ground directional and flight source poses routed as honest temporary neutral/rush fallback; no fake keyframes, no VPK")
if __name__=="__main__":patch()
