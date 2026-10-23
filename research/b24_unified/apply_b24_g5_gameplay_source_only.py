#!/usr/bin/env python3
"""B24 G5: patch the generated REAL B24 game main, not a standalone demo.
Run only AFTER apply_b24_gpu_main_source_only.py. Exactly-one markers fail
closed on drift. CPU B14 flight/physics and original game state unchanged.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[2]/"work"
p=root/"src/main.c"
s=p.read_text()
def replace(before,after):
 global s
 n=s.count(before)
 if n!=1: raise RuntimeError(f"G5 main source drift: {n} matches: {before[:100]!r}")
 s=s.replace(before,after)
# On G4 the old event path changes weapon/suit even when pause menu is open,
# which conflicts with the B21 menu's D-pad and Cross navigation.
replace(
 "if(e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_LEFT)b16_combat_mode(&combat,-1);",
 "if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_LEFT)b16_combat_mode(&combat,-1);"
)
replace(
 "if(e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_RIGHT)b16_combat_mode(&combat,1);",
 "if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_RIGHT)b16_combat_mode(&combat,1);"
)
replace(
 "if(e.cbutton.button==SDL_CONTROLLER_BUTTON_BACK){",
 "if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_BACK){"
)
# Circle resumes/backtracks the B21 pause menu. Its SDL event must not
# also toggle the B14 flight mode or overwrite the landing timestamp.
replace(
 "if(e.cbutton.button==SDL_CONTROLLER_BUTTON_B){",
 "if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_B){"
)
# SDL controller events can be much shorter than heavy frame times.
# Latch pause menu keys exactly like the known-working C2 START event;
# the unified input decoder remains the only UI state owner.
needle='''if(e.cbutton.button==SDL_CONTROLLER_BUTTON_START)
                    b24_input_latched|=IM2_BT_START;'''
replace(needle,needle+'''
                if(b24_unified_paused(&b24_game)){
                    switch(e.cbutton.button){
                    case SDL_CONTROLLER_BUTTON_A:b24_input_latched|=IM2_BT_CROSS;break;
                    case SDL_CONTROLLER_BUTTON_B:b24_input_latched|=IM2_BT_CIRCLE;break;
                    case SDL_CONTROLLER_BUTTON_DPAD_UP:b24_input_latched|=IM2_BT_DUP;break;
                    case SDL_CONTROLLER_BUTTON_DPAD_DOWN:b24_input_latched|=IM2_BT_DDOWN;break;
                    case SDL_CONTROLLER_BUTTON_DPAD_LEFT:b24_input_latched|=IM2_BT_DLEFT;break;
                    case SDL_CONTROLLER_BUTTON_DPAD_RIGHT:b24_input_latched|=IM2_BT_DRIGHT;break;
                    default:break;
                    }
                }''')
assert "b24_buttons|=b24_input_latched;" in s
assert "b24_unified_tick(&b24_game,&b24_obs)" in s
p.write_text(s)
print("PASS G5 real B24 input bridge: START+pause action keys event-latched, paused suit/weapon/flight mutation blocked, B21 state owner retained")
