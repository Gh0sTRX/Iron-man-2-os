# B12 — C1L1 original texture recovery (2026-10-12)

## VERIFIED from the user's actual original Iron Man 2 iOS 1.0.0 IPA

- Analyzed all **15 original C1L1 BRES/BDAE model files** carried in `research/B11_C1L1_Source_Parser.zip`.
- Parsed **190 independent, pointer-validated texture records** in the form (name, internal alias, full historical source path).
- The records contain **39 distinct referenced texture filenames** (case-insensitive). **39/39 files exist** in the actual original IPA `Payload/IronMan2.app/textures` archive. No texture names were invented.
- Converted **42 PNGs**: all applicable first-level referenced textures plus three additional C1L1-related assets. 4bpp PVR v2/PVRTC1 use our previously developed *experimental* decoder; reference exactness is not fully tested. `C1L1_map.tga` uses 16-bit RGBA4444 masks and was converted separately (512×512).
- Generated a true original-texture contact sheet `B12_ALL_C1L1_TEXTURES.jpg` showing Stark Expo architecture, logo and signs, road, vehicles, sky, trees and ground.
- Independently built a genuine original-textured **C1L1 vehicle GLB** from `C1L1_car_01.bdae` and `C1L1_car_02.bdae`: 22 mesh geometries with original UVs and original `C1L1_Vehicles.tga` atlas. glTF Y-up conversion applied; scene successfully reloaded with 22/22 texture visual materials. **The named `little_cars_002LightingMap` lightmap and full shader are NOT yet reproduced.**
- This is **NOT a fully textured level**: most `Standard_*` material-to-texture bindings and mixing of diffuse/lightmaps remain unsolved. The B11 environment remains partial original geometry with placeholder colors. No B12 VPK has been built.
- The C1L1 naming suggests Chapter 1 Level 1, but **the `level1.bclara` mission instance relationship and spawn are not proven**. No direct literal `C1L1` string exists in `level1.bclara` and simply counting BCLARA files does not establish the campaign structure.

## Reproducibility

- `research/b11_material_inventory.py`, `research/b11_pointer_audit.py`, `research/b11_texture_catalog.py` and the successful GitHub Actions job https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38275136012 verify the original texture references.
- Local working bundle `IronMan2_B12_Vehicles_Parser_and_Research.zip` contains the reusable `build_b12.py`, old `pvr_v2_decode.py`, `extractor.py`, `bdae_scene_parser.py`, original texture reference/matching CSVs, preview and sample GLB.
- Separate texture archive `IronMan2_B12_Original_C1L1_Texture_Atlases.zip` contains original-derived decoded PNGs and exact reference CSVs.
- Backed up the full texture bundle to **private user Google Drive**: `https://drive.google.com/file/d/1nMiYcALq7anasa0PVo0Suy22nLwYkN1e/view`. Do not publicly redistribute it.
- Source ZIP and standalone GLB can also be downloaded from the originating ChatGPT conversation while it remains available; the user's original IPA and the B11 parser repository files are the reproducible raw sources.

## Next engineering work

1. Solve **per-submesh material/diffuse/lightmap pairing** by traversing validated 2010 BDAE material tables; don't guess texture by visual resemblance.
2. Build a SMALL authentic-textured, camera-visible C1L1 test slice / LOD rather than throw ~22,919 triangles at our 480×272 CPU rasterizer.
3. Profile actual B10 on Vita: SELECT toggles VSync; record 15-second stationary FPS, AN/CPU/UP/COPY/PRES ON/OFF values. B9 five-suit Vita test is also pending.
4. Decode BCLARA mission instances and real spawn/object placement independently.

Keep private repository PRIVATE; original copyrighted assets must not be posted publicly.
