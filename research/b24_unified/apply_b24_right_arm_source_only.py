#!/usr/bin/env python3
"""Source-only corrective edit; apply to generated work/ after B24-C2.
Never builds or distributes Vita VPKs. Right-palm-only repulsor, including
ground-walk upper-arm pose, regardless of legacy shots parity.
Original beam clip source remains not fully validated on hardware.
"""
from pathlib import Path
src=Path("work/src")
def change(name,old,new):
 p=src/name;s=p.read_text()
 assert s.count(old)==1,(name,old,s.count(old))
 p.write_text(s.replace(old,new))
change("main.c",
 'const unsigned palm=((combat.shots&1)==0)?attack.palm_r:attack.palm_l;',
 'const unsigned palm=attack.palm_r; /* B24: RIGHT REPULSOR ONLY */')
change("main.c",
 'b16_attack_begin(&attack,now,world.flying,palm==attack.palm_l,0);',
 'b16_attack_begin(&attack,now,world.flying,0,0);')
change("main.c",
 '(attack.hand?(int)attack.palm_l:(int)attack.palm_r);',
 '(int)attack.palm_r; /* B24: HUD muzzle uses SAME right arm */')
change("b16_action.c",
 '  fclose(f);return 1;',
 '''  fclose(f);
  /* Keep genuine upper-body source pose only on the right half of suit.
     Mid-plane inferred from known BOTH original palm vertices; no guessed
     +X/-X naming and no procedural arm pose substitution.
     The original B16 mask continues to isolate arms from ground gait.
     Bind-stage mesh coordinates must remain stable for this precomputation. */
  if(a->palm_l>=model->nv||a->palm_r>=model->nv)goto fail;
  const IM2Vertex left=model->vertices[a->palm_l];
  const IM2Vertex right=model->vertices[a->palm_r];
  const float vx=right.x-left.x,vy=right.y-left.y,vz=right.z-left.z;
  const float span=vx*vx+vy*vy+vz*vz;
  if(!(span>1.e-5f))goto fail;
  const float mx=(left.x+right.x)*.5f,my=(left.y+right.y)*.5f,
              mz=(left.z+right.z)*.5f;
  for(unsigned i=0;i<a->nverts;i++){
      const IM2Vertex v=model->vertices[i];
      const float side=(v.x-mx)*vx+(v.y-my)*vy+(v.z-mz)*vz;
      if(side<0.f)a->arm_mask[i]=0;
  }
  return 1;''')
print("PASS source-only B24 right-arm repulsor: same right muzzle in combat/HUD, no parity toggle, original arm-mask split, no VPK")
