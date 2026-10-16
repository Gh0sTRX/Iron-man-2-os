# G73 — EXPО ORIGINAL NIGHT MAP / G74 REAL SOURCE GROUND CONTACT — 2026-10-16

## Goal and user approval
User wants final *map traversal* polish and a single testable PS Vita package before starting authored enemy models, full Mission000 Lua, cutscenes, dialog. Preserve hardware-verified G68 city/texture/collision geometry and earlier successful G9/B24 gameplay rather than rewriting controller. Device currently not nearby; verify host/VitaSDK first.

## Last verified candidate
GitHub Actions successful full B24/G9 gameplay + original sourced sky / G68 world:
https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38903453286
GitHub artifact ID `12046124343`:
`IronMan2_G73_B24_Playable_Authentic_2010_Expo_Sky_Model_Moon_Skyline_Candidate_VPK`
Contained VPK `IronMan2_B24_G73_Expo_Original_Night_Sky_Candidate.vpk`; user-friendly exported VPK `IronMan2_B24_G73_Expo_Orijinal_Gece_Final_Test.vpk`.
Title ID **IM2G73001** (no overwrite G68/G70/G72).
Exact VPK SHA256 **31029eb34387291c9c2263ad4b08e4662b4821e11eba9949a5266e00031792a1**, **66,834,044 bytes**. 421 ZIP members, ZIP CRC clean.

## What was VERIFIED in actual built VPK
- All **22,441 genuine C1L1 static scene original triangles**, 31 owner source PVR city atlas decoded textures and authentic G68 original 1,910 collision faces **byte-for-byte equal** to G68 user-photographed hardware-sound map VPK `IM2G68001`.
- The original B24/G9 gameplay code and five suits `mark6/mark4/warmachine/stealth/suitcase` (Mark V available through suit selection; default remains Mark VI if old G9 startup unchanged), **363 original IM2V authored animation streams**, six original WM gun streams, native B24 HUD, input, melee/flight stages; no G68 placeholder standalone 2-wave game update loop.
- **G71** alpha-aware rendering opt-in built ON in G73: original source 7 RGBA atlas groups and 1,282 original triangles in transparent pass, depth-write OFF there, opaque 21,159 city triangles first.
- **G72** local static geometric normal ambient dusk tint ON, source vertex RGB only; authentic XYZ/UV/alpha unchanged, no additional scene texture, no per-frame CPU lighting cost. Diagnostic soft-gradient background ON without synthetic skyline silhouette.
- **G73 REAL ORIGINAL SOURCE SKY**: original `Deco001` resource22 maps `C1L1_sky_001.bdae`; genuine original six BRES meshes, 96 source faces flattened into `G73_original_sky_mesh.g73m` (288 vertices). True owner's original named PVR `C1L1_sky_02.tga` city skyline and `C1L1_sky_03.tga` moon/stars/clouds decoded. Vita diagnostic resampled from 512² to 256² RGBA each (additional 524,288 bytes of sky texture mip0 and 6,912 bytes of vertex data). `b24_gpu_g73_sky_vitagl.c` draws original shell within same B24 VitaGL owner before the real G68 source city geometry and old 5-armour actor/HUD.
- CRITICAL unproven: exact original source `Material__2717,2718,2719` to PVR sampler mapping. Current sky mesh[0]→sky03 and meshes[1..5]→sky02 is a provisional geometry/UV-based map. Thus original *asset provenance* is VERIFIED, but exact original *rendering/material semantics* are NOT. This A/B candidate can look incorrect until user device screenshots reveal surface swaps.
- **G74** optional original-G68-grounded floor support active in current G73 build `B24_G74_GROUND_CONTACT=ON`. Loads same 1,910 source triangles to existing B24 sole CPU movement engine and samples real nearby non-wall walkable floor/roof barycentric Z only when `world.flight_stage==0`. Accepts floor within [-0.5,+0.45] of actor feet to prevent distant roof teleport; B24 gameplay remains the sole physics/time/flight owner. Checks 220 genuine walkable source triangles in host test and no far-roof snapping.
- Host test SUCCESS: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38903578693 (220 nearby support probes and ARM compilation of G70 scene/collision). G73 full VitaSDK source+VPK packaging success is independent. Neither proves actual device floor height integration or FPS.

## Device QA when owner near console
1. Install separate VPK **IM2G73001**, leave G68 `IM2G68001` and G70 `IM2G70001` intact. Initial suit may be Mark VI; cycle to Mark V with old B24 suit-selection input (historically SELECT); verify input controls in real device instead of assuming.
2. Confirm true 2010 sourced night sky moon/stars + distant skyline visible at horizon. If sky upside-down, too low/high, tiled, black or moon invisible, screenshot from ground/hover plus 1 high altitude camera and adjust *only* explicit provisional material shader/mapping. Original native 96-face geometry remains intact.
3. Compare G68 map features: Expo central sphere, arch, two domes, buildings, grass/trees, parking roads, street lights; no geometry loss. Check leaf card black planes vs G68 and dark special nonstandard Material__20 globe; G71 is only transparent pass fix, not full native original shader recovery.
4. Run into wall at walking speed and Stage 2 flight, explore ramps and roofs, reverse walking/hover/landing; verify G74 ground source height and B14 fallback. Some original collider floor coverage is limited and three-slice G67 capsule is not yet a drop-in full replacement.
5. Check HUD/melee/repulsor/flight stage1→2→rush/suit selection/START-only pause from retained old B24; original 363 streams ≠ 363 physically verified visibly correct clips.
6. PSVshell sustained 60-second FPS/battery/MEM/VMEM after switching to Mark V and flying above expo. Previous **G68** single-shot 59 FPS and 237/256MB MEM/112/112MB VMEM **CANNOT** be represented as G73 performance.
7. Any boot failure, black screen, memory crash, wrong sky mapping: keep G68 good version and send screenshot + repro. G73 never overwrites previously known device baseline.

## Still incomplete before a faithful full first mission
Full original Mission000/Level1 iOS Lua intro/mission progression, authentic Drone/Enemy_spider autonomous BRES rigs and animations, sound/VO/cutscenes, special original globe 408-geometry triangles shader, native vegetation alpha-test sorting beyond two passes, original lighting Sun nodes and real sky shader/material binding, exact full G67 3-slice swept collision algorithm, real physical Vita G73 QA.
This G73 is the final host-prepared **MAP PLAYABILITY TEST candidate**, not a verified finished port.
