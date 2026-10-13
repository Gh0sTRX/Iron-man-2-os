#!/usr/bin/env python3
"""Early B24 live gameplay-adapter PATCH after B17. Not a completed GPU port.
Only modifies generated work/, never commits over known-good B17 or B15.
Fail closed on unknown upstream sources instead of silently applying bad diffs.
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2] / "work"
def replace(rel,old,new,expected=1):
    path=ROOT/rel
    s=path.read_text()
    if s.count(old)!=expected:
        raise RuntimeError(f"B24 patch refused {rel}: expected {expected} occurrences of {old[:80]!r}, got {s.count(old)}")
    path.write_text(s.replace(old,new))

# Input hysteresis: user explicitly requested near-full analogue for both run and fly.
replace("src/b14_world.c",
        "const float normal_threshold=was_fast?.67f:.78f;",
        "const float normal_threshold=was_fast?.88f:.96f;")
replace("src/b14_world.c",
        "(len>=.78f?2.4f:1.1f);",
        "(len>=.96f?2.4f:1.1f);")
replace("src/main.c",
        "const int ground_run=!world.flying && world.speed>=.78f;",
        """B17GateInput b24_analog={0};
        b24_analog.stick_x=move_x;b24_analog.stick_forward=move_y;
        b24_analog.airborne=world.flying;
        b17_gate_step(&b24_gate,&b24_gate_cfg,&b24_analog);
        const int ground_run=b24_gate.is_ground_running;""")
# Real weapon animations should not restart on a still-active attack clip.
replace("src/main.c",
        "if(fired>=0 && combat.mode==B16_REPULSOR)",
        "if(fired>=0 && combat.mode==B16_REPULSOR && !attack.attack_active)")

# The first repulsor fix: prevent arbitrary Beam1/2/3 on each consecutive shot.
# Clip retarget verification / proper firing animation still required.
replace("src/main.c",
        "b16_attack_begin(&attack,now,world.flying,palm==attack.palm_l,combat.shots%3);",
        "b16_attack_begin(&attack,now,world.flying,palm==attack.palm_l,0);")

# Keep user-proven B17 movement & original pose as authoritative.
replace("src/main.c", '#include "b16_action.h"',
        '#include "b16_action.h"\n#include "../b24/b24_unified/b24_unified.h"\n#include "../b24/b18_gpu_probe/b17_input_landing_gate.h"')
replace("src/main.c", "static B8Combat range={0};",
        "static B8Combat range={0};\nstatic B24Unified b24_game={0};\nstatic B17GateState b24_gate={0};\nstatic B17GateConfig b24_gate_cfg={0};")
replace("src/main.c", "B16Combat combat; b16_combat_init(&combat);",
        "B16Combat combat; b16_combat_init(&combat);\n    b24_unified_init(&b24_game);\n    b17_gate_defaults(&b24_gate_cfg);b17_gate_init(&b24_gate);")

# New B21-style map. For this early integration, SELECT = test-suit-cycle.
# R = held fire; L = missile lock; Square = melee (genuine animations pending);
# Circle = flight toggle; Triangle = held RUSH; Dpad L/R weapon, Up/Down altitude.
# START handled by B21 pause UI; user can still close with keyboard Escape.
replace("src/main.c",
        "if(e.cbutton.button==SDL_CONTROLLER_BUTTON_A){idx=(idx+1)%5;load(idx);world.head_height=b15_suit_head(&model);}",
        "/* B24: Cross is an interaction input; suit switching moved to SELECT. */")
replace("src/main.c",
        "if(e.cbutton.button==SDL_CONTROLLER_BUTTON_X)trigger=1;",
        "/* B24: Square is reserved for melee, not repulsor. */")
replace("src/main.c",
        "if(e.cbutton.button==SDL_CONTROLLER_BUTTON_START)running=0;",
        "/* B24: START toggles pause in unified controls. */")
replace("src/main.c",
        'if(e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_UP)b16_combat_mode(&combat,1);',
        '/* B24: D-pad Up moves vertically when airborne. */')
replace("src/main.c",
        'if(e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_DOWN)b16_combat_mode(&combat,-1);',
        '/* B24: D-pad Down moves vertically when airborne. */')
replace("src/main.c",
        'if(e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_LEFT)invert_move_x=!invert_move_x;',
        'if(e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_LEFT)b16_combat_mode(&combat,-1);')
replace("src/main.c",
        'if(e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_RIGHT)invert_camera_y=!invert_camera_y;',
        'if(e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_RIGHT)b16_combat_mode(&combat,1);')

# Existing SELECT toggles renderer state: leave VSync on keyboard V and use SELECT
# to inspect the five authentic suit models on device during integration QA.
old='''if(e.cbutton.button==SDL_CONTROLLER_BUTTON_BACK){
                    if(!b10_switch_display(window,&sdl,&display,&vsync_requested,&vsync_active,&profile_error))running=0;
                    profiler=(B10Profiler){0};
                }'''
new='''if(e.cbutton.button==SDL_CONTROLLER_BUTTON_BACK){
                    idx=(idx+1)%5;
                    if(!load(idx))running=0;
                    world.head_height=b15_suit_head(&model);
                }'''
replace("src/main.c",old,new)
old='''if(e.cbutton.button==SDL_CONTROLLER_BUTTON_Y){
                    boost=!boost;world.rush=boost;rush_begin=SDL_GetTicks();
                }'''
replace("src/main.c",old,'/* B24: Triangle RUSH held state is applied before movement tick. */')

# The prior controls put altitude on L/R shoulders. B24 gives R fire and L lock.
replace("src/main.c",
        "if(SDL_GameControllerGetButton(pad,SDL_CONTROLLER_BUTTON_RIGHTSHOULDER))ascend+=1;",
        "if(SDL_GameControllerGetButton(pad,SDL_CONTROLLER_BUTTON_RIGHTSHOULDER))trigger=1;")
replace("src/main.c",
        "if(SDL_GameControllerGetButton(pad,SDL_CONTROLLER_BUTTON_LEFTSHOULDER))ascend-=1;",
        """if(SDL_GameControllerGetButton(pad,SDL_CONTROLLER_BUTTON_DPAD_UP))ascend+=1;
            if(SDL_GameControllerGetButton(pad,SDL_CONTROLLER_BUTTON_DPAD_DOWN))ascend-=1;
            boost=SDL_GameControllerGetButton(pad,SDL_CONTROLLER_BUTTON_Y)!=0;
            world.rush=boost;""")

# Single button mapping for the B21 parser. B17 world still owns physical motion;
# unified module reads current world state AFTER it has stepped.
needle='''        world.camera_distance=clip(world.camera_distance-zoom*dt*1.8f,2.8f,6.4f);'''
buttons='''        uint32_t b24_buttons=0;
        if(pad){
          static const struct {SDL_GameControllerButton b; uint32_t mask;} buttons[]={
            {SDL_CONTROLLER_BUTTON_RIGHTSHOULDER,IM2_BT_R},
            {SDL_CONTROLLER_BUTTON_LEFTSHOULDER,IM2_BT_L},
            {SDL_CONTROLLER_BUTTON_X,IM2_BT_SQUARE},
            {SDL_CONTROLLER_BUTTON_Y,IM2_BT_TRIANGLE},
            {SDL_CONTROLLER_BUTTON_B,IM2_BT_CIRCLE},
            {SDL_CONTROLLER_BUTTON_A,IM2_BT_CROSS},
            {SDL_CONTROLLER_BUTTON_DPAD_UP,IM2_BT_DUP},
            {SDL_CONTROLLER_BUTTON_DPAD_DOWN,IM2_BT_DDOWN},
            {SDL_CONTROLLER_BUTTON_DPAD_LEFT,IM2_BT_DLEFT},
            {SDL_CONTROLLER_BUTTON_DPAD_RIGHT,IM2_BT_DRIGHT},
            {SDL_CONTROLLER_BUTTON_START,IM2_BT_START},
            {SDL_CONTROLLER_BUTTON_BACK,IM2_BT_SELECT}};
          for(unsigned b=0;b<sizeof(buttons)/sizeof(buttons[0]);b++)
            if(SDL_GameControllerGetButton(pad,buttons[b].b))b24_buttons|=buttons[b].mask;
        }
        world.camera_distance=clip(world.camera_distance-zoom*dt*1.8f,2.8f,6.4f);'''
replace("src/main.c",needle,buttons)

old='''        b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);
        b16_combat_tick(&combat,&world,dt);'''
new='''        if(!b24_unified_paused(&b24_game)){
          b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);
          b16_combat_tick(&combat,&world,dt);
        }
        B24Observation b24_obs={0};
        b24_obs.player_z_up=(Im2Vec3){world.x,world.y,world.z};
        b24_obs.heading_rad=world.heading;
        b24_obs.orbit_rad=world.orbit;
        b24_obs.pitch_rad=world.pitch;
        b24_obs.left_x=move_x;b24_obs.left_forward=move_y;
        b24_obs.right_x=turn;b24_obs.right_y=look;
        b24_obs.buttons=b24_buttons;
        b24_obs.stage=world.flying?world.flight_stage:0;
        b24_obs.suit_index=idx;
        b24_obs.weapon_index=combat.mode;
        b24_obs.target_visible=world.visible;
        b24_obs.target_alive=world.visible;
        b24_obs.target_id=world.visible?0:-1; /* B17 sphere ONLY, not real enemy */
        b24_obs.target_occluded=0; /* real mission raycast unavailable */
        b24_obs.target_distance=world.visible?8.f:0.f; /* provisional demo range */
        b24_obs.target_screen_x=(int)world.screen_x;
        b24_obs.target_screen_y=(int)world.screen_y;
        b24_obs.target_health_percent=-1.f;
        b24_obs.melee_anim_active=0; /* no original combo pose linked yet */
        b24_obs.energy_percent=combat.energy;
        b24_obs.wave=(int)combat.wave;
        b24_obs.real_enemies_loaded=0; /* no invisible B19 drones */
        b24_obs.dt=dt;
        b24_unified_tick(&b24_game,&b24_obs);
        world.camera_distance=b24_unified_chase_distance(&b24_game);'''
replace("src/main.c",old,new)

# Camera + GPU migration remains a single game pipeline; present existing fallback
# while we replace CPU geometry with true vitaGL. Now B22 & B23 HUD and Rush edges
# are actually rendered OVER the same on-device frame as B17, not a separate demo.
replace("src/main.c",
        "im2_render(pixels,zbuffer,&model,&camera,label,frame++);",
        "im2_render(pixels,zbuffer,&model,&camera,label,frame++);\n        b24_unified_draw_overlay(&b24_game,pixels,IM2_W);")

print("B24 live adapter patch applied after B17. Legacy CPU scene still present;")
print("new visor/missile RUSH overlays linked; true GPU, flight 3D, melee assets remain.")
