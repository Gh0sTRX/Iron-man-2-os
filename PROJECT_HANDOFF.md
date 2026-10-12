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


## B6 ORIGINAL BDAE RIG RECOVERY — 2026-10-12
- Continued analysis reached a SECOND B6 breakthrough: original version `0,0,0,133` BDAE scene nodes are 72-byte records: node-name u32 at +0, pos 3*f32 at +0x0C, quaternion 4*f32 at +0x18, scale 3*f32 at +0x28, child count u32 at +0x34 and absolute children array pointer at +0x38; children contiguous 72-byte records.
- Verified real **96 nodes for Iron Man Mark VI and 112 nodes for War Machine** with complete parent-child graph, valid local transforms and no cycles/duplicate names.
- Bound real decoded .anim channels to those named nodes, evaluated true graph-propagated positions and orientations with quaternion composition. Produced 31-frame **diagnostic moving skeleton GIFs** for `IronMan_Air_land.anim` and `Warmachine_Aim_Float_idle.anim`; animations have changing joint positions as expected.
- Rig prototype code + JSON + GIFs: `research/B6_Rig_Hierarchy_Prototype.zip`; report `research/B6_RIG_PARENT_HIERARCHY.md`; commit `985c04b5d57c72f5e1c6ae2aee4ac357491679cb`.
- **Still no skinned 3D armor animation nor new B6 VPK.** Missing vertex joint indices/weights, bind-pose inverse matrices and mesh-node association. Do not misrepresent skeleton preview as textured original-game animation.
- Priority: reverse engineer skinning layout in Mark VI / War Machine BDAE and apply B6 animations to existing Vita armor renderer. Preserve B4/B5. Actual B5 FPS/CPU/SDL hardware values remain unknown.


## B7 SKINNING BREAKTHROUGH (2026-10-12) — AUTHENTIC TEXTURED VERTEX DEFORMATION
- Original Iron Man 2 iOS 1.0.0 BDAE v0.0.0.133 **skinning tables are recovered**, not guessed.
- Original Iron Man Mark VI (802 vertices / 970 triangles): 25 bone palette entries, 945 total joint influences, 659 one-bone + 143 two-bone vertices, 19 unique weight floats. Descriptor offset 0xB848.
- Original War Machine (1,292 vertices / 1,410 triangles): 29 palette entries, 1,484 influences, 1,100 one-bone + 192 two-bone vertices, 15 unique weight floats. Descriptor offset 0x12A28.
- Skin descriptor has bone name pointers, a float32 4x4 inverse bind matrix for each palette bone, palette weight values, a uint8 per-vertex influence-count array, and joint-index/weight-index u16 pairs.
- ACTUAL bone labels: scene node offset+8 maps e.g. Bone1->Bip01_Head-node and Bone11->Bip01_L_UpperArm-node, fully resolves all palette bones.
- CRITICAL B6 CORRECTION: original scene/animation quaternion [x,y,z,w] vector parts require conjugation [-x,-y,-z,w] for our conventional transforms. Previous B6 diagnostic GIFs used incorrect quaternion sign and should not be trusted as final visual poses. The corrected joint hierarchy yields world_rest[joint] * original_inverse_bind[bone] == identity to maximum coefficient ~1.02e-5 for BOTH model skeletons. This verifies rig/bind mapping exactly.
- Original .anim keyframes are now applied to actual fully textured meshes via LINEAR BLEND SKINNING, validated in Mark VI landing and hover, War Machine hover/fly. Generated animated preview GIFs from CPU-rendered 3D (NOT AI-created): IronMan_Original_Hover_Skinned.gif, IronMan_Original_Landing_Skinned.gif, WarMachine_Original_Fly_Skinned.gif.
- Separate, CPU-friendly independent Vita demo B7 authored. Six original animations baked at 20 fps from authentic .anim + bone influences: Mark VI idle-hover, walk, landing, War Machine idle-hover, walk, forward flight. Files .im2v hold per-frame vertex coordinates, so Vita plays original precomputed poses cheaply; not yet a native Vita runtime skeletal animation parser. Mark IV/Stealth intentionally static in this beta.
- New app/title ID IM2D00004, base B4/B5 not overwritten. Source: `skinning_b7/b7_vita_overlay.zip`; reproducible Python analytical tools + GIFs: `research/B7_Skinning_Tools.zip`. Overview: `research/B7_SKINNING_OVERVIEW.md`.
- The new workflow `.github/workflows/animation-b7.yml` ran. First job 38238551244 failed linking SDL2 backend platform stubs, NOT code compile. Follow-up run 38239085595 adds available Vita SDK SDL/graphics/audio/dialog/motion link libraries. Check current result in GitHub Actions; only declare B7 VPK build successful after green CI.
- Real PS Vita B7 **NOT YET TESTED**, pending successful build and user's device test. B4 measured 13-15fps; B5 actual measurements still needed.
- Next step after B7 hardware pass: optimizations of software rasterizer or native Vita GPU, blend original animation transitions smoothly, authentic flight/repulsor effects, and first level/collision.


## B7 CI SUCCESS — INDEPENDENT AUTHENTIC ORIGINAL ARMOR ANIMATION VPK (2026-10-12)
- Third independent B7 VitaSDK CI iteration **SUCCESS** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38239658333 . GitHub run ID `38239658333`, successful build artifact ID `11742861217`, name `IronMan2_OriginalAnimation_B7_VPK`. First B7 CI `38238551244`, second `38239085595` failed at SDL2/vitaGL static linker symbols; resolution was grouped GNU ld static library linker flags and optional VitaSDK stubs in workflow commit `8210fa163a4d562dbaaac7946061e570a040400b`.
- The actual VPK `IronMan2_Anim_B7.vpk` was extracted from GitHub artifact and ZIP CRC verified. **4,308,620 bytes**; SHA256 `e868410da6b1f1abbf4caeb2e314f68e9a40e01720e3e640a31342078a3eb718`. Contains `eboot.bin`, four `models/*.im2t`, six `animations/*.im2v`, SFO verified app ID **`IM2D00004`**, title "Iron Man 2 - Anim B7", version 01.04. It installs beside B4 and B5 (no replacement).
- Six independently rebuilt, original IPA-keyframed textured-skinned motion payloads: MarkVI hover 33x802; walk 19x802; land 17x802, WarMachine hover 33x1292; walk 19x1292; fly 33x1292. Animation storage is **pre-baked at 20fps**, not live Vita bone quaternion skinning; original motion data produced them. MarkIV and Stealth remain static in this build. Ground/flight original B4 controls maintained.
- All six archive resources passed binary header/length/frame validation and native C restore test; four assets passed, VitaSDK compiled; GitHub successful artifact upload.
- **B7 NOT YET TESTED on actual PS Vita hardware**, so FPS, character animation visibility, performance and fluidity are unknown. Please ask user to install new B7 VPK, choose MarkVI/WarMachine, test walk, Circle ground/flight, WarMachine forward fly, landing, and send screenshots/FPS + CPU MS/SDL MS. Ask specifically if zırh arms/legs genuinely move and any deformations/crashes. Compare B4 ~13–15fps and B5 unknown. Do not declare full game port.
- Latest correct code snapshot: `skinning_b7/b7_vita_overlay.zip` + baseline/B4/B5; workflow `.github/workflows/animation-b7.yml`. Keep old apps as rollback.


## B8 FIRST TARGET COMBAT RANGE — CI SUCCESS; HARDWARE PENDING (2026-10-12)
- New independent prototype built from exact B7 + B5/B4 baseline. `combat_b8/b8_overlay.zip`, README `combat_b8/README.md`, workflow `.github/workflows/combat-b8.yml` tracked at commit `d0ad1335fbeb6301f894de4b3fcfd37a85fae1e9`.
- B8 implements **screen-space** right-stick aimed three-target repulsor practice, not the original game weapons: Square fires, 220ms cooldown, 21px radius hit, hit/shot counters, win state, 2D beam/spark. Ground/Flight, selected armor and six B7 original baked animation motion clips preserved.
- Right analog now aims reticle **instead of** B7 camera orbit; D-pad L/R rotates armor, D-pad U/D zooms. Left analog move; Circle fly/land; L/R altitude down/up; Cross next armor; Select wireframe; Triangle reset arena; Start exit.
- GCC C11 -Wall -Wextra -Werror native combat test PASS (miss, debouncing, 3 hits, victory, HUD). Four model assets verify. B7 native animation test PASS.
- VitaSDK CI **SUCCESS** run https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38241156963 . GitHub artifact `IronMan2_Combat_B8_VPK`, ID `11742264631`.
- Actual file `IronMan2_Combat_B8.vpk` **4,311,543 bytes**; SHA256 `1f849dbc21ce1e59bdb901fe75b58b4bfecbfe3a7b5ceb97730c01b16d43060a`. ZIP integrity passes, `eboot.bin`, 4 model .im2t and 6 original-motion .im2v found. `param.sfo` includes `IM2E00005` (new independent title ID), Combat B8.
- **B8 NOT YET TESTED ON REAL PS VITA**; the user has the actual VPK in previous chat. Request screenshots + FPS and report success/fail for three target hits and the B7 arm/leg animation. No claim that its performance improved over hardware-tested B4 13-15 FPS (B5 hardware metrics pending).
- Separate graphics/gameplay improvement track: optimization to >30 FPS and future GPU path + actual 3D ray/collision, repulsor projectile and real-world enemy/missions. B8 is a REPRODUCIBLE PLAYABLE PROTOTYPE, not a faithful port of Iron Man 2 campaign.


## USER HARDWARE VALIDATION OF B8 / B7 ANIMATIONS — 2026-10-12 15:41 TR
- User supplied TEN genuine PS Vita photos of `VITA COMBAT B8` running four armor selections, ground/flight, and poses. Confirmed **Mark VI and War Machine walking and other animation motions work on actual PS Vita**; significant B7->B8 hardware milestone. Photos visibly show articulated arm/leg movements (including flying horizontal War Machine).
- User finds Mark VI hover works but **forward flight pose/motion is absent**; War Machine forward flight works but **flight-to-ground landing clip/transition absent**. Mark IV and Stealth currently static by B7/B8 design.
- On-screen FPS from photos: Mark VI 21–23 FPS, War Machine 18–22 FPS, Stealth 27 FPS; HUD shows SDL 28–29ms almost fixed, CPU ~8–25ms varying by armor and view. These are observed snapshots, not sustained benchmarks. B4 device baseline was ~13–15.
- User requests adding **Mark V** supposedly used early in the game. Direct audit of BOTH original v1.0.0 and 1.0.3 IPA models found no asset named Mark5 but found exactly `suitcase.bdae` (53020 bytes), `LC_MC_SuitCase.bdae` (47740 bytes), `MC_SuitCase.tga` (131124 bytes) and `body_reflection_Suitcase.tga`. This strongly suggests the Mark V / suitcase armor (still requires model/texture visual confirmation before unqualified naming).
- NEXT TASK: visually verify suit-case model and texture; extract mesh/texture for Vita with consistent formats. In parallel add original `IronMan_Aim_Fly_M` (or candidate original forward flight) to Mark VI and original landing clip to War Machine; extend original animations to Mark IV/Stealth if compatible with shared skeleton and texture. Test without replacing successful B8.
