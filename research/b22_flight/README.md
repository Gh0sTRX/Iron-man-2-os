# Iron Man 2 Vita — B22.2 Directional Flight / Banking (HOST LAB)

**Date:** 2026-10-13. The project is a private 2010 Gameloft iOS asset-based reconstruction. This small flight controller is **new C11 design**, not the recovered original flight engine, a Vita build, or authenticated iOS physics. B17 real-Vita validation is still pending; no new VPK and no GitHub Actions are required for this experiment.

## What is implemented and host-tested

- World Y-up. Stateful velocity and position, smoothing through dt, stable numeric heading/yaw rotation and quaternion rotation for 3D suit and weapon sockets.
- Stage 1 (`HOVER`): fine slow camera-relative 2D translation and separate vertical up/down axis; no forced bank. Stage 2 (`CRUISE`): actual 3D climb/dive determined by camera pitch while left stick provides forward propulsion and a steering yaw offset; roll/bank in steering direction. Stage 3 (`RUSH`): higher speed and greater allowed bank, same flight steering, with visual pose blend weight.
- Analog magnitude enter 0.78 / exit 0.68 hysteresis avoids stage jitter, while actual threshold also requires forward component. Temporary values, not original gameplay constants.
- Body pitch/roll smooth with exponential correction; yaw shortest arc ±π; left turn banks left, right turn banks right, return to neutral does not snap instantly. Camera-roll hint constrained to ±3 degrees; **camera rig integration itself not implemented**.
- Collision placeholder is only a configurable Y floor/ceiling clamp. It cannot replace the actual level geometry, walls or fly boundaries recovered from `BCLARA`.
- Pose hints `HOVER`, `AIR_MOVE`, `FLY_F`, `RUSH` are **selection output**, NOT real `.im2v` animations connected to this host module. Existing pre-baked B17 motion data is untouched. Mark IV/Mark V/War Machine animation compatibility needs real hardware QA.
- Quaternion composed Yaw(Y) * Pitch(X) * Roll(Z) for local +Z forward / +X right / +Y up. `socket_world()` is intended to rotate the actual hand/chest/shoulder attachment points along with the flight mesh, but individual local coordinates are not recovered or connected here.
- Current default is *camera-guided arcade flight* (left stick steers/thrusts, right-stick camera pitch steers climb/dive). A later optional *direct-nose/pilot* scheme can map analog vertical directly to pitch **only with an explicit cruise throttle memory** so it doesn't break B15 forward movement or stage thresholds.

## Local repeatable tests

```bash
gcc -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  im2_flight.c test_im2_flight.c -lm -o test_im2_flight
./test_im2_flight

gcc -std=c11 -Wall -Wextra -Werror -pedantic -O2 \
  im2_flight.c demo_im2_flight.c -lm -o demo_im2_flight
./demo_im2_flight > flight_12sec_trace.csv
```

Actual GCC ASan+UBSan host test: **PASS**, verifies stage hysteresis, physical climb and descent, left/right bank sign and root orientation, recovery and RUSH, floor/ceiling, stable 180° yaw boundary, transformed sockets, 30 vs 60 Hz comparability, 20,000 deterministic input cases with NaN/Infinity guards. **These tests do not prove Vita FPS or faithful source-engine steering**.

## Integration gates and known B17 conflict

B17/B15 flight relies on the existing renderer input and 3-stage mapping; a later integrated branch must check actual coordinate conventions, root pose and camera inverted-axis flags. The proposed B21 Vita mapping uses **R fire, L missile lock, D-pad up/down fine altitude**. Do not accidentally retain old B17 R/L vertical movement at the same time. `B22.1` missile lock center reticle must remain screen-space despite body bank, with actual projected target ID/world origin unaffected by camera auto-snap.

Before releasing the *one consolidated* B17-successor VPK: user hardware feedback on B17, host B19/B21/B22 regression, GitHub VitaSDK build, explicit rendered viewport screenshot, real device FPS/UP phase and visual flight trials. **B15 remains a known working fallback.**
