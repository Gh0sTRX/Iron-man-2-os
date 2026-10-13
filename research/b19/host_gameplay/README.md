# B19 portable game-loop seed — host verified, NOT a Vita game

File paths:
- b19_gameplay_core.h — tiny C11 state/event interfaces.
- b19_gameplay_core.c — deterministic two-wave prototype, enemy approach, player HP/shield, 3D world-space ray/sphere hit, shot cooldown, win/fail/retry and event dispatch.
- test_b19_gameplay.c — host unit/regression tests covering miss, cooldown, five kills across two waves, wave transition hit entity ID, shield depletion, failure and restart.

## Actual validation (2026-10-13)

Locally compiled native C11 with:

    gcc -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer b19_gameplay_core.c test_b19_gameplay.c -lm -o b19_host_tests
    ./b19_host_tests

Output:

    PASS B19 native gameplay: miss/cooldown/ray, 2 waves, 5 kills, win/fail/restart, shield, events

**Honest boundary:** This code implements a deterministic standalone PROTOTYPE state loop, not game rendering, true projectile collision, original NPC AI, original audio, source BCLARA mission graph, real enemy meshes or a VPK. Enemy HP, map coordinates, cooldown, speed and wave size are placeholders. Enemy attacks currently apply deterministic range/timer-based immediate damage; real actor-projectile trajectories, animation timings and world collision are to be integrated later from recovered sources. Drowning/water, collision with C1L1, time-step accumulator for native display FPS, inventory and mission restore still need work.

## Integration path after the user reports the real-device B17 test

1. Bind game player position to existing B17 world coordinates at a deterministic simulation tick.
2. Use b19_pop_event to dispatch render/SFX/UI events, keeping audio engine separate.
3. Recover an original Drone_Army, Drone_Navy or Drone_Floating skinned .bdae model and bake original idle/move/attack/hurt/death before claiming a true enemy.
4. Add physics/geometry and actual enemy projectile object; replace immediate enemy range damage.
5. Join to small original C1L1 real map with GPU 3D render and collision.
6. Extend objective/wave data to decoded BCLARA objects before claiming original first mission.
7. Re-run host Debug+ASan/UBSan, integrate VitaSDK compilation in a single non-spam run, preserve B15/B16/B17.

The user explicitly cannot test Vita yet. Do not generate a new B19 VPK just to show prototype boxes/spheres; next VPK must make a meaningful visible/interactive improvement over B17.
