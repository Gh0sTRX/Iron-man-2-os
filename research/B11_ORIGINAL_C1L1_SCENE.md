# B11 — C1L1 Original Level Environment Geometry (2026-10-12)

**Source:** original user-provided Iron Man 2 (Gameloft, 2010) IPA v1.0.0; no AI-generated environment geometry.

## Verified reconstruction milestone
- The IPA's `Payload/IronMan2.app/models` named archive contains 15 resources with names beginning `C1L1_`. Ten are rendered environmental model sources (`C1L1_ground_001`, `obj_001..004`, `car_01..02`, `light_001..003`). Four more include collision/sky/floor geometry; `C1L1_Temp_doc` has no validated triangles.
- Adapted a new parser specifically to **2010 BRES/BDAE 0,0,0,133**, not the later 0.0.0.779/946 formats. Its 52-byte mesh descriptors include model name +0x04, friendly name +0x08, vertex count +0x10, vertex descriptor pointer +0x14, submesh count +0x18, submesh ptr +0x1C and bounding box +0x20. The vertex descriptor has stride at +0x00 and source vertex pointer at +0x14. Each submesh record is 56 bytes: triangle count +0x08, index count +0x18, 16-bit index pointer +0x1C.
- Reader handles several static vertex formats (20,24,28,32-byte strides). For each accepted mesh, it validates finite coordinates, in-file buffers, min/max bounding box, and **exactly 3×triangle_count index values** with every index less than actual vertex count.
- Of all C1L1 BDAE sources, **24,925 triangles** validated; 10 visible environment sources yielded **370 verified submeshes**, **37,946 vertices**, and **22,919 triangles** and were assembled at their original stored xyz positions.
- **Both full GLBs were exported and reloaded successfully**: (1) untextured environment with distinct placeholder colors by asset category (370 geometries), (2) same environment + original textured Mark VI model (371 geometries). Original coordinates are Z-up; GLBs rotated into standards-compatible Y-up. The Mark VI is placed at world origin as an **illustrative test placement only**, not the verified mission spawn.
- Generated two static geometry-preview PNGs. These are **NOT authentic game screenshots**, are **not fully material-textured**, and include only a recovered subset. The level1 `.bclara` graph was **not** matched to these assets' original transforms and mission state. The `C1L1` naming supports the first chapter/level association but that is **not** yet a proven exact BCLARA reference.
- No B11 VPK was built: the current 480x272 CPU rasterizer would be impractical for 22.9k additional triangles, so prioritize a LOD test or GPU path before on-console rendering.

## Private artifacts, all in this repository
- `research/B11_C1L1_Source_Parser.zip`: original private C1L1 source models, reproducible extraction and mesh reader, Mark VI, README and mesh CSV.
- `research/B11_C1L1_Scene_GLBS.zip`: standard glTF models for Blender or GLB viewers.
- `research/B11_C1L1_Previews.zip`: oblique overview images.
- All original game resource contents must stay **PRIVATE**.

## Next steps
1. Resolve per-submesh **material-to-original-TGA** references and PVRTC atlases for visually faithful C1L1 environment. The current flat palette is diagnostic only.
2. Decode `level1.bclara` **instance schema** to identify actual original spawn, dynamic object transforms and objectives, and verify if `C1L1` is tied to level1. Merely seeing `SpawnPoint` in the class dictionary is not a decoded instance.
3. Select actual original ground and walls as a low-triangle collision/scene test, then implement correct camera + GPU draw path or measured LOD. Keep B8/B9/B10 rollback artifacts. Wait on new Vita hardware tests rather than saturating user with speculative VPKs.

In future ChatGPT chats, read `PROJECT_HANDOFF.md` and this report first.
