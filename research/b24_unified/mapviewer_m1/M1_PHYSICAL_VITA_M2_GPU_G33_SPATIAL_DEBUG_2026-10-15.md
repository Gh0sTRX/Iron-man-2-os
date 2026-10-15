# C1L1 MapViewer M1 Vita on-device failure and M2 static GPU test (15 October 2026)

## M1 on-device genuine evidence
The user installed original M1 native PS Vita VPK and uploaded 3 PHOTOS. M1 **boots and visually draws original source grass texture, white road pattern, blue/cyan source non-textured light meshes and distant building clusters**. M1 HUD shows source texture mode and both whole-level overview and MC focus. BUT the source city geometry looks disconnected: a large green ground slab, many distant city parts, other models apparently outside/under plane. User reports **severe apparent ~1 FPS and crashes**; no verified profiler value or crash code. Do not claim the game map is faithful/completed.

## Why issues differ
M1 IS native VitaGL GPU-indexed triangle rendering and uploaded source PVR atlas textures. It is NOT a CPU software renderer. However the existing world renderer repeatedly references client-side CPU RAM arrays for each material glDrawElements, which can create CPU/driver overhead and synchronization; this is a *hypothesis*, not proven device bottleneck. The HUD also builds per-character CPU vertices and uses GL_POINTS each frame.
M1 ORIGINAL 370 BRES mesh XYZ coordinates are rendered raw, WITHOUT full source CLARA mesh-instance/world transformation; original 601 named classed scene records and 663 native transform subrecords do not yet establish exact individual mesh-to-CLARA source binding. DO NOT arbitrarily position models.

## G33 authentic source spatial audit
G33 private source CI https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38772268647 **SUCCESS**, artifact 11992187047. Original 370 source meshes, 22,919 triangles. Original 16 ground meshes (3280 tris) have aggregated source XY bbox -1219.11,-1090.07 to 191.117,270.135. 40 meshes are wholly OUTSIDE even this loose original ground XY AABB: 28 of 121 urban, 7 of 22 vehicles, 5 of 211 light meshes. This is a raw coordinate observation, not proof of what native runtime placement should be. The original level1.bclara lacks direct ASCII references to expected C1L1_obj_001 and other BRES filenames, so must recover BINARY resource binding, not guessed substring mapping.

## M2 compiled real native separate VPK
CI https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38772223381 **SUCCESS**, artifact 11992715418. VitaSDK 2026.08 native VPK (3,866,458 bytes, sha256 b647e224e740c70658317adcbaa5e59d6ce15aa00718823753600b58a0001203). NEW TITLE ID IM2M20002, no overwrite M1 IM2M10001 / full port.
New source path research/b24_unified/mapviewer_m1/mapviewer_m2.c and mapviewer_m2_gpu.c/h; independent research/b24_unified/mapviewer_m2/CMakeLists.txt, CI .github/workflows/m2-c1l1-gpu-static-profiler-vpk.yml.
M2 uploads immutable original BRES vertices, UV and both original and material indices ONCE to GPU VBO/EBO and issues GL_TRIANGLES from static GPU buffers. Shows GPU STATIC VBO EBO ACTIVE or SLOW CLIENT RAM FALLBACK, numeric FPS + DRAW/SWAP wall times, and source map category isolation. D-pad left/right cycles ALL/GROUND/CITY/VEHICLES/LIGHTS, up/down camera Z, SELECT texture/color modes, TRIANGLE whole map, SQUARE MC, CIRCLE city, L/R zoom, left/right analog pan/orbit, START HUD.
The native M2 VPK compiles and checks out as a ZIP package. **No real M2 device performance/renderer stability confirmed yet.** No source scene binding fixed in M2. The VBO approach may or may not fix the slow frame issue, and M2 may need hardware-specific debugging.

## Next
Ask user for M2 FPS DRAW SWAP + GPU static/fallback status after 6 frames, same camera view in source textured and vertex colored modes; group isolate for misplaced geometry. Continue source-native scene model resource ID + parent-to-world matrices, shader effects and transparency. Preserve explicit roadmap: faithful map first, then original animation/combat with later original audio cutscene data for first playable mission; do not treat successful viewer source VPK as completed game.
