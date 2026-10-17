#!/usr/bin/env python3
"""G164 source original sky camera-relative + camera framing device feedback.
Patch the ACTUAL one G163 Vita B24GPU render owner, no new game owner,
material atlas, fake original moon/sun or model scaling. NO VPK.
"""
from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
R=HERE.parents[2];W=R/'work'
D=W/'b24/b24_unified'
P=D/'b24_gpu_runtime.c'
CM=W/'CMakeLists.txt'
M=W/'src/main.c'
def rep(t,a,b):
 n=t.count(a)
 if n!=1:raise ValueError(f"G164 verified GPU render anchor {n}: {a[:100]!r}")
 return t.replace(a,b,1)
def apply():
 for p in (P,CM,M,D/'b24_gpu_g73_sky_vitagl.c'):
  if not p.is_file():raise FileNotFoundError(str(p))
 s=P.read_text();cm=CM.read_text();main=M.read_text()
 if "B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY" in cm:
  raise ValueError("G164 duplicate real GPU render source")
 if "B24_G163_CAMERA_AIM_FACING" not in cm or "B24_G73_REAL_SKY" not in cm:
  raise ValueError("G164 requires real G163 aim and original source G73")
 if main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G164 refuses replacing existing B14 owner")
 if main.count("b24_gpu_runtime_draw(")!=1:
  raise ValueError("G164 must preserve one B24GPU frame renderer")
 s=rep(s,'#include "b24_gpu_runtime.h"',
  '#include "b24_gpu_runtime.h"\n'
  '#if defined(B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY) || defined(B24_G164_HERO_CAMERA_FRAMING)\n'
  '#include "b24_g164_camera_sky_framing.h"\n'
  '#endif\n#ifdef B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY\n'
  '#include <vitaGL.h>\n#endif')
 s=rep(s,''' float fd=c->camera_distance;
 if(!isfinite(a)||!isfinite(cp)||!isfinite(sp)||''',
 ''' float fd=c->camera_distance;
#ifdef B24_G164_HERO_CAMERA_FRAMING
 /* ONLY perspective, G161 MarkV original sourced 2.2355 unit model and
  * original world collision G75/G66C coordinates remain BIT-IDENTICAL.
  * Stage2/RUSH centered chase uses previous 72deg/distance. Ground and
  * upright hover blend slightly closer when shoulder mode is active. */
 float g164_fov=72.f,g164_distance_multiplier=1.f;
 if(!b24_g164_camera_framing(
      1.f-g->camera_base.shoulder_to_chase,
      &g164_distance_multiplier,&g164_fov))return 0;
 fd*=g164_distance_multiplier;
#endif
 if(!isfinite(a)||!isfinite(cp)||!isfinite(sp)||''')
 s=rep(s,'''  72.f,960.f/544.f,.15f,2600.f
 };''',
 '''#ifdef B24_G164_HERO_CAMERA_FRAMING
  g164_fov,960.f/544.f,.15f,2600.f
#else
  72.f,960.f/544.f,.15f,2600.f
#endif
 };''')
 s=rep(s,'''#ifdef B24_G73_REAL_SKY
 if(!b24_g73_sky_draw(&r->original_sky))return 0;
#endif''',
 '''#ifdef B24_G73_REAL_SKY
#ifdef B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY
 /* G164: authentic 2010 skyline/moon/stars G73 288 source vertices are
  * centered near source origin x/y=0. The G161 render owner applied the
  * WORLD camera translation; roaming original C1L1 hundreds of units
  * off-center meant skyline/crosstrees drift or vanish while stars
  * (full spherical UV sheet) remained. Preserve authored UV/PVR, sky
  * rotation and original scene draw depth behavior; strip translation
  * ONLY in the temporary sky-only modelview. Restore before G68 city. */
 float skyview[16]={0};
 if(!b24_g164_source_sky_view(matrices.view,skyview))return 0;
 glMatrixMode(GL_MODELVIEW);
 glPushMatrix();
 glLoadMatrixf(skyview);
 const int g164_sky_ok=b24_g73_sky_draw(&r->original_sky);
 glPopMatrix();
 if(!g164_sky_ok)return 0;
#else
 if(!b24_g73_sky_draw(&r->original_sky))return 0;
#endif
#endif''')
 for name in ("b24_g164_camera_sky_framing.h","b24_g164_camera_sky_framing.c"):
  shutil.copyfile(HERE/name,D/name)
 cm+="""
# G164 actual C1L1 G73 original 2010 sky source: retina stars/skyline
# camera-rotation-only draw. No original sampler guess becomes a claim.
option(B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY "Correct world-translated G73 actual original iOS sky source rendering to camera-relative background" OFF)
# G161 owner noticed armor too small; source MarkV rest mesh is 2.2355
# units tall (REAL). Camera only QA: do NOT alter scale or collision.
option(B24_G164_HERO_CAMERA_FRAMING "Ground and hover over-shoulder view camera-only 68deg FOV .87 distance to improve 2.2355 MarkV onscreen size" OFF)
if(B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY OR B24_G164_HERO_CAMERA_FRAMING)
 if(NOT B24_G68_CITY_BACKEND OR NOT B24_G75_SOURCE_CAPSULE OR
    NOT B24_G73_REAL_SKY)
  message(FATAL_ERROR "G164 camera/background requires original G68/G73 and one B14/G75 source world")
 endif()
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g164_camera_sky_framing.c")
 if(B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY)
  target_compile_definitions(im2_beta PRIVATE
   B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY=1)
 endif()
 if(B24_G164_HERO_CAMERA_FRAMING)
  target_compile_definitions(im2_beta PRIVATE
   B24_G164_HERO_CAMERA_FRAMING=1)
 endif()
endif()
"""
 P.write_text(s);CM.write_text(cm)
 if s.count('b24_g164_source_sky_view(')!=1 or s.count('b24_g164_camera_framing(')!=1:
  raise ValueError("G164 double sky/camera source owners")
 if list(W.rglob("*.vpk")):raise ValueError("G164 NO Vita installs until G161 feedback addressed")
 print("G164 actual G161 renderer patched source sky rotation-only, new camera distance/FOV grounded QA only, true model/G75 map coords unchanged; no VPK")
if __name__=="__main__":apply()
