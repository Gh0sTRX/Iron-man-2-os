# IRON MAN 2 — KALICI DEVIR / CURRENT PROJECT STATE
Updated: 2026-10-12 (Türkiye) — authoritative cross-conversation handoff

## Source of truth
Private repo: https://github.com/Gh0sTRX/Iron-man-2-os
Primary branch: main. Keep repository PRIVATE because it contains original game assets.
Original IPAs are in the user's connected Google Drive:
- `IronMan2_1.0.0_ios_2.2.1.ipa` (248,613,763 bytes; minimum iOS 2.2.1; 32-bit ARM Mach-O)
- `Iron Man 2 iOS 3.0.ipa` (275,580,565 bytes; actual game version 1.0.3; 32-bit ARM Mach-O)
No decrypted complete original C/C++ source has been recovered. Work is reverse engineering of assets and limited ARM symbols.

## IMPORTANT REAL DEVICE MILESTONE — VERIFIED BY USER
On 2026-10-12 the user installed `IronMan2_Asset_Beta.vpk` on their real modded PS Vita and supplied a screenshot showing the in-app Mark VI textured mesh. They explicitly confirmed **ALL FOUR** playable viewer selections — Mark VI, Mark IV, War Machine, and Stealth — display successfully and can be inspected with Vita controls. This is VERIFIED HARDWARE FUNCTIONALITY, not a desktop mockup. They did not yet report a measured FPS.
The result is **a standalone PS Vita textured model viewer**, not a port of the original Iron Man 2 game. No walking, missions, flight, combat, enemy AI, game audio, rigging or original gameplay exists in this VPK.

## Latest green CI build
Workflow: `.github/workflows/vita-build.yml`
Successful GitHub Actions run #4: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38176491645
Commit: `91466c220a030c30192e745412b9a1b8a4ff5325`
Artifact: `IronMan2_Asset_Beta_VPK` (artifact ID 11715913190).
Private source archive tracked at `source/IronMan2_Vita_GitHub_Ready_CI_R2.zip`, 1,839,515 bytes.
Pipeline: unzip; check four `.im2t` models; desktop C renderer preview; official VitaSDK `vitasdk/vitasdk:2026.08` build; validate eboot.bin; upload VPK.

## Engineering details
- Rendering: software textured triangle rasterizer in C (SDL2 for display/control), internal resolution 480x272; Vita display scales to 960x544.
- IM2T contains vertex positions/UV, triangle indices, RGBA atlas.
- Four source models and original dithered PVRTC-derived textures work on real Vita.
- Initial reverse engineering extracted 49 of 207 inspected named BDAE meshes with a heuristic parser; earlier intermediate packaging sometimes counted more geometry exports. Do not equate that with full model correctness. Other geometry layouts/rigs remain unsolved.
- Y-up GLB axis was corrected for external viewers. V3.1 HTML was fixed for WebGL-less iPhone preview, confirmed by user.
- User said Meshy viewers sometimes showed models not matching their appearance; model hierarchy/material/rig fidelity remains open.
- IPA's native ARM code contains C++/Lua-related symbol names; decompilation is incomplete and there is no playable engine port.

## Near-term roadmap (highest value)
1. Preserve a reproducible VPK baseline and documented hardware proof.
2. Prototype 2 controls in a NEW, separately named Vita test VPK: left analog movement, circle takeoff/land, R ascend and L descend, optional camera right analog. This is an ORIGINAL implementation using original game assets; **do not call it the original gameplay port**.
3. Verify this VPK via GitHub Actions and real PS Vita. Do not overwrite the known-good beta accidentally.
4. In parallel inspect original IPA `.anim` rig/hierarchy; move toward authentic run/flight animations. Eventually port level geometry, collision, enemies, missions, etc.
5. Keep project docs and version states updated at each verified milestone. Never claim background tasks ran after the chat ended.

## Continuation recipe for a fresh ChatGPT chat
Ask: "Continue the Iron Man 2 PS Vita reverse-engineering project. Read the private GitHub repo Gh0sTRX/Iron-man-2-os, especially PROJECT_HANDOFF.md and the latest GitHub Actions run. Four armors work on actual PS Vita. Continue the next verified gameplay prototype; preserve the existing VPK."

## User preference
Prioritize visibly useful milestones, efficient engineering, rigorous verification and straightforward instructions (the user isn't a programmer). The user mentioned future selectable fan-made armor packs; defer until engine/movement is established.

## NEW MILESTONE — Flight Beta B4 CI GREEN (2026-10-12)
- NEW movement + hovering prototype code was implemented as an isolated overlay in `flight_b4/flight_b4_overlay.zip`. It replaces only src/main.c, src/renderer.c, src/renderer.h while reusing the original protected model assets from the baseline source archive.
- Separate workflow: `.github/workflows/flight-b4.yml`.
- Successful workflow: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38226936652 (run #2).
- Produced downloadable artifact `IronMan2_Flight_B4_VPK` (artifact ID 11736559138).
- Independent VPK: `IronMan2_Flight_B4.vpk`; verified SFO `TITLE_ID=IM2B00002`, `TITLE=Iron Man 2 - Flight B4`, `APP_VER=01.02`; it does NOT replace existing `IM2A00001`.
- VPK archive includes eboot.bin and all four original derived model .im2t files. Archive CRC test passed. GitHub CI checked source, desktop rendering, VitaSDK and ZIP structure.
- B4 controls: left analog move, right analog camera, Circle toggle hover/takeoff/land, R/L climb/descend, D-pad zoom, Cross change armor, Square wireframe, Triangle reset, Start exit.
- B4 on actual Vita hardware is NOT YET TESTED. Ask user to install, send screenshot and report controls & FPS. Preserve known-good original asset viewer.
- The B4 'flight' is an original basic movement and hover simulation with STATIC ARMOR POSE, NOT authentic Iron Man 2 flight animations, missions, enemies, collision, or port of engine.
- Next engineering priority after hardware verification: reverse engineer rig/animation BDAE from the original IPA; compare https://github.com/fata1error404/oac-bdae-viewer and https://github.com/lOlbas/Game-Engines-Filetypes-Reverse-Engineering/tree/master/engines/Gameloft/bdae . Their BDAE format revisions may differ; adapt to OUR files before assuming compatibility.


## REAL DEVICE B4 VALIDATION — USER REPORT 2026-10-12
- The user **installed and ran** `IronMan2_Flight_B4.vpk` on real PS Vita. Screenshot shows War Machine armor in the application, heading `VITA FLIGHT B4`, `FLIGHT MODE`, coordinate/altitude HUD, FPS overlay reading `14`.
- User confirms switching between `GROUND MODE` and `FLIGHT MODE` is **seamless**. In flight mode the armor rises slightly and bobs up/down but remains upright in the original static pose, without articulated arms/legs, character flight pose or engine/thruster particles.
- User-reported performance: approximately **13–15 FPS**. This is the new measured device baseline. Do not claim B4 flies with original game animations.
- Flight B4 is a successful **hardware-tested movement state prototype**, but is too slow for satisfactory actual gameplay.
- NEXT PRIORITIES: optimize software rasterizer and presentation pathway; use *actual Vita* frame-rate measurements to validate any gain; then recover authentic rigging and flight animation from original BDAE/ANIM. Optimize before loading levels/enemies. Keep B4 and baseline VPK unchanged as rollback versions.
- If this project resumes in a fresh conversation, do not ask user to repeat these details: check repo docs and build/run the next independent optimization test variant. Do not pretend the project is running in background.


## B5 PERFORMANCE TEST READY (built 2026-10-12; hardware test pending)
- GitHub commit `0022dd5badd3790828c1f8d4b9fdde47ef631709` introduced a NEW, isolated optimized rasterizer overlay `performance_b5/b5_optimized_renderer.zip` and separate workflow `.github/workflows/performance-b5.yml`.
- Successful GitHub Actions workflow `Build Iron Man 2 Vita Performance Beta B5`: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38230545688 (all build, asset, desktop render, VPK verification steps green).
- Artifact `IronMan2_Performance_B5_VPK`, ID `11737869856`; actual `IronMan2_Perf_B5.vpk` 2,958,871 bytes; SHA256 `f94c00beb9b7226d2cefad19681a3fc7f3d93e9374be200771899e9310ab5b01`. VPK archive CRC verified. `TITLE_ID=IM2C00003` distinct from B3 and B4; includes all four .im2t and eboot.bin.
- B5 code improves inner triangle raster loop with incremental barycentric coordinate/depth/texture calculations, reduces expensive per-pixel calls while retaining perspective-correct texture mapping.
- Desktop test at fixed camera: FOUR models match B4 image within 0–1 changed pixels per model (excluding HUD). Across 9 repeated native benchmarks the median per-frame raster time improved by about 1.3x–1.5x. This is **NOT** a measured Vita performance gain.
- New upper-right performance HUD shows `FPS`, `CPU NNMS` (CPU 3D raster), `SDL NNMS` (texture upload + present). This diagnostic will identify the 13–15fps B4 bottleneck.
- **HARDWARE TEST B5 STILL PENDING**. Next ask: install B5 beside B4, wait 15 seconds with War Machine/Mark VI idle in same camera settings, report three numbers FPS/CPU/SDL and if flight mode remains stable. Do not promise 30/60 FPS until measurements.
- True skeletal animation / hand thrusters are not restored. Still independent prototype, not original game port.


## ANIMATION TABLE DISCOVERY — 2026-10-12 (while user away from device)
- Verified `anims` in original iOS v1.0.0 IPA: **972 .anim records**, each leading length-prefixed name table parsed successfully (972/972).
- 248 `IronMan*` clips, 56 `Warmachine*` clips. Key originals: `IronMan_Aim_Float_idle.anim`, `IronMan_Air_land.anim`, `IronMan_Aim_Ground_move_F.anim`, `Warmachine_Aim_Fly_M.anim`.
- Bone-name mapping: IronMan float idle has 38 name strings; 31/37 non-path names occur in both Mark IV and Mark VI BDAEs. WarMachine flight has 42 strings; 41/41 non-path names occur in WarMachine BDAE. Contains `Bip01`, limb joints and `Gun01`.. `Gun04`.
- This is NOT a keyframe decoder, skinning implementation, or original animation reproduction.
- Reproducible script + full 972-entry inventory (file names/sizes): `research/IronMan2_Animasyon_Tarama_2026-10-12.zip`. Findings: `research/ANIMATION_AUDIT_2026-10-12.md`.
- Next research: decode original per-bone keyframe data and skeleton-parent graph, then skeletal weights, after prioritizing actual PS Vita B5 profiling (CPU vs SDL) when user returns. No new Vita install is needed to do that offline.


## B6 MAJOR BREAKTHROUGH — FULL ANIMATION TRANSFORM STREAMS (2026-10-12)
- User authorized continued technical progress. Original `.anim` streams for **both complete iOS IPAs** were reverse engineered end-to-end: iOS 1.0.0 **972/972** valid, iOS 1.0.3 **989/989** valid. Every clip's bytes consumed with no leftovers; all names and transform channels parsed.
- Both IPAs share **972 byte-identical clips**, while iOS 1.0.3 adds **17 iPad civilian clips** (man1/woman1). These are not Iron Man armor additions.
- Format: for each named joint, position channel constant 3*f32 or dynamic signed i32 timestamp+3*f32; next, for each named joint, quaternion channel constant 4*i16 or dynamic signed i32 timestamp+4*i16. Quaternion normalized by 32767. Spider enemy clip has -66/-33ms preroll. 1.0.0 contains 962,221 keyframe/static samples (5419 animated position and 18,619 animated rotation channels), 1.0.3 contains 983,310 samples.
- A functional **C11 .im2a loader/player** with normalized interpolated bone positions/quaternions was compiled under GCC with -Wall -Wextra -Werror, passed 45 sample tests and 5 exact binary reserializations. Six example clips + conversion scripts, both full CSV inventories and an offline local joint quaternion motion inspector HTML are saved.
- **New immutable source bundle** `research/B6_Animation_Decoder_Runtime.zip`; technical report: `research/B6_ANIMATION_DECODER_REPORT.md`; commit `2d522aaf99c9ea6d1481b2047949c86473fee0a3`. Nothing changed B4/B5 versions.
- **NOT YET accomplished**: animating 3D armor itself. Missing original BDAE skeleton parent hierarchy, bind matrices and per-vertex skinning weights; quaternion convention orientation needs 3D confirmation. This is a data/runtime breakthrough, **not a working B6 VPK**. Do not claim otherwise.
- Next crucial engineering step: parse bone hierarchy, transforms and skin weights from `Iron_man_mark6.bdae` or `warmachine.bdae`, connect one of the newly decoded motion tracks, then compile isolated actual animated Vita hardware test. B5 FPS/CPU MS/SDL MS hardware test still pending.
