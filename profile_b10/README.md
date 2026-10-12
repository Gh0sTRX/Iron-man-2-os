# B10 — Frame Profiler / SDL presentation experiment

This is a separate, optional PS Vita diagnostic build, **not** a new game-engine port. Based on the five-suit B9 code and 12 authentic .im2v animation clips. Old B9 remains untouched.

## Why
User-supplied B8 hardware screenshots showed 18–27 FPS, CPU 8–25ms and aggregate SDL 28–29ms. That aggregate mixes pixel upload, render commands and presentation wait, so VSync is a hypothesis rather than a diagnosed cause.

## What B10 actually measures
* `AN`: time to apply already-baked original motion to model vertices.
* `CPU`: software 480x272 rasterizer + B8 target overlay time.
* `UP`: SDL_UpdateTexture time.
* `COPY`: SDL_RenderClear and SDL_RenderCopy call duration (possibly asynchronous).
* `PRES`: SDL_RenderPresent elapsed wall-time, including potential VSync wait.
* `FPS`: EMA of completed frame interval.
* `VS ON/OFF/FALL`: actual renderer flags after successful SDL_CreateRenderer; FALL means VSync requested but the selected renderer didn't advertise it.

**Controls:** SELECT toggles VSync, reconstructing SDL renderer+texture so it works without requiring newer SDL_RenderSetVSync; the application falls back to a no-VSync renderer if the requested one fails. Keyboard V toggles (desktop only). Old B9 SELECT=wireframe is moved to keyboard Z only in B10. Gameplay controls unchanged otherwise.

## Validation
- Local native C tests `b7_validate, b8_validate, b9_validate, b10_validate` pass.
- No Vita hardware FPS/tearing/input tests have yet occurred. Disabling VSync can cause tearing and may increase battery usage.
- Timing counters are approximations for API call wall-time, **not** GPU profiler numbers. Frame draw can be asynchronous; screenshots + an A/B test are necessary.
- VPK title ID: `IM2G00007` (distinct from B9 `IM2F00006`).

## Hardware test when available
1. Keep same suit, camera, and camera zoom with model idle for 15s, capture FPS/AN/CPU/UP/COPY/PRES with VS ON.
2. Tap SELECT once, wait 15s, capture same seven values with VS OFF.
3. Report whether the picture tears or stutters. Avoid treating transient measurements while renderer is recreated as valid.
4. If PRES is the bottleneck, next optimization is GPU/SDL presentation policy. If UP or CPU dominates, prioritize upload path or hardware-renderer plan instead.
