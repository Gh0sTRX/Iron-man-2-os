# Mark 43 — Iron Man 2 iOS-style 3D armor study (v1)

This folder contains a **real editable 3D armor asset**, not an image or an HTML mockup.

## Model
- `Mark43_iOS_Style_v1.gltf`: self-contained **glTF 2.0** mesh with embedded binary data; **no external texture or .bin files needed**
- 141 separately named component meshes, ~3,584 triangles, 12 PBR color materials
- Upright axis: **Y-up**, glTF meters; height ~2.12 units; front faces toward **+Z**
- Designed as a fresh low-poly armored silhouette influenced by the source Iron Man 2 iOS Mark IV art direction, matching the approximate game-scale and retro metallic red/gold material balance
- NOT an extraction of an actual Mark 43 model; NOT a recolored Mark IV; NOT a rigged/playable character yet

## Blender use
1. Download `Mark43_iOS_Style_v1.gltf` from GitHub (**Download raw file**).
2. Blender > File > Import > glTF 2.0 (.glb/.gltf), select it.
3. Each armor segment (helmet, chest, arms, legs, etc.) is a separate mesh; select/join or edit them as needed.
4. Save as .blend or export to .glb from Blender via File > Export > glTF 2.0.

## Vita integration roadmap
- Verify silhouette against actual iOS Mark IV render, adjust armor proportions and chest profile.
- Optimize mesh/polygons and material batching for Vita.
- Match target iOS Mark IV skeleton; skin weights, inverse bind transforms and deformation.
- Connect existing iOS anim sets (ground/hover/flight/combat), validate clipping and pivot points.
- Convert to the game's importer format (.im2m/.glb or runtime-defined custom format) only after rig verification.

## Model structure
- Head: helmet shell, faceplate, eyes, jaw vents, cheeks, ear devices
- Torso: segmented front/rear torso, collar, chest reactor, abs, hip armor
- Arms: separated shoulder caps, biceps, elbows, forearms, wrists, hands and palm repulsors
- Legs: hips, thighs, knee armor, shins, boots and heel thrusters
- Materials: primary/secondary red, gold, dark mechanical metal, chromed accents, white/cyan emissive reactor

## Status and caveats
Mesh structure, accessor counts, materials and self-contained buffer have been checked after GitHub commit. This file has **not** yet undergone a Blender render check or a Vita runtime test, and the embedded glTF 2.0 has **no rig or animations**.

Reference style data: original game Mark IV technical preview recovered from the user's own prior research archive (802 vertices, height ~2.21 original model units). Its geometry was *used for scale/style guidance*, not copied wholesale.

The research stays on `feature/mark43-ios-style-model` to avoid disrupting the playable Iron Man 2 Vita project on `main`.
