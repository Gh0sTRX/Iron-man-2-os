# G70 Full Gameplay and G68 City: successful full VitaSDK package (2026-10-16)

GitHub Actions run: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38893606345 — success.
Artifact ID: 12043016358.
Artifact title: IronMan2_B24_G70_Original_G9_Gameplay_Actual_G68_C1L1_5_Suits_363_Animations.

Isolated packaged game: IronMan2_GPU_B24_G70_G68_WORLD.vpk.
Vita TITLE_ID: IM2G70001.
Size: 66,596,011 bytes.
SHA256: 75433cedeb77ca858d5a26a41e995e110b40a10b96affce33190aca80317e134.
Verified VPK ZIP CRC and 418 package entries, including SCE executable, five original armors, 363 original motion streams, six WM gun streams, 31 G68 original city textures, 22,441 original C1L1 city triangles, and G68 original 1,910 C1L1 collider triangles.

Architecture: full original B17/G9/B24 game input+HUD+combat+animation loop. G68 standalone gameplay main.c, its simplified seven-clip policy and wireframe 2-wave enemy demo are NOT used. A source-only VitaGL city adapter swaps only the GPU environment rendering backend, while original B14 CPU movement retains sole gameplay ownership.

Limitations: real Vita device G70 NOT tested; 59 FPS is observed from G68, not G70. G70 renderer's GPU scene and G68 map data proven in G68 independently; merged memory, boot and 1-to-1 pose orientation unproven. Original G68 roof/floor contact physics was not fully inherited: G70 maps authentic 1,910 source triangles into older B24 wall-sweep algorithm, which does NOT equal G68 G67 sweep+floor solver. Treat this as highest-priority device QA item.

Initial G70 default armor is Mark VI (G9 idx=0). Mark V Suitcase armor is included in original five suits, selectable via SELECT cycling to idx=4. Mark V as startup default is NOT verified, and G8 extra source streaming is complete chiefly for Mark VI and War Machine; other suits may use existing B13 fallbacks.

Visual issues still known: unported native sky, lighting, some alpha planes and Expo globe shading. Do not rework G68 geometry until the combined G70 build survives actual PS Vita test.

Device QA request: install G70 separately without replacing G68; test boot, swap suit, camera centered crosshair+shoulder avatar, forward/backward and flight1/2/rush, melee, pause START only, wall/floor/ramp traversal, GPU artifacts, fps and memory. Provide actual Vita images/short video for regression comparison.
