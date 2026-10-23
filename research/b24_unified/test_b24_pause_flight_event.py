#!/usr/bin/env python3
"""Exercise G5's generated Circle event with real B21 pause controls.

This host test uses the current reconstructed main as its SDL event source.
Only G5's guards/latch are undone in a temporary copy, then the actual G5
patcher regenerates them. SDL event/time values are synthetic; no GPU or
device behavior, original iOS flight semantics, or new VPK is asserted.
"""
from pathlib import Path
import os
import re
import shlex
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PATCHER = HERE / "apply_b24_g5_gameplay_source_only.py"


def block(source, pattern):
    matches = list(re.finditer(pattern, source))
    assert len(matches) == 1, f"Expected one source anchor: {pattern}"
    start = matches[0].start()
    opening = source.index("{", matches[0].start())
    depth = 0
    for end in range(opening, len(source)):
        if source[end] == "{":
            depth += 1
        elif source[end] == "}":
            depth -= 1
            if not depth:
                return source[start:end + 1]
    raise AssertionError("Unclosed source block")


def pre_g5(source):
    """Preserve the real event body; undo only the named G5 transforms."""
    for button in ("DPAD_LEFT", "DPAD_RIGHT", "BACK", "B"):
        old = f"if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_{button})"
        new = f"if(e.cbutton.button==SDL_CONTROLLER_BUTTON_{button})"
        if old in source:
            assert source.count(old) == 1
            source = source.replace(old, new, 1)
        else:
            assert button == "B" and source.count(new) == 1
    menu = block(source, r"if\(b24_unified_paused\(&b24_game\)\)\{")
    assert "b24_input_latched|=IM2_BT_CIRCLE" in menu
    return source.replace(menu, "", 1)


source = (ROOT / "work/src/main.c").read_text()
with tempfile.TemporaryDirectory(prefix="b24_pause_circle_") as temporary:
    temp = Path(temporary)
    main = temp / "work/src/main.c"
    main.parent.mkdir(parents=True)
    main.write_text(pre_g5(source))
    namespace = {"__file__": str(temp / "research/b24_unified" / PATCHER.name)}
    exec(compile(PATCHER.read_text(), str(PATCHER), "exec"), namespace)
    generated = main.read_text()
    event = block(generated, r"if\([^\n{}]*e\.cbutton\.button==SDL_CONTROLLER_BUTTON_B\)\{")
    menu = block(generated, r"if\(b24_unified_paused\(&b24_game\)\)\{")
    paused = block((HERE / "b24_unified.c").read_text(), r"int b24_unified_paused\(")
    harness = r'''
#include "b24_unified.h"
#include "b14_world.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
typedef unsigned Uint32;
enum {SDL_CONTROLLER_BUTTON_A,SDL_CONTROLLER_BUTTON_B,
      SDL_CONTROLLER_BUTTON_DPAD_UP,SDL_CONTROLLER_BUTTON_DPAD_DOWN,
      SDL_CONTROLLER_BUTTON_DPAD_LEFT,SDL_CONTROLLER_BUTTON_DPAD_RIGHT};
typedef struct {struct {int button;} cbutton;} SDL_Event;
static Uint32 SDL_GetTicks(void){return 1234u;}
static B24Unified b24_game;
static B14World world;
static int landing_now;
static Uint32 landing_started;
static uint32_t b24_input_latched;
''' + paused + r'''
static void actual_circle_event(void){
 SDL_Event e={{SDL_CONTROLLER_BUTTON_B}};
''' + event + "\n" + menu + r'''
}
static void scenario(int paused_ui,int airborne,int options){
 im2_controls_init(&b24_game.controls);
 if(paused_ui){
  im2_controls_tick(&b24_game.controls,IM2_BT_START,0,0,0,0);
  im2_controls_tick(&b24_game.controls,0,0,0,0,0);
  if(options){
   im2_controls_tick(&b24_game.controls,IM2_BT_CROSS,0,0,0,0);
   im2_controls_tick(&b24_game.controls,0,0,0,0,0);
   assert(b24_game.controls.menu==IM2_MENUOPTIONS);
  }
  assert(b24_unified_paused(&b24_game));
 }
 world=(B14World){0};world.flying=airborne;
 world.target_z=airborne?2.5f:0.f;
 landing_now=0;landing_started=99u;b24_input_latched=0;
 actual_circle_event();
 im2_controls_tick(&b24_game.controls,b24_input_latched,0,0,0,0);
 if(paused_ui){
  assert(world.flying==airborne);
  assert(world.target_z==(airborne?2.5f:0.f));
  assert(landing_now==0 && landing_started==99u);
  assert(b24_game.controls.state==(options?IM2_PAUSED:IM2_PLAYING));
  assert(b24_game.controls.menu==IM2_MENUMAIN);
  assert(!b24_game.controls.flight_toggle);
 }else{
  assert(world.flying==!airborne);
  assert(world.target_z==(airborne?0.f:.8f));
  assert(landing_now==airborne && landing_started==1234u);
  assert(b24_game.controls.state==IM2_PLAYING);
 }
}
int main(void){
 scenario(0,0,0);scenario(0,1,0);
 scenario(1,0,0);scenario(1,1,0);scenario(1,0,1);
 puts("PASS generated G5 Circle: playing flight toggle/landing preserved; pause resume/options do not change flight or landing state (5 host scenarios, no Vita claim)");
 return 0;
}
'''
    test = temp / "test.c"
    test.write_text(harness)
    binary = temp / "test"
    includes = [HERE, ROOT / "work/src"] + [ROOT / "research" / folder for folder in
        ("b22_flight", "b22_camera", "b22_4_6", "b22_hud", "b23_missile_lock", "b21_controls", "b19/host_gameplay")]
    command = shlex.split(os.environ.get("CC", "cc")) + [
        "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic", "-O2",
        *["-I" + str(path) for path in includes], str(test),
        str(ROOT / "research/b21_controls/b21_control_lab.c"), "-lm", "-o", str(binary)]
    subprocess.run(command, check=True)
    subprocess.run([str(binary)], check=True)
