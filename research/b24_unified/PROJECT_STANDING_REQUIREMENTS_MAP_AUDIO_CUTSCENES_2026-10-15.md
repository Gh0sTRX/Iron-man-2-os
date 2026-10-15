# Iron Man 2 (Gameloft iOS 2010) — source-faithful port roadmap / user directive — 2026-10-15

## NON-NEGOTIABLE ORDER

**The original C1L1 first map is NOT complete. Do not declare it finished based on triangulated geometry or a 2D schematic.**
Work until a reusable source-authored level loader is sufficiently understood and a convincing, testable, source-faithful first-level map is available. Build a high-quality, installation-free diagnostic test interface for visual/scene/material/placement inspection before repeatedly deploying VPKs.

1. **Original first level (C1L1):** unpack original BRES models, atlas textures and relevant scene materials/shaders; recover original `level1.bclara` nodes, identities, local / parent world transform chains, appropriate spawn/camera, objects, original level topology, floor/wall/collision, LOD/draw ordering, lighting/blend/vertex-color semantics; fit first world scene to PS Vita GPU renderer with stable frame times. Every visible surface should use real source textures or clearly marked verified source shader/color handling, not guessed clay/cyan. Demonstrate coverage and unknowns via explicit test evidence.
2. **After map AND strong reusable level-loader foundation:** recover ALL missing animations, grounded/flying/hovering/landing and War Machine model rigs/clips, combat (repulsor, missiles, lock-on, Unibeam, melee, combo, target prioritization), actual controller actions and UI/HUD/pause. Reuse original data wherever possible, avoid synthetic moves when corresponding authentic 2010 animation exists.
3. **Audio begins AS SOON AS first C1L1 map is structurally usable:** unpack/decode actual `.www` WAVE/IMA-ADPCM/PCM audio and match source asset names to events, music, cues and dialogs. Existing source audit saw 803 RIFF/WAVE assets: 647 IMA ADPCM + 156 PCM. Exact sound->gameplay bindings are not yet known. Keep authentic filenames and provenance.
4. **Cutscene/event reconstruction runs alongside first playable map demo**: source scene events, character animations, camera rails, scripting, dialogues, audio cues and mission transitions. No pretending missing timelines are recovered; version evidence and uncertainty on each event.
5. **First end-to-end playable C1L1 demo** requires original 3D map, reliable 30 FPS target evaluated by real Vita measurements (not claimed until test), full ground/flight/control combat as relevant, sound effects/voices and intro/outro/cutscene content when recoverable.
6. **Subsequent mission maps** may use fundamentally different control modes: open traversal versus restricted on-rails forward motion with left/right steering. Classify each chapter from its real original LUA/BCLARA asset and control structure before creating a universal world-loader. Build per-level scripts/cutscenes and the rest of original game gradually.

## Delivery and testing rules
- Do NOT force user to reinstall VPK per iteration. Prefer private GitHub Actions source-level CI and reproducible host-rendered screenshots, actual BRES/UV source material before-after comparisons, animations as original-clip skeletal previews (HTML/GIF), searchable entity/scene inspector, explicit provenance/debug overlays.
- Build one polished multitab inspector: 3D map/main HUD camera with controls, scene graph browser, source mesh/material/UV/shader evidence, exact spawn/trigger/actor IDs, cutscene/audio cue timeline preview when source-backed, and toggles for shader/geometry statuses. Explicitly label unverified renderer modes and make them visibly distinct from original source.
- No falsely claiming GPU texture test FPS / original playable behavior. G22 proves only original static CLARA node event references; full scene graph/parent transforms and mission player role unknown.
- Maintain original owner assets in PRIVATE GitHub and offline private artifacts. Avoid publicly distributing original IPA/asset content. Never label original source records as reconstructed engine code.
- Update this roadmap/handoff after actual verified milestones; keep known-good B15/B17 and B24 variants untouched until integrated GPU source proof.

## Current status at this directive
- G13 original Expo PVR + 206 triangles restored via original 40th atlas; G14–G16 original 2010 native material/shader CH1 evidence but actual shader lighting semantics not proven.
- G19 authenticated 16 CLARA SpawnPoint local XYZ/quaternion/unit scale; source only, not player start.
- G21 authenticated three native OnDestroy Enable/Disable target node-ID relationships; G22 authentic source city XY overlay with 16 spawn, two fence nodes and three real source-event edges. Original polygons true but parent-world transform chain and full GL effects still missing; 2D source diagram is NOT full 3D scene.
- Next MAP ONLY: scale G19 transform extraction from 16 spawns/2 fence targets to full CLARA node registry, recover actual parent and local/world transforms, quantify unmapped BRES/materials/camera, show source-authentic 3D map test interface. No separate gameplay mechanic changes yet.

Owner explicitly requested this sequencing and deferred audio, cinematics and rail-mode classification to just after map groundwork; do not forget these tracks.
