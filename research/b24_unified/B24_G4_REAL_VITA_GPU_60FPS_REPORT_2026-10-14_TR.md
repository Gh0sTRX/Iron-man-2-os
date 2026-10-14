# B24 G4 — FIRST REAL PS VITA GPU GAMEPLAY (14 October 2026) — HARDWARE-OBSERVED

## Confirmed by user's two actual on-device photos + gameplay observations
- Title: Iron Man 2 GPU B24 G4, `IM2G00029`; screenshot shows REAL Mark VI original textured high-fidelity source model in native VitaGL scene, visor/HUD drawn natively, colorful authentic C1L1 polygon geometry, and FPS overlay `60`. Another photo shows real `PAUSED` panel overlaying scene. **This marks the FIRST VERIFIED VITA RENDERED GPU B24 FRAME**; previous G1/2 splash crash, G3 false-negative init return resolved.
- User played Iron Man suits incl. War Machine on standard clocks, reports **60 FPS consistently with no noticed drops** while moving, flying, suit changing; photo FPS reads 60. Do not claim scientifically benchmarked 60 under authentic fully textured first mission; GPU-only frame accepted as real, future objective performance instrumentation still pending. No artificial overclock was enabled by user.
- Five suits display good reconstructed textured armor. User says non-WM animation mostly okay but full original animation coverage and WM flight still insufficient.
- Real defects, from photos and user playback:
  1. Sight moves from offset shoulder `(278,110)` to center `(240,136)` when changing hover→cruise→RUSH; MUST remain center always.
  2. Pause panel visible but navigation does NOT appear interactive. UI code was static `PAUSED / START RESUME / CIRCLE RESUME / CROSS OPTIONS` regardless live `B21 controls.menu` / `selected_option` / settings. Actions can be masked by raw SELECT/DPad suit/weapon logic.
  3. HUD gives no active weapon identity or actual controls. R trigger raises right arm but beam and hit VFX either invisible/unverified; Unibeam not shown, no enemies available. Do not falsely claim fully functioning combat.
  4. Scene is authentic 22,919 original C1L1 polygon geometry but MATERIAL texture atlas binding not recovered, buildings/ground are flat diagnostic colors. More wall/prop facets are shown but player currently walks/flies through them because authoritative B14 world physics never consumes GPU C1G2 triangles; DO NOT just add generic rectangular collision walls or fabricate original textures.
  5. War Machine animations need specific original-source retarget / weapon pose/suit state attention; no evidence that all 304 original source animations run.
- Note explicit screenshots come from user's chat and are **not** re-uploaded to public GitHub.

## Immediate G5 source fixes and hardware gate
- `research/b24_unified/b24_gpu_hud_native.c`: reticle independently fixed at **(240,136)** regardless stage; weapon identity HUD `REPULSOR / UNIBEAM / MISSILE / MELEE` from B23 weapon state, controls hints without implying projectile is visible. Interactive real B21 **Options** page GPU UI with selected row and current setting values, not placebo/static menu text.
- `research/b24_unified/apply_b24_g5_gameplay_source_only.py`: after C2 and GPU owner integration, suppress raw SELECT armor and DPAD weapon events during paused menu, preserve B21 as menu state owner, latch short Cross/Circle/DPad presses during Pause just like C2 START.
- `research/b24_unified/test_b24_gpu_hud_native_mock.c`: 20k GPU HUD shape regression and options states; center reticle invariant regardless chase, missile-only lock, no per-frame bitmap. Source-specific CI for generated real B24 main.
- New candidate `b24-gpu-ux-input-candidate-g5.yml` has distinct ID `IM2G00030`. **No device verification until actual user test.** Logs and pass outcome must be checked before describing any available artifact. G4 remains gold working/reference backup.
- Future P0: genuinely interactive settings visual and Start resume; then actual material sampler→texture binding and optimized original C1G2 spatial wall collision (separate physics mesh/broadphase; no O(22919) per frame), actual VFX/right palm/Unibeam/chest rig and War Machine source animation, original missions/enemies. Preserve current user-observed 60 FPS.

## Technical warning
- GPU rendering != GPU collision. CPU B14 still simulates motion/physics; GPU VitaGL only draws full source city/suits/visor. Currently authentic city lacks a **shared CPU collider** and physics-owner integration. No unsupported assertions like "all walls collide" until tested.
