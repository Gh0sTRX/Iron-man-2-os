# B22.1 Missile-only lock-on HUD lab — HOST ONLY (2026-10-13)

This is a **new PS Vita gameplay/HUD design prototype**, not a recovered or confirmed feature implementation from the 2010 iOS executable. The user's PSP-style targeting inspiration is a visual design direction, not evidence that the original Gameloft iOS game used these exact reticles or timing values. This work is NOT the planned gameplay-roadmap "B23 enemy AI milestone".

## Verified behaviors
- L must be held AND `B23_MISSILE` selected to begin acquiring a visible, unobstructed, on-screen enemy. Repulsor, Unibeam and melee do NOT trigger a persistent missile target lock. R remains proposed fire.
- Candidate eligibility: 250 world-distance units and `aim_cos >= 0.80` (provisional, configurable). Acquire duration 0.45 s (provisional), at most 0.1 s advancement per `tick` to prevent frame stalls instantly locking.
- Picks best aligned candidate; retains stable target ID despite reordered lists or a stronger target appearing, until target dies, is occluded, leaves the field of view or range, weapon switches or L releases. Switching valid targets restarts acquisition.
- A dedicated 480x272 missile-only layer draws enemy brackets, health gauge **only when HP is known**, center targeting inset, progress rail and acquired-lock glyph. Uses a classic cyan-ish color for original-layout approximation; suit-dependent Iron Man / War Machine colors for the *new optional* visor. This does not use original extracted HUD/SWF pixel art.
- `b23_prepare_b22_ui` clears old B22 weapon-agnostic lock brackets. Future compositor order: prepare B22UI -> `b22_draw_hud` -> `b23_draw_missile_hud` (only once). Non-missile aiming reticle could be provided by the gameplay renderer, but do not use this missile lock layer for other weapons.

## Native host validation
Compile from repo root:

```bash
cd research/b23_missile_lock
gcc -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  b23_missile_lock.c test_b23_missile_lock.c -lm -o /tmp/test_b23_missile_lock
/tmp/test_b23_missile_lock
```

Actual result: `PASS B23: missiles-only acquisition, stable ID, loss/reset, elapsed-time guard, B22 adapter, 300 framebuffer guard tests`. Testing compiles against the exact existing B22 UI *header* API, not the Vita game. No VitaSDK/real device code was built, no VPK released, and missile damage/projectile homing is NOT implemented.

## Next integration gate
After user's outstanding B17 physical test: merge into B21 weapon/controller state (including D-pad selection and L hold) and B22 UI compositor, connect target selection to B19 live enemy IDs and projection/occlusion/HP. Add real 3D missile launch socket/projectile/damage and original audio only after assets are recovered. Preserve B15 known-good rollback and B17 test package; avoid repeat GitHub Actions spam.
