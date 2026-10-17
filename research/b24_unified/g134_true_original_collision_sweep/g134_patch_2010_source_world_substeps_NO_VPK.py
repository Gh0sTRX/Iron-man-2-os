#!/usr/bin/env python3
"""G134 cap one Vita G75/B14 player displacement to ORIGINAL source
swept capsule resolution's .22-unit * 80 substep safety window.
Previously code limited steps to 80 but applied FULL displacement
dx/80 so fast movement crossed thin walls BETWEEN samples.
Apply AFTER G108 and all G75 original Vita physics assembly, source only.
Never adds physics tick or replaces real 2010 source mesh. NO VPK.
"""
from pathlib import Path
R=Path(__file__).resolve().parents[3]
W=R/'work'
M=W/'src/main.c';SRC=W/'b24/b24_unified/b24_g75_source_capsule.c'
CM=W/'CMakeLists.txt'
def apply():
 if not M.is_file() or not SRC.is_file() or not CM.is_file():
  raise FileNotFoundError("G134 requires G128 real Vita G75 + G108 merged first")
 main=M.read_text();code=SRC.read_text();cm=CM.read_text()
 assert main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")==1
 assert code.count("b24_g108_grid_clear(")==1
 assert code.count("b24_g108_grid_load(")==1
 assert "B24_G108_SOURCE_VISUAL_WALLS" in cm
 if "G134_LIMIT_LONG_FRAME_DISPLACEMENT" in code:raise ValueError("G134 duplicate")
 old=''' int steps=(int)ceilf(fmax2(fmax2(fabsf(dx),fabsf(dy)),fabsf(dz))/.22f);
 if(steps<1)steps=1;
 if(steps>80)steps=80;
 float x=x0,y=y0,z=z0;
 const float stepx=dx/steps,stepy=dy/steps,stepz=dz/steps;'''
 new=''' /* G134_LIMIT_LONG_FRAME_DISPLACEMENT: G75 once limited the number
  * of sweep queries to 80 but did NOT limit displacement, making every
  * substep larger than .22 units on a long stall/rush/hitch. A thin real
  * source wall (x=10.6) can be passed between two 1.25-unit samples.
  * One game tick, 80 MAX steps. If a long frame reports huge movement,
  * accept at most 80*.22 SOURCE units this frame (conservative fail
  * safe), rather than teleport through city geometry. No altered source
  * collision polygon, no fake hit, no second B14 physics tick. */
 const float dmax=fmax2(fmax2(fabsf(dx),fabsf(dy)),fabsf(dz));
 if(dmax>80.f*.22f){
  const float keep=(80.f*.22f)/dmax;
  dx*=keep;dy*=keep;dz*=keep;
 }
 int steps=(int)ceilf(fmax2(fmax2(fabsf(dx),fabsf(dy)),fabsf(dz))/.22f);
 if(steps<1)steps=1;
 if(steps>80)steps=80; /* float rounding guard, not an acceleration */
 float x=x0,y=y0,z=z0;
 const float stepx=dx/steps,stepy=dy/steps,stepz=dz/steps;'''
 if code.count(old)!=1:raise ValueError("G134 original G75 source cap site changed")
 SRC.write_text(code.replace(old,new,1))
 assert not list(W.rglob("*.vpk"))
 print("G134 real ONE Vita B14 native source-owner capped long-frame displacement to 80x.22 instead of tunnelling through authentic city walls, NO VPK")
if __name__=="__main__":apply()
