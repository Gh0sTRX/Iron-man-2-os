# Iron Man 2 (2010) — C1L1 Map Viewer M1 — PS Vita device QA

**15 October 2026.** User explicitly requested a real VPK because all previously provided host HTML/GIF previews were not useful/interactively responsive on their phone. This **overrides the previous "no VPK until map complete" policy for ONE isolated viewer build**, not for reinstating full gameplay VPK iteration.

## Deliverable (native PS Vita, actual build)

- **GitHub Actions run [38762810316](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38762810316) — SUCCESS.**
- Artifact ID **11985499702**: `IronMan2_C1L1_M1_REAL_PS_VITA_MAPVIEWER_TEST_VPK`, ZIP wraps `IronMan2_C1L1_MapViewer_M1.vpk`.
- VPK size **3,864,179 bytes**, SHA-256 `10d21b28c262bb6ada51b61778b0cc2e156e4a4f8c1fcf73dae5389cd04b65cf`.
- **Separate TitleID `IM2M10001`**, display name `Iron Man 2 - C1L1 Map Viewer`, does not overwrite the user's older IM2B/IM2G port/game.
- VitaSDK Docker `vitasdk/vitasdk:2026.08` compiled Vita native ELF to eboot SELF; VPK contents validated ZIP CRC + `eboot.bin` + `sce_sys/param.sfo` and 29 package files (23 original `.c1tx` atlas, 4 source geometry/material sidecars, 2 Vita metadata/executable).
- No firmware/physical Vita boot, runtime FPS, visual screenshot, or joystick handling verified until user tests device.

## Exact original visual source

- Standalone native VitaGL renderer uses **actual original 2010** indexed C1G2 BRES world (370 meshes, 37,946 vertices, 22,919 triangles), exact native BRES candidate C1UV, authentic face/source C1MA and source-verified 94-mat C1MT with **23 actually-referenced original PVR RGBA C1TX atlases**.
- Stage-generated in CI from original owner archival IPA. Only the map/city content included, no original full IPA, no missions/anim/sound. Original Expo 40th atlas and shaders are NOT present in M1, so some original surfaces are still incomplete. Compared to G32, this is deliberately simpler.
- **Draw path** is source existing `b24_gpu_c1_draw_original_2010_world` or fallback source `b24_gpu_c1_draw_vitagl`. One VitaGL context, one swap, no SDL Renderer or doubled GPU frame. No game logic.
- Viewer orbit target starts at **source-authored MC MainCharacter local XYZ (-1.319,-6.747,25.054)**, but original actual player startup camera not verified, so camera is explicitly diagnostic and freely movable.
- Core C source: `research/b24_unified/mapviewer_m1/mapviewer.c`, build config `research/b24_unified/mapviewer_m1/CMakeLists.txt`, reproducible GHA `.github/workflows/m1-c1l1-map-viewer-test-vpk.yml`.
- This **is genuinely compiled** as native Vita VPK. Yet **native device runtime not checked**. Avoid "verified runs on PS Vita" until the user sends screenshots/video.

## Controls

- LEFT ANALOG: pan target laterally on source XY plane
- RIGHT ANALOG: orbit yaw/pitch
- L: zoom IN
- R: zoom OUT
- TRIANGLE: wide entire original geometry scene (overview)
- SQUARE: source MC MainCharacter local XYZ region
- CIRCLE: central city geometry area
- D-PAD UP/DOWN: raise/lower target altitude
- SELECT: original source diffuse / source vertex-color diagnostic mode
- START: hide/show text HUD, three/four user guidance lines.
- PS button is usual system exit. No integrated game missions, animation or combat yet.

## Explicit next user-required QA

Wait for physical Vita test: ask for close (Square), full city (Triangle) screenshots and/or error at launching (including PS Vita error code). Do not prescribe again HTML interactions in place of native test. This VPK is the first test proving visibility of recovered C1L1 on actual Vita. Next after device report: work on actual renderer issues, original Expo 40th source atlas, original untextured shaders, memory/FPS and camera culling, then return to map-first plan and audio/cutscene project roadmap. Preserve G24/G32 research, old B24 full port builds and control code.

Do not automatically claim 60FPS, finished map, or original exact shader fidelity. No second VPK unless actual hardware result requires it or user asks.
