# Iron Man 2 Vita — B22.4–B22.6 Thrusters, RUSH FX and Soft Melee Camera
Date: 2026-10-13. **HOST TESTED RESEARCH, NOT VITA SOFTWARE.**

This private repo module implements the user's exact confirmed design using new portable C11 logic. It does not recover or claim to reproduce proprietary 2010 Gameloft particle assets/shaders or original engine physics. Real VPK B17 remains pending on-device test; do not start Actions or create another VPK until hardware feedback. B15 known-good rollback preserved.

## Strict stage rules

| Flight stage | Feet L+R | Palms L+R | Back L+R | RUSH edge streaks |
|---|---|---|---|---|
| Ground | No | No | No | No |
| Stage 1 HOVER | Yes | No | No | No |
| Stage 2 CRUISE | Yes | Yes | **NO** | No |
| Stage 3 RUSH | Yes | Yes | **YES** | Yes |

Back is **exclusively RUSH**: exiting RUSH immediately stops and purges every back emitter particle, even on a zero-delta frame, with no lingering back jet in Stage 2. Entering RUSH creates immediate paired back flares; lift-off creates paired foot flares when their sockets are valid. This state matrix was explicitly approved by the user, and regression asserts it.

## Separate modules

1. `im2_thruster.[ch]`: bounded 128-particle world-space simulation; six local position + exhaust-direction sockets passed in from caller with `valid` bit. Invalid or missing sockets create NO particles; never synthesize unverified original armor exhaust anatomy. Applies exact B22.2 flight quaternion/root world transform to emission. Original skinned pose/rig/BDAE attachments NOT hooked up to Vita. Host unit-test uses **synthetic sockets** only. Iron Man cyan/blue and War Machine amber are optional new aesthetic choices, not verified original colors.
2. `im2_speed_fx.[ch]`: maximum 20 cheap 480x272 screen-edge streaks, RUSH only. Screen center/reticle remains untouched. No full-screen motion blur or actual temporal framebuffer copies. The 64 to 72 to 80 degree FOV stage system already exists in B22.3 camera; do NOT add a second FOV increase when integrating.
3. `im2_melee_focus.[ch]`: additive/non-destructive view compositor. Only when a *melee attack* actually starts AND a visible/alive enemy is nearby (4.5 arbitrary prototype units) AND on ground/hover; framed midpoint and moderate dolly/FOV adjust, no player-turn hijack. Enemy mere proximity never activates it. Right-stick manual look reduces focus influence to 40%. Normal shoulder/chase camera persists underneath, returned to smoothly after combo/target loss. This is not target-lock/collision/real melee animation.
4. `test_b22_4_6.c`: exact stage mask, immediate back/entry and no-back-on-return assertions, memory budget, off-screen guard and center-reticle exclusion, real B22.3 camera compositing, plus 20,000 deterministic randomized cases.
5. `demo_b22_fx.c`: 12-second interactive-loop simulation CSV of stage/emitter/motion/camera decisions; NOT a screenshot/video or measured Vita performance.

## Reproducible host build (from research/b22_4_6)

```bash
gcc -I../b22_flight -I../b22_camera -std=c11 -Wall -Wextra -Werror -pedantic \
  -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer \
  ../b22_flight/im2_flight.c ../b22_camera/im2_camera.c \
  im2_thruster.c im2_speed_fx.c im2_melee_focus.c test_b22_4_6.c \
  -lm -o test_b22_4_6
./test_b22_4_6
gcc -I../b22_flight -I../b22_camera -std=c11 -Wall -Wextra -Werror -pedantic -O2 \
  ../b22_flight/im2_flight.c ../b22_camera/im2_camera.c \
  im2_thruster.c im2_speed_fx.c im2_melee_focus.c demo_b22_fx.c \
  -lm -o demo_b22_fx
./demo_b22_fx > b22_fx_trace.csv
```

Developer's local version compiled and passed both GCC ASan/UBSan and optimized tests; local test suite 20k fuzz passed, and 12-second CSV generated. The complete EXACT locally tested files, inherited B22.2/B22.3 dependencies, test and trace are backed up in session artifact `IronMan2_B22_4_6_Thrusters_Rush_Melee_HostLab.zip` (SHA256 `002cd45bf6af8e8f2ca327249739bd21ada7960c279b3149c2cb538d3715bb5c`). Connector-authored copies should receive independent CI/compiler validation before deployment. No VitaSDK build or device frame-time proof exists.

## True original-asset/Vita integration BLOCKERS

- Obtain original iOS IPA data again and inspect particle/sprite atlas and FX event/config assets before claiming source-exact flames/particle colors. Current private research bundles have not yielded **verified original thruster particle texture files**. Exact back thruster bones/sockets, especially Mark V, Stealth and War Machine, have NOT been verified; do not substitute arbitrary shoulder offsets without testing.
- Hook verified hand/foot/back geometry per skinned IM2V pose. Existing B16 palm mapping can help but cannot be reused as original jet mount without validating orientation. Mesh yaw/pitch/roll and actor velocity must be in the same coordinate convention.
- Render particles with inexpensive Vita GPU camera-facing cards/limited draw calls; measure old SDL_UpdateTexture wall-time bottleneck (~29 ms observed B10) rather than making promises of 60 FPS. Profile frame/CPU/UP/COPY/PRES.
- Wire real B19 target IDs/visibility, original melee animation clips, B21 R-shoot/L-missile lock and B22 HUD with camera focus in one future game build. Avoid any forced camera snap during melee, combat shooting, flight or lock-on.
- B17 hardware test remains FIRST deployment gate. Only after it: combine modules in a single meaningful gameplay VPK, preserving B15/B17 untouched.
