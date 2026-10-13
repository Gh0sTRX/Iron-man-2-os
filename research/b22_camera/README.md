# Iron Man 2 Vita — B22.3 Smooth Third-Person Flight Camera (HOST ONLY)

**2026-10-13.** This C11 camera is a *new game implementation*, not recovered 2010 iOS camera code or a Vita build. Existing B15 and B17 VPKs are unchanged.

## Camera behavior

- Ground / Stage 1 hover: over-the-right-shoulder camera, lateral offset +0.72, aim offset +0.42, camera distance 3.15, 64-degree FOV.
- Stage 2 cruise: smooth transition to centered character chase camera, distance 4.65 and 72-degree FOV.
- Stage 3 RUSH: camera moves farther back to distance 5.85 and broadens to 80-degree FOV; transition reverses smoothly when slowing.
- Exponential smooth position and stage parameters, no instantaneous cuts; yaw correction uses shortest-angle path. With right stick in use, preserve manual orbit; if released in flight, gently realign behind armor heading.
- Optional very small horizon roll tied to body banking, bounded to 1.5 degrees; no fully tilted camera. Returns camera position, target, forward/right/up orthonormal basis and FOV.
- The optional wall_hit_distance is an EXTERNAL value to be supplied by a future C1L1 world raycast. This code alone does not perform collision, obstruction tests, or a world render.

This module only **reads** the B22.2 flight state and never modifies velocity or direction. Do not feed the visual camera's smoothed yaw back into camera-guided flight physics; avoid accidental feedback loops. B22.1 missile target identity and projection need to remain stable across transitions.

## Reproduce native tests

From research/b22_camera (header dependency from ../b22_flight):

    gcc -I../b22_flight -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer im2_camera.c test_im2_camera.c -lm -o test_im2_camera
    ./test_im2_camera
    gcc -I../b22_flight -std=c11 -Wall -Wextra -Werror -pedantic -O2 im2_camera.c ../b22_flight/im2_flight.c demo_camera_stage.c -lm -o demo_camera_stage
    ./demo_camera_stage > camera_12sec_trace.csv

Actual host ASan+UBSan test PASS: reversible stage changes, right-stick free-look, yaw recenter, cross-180-degree yaw, temporary obstacle-distance zoom, pitch/roll bounds, smooth player follow, 30Hz/60Hz near-equal outputs, 20,000 random input checks. Demo builds WITH actual B22.2 flight code and emits a 12-second numerical trace. This does not establish real PS Vita FPS.

## Before actual Vita gameplay integration

1. Get user's B17 hardware observations, preserve working B15 fallback and unmodified B17 VPK.
2. Adapt actual B17 head pivot, world axes, camera input inversion, renderer view/projection matrices, FOV and target marker projection. Camera-based flight guidance must use an explicitly defined physical direction, not silently chase camera state.
3. Add real scene raycast for walls and refine aim/lock and real weapon muzzle attachment projection. Profile CPU vs SDL texture upload before a scene with enemies.
4. Build ONE meaningful consolidated Vita gameplay release after B17 QA, not another cosmetic beta.

All camera distances, blend speeds and FOVs are new design estimates, not recovered original Gameloft parameters. No copyrighted source art in this module.
