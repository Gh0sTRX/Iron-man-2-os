#!/usr/bin/env python3
"""G299 patch only opt-in ambient color of ONE G168 Vita animated suit draw.
Retain authenticated G168 IM2T native_bind_min_z anchor, G75 collision,
G8 original IM2V, B14 flight and all already-tested code. NO VPK.
"""
from pathlib import Path
import argparse

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REF=ROOT/"research/b24_unified/b24_gpu_suit_vitagl.c"

def one(data:str,old:str,new:str,why:str)->str:
 n=data.count(old)
 if n!=1:raise ValueError(f"G299 fail closed {why}: anchor count={n}")
 return data.replace(old,new,1)

def install(root:Path):
 work=root/"work"
 path=work/"b24/b24_unified/b24_gpu_suit_vitagl.c"
 cm=work/"CMakeLists.txt"
 main=work/"src/main.c"
 for name in (path,cm,main,REF):
  if not name.is_file():raise FileNotFoundError(str(name))
 if list(work.rglob("*.vpk")):raise ValueError("G299 NO VPK")
 c=path.read_text();cfg=cm.read_text();game=main.read_text();reference=REF.read_text()
 if "B24_G299_SUIT_ENVIRONMENT_CANDIDATE" in c or "B24_G299_SUIT_ENVIRONMENT_CANDIDATE" in cfg:
  raise ValueError("G299 duplicate source modification")
 if "src->native_bind_min_z" not in c or "B24_G168_ORIGINAL_SUIT_RENDER_FOOT" not in cfg:
  raise ValueError("G299 requires intact G168 authentic IM2T foot-bound suit code")
 if "B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE" not in cfg:
  raise ValueError("G299 requires existing original four-Sun candidate CMake")
 if game.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G299 requires one B14 integrator")
 if game.count("b24_g8_motion_tick_g84(")!=1:
  raise ValueError("G299 requires one real G8 source pose renderer")
 header=reference.split("#ifdef B24_G299_SUIT_ENVIRONMENT_CANDIDATE",1)[1].split("_Static_assert(",1)[0]
 header="#ifdef B24_G299_SUIT_ENVIRONMENT_CANDIDATE"+header
 c=one(c,"#include <string.h>\n","#include <string.h>\n"+header,
       "insert original shared candidate source only")
 start=reference.index(' glBindTexture(GL_TEXTURE_2D,s->texture_id);')
 end=reference.index(' glEnableClientState(GL_VERTEX_ARRAY);',start)
 source_block=reference[start:end]
 c=one(c," glBindTexture(GL_TEXTURE_2D,s->texture_id);\n glColor4f(1.f,1.f,1.f,1.f);\n",
       source_block,"real animated suit alpha-preserving RGB light")
 start=reference.index(" glDisable(GL_TEXTURE_2D);\n#ifdef B24_G299_SUIT_ENVIRONMENT_CANDIDATE")
 end=reference.index(" glPopMatrix();",start)
 c=one(c," glDisable(GL_TEXTURE_2D);\n",reference[start:end],
       "restore old texture env and white to next HUD")
 cfg+='''
# G299: experimental only, source-local 2010 Sun001..004 positions
# shared with G95. Dynamic suit uniform attenuation only; no original
# shading claim, no new normal buffers/texture uploads, no collisions.
option(B24_G299_SUIT_ENVIRONMENT_CANDIDATE "Candidate four-Sun source placement uniform dynamic armor ambient" OFF)
if(B24_G299_SUIT_ENVIRONMENT_CANDIDATE)
 if(NOT B24_ENABLE_GPU OR NOT B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE OR
    NOT B24_G168_ORIGINAL_SUIT_RENDER_FOOT)
  message(FATAL_ERROR "G299 requires verified G95 four source-Sun nodes and G168 original suit foot renderer")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G299_SUIT_ENVIRONMENT_CANDIDATE=1)
endif()
'''
 if c.count("b24_gpu_suit_draw(")!=1 or
    c.count("glDrawElements(")!=1 or
    c.count("src->native_bind_min_z")!=2 or
    c.count("g299_prior_texture_env")!=3:
  raise ValueError("G299 sole renderer draw, G168 foot, and state restoration broken")
 if list(work.rglob("*.vpk")):raise ValueError("G299 NO VPK")
 path.write_text(c);cm.write_text(cfg)
 print("G299 SOURCE PASS one authentic G168 IM2T animated armor draw, optional G95 source-local four-Sun ambient, no damage to G8/B14, no VPK")

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=ROOT)
 install(p.parse_args().root)
