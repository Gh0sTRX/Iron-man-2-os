# G70 — REVERSE MERGE B24 G9 GAMEPLAY + G68 C1L1 SOURCE MAP
Date: 2026-10-16. **SOURCE-ONLY BRIDGE**. No G70 merged VPK or physical validation yet.

## Owner decision and architecture
User explicitly prefers the last successful original B24/B17 gameplay/animation/HUD engine as authority, **not** the new G68 placeholder/gameplay. Only import the one component G68 did better: authored original C1L1 city materials, world scene and source triangle collisions. Never rebuild the entire animation/player system on top of G68's 7-clip/2-wave alpha.

Legacy anchor:
- G9 complete VitaSDK successful https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38623462548
- `B24 GPU G9`: 5 original suits, 363 IM2V original rigged sample files, six original WM gun streams, B17/B14 flight/melee/combat, B24/B22 HUD/camera and original player weapon stage policies.
- Prior G9 **CI success** != physical-device gameplay guarantee; actual latest visually verified world is G68.

Ground-truth G68:
- Real Vita photos supplied by owner, original Mark V moving/standing/flying, 59 FPS snapshot and 237/256MB PSVshell MEM, 112/112 VMEM snapshot, source C1L1 world usable. G68 standalone combat/pose mechanics unacceptable replacement.
- G68 successful CI https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38885906487 ; owner asset artifact `IRONMAN2_B24_G68_MARK_V_MEDIA_MAYHEM_SOURCE_CANDIDATE_VPK`. G68 owner-verified world 22,441 source triangles, 31 source atlases and 1,910 G59 real collision triangles.

## What G70 has implemented
1. `research/b24_unified/b24_gpu_g68_city.h/.c`: VitaGL G66M/G66T scene renderer. Opens **exact original hardware-proven** atlas files and 32 source city batches in old B24 single-GPU context. No second GPU ownership, gameplay input, pause/mission or avatar physics engine. Same G68 blending baseline; alpha/sort/shader flaws unresolved.
2. `research/b24_unified/b24_gpu_runtime.c/.h`: optional `B24_G68_CITY_BACKEND`. OLD `b24_gpu_runtime_sync_model` original five suit IM2T GPU stream, `b24_runtime_armor_draw`, native B24 HUD, flight and old B24 game tick UNCHANGED. Only swap old 2010 C1 GPU scene draw with hardware-proven G68 2010 scene.
3. `b24_gpu_g68_collision.h/.c`: load all **1,910 real G68 G59 wall/floor source triangles** into original G9 `B24C1OriginalCollision` structs; preserve OLD B24 `b24_c1_original_collision_resolve` behavior to avoid two motion engines. This is SAME SOURCE collider DATA, not identical G68 G67 collision ALGORITHM: G68 reliable multiple-height slices/floors still need stepwise integration into B14 gameplay after a merged render build.
4. `g70_reverse_merge/g70_stage_g68_source_scene.py`: copies only 33 G68 user-owned files (city 1 + original collider 1 + PVR tex 31) directly from successful VPK and validates G66 layout; never rebuilds speculative C1L1 pivot hierarchy or checks original IPA into Git.
5. `g70_reverse_merge/apply_b24_g70_scene_backend.py`: applies opt-in backend to a restored G9 B17/B24 work tree after G8 animation/gameplay patches, preserves `b14_world_tick` and B24 old main loop, replaces only G7 old 1,908 collider loading with real G68 G59 loader, updates old B14 world boundaries to G68 original source full region. Adds CMake `B24_G68_CITY_BACKEND=ON` opt-in; prior G9 builds remain default off.
6. `g70_reverse_merge/test_g70_original_1910_collision_bridge.c`: original 1,910 scene triangle load + old G9 CPU sweep host regression.

## Verified, 2026-10-16
GitHub Actions successful run:
- https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38890210223: real G68 owner VPK recovered to ephemeral runner, staged exact original city and 1910 original source collider, original G9 collision solver C host run, B24 gameplay source guard.
- https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38890332228: same + compile G70 original city VitaGL backend and source collision adapter as native **PS Vita ARM** objects in `vitasdk/vitasdk:2026.08`. Both passed.
- This verifies source modules, NOT a linked, packaged or device-tested FULL G70 game. No new G70 VPK exists.

## Next active gates, strict
- Reproduce earlier successful G9 full build from original overlay tree using original `.github/workflows/b24-gpu-g9-original-city-combat-beta.yml` as authoritative, but use new separate G70 workflow/branch; do not overwrite G9/G68 known-good runs.
- Get exact owner G68 `G66_city.g66m`, 31 `G66_city_tex_*.g66t`, `G66_original_collision.g66c` into G70 VPK under `assets/`. Compile with `-DB24_ENABLE_GPU=ON -DB24_ENABLE_NATIVE_HUD=ON -DB24_G68_CITY_BACKEND=ON`. Unique PS Vita title ID. Host engine input/suit/hud/weapon smoke tests first.
- Do NOT claim physical hardware convergence before actual G70 Vita screenshot/video and button/movement test. Old G9 B14 motion coordinate/ground height and new G68 map physics might not align. Users deserve working collision, no wall tunneling, proper grounded ramp height. Bring over G67 multi-z player capsule and source-floor snap with separate isolated native tests; preserve G9 controller as sole position-integrator.
- Preserve all prior 363 source sampled animations but stream them and bind directional controller states; don't preload 363 into 237MB/256MB reported memory. G69 directional source selection test already passed.
- GPU shader/alpha/ambient original 2010 not yet recovered: 7 source atlas groups have alpha. No sky cubemap/source native shader guarantee. Report diagnostic rendering deficiencies precisely.
- Reconcile old B24 control bindings and input precedence, five suit selection, full stage1 hover/stage2 flight/stage3 rush, repulsor right arm, unibeam, missile lock, combos, native B24 HUD and pause. Test actual actions on Vita rather than assuming old link succeeded.
- Don't run G68 `g68_assemble.py` standalone player engine or its fake wireframe robot enemies in the combined build.

**End-state wanted by user**: G9/B17/B24 original gameplay + real G68 C1L1 map and collision in one game. No new custom game logic unless exact gaps require it.
