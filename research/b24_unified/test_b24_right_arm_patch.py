#!/usr/bin/env python3
from pathlib import Path
main=Path("work/src/main.c").read_text()
action=Path("work/src/b16_action.c").read_text()
assert main.count("const unsigned palm=attack.palm_r;")==1
assert "((combat.shots&1)==0)?attack.palm_r:attack.palm_l" not in main
assert main.count("b16_attack_begin(&attack,now,world.flying,0,0);")==1
assert "palm==attack.palm_l" not in main
assert "(int)attack.palm_r; /* B24: HUD muzzle" in main
assert "const float span=vx*vx+vy*vy+vz*vz;" in action
assert "if(side<0.f)a->arm_mask[i]=0;" in action
assert "if(a->palm_l>=model->nv||a->palm_r>=model->nv)goto fail;" in action
print("PASS B24 source-only right repulsor: world muzzle/beam animation/HUD all RIGHT + upper mask halfspace and safety guards")
