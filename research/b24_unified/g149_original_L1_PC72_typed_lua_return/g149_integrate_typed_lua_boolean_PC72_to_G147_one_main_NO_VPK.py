#!/usr/bin/env python3
"""G149 opt-in typed Lua PC72 Boolean return bridge.
Run after the canonical G147 integration script; preserve the one-game
source owner. It does NOT implement the original PC73 EQ, a renderer,
QTE completion, gameplay release, or produce a VPK.
"""
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
R = HERE.parents[2]
W = R / "work"
D = W / "b24/b24_unified"
M = W / "src/main.c"
CM = W / "CMakeLists.txt"

def once(source, old, new):
    count = source.count(old)
    if count != 1:
        raise ValueError(f"G149 canonical G147 source drift: {count} matches for {old[:90]!r}")
    return source.replace(old, new, 1)

def run():
    if not M.is_file() or not CM.is_file():
        raise FileNotFoundError("G149 requires assembled canonical G147 one-Vita main")
    main = M.read_text()
    cm = CM.read_text()
    required = (
        "B24_G145_SOURCE_MISSION_AUDIO",
        "B24_G146_SOURCE_2010_QTE_1456",
        "B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE",
    )
    if any(item not in cm for item in required):
        raise ValueError("G149 requires canonical G145/G146/G147 one-game chain")
    if "B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE" in cm:
        raise ValueError("G149 cannot be applied twice")
    for invariant in (
        "b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
        "b24_unified_tick(&b24_game,&b24_obs);",
        "b24_g83_timeline_tick(",
    ):
        if main.count(invariant) != 1:
            raise ValueError("G149 requires one gameplay/physics/timeline owner: " + invariant)
    main = once(
        main,
        '#include "../b24/b24_unified/b24_g147_authentic_tutorial_actor.h"',
        '#include "../b24/b24_unified/b24_g147_authentic_tutorial_actor.h"\n'
        '#ifdef B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE\n'
        '#include "../b24/b24_unified/b24_g149_native_lua_bool_return.h"\n'
        '#endif',
    )
    old = """  g147_native_Lua_PC72_queried_only=1;
  g147_native_PC72_original_result=
    b24_g147_lua_IsTutConfirmed_native(&g147_original_L1_source_tutorial);
  return 0;"""
    new = """#ifdef B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE
  B24G149LuaBooleanReturn lua_return={0};
  if(!b24_g149_capture_original_PC72_boolean(
      e,&g147_original_L1_source_tutorial,&lua_return))return 0;
  /* Successful native Boolean FALSE is a completed Lua CALL, not a
   * failed scene binding. G137 still STOPS at the original PC73 EQ. */
  g147_native_Lua_PC72_queried_only=lua_return.result_is_valid;
  g147_native_PC72_original_result=lua_return.lua_boolean;
  return lua_return.result_is_valid;
#else
  g147_native_Lua_PC72_queried_only=1;
  g147_native_PC72_original_result=
    b24_g147_lua_IsTutConfirmed_native(&g147_original_L1_source_tutorial);
  return 0;
#endif"""
    main = once(main, old, new)
    cm += """
# G149 source-faithful Lua PC72 native IsTutConfirmed typed bool result.
# PC73 Lua EQ and gameplay release remain unresolved; NO VPK.
option(B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE "Record source Lua PC72 bool separately from callback ACK" OFF)
if(B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE)
 if(NOT B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE)
  message(FATAL_ERROR "G149 requires original G147 tutorial source gate")
 endif()
 target_sources(im2_beta PRIVATE
   "b24/b24_unified/b24_g149_native_lua_bool_return.c")
 target_compile_definitions(im2_beta PRIVATE
   B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE=1)
endif()
"""
    D.mkdir(parents=True, exist_ok=True)
    for filename in ("b24_g149_native_lua_bool_return.h", "b24_g149_native_lua_bool_return.c"):
        shutil.copyfile(HERE / filename, D / filename)
    M.write_text(main)
    CM.write_text(cm)
    if list(W.rglob("*.vpk")):
        raise RuntimeError("G149 NO VPK contract violated")
    print("G149 PC72 true/false native return captured by one Vita main. PC73 still unresolved. NO VPK.")

if __name__ == "__main__":
    run()
