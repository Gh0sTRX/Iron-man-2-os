# G69 REAL PS VITA DEVICE TEST — G68 USER PHOTOGRAPHS / PRESERVE MAP
Date: 2026-10-16, branch `feature/b24-unified-gameplay`.

## Device evidence (USER-SUPPLIED, 6 in-chat photographs)
- Actual hardware: user PS Vita. Title screen overlay PSVshell indicates `IM2G68001`, first real-device observations of G68.
- Multiple original G65 city surface/material shots show streets, poles, vegetation, buildings, elevated ramps, domes, rear city area. Moving player/flight shown; user confirms collision with walls and walking in the environment are **the most usable map and collisions so far**.
- True native Mark V Suitcase character visible, red/silver on ground and airborne. No textureless Mark VI swap as occurred in older beta.
- One PSVshell overlay reports **59 fps** (snapshot only), total CPU ~19%, MEM 237/256 MB, VMEM 112/112 MB, PHY 26/26 MB. Frequency CPU333/ES4111/BUS222/XBR111 MHz. This is NOT a sustained 59 FPS benchmark; other scenes and input response unmeasured. Memory margin critical; do not preload 248 source clips.
- User's authoritative QA: flight-combat, original B24 melee/combo, richer HUD, controls and other gameplay developed before G68 are **missing**; G68's two-wave prototyped target logic does not replace them. Walking animation visibly runs wrong when reversing/back strafing. Game is an impressive C1L1 free-traversal test, **NOT** finished chapter 1.
- User's map defects: near-black sky without authentic sky source shader/texture, insufficient scene/environment illumination, black blocks/background for some vegetation/material alpha PNGs and some glass/city anomalies. User otherwise strongly values **this exact G68 map/geometry/collisions**: preserve without any guessed recenter/replacement.

## Independently verified G68 original native source code causes
- `research/b24_unified/g68_media_mayhem/g68_assemble.py` G68 selects one `g68_walking` bool from all analog directions and plays clip index 1 = `IronMan_Aim_Ground_move_F.anim` for F/B/L/R. The **original per-direction clips exist**, are independently confirmed in `research/B18_COMPLETE_304_PLAYER_ANIMATIONS_CATALOG_TR.md`. G68 first seven clip pack omits all ground B/L/R and hover directional clips.
- Same assembler simplistically picks `rush` from `player.cruise` rather than real B22/B24 flight stage 1/2/3. It plays one melee clip and a basic `g68_shoot` target-damage cone in `g68_mission.h`, no previous right-arm repulsor socket, overlay, Unibeam, missile lock or original enemy rig/hit.
- Previous deeper, separately host-tested modules remain in repository: `research/b24_unified/b24_unified.c`, `b24_g8_live_original_motion.c`, `b24_g8_melee_source_chain.c`, `b24_g11_combat_stage_policy.c`, `b24_gpu_runtime.c`, `b24_gpu_hud_native.c`, `research/b22_flight/im2_flight.c`, `research/b22_hud/b22_visor.c`. Import carefully into VitaGL G68 world with single CPU physics owner and single GPU frame owner. The old separate demo is not a drop-in with guaranteed original Level1 coordinates.
- `research/b24_unified/g66_playable/main.c` sets `glClearColor(.011f,.025f,.078f,1.f)`, which explains near-black **background clear**. Original game's sky shader/cubemap and original scene visibility not reconstructed. Do not falsely call flat arbitrary sky-blue an authentic 2010 asset.
- `render_mesh` loops all 32 scene batches in original grouped order, no explicit opaque vs alpha pass sorting or depth-mask management. Actual G68 VPK checked offline: 31 city `G66_city_tex_XX.g66t`, **7 with alpha<255**, corresponding 7 source material batches and 1,282 triangles (3,846 draw vertices). Thus transparency is **present** in original packaged textures; black vegetation/decals may be ordering/alpha-test/depth-write or original compositor issue. Root cause not yet proven on hardware: before patching exact source alpha semantics confirm by A/B GPU frame.
- Other unknown original shaders e.g. Expo globe native `Material__20/21` not fully proven; black or overbright hemisphere should not be painted with invented texture.
- Uploaded G68 VPK texture mip0 straight RGBA uncompressed 10,833,920 bytes (~10.33 MiB). `VMEM 112/112` in PSVshell is a user screenshot reading, not a measured additional free allocation; ensure future texture streaming and no massive CPU/GPU duplication.

## G69 implemented source-only this conversation, before new device VPK
- `research/b24_unified/g69_device_qa/g69_motion_policy.h`: canonical source-named F/B/L/R per-state ground/hover/cruise + RUSH forward-only (other headings don't incorrectly use forward RUSH) + separate melee/fire decision, input deadzone/validation, no physics changes.
- `research/b24_unified/g69_device_qa/test_g69_motion_policy.c`: ground 4 directions, hover 4, cruise 4, RUSH cases, idle/one-shot/NaN tests.
- `research/b24_unified/g69_device_qa/g69_vpk_alpha_audit.py`: VPK read-only alpha metadata scanner, never exports source texture pixels.
- `.github/workflows/g69-original-directional-animation-host.yml`: host-only source catalog verified clips and actual G8 direction motion regression. Original G8 linkage requires adding IM2V stream, hover blend, melee chain C files; repaired in second commit. Verify latest CI conclusion before claiming success.
- No new G69 Vita VPK generated. G68 and G67 known-booting user hardware snapshots must remain untouched.

## Implementation acceptance gates for next gameplay Vita build
1. Freeze current G68 city 22,441 source faces/31 PVR and 1,910 G59 native collision faces, confirmed camera projection and bbox. Keep texture hash/batch checksum regression; do not change camera offset inadvertently. User to re-test any newly added memory.
2. Replace G68 single ground 'walk' with per-direction source Mark V BRES B13-skin original 20Hz clips and velocity/camera relative heading parity test (asset filename vs pose not necessarily proof forward axis).
3. Restore old B24 input routing (START only pause; face buttons/trigger assignments according to agreed B24 controls), detailed HUD/weapon panels, camera shoulder/right-arm aim. Integration should resolve legacy Square/L/R mapping; G68 prototype different controls.
4. Restore stage-based flight/ground/hover/cruise/RUSH and original Mark V upright/pitch/bank/yaw/smooth transition, CPU position updated once using **G67** triangle wall + floor. Restore right-arm repulsor, missile lock, Unibeam/chest emitter, melee combo/feedback, hit geometries and true original animations where proof exists. Do NOT declare old B24 functionality restored merely by linking static C functions; test actual frame and input result.
5. 2-pass alpha with opaque depth write and blended transparent depth test/disabled depth write + appropriate material sorting; texture/filter/alpha cutoff/discard only if proven by original reference. Try A/B on 7 source alpha batches. Source-backed lighting from original scene, original sky and globe sampler shaders investigated via touchHLE 1.0.0 screenshots/apitrace; can offer diagnostic ambient fallback clearly marked until exact source found.
6. Add original Mission000 triggers/camera/Deco, real Drone_Army BRES rig/AI, audio/cutscenes for authentic first mission, not fake wireframe enemies.
7. Host and VitaSDK CI must pass, then ACTUAL Vita video/screenshots, sustained FPS, memory and 10-minute travel + collisions + alpha + input + combat+HUD checklist. Any severe regression: rollback safely to G68 map baseline.

## Real G68 VPK/CI anchor
https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38885906487 (success)
Mark V 629 vertices /902 original tris /7 selected original player clips. First actual Vita user shots in conversation; not on GitHub and should not be uploaded without user authorization.
