# Iron Man 2 | G29–G32 Original C1L1 Camera, Light and 3D PVR Map Handoff — 2026-10-15

**Status: still NOT a finished first level or a Vita gameplay build.** Original iOS assets stay private. No VPK produced. User's priority remains authentic first map completion, then original armor animations/combat, and original sound & cutscenes for a playable first-level demo.

## G29: Real source camera → PositionDummy references (success)

GitHub CI: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38754980652; artifact 11983425898. Source tool: `research/b24_unified/b24_g29_original_CameraPreset_PD_CameraConfig_source_map.py`.

- All 57 original CameraPreset class objects' actual `level1.bclara` 4B field at name-end+91 references CameraConfig ID 587 `CC_FollowMC`.
- 51/57 have a native 4B field at name-end+67 referencing a classed real PositionDummy (3 native local 12/16/12B transforms EACH, 153 total).
- 6 use `UINT32_MAX` no PD: Camera_Tutorial_move, Camera_IM_attack_look, Camera_IM_Down, Camera_check_IM_close, Camera_tuto_missile, Camera_around_bomb.
- Intro `Camera_start_show` (ID1864) points PD_start (ID1848); `Camera_start_show2` (ID1868) points PD_start_end (ID1852); both real PositionDummy class. Camera render eye/lookAt semantics of each three PositionDummy XYZ transforms not proven.
- Both genuine CameraConfig sources CC_FollowMC (ID587) and CC_FrontMC (ID589) have original 18 tagged vec3 field arrays numerically equal. This alone does NOT demonstrate identical in-game camera behavior.
- Standalone offline interactive source BRES XY plan + 57 CameraPreset PD target triples: G29_C1L1_KAMERA_SAHNE_INCELEYICISI.html, actual G29 GitHub Action artifact, no installation.

## G30: Four ORIGINAL 2010 Sun Light class objects (success)

GitHub CI: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38755917470; artifact 11983401934. Source tool: `research/b24_unified/b24_g30_original_C1L1_four_Sun_Light_source_native_fields.py`.

- Exact typed Light nodes and native source 12+16+12 local transforms:
  - Sun001 XYZ=(-23.170,-21.477,37.670)
  - Sun004 XYZ=(-21.325,-20.287,37.906)
  - Sun002 XYZ=(-19.994,-21.699,37.906)
  - Sun003 XYZ=(-32.448,100.158,29.493)
- All four include genuine native raw color-LIKE UINT32 `0xFFBEAEFF` and unknown float field (first 3 0.3, last 1.0), exact byte positions relative to real Light name; also tagged raw u32 numeric fields first 3 2, last 0. **Not proven** actual RGB/alpha, intensity or lighting shader operations.
- Generated small standalone offline HTML source city XY light locator, original geometry drawn with exact BRES triangles.

## G31: Real offline INTERACTIVE 3D original native BRES viewer (success)

GitHub CI: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38757140178; artifact **11983558239**. Tool: `research/b24_unified/b24_g31_original_C1L1_BRES_WebGL2_3D_source_inspector.py`.

- Verified **370 BRES original meshes**, **37,946 source vertices**, **22,919 exact source triangles**, **460 native material submesh draw batches**.
- Actual vertex positions/indexes embedded to an independent single-file ~1.15MB HTML, orbit and zoom WebGL2 with material proof/group filters. One panel can choose among 57 real camera PD source records; MC and original 4 Suns are authentic CLARA-local marker locations. Browser 3D is not the real Gameloft/iOS renderer.
- Final exclusive triangle classification (source mesh UV positive plus native material PVR property):
  - 18,568 source-PVR+UV triangles
  - 206 original Expo CAHP01 PVR + UV triangles
  - 1,861 original UV-positive but no verified native standard diffuse link
  - 132 native PVR-linked but UV absent on source mesh
  - 2,152 source UV/PVR both not usable
  = 22,919 total. 18,774/22,919 = 81.9% available per-pixel texturable native owner geometry. The rest 4,145 triangles require 2010 shader/non-diffuse/UV/vertex color or other source mechanisms and SHOULD NOT get guessed textures.
- CPU original BRES geometry rendered to a GIF and PNG previews as *diagnostic proof-color shapes*, no Vita screenshot.

## G32: Real native 2010 owner PVR RGBA and BRES UV0 in 3D WebGL2 source viewer (success)

GitHub CI: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38759136193; artifact **11985730243**. Tool: `research/b24_unified/b24_g32_original_2010_BRES_PVR_UV_real_textured_WebGL2.py`.

- Native 2010 owner IPA textures resource bank has 39 authentic C1L1 PVR/TGA entries and separate actual `CAHP01_c_expo_building.tga`. **24 source-named PVR atlas assets are USED by currently authenticated C1L1 source material+positive UV pairs**, including the original Expo 40th source.
- Entire original source BDAE 370 mesh UV0 array exactly vertex/index-matched to original 2010 BRES geometry (37,946 native UV0 pairs), and native real PVR2 RGBA pixel data decompressed by source-aware texture2ddecoder from owner archive.
- 18,774 original triangles are WebGL textured with genuine user-owned atlas pixels and original source UV0 interpolation; remaining triangles still use G31 diagnostic evidence-status colors. WebGL2 graphics code itself is custom host, **NOT original engine** shader/blend/emissive/lighting/collision, no original game FPS/device test and no original render claim. Embedded single file ~4.94MB HTML in private Actions and attached chat ZIP.
- Generated extra independent host CPU previews as flat **one sampled source texel per visible triangle**: `G32_2010_KAYNAK_DOKULU_3B_MC.png`, `G32_2010_KAYNAK_DOKULU_3B_KAMERA_START.png`, plus **offline before-after slider** `G32_G31_ONCESI_SONRASI_ETKILESIMLI.html`. These CPU images are not per-pixel UV (only WebGL supports full per-pixel).
- WebGL HTML produced and verified source CI, and JavaScript syntax checked separately with Node. Sandbox Chromium disabled WebGL2; actual browser rendering remains to be user/device checked. No Vita VPK created.
- Protect against confusion: G31 and G32 3D source rendering does NOT prove original scene CLARA parent/world transformations of each BRES mesh, original indoor layouts, original player/camera intro, original 2010 lighting or actual PS Vita performance.

## Highest-priority NEXT work (map-first)

1. Prove why 4,145 source triangles are not standard source PVR+UV: native original no-diffuse shader/vertex-color/material blending; original `Material__20` and `c1l1_3building` need original engine semantics. No arbitrary PVR reassignment.
2. Actual CLARA node↔BRES 3D mesh owner bindings, parent/world matrices, camera PositionDummy A/B/C field semantics. Source Class SceneGraph enough to identify MC and mission callbacks, not enough yet to show exact game camera.
3. Align original shader lighting with real Sun source Light nodes and original armor skin materials. GPU performance/quality stage should test on PS Vita only after a coherent scene, preserving no repeated VPK churn.
4. When first map visibly, structurally, interactively sound, restore original armor/War Machine animation rigs/clips, ground/hover/flight/combat mechanics and original cutscene/script + 803 sound asset bank for first playable real mission. Original unrestricted traversal and later on-rails chapters have separate control systems.

G32 material/source proof success is an IMPORTANT partial map renderer advance, but do not call C1L1 or the project completed.
