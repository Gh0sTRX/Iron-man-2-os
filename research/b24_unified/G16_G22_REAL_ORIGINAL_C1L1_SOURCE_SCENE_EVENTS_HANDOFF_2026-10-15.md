# Iron Man 2 PS Vita | G16–G22 original source map/scene/mission handoff | 2026-10-15

**Branch:** feature/b24-unified-gameplay. **G13/G22 NOT Vita installed; NO NEW VPK.** Original first mission city map source recovery stays highest priority. Gameplay additions deliberately parked.

## G16 and G16.1 — Shader native pointer chain
- CI G16 https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38728602759 **SUCCESS**, 194 original per-file source BRES shader material records / true relocated pointer locations (not guessed u32 values). Source shaders named Material__20 and c1l1_3building both have native string destination **CHANNEL1**. Material__20 native property 60B; nonstandard/no-source-PVR c1l1_3building 40B.
- CI G16.1 https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38728858832 **SUCCESS** and raw original 2010 binary target-pointer bytes traced. Crucial: original CHANNEL1 source string proven, but pointer to other data has not been interpreted as confirmed color/alpha/emissive. No shader color/render emulation should be claimed or fabricated.

## G17–G19 — Original level1 authored scene transforms and map
- G17 CI https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38729082703 **SUCCESS**, 339733-byte authentic original 2010 level1.bclara, original SpawnPoint000..015 16 authored named nodes. Conventional generic scanning of named strings does not identify the player start or typed fields.
- G18 private archival source stage CI https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38729457618 **SUCCESS**. Exact original level1 SHA256 `31c794a0140d607c1abd43e463a02cab73d5e2cbbc8495d7cc96f55876aead3c`. Only 2-day PRIVATE Actions artifact contains the raw 339733-byte file; do NOT publicly redistribute it.
- **G19 BREAKTHROUGH** CI https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38730426440 **SUCCESS**, artifact **11969784334**, 16 EXACT original level1 SpawnPoint entries, every record has native tagged transform data **12B XYZ floats**, **16B xyzw quaternion floats**, **12B XYZ scale floats** starting at name offset +107. 16/16 normalized quaternion, unit scale and exact IDs; no guessed nearby triples. Real 370 original BRES model polygons and 22919 triangles plotted with the exact source node XY. **16/16 positions fall inside loose original BRES XY AABB** (not proof of actual node parent hierarchy/camera). Authenticated BRES coordinate AABB min (-1219.109985,-1090.069946,-44.661098), max (414.704986,531.976013,44.661098).
- Critical original source 16 node XYZ (rounding shown): 000=(-5.293,-184.602,0), 001=(-5.295,-190.379,6.097), 002=(187.251,-17.795,1.433), 003=(122.435,-205.013,0), 004=(157.643,-209.187,10.207), 005=(-3.349,169.086,0), 006=(6.418,166.922,0), 007=(18.156,165.407,0), 008=(226.273,58.644,0), 009=(-144.033,-82.305,0), 010=(-156.261,-93.549,0), 011=(-204.148,177.331,0), 012=(-196.871,57.943,0), 013=(209.572,-141.573,0), 014=(112.049,65.555,0), 015=(-246.341,42.068,0).
- G19 no-install artifacts are native-source 1400×920 2010 true triangle plan view PNG + self-contained searchable HTML map; **NOT real in-game screenshots or game mission spawn verification**.

## G20–G22 — Original level1 event static graph from true source
- G20 CI https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38731181347 **SUCCESS**: authentic BCLARA defines 4 original callbacks with native literal names SpawnPoint004_OnDestroy, SpawnPoint012_OnDestroy, SpawnPoint014_OnDestroy, SpawnPoint015_OnDestroy. Three have real typed 4B string records Enable/Disable followed by **type-3 original float32 exact integers**. The fourth has no proven Enable/Disable record in bounded source callback.
- **G21 CI https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38731712854 SUCCESS**: the native float32 integers match independently located **type1+u16 ASCII length named original CLARA node record IDs** (actual IDs in source bytes before node name). 600 raw type1 named candidates, 593 unique numeric IDs; exact three action destinations UNIQUE, verified:
  1. `SpawnPoint012_OnDestroy` → authentic `Enable` (numeric ID 1616) → `SpawnPoint015`.
  2. `SpawnPoint014_OnDestroy` → authentic `Disable` (ID 2489) → `Deco_fence2`.
  3. `SpawnPoint015_OnDestroy` → authentic `Disable` (ID 2509) → `Deco_fence6`.
- **G22 CI https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38732116341 SUCCESS**, artifact **11970586954**: independently recovered TRUE source positional 12B/16B/12B native CLARA transform for Deco_fence2 and Deco_fence6 at original node-name+184. Fence2 XYZ=(83.723,52.216,0) approximately, scale=(7,1,5); fence6 XYZ=(-248.706,14.226,0.051), scale=(6.5,1,5). All three source-matched event endpoints plotted as arrows over original BRES city mesh with authored XY distance:
  - SpawnPoint012→SpawnPoint015 Enable: 51.9548 source XY units.
  - SpawnPoint014→Deco_fence2 Disable: 31.3096.
  - SpawnPoint015→Deco_fence6 Disable: 27.9423.
  Saved exact CI JSON, PNG true-source plan and single-file offline interactive HTML with event-selection. No invented city polygons or gameplay events; no new VPK.

## Strict remaining limitations and next work
1. Source-static source name/ID event graph is recovered, **NOT live 2010 event execution**, timeline, player actor start or actual story script QTE order. Do not claim the 16 SpawnPoints are all actual player respawn points.
2. Source BRES geometry/CLARA local transform combined in a top-down diagnostic; actual level1 node parent scene graph and actor mounting/camera transforms remain to be verified.
3. Original material Shader CHANNEL1 meaning and true RenderState/vertex color, emission, blend and light effects remain unknown. G13 G14 Expo asset correction authentic but full map still incomplete.
4. The map has **NO real device G13/G19/G22 VitaGL test**; previous B24-C2 on physical Vita remained erroneous, with START input bug fixed in source only. Avoid repeated VPK installs until native original map content works in source and all old gameplay changes are unified.
5. Continue mission scene graph and shader proofs, then C1L1 source-faithful 3D map, only after those stage one **single** combined VitaGL test; do not add random enemy AI/missile/flight mechanics.

Code and workflows:
- research/b24_unified/b24_g16_bres_original_shader_property_relocation_semantics.py
- research/b24_unified/b24_g16_1_original_shader_indirect_channel_payload_source_probe.py
- research/b24_unified/b24_g17_owner_original_level1_clara_spawn_pointer_crossrefs.py
- research/b24_unified/b24_g19_original_2010_level1_spawn_transforms_city_xy_map.py
- research/b24_unified/b24_g20_original_C1L1_SpawnPoint_OnDestroy_native_event_probe.py
- research/b24_unified/b24_g21_original_C1L1_clara_OnDestroy_action_real_node_id_links.py
- research/b24_unified/b24_g22_original_C1L1_event_target_fence_source_world_render.py

All seven corresponding original-source CI jobs verified SUCCESS, and their source must remain PRIVATE because the owner's assets are proprietary. No new game VPK produced.
