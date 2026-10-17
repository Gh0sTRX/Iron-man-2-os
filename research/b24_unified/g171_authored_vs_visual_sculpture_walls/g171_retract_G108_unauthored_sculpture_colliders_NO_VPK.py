#!/usr/bin/env python3
"""G171 reversible SOURCE collision admission correction, NOT proof that
the genuine original iOS sculpture was non-solid. Actual 2010 city source:
G66M draw group21/atlas21 -> pixel-identical c1l1_diaosu.tga in G64.
G170 at homebrew (0,1.1,0.0725) source G66C original wall count=0,
G108 visual-only inferred opaque wall contacts=2, both group21.
Treating source rendering opacity as collision solidness is not
native source proven. Declassify ONLY this group as supplemental wall
when opt-in. Do not touch original G66C collision or other G108 groups.
No inferred real 2010 solidity, no arbitrary world/scale/spawn, NO VPK.
"""
from pathlib import Path
R=Path(__file__).resolve().parents[3]
W=R/"work"
G=W/"b24/b24_unified/b24_g108_visible_original_wall_grid.c"
CM=W/"CMakeLists.txt"
M=W/"src/main.c"
def one(s,a,b):
 n=s.count(a)
 if n!=1:raise ValueError("G171 geometry source drift count="+str(n)+" "+repr(a[:100]))
 return s.replace(a,b,1)
def patch():
 for p in (G,CM,M):
  if not p.is_file():raise FileNotFoundError(str(p))
 s=G.read_text();cm=CM.read_text();m=M.read_text()
 if "B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL" in cm:raise ValueError("already G171")
 for x in ("B24_G108_SOURCE_VISUAL_WALLS","B24_G156_CONTINUOUS_TRI_CONTACT",
           "B24_G168_ORIGINAL_SUIT_RENDER_FOOT","B24_G169_AUTHENTIC_BEAM_3_PHASE"):
  if x not in cm:raise ValueError("G171 needs original single Vita game "+x)
 if m.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G171 must preserve ONE B14 source movement owner")
 s=one(s,
 '''  cursor+=count;
  if(tex==UINT32_MAX||translucent[tex]){tmp.skipped_alpha+=count/3;continue;}''',
 '''  cursor+=count;
#ifdef B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL
  /* ORIGINAL source authored solid: G66C, never changed. G170 source:
   * x0,y1.10,footZ.0725 G66C native wall 0; G108 opacity-derived
   * two wall candidates group21 texture21. G158 original named RGBA
   * source verifies tex21=c1l1_diaosu.tga. Material rendering is NOT
   * native authored collision state. In strict SOURCE-only mode do
   * not import this one unproven draw group as physics. Other groups
   * and all native-source G66C remain unchanged. */
  if(group==21u&&tex==21u)continue;
  if(group==21u&&tex!=21u)goto fail; /* asset drift cleanup, fail-closed */
#endif
  if(tex==UINT32_MAX||translucent[tex]){tmp.skipped_alpha+=count/3;continue;}''')
 cm+="""

# G171 material backed STRICT SOURCE collision eligibility (opt-in).
# The source 2010 c1l1_diaosu opaque rendered triangle is not proof
# of original authored physical collision; G170 native G66C source
# face count is zero at the G161 homebrew start threshold.
# Real native sculpture physics remains UNPROVEN; no new objects.
option(B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL "Do not infer solid wall from original 2010 sculpture c1l1_diaosu opaque-only visual mesh" OFF)
if(B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL)
 if(NOT B24_G108_SOURCE_VISUAL_WALLS OR NOT B24_G75_SOURCE_CAPSULE
     OR NOT B24_G156_CONTINUOUS_TRI_CONTACT)
  message(FATAL_ERROR "G171 needs original one-G75 source wall/contact game")
 endif()
 target_compile_definitions(im2_beta PRIVATE
  B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL=1)
endif()
"""
 G.write_text(s);CM.write_text(cm)
 if list(W.rglob("*.vpk")):raise ValueError("G171 NO VPK")
 print("G171 original source G66C physical walls unchanged, 2010 c1l1_diaosu rendered-only supplemental pseudo-wall opt-in removed, NO VPK")
if __name__=="__main__":patch()
