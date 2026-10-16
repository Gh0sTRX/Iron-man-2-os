# G72 — G70 Gameplay + Original G68 Map + Dusk Source Lighting and REAL Sky Source Investigation — 2026-10-16

## Scope / user goal
User is away from the PS Vita and wants host-side progress to produce a functional first-level traversal environment by evening: old B24 G9 gameplay and 363 original motion streams + genuine G68 mapped C1L1 collisions, dark sky corrected, evening-lit city, no black alpha planes, and original distant city skyline/clouds/moon as assets if present. Actual enemy Lua mission, NPCs and full source iOS rendering semantics are later goals.

## G72 working build (VitaSDK CI, no Vita device run)
- GitHub Actions https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38897844117 — **SUCCESS**. Earlier G72 CI also passed https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38897683475.
- Build artifact 12045205929 `IronMan2_G72_Original_B24_Playable_Twilight_SourceCity_Alpha_Candidate_VPK`.
- Direct VPK `IronMan2_B24_G72_Expo_Twilight_Visual_Candidate.vpk`, TITLE_ID `IM2G72001`, size **66,597,675 bytes**, SHA256 **d3297c48e8cbde7ae1dca2debe3349b9ffe302f95d8a27bedc94004ddc68598e**. Fetched, ZIP CRC passed independently.
- Existing `IM2G70001` G70 and `IM2G68001` G68 are NOT replaced.
- 5 original B24 suits (Mark IV, Mark V Suitcase, Mark VI, Stealth, War Machine), 363 authentic motion IM2V, 6 WM streams, native B24/B17/G9 gameplay / melee / flight / HUD code remain authoritative, no G68 7-clip fake mission player update. Initial G9 suit still Mark VI (index0) unless manually SELECT cycled.
- Original G68 22,441 C1L1 city triangles, 31 textures and 1,910 source collision triangles verified **byte for byte identical** to G70. Collision uses G9 B14 algorithm on G68 G59 data, NOT identical physical G68 three-slice/floor solver: device validation required.
- NO verified G72 FPS, memory, successful button inputs, sky behavior, material appearance or real hardware boot. GitHub compiled ≠ physically tested.

## Implemented G72 optional visual layers, original data untouched
1. G71 alpha source 2 passes `-DB24_G71_ALPHA_PASSES=ON`: opaque groups first, translucent later without depth writes; 7 original atlas RGBA IDs [1,6,7,9,15,19,20], 1,282 true alpha triangles (21,159 others), original 32 city groups unchanged. Device visual regression not verified.
2. `b24_gpu_g72_sky_vitagl.c`: fullscreen camera-relative gradient dusk sky with optional explicitly SYNTHETIC silhouette behind city. No background texture, no second GPU context; screen-color vertices, zero extra sky atlas VRAM. This is a **DIAGNOSTIC placeholder**, not original skybox or iOS shader.
3. `b24_gpu_g72_light.h` + `b24_gpu_g68_city.c` opt-in `-DB24_G72_SOURCE_LIGHTING=ON`: one-time CPU baked original-world-face-normal soft directional dusk tint, modulates native RGBA RGB only for selected opaque city atlases before original single static GPU VBO upload. Native alpha and XYZ/UV are untouched. No per-frame lighting CPU burden. Four CLARA original Sun nodes found earlier, but this chosen light vector/intensity is diagnostic not decoded original source Sun shaders.
4. Existing source `B24_GPU_RUNTIME` + same single frame owner renders diagnostic sky -> true original city -> animated armor -> old HUD -> one present. New independent app ID / opt-in all flag variants; G70 defaults remain unchanged.

## BIG BREAKTHROUGH — full REAL FIRST LEVEL SKY source materials in owner IPA
- G38 source proof maps `Deco001` Level1 BCLARA resource ordinal 22 -> models[21] `C1L1_sky_001.bdae`.
- G72 TRUE SOURCE proof https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38897330341 and follow-up https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38897844180.
- Decoded actual ORIGINAL `C1L1_sky_001.bdae`: **six true mesh pieces, 96 authored source triangles**, local CLARA translation (0,0,0), rotation identity and scale identity.
- Its largest sky shell spans XY roughly (-632,+632), Z (-269,+269), consistent with covering original city; this coordinate footprint alone does not prove engine attachment or follow-camera behavior.
- Three original native shader material records `Material__2717`, `Material__2718`, `Material__2719`, but 60-byte standard sampler parser finds NO direct verified TGA binding. This does NOT imply no texture.
- Enumerated original owner's full source textures archive: 412 named textures. Two authentic C1L1 original night sky names `C1L1_sky_02.tga` and `C1L1_sky_03.tga`. G72 private source decode https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38898199037 **SUCCESS**:
  - `C1L1_sky_02.tga`: two transparent night CITY SKYLINE strip layers, 512x512 genuine PVRTC decoded RGBA.
  - `C1L1_sky_03.tga`: moon, clouds and stars over luminous dark navy sky, 512x512 genuine PVRTC decoded RGBA.
  - Shader material to sky_02/_03 assignments **NOT VERIFIED**. No arbitrary texture-to-mesh remap presented as authentic final.
  - Original native sky mesh UV ranges verified for 6 mesh groups, including alpha/city strips with V roughly .554..1 and wide repeating U, supports further inference but no authority.
- Source atlas comparison image in GitHub Actions artifact `G72_Original_C1L1_Sky02_Sky03_Owner_PVR_True_Source_Atlas_and_UV`; do not publish original IPA or full model archive into Git.
- Local preview `IronMan2_G72_Expo_Aksam_Orijinal_Harita_Diagnostic.png` generated from real G70 source city + G68 original armor in VTK with **HOST diagnostic** dusk background; NOT screenshot of new G72 Vita build and NOT yet using the two authentic sky PVR assets. Do not conflate these.

## G73 next investigation / incomplete exploratory source work
- `research/b24_unified/g72_sky_light/g73_pack_actual_original_sky.py` is prototype to build small native sky G73M (6 groups/288 flat vertices) from sky.bdae and 2 authored C1L1 sky atlas PVRTC RGBA downscaled to 256², explicitly lowers VRAM to ~0.5MiB.
- `research/b24_unified/b24_gpu_g73_sky.h` and `b24_gpu_g73_sky_vitagl.c` are **NOT linked to G72 runtime or included in successful G72 build**. Tentative UV/shape-based mesh->atlas assignment of first mesh sky_03, others sky_02 is NOT sourced native Material__2717/2718/2719 binding.
- Source pack and full G73 Vita pipeline not yet validated; avoid claiming G73 works. Do not rush unsupported source texture swaps without actual original game/engine material semantic checks.

## Hardware gates / source path
User-away status: wait before new device installation; G72 can be downloaded separately.
First actual PS Vita test compare G68 vs G72 startup, Mark V selectable from five suits, HUD, centered reticle and left avatar, walk back, melee, flight1/2/rush, wall+roof+floor, no clipping, sky gradient and silhouette, 7 alpha materials, Expo dome special shaders, memory vs user G68 snapshot 237/256MB and 112/112MB VMEM, sustained 3min FPS not single 59 snapshot.
No guarantee 'fully playable mission': native Mission000 Lua, enemies and voice/cutscenes not yet restored.
