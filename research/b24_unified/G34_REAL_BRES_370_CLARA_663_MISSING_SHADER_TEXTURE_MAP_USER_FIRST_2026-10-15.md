# G34 — C1L1 original coordinates + texture gap source-first static preview (2026-10-15)

## User directive: MAP ONLY
The user explicitly overrode mapviewer FPS profiler focus: **STOP performance tasks, stop GPU culling/occlusion and no new VPK**, invest effort solely in authentic first level model placements, original authored coordinates, missing diffuse or other source shader behavior, with actual visible preview at each step. Previous M1 Vita screenshots exposed a bare green ground and disconnected structures. Do not fabricate positions or any replacement texture.

## Locally produced, checked G34 original-source deliverable

Verified locally on immutable earlier **G32 original source HTML** (original native 2010 BRES geometry + actual 24 source atlas decoded PVR pixel data + exact BRES indexed UV) and **G23 original source CLARA scene inventory** (original 2010 level1.bclara native typed node transforms):
- Authored BRES exactly **370 meshes, 37,946 vertices, 22,919 indexed source triangles, 460 native material batches**.
- Source CLARA **601 native named/ID records and 663 original tagged 12-byte XYZ + 16-byte quaternion + 12-byte scale transform records**.
- **24 source-authored material-linked atlases** available with exact PVR pixels, 18,774 BRES source triangles have original UV+PVR links; includes Expo 40th extra atlas.
- **NO geometries moved.** G34 exported per-mesh 370-row source raw min/max XYZ CSV and all 663 CLARA local transforms (including entity ID, child ID, parent ID, quaternion/scale) CSV. These are TWO DISTINCT native source coordinate sources with **NO fully proved BRES mesh ↔ CLARA actor/resource binding**. The CLARA list is not a final world-coordinate scene placement!
- G34 built user-facing STATIC PNG (not dead HTML interactions) plus independent atlas contact gallery and focused non-invented exact missing-material-mesh contact previews. A/B are overhead from raw native source triangles; pixel color is ONE real PVR texel at triangle centroid, not original GPU per-pixel texture/shader or verified actual iOS scene. D paints unknown shader state as diagnostic color; E reproduces exactly real indexed BRES source mesh triangles with panels re-framed individually, NOT repositioned in the actual scene.
- Current conversation's **verified** sandbox:
  - `/mnt/data/IronMan2_G34_Kaynak_Harita/G34_A_TUM_2010_KAYNAK_HARITA_ONIZLEME.png`
  - `/mnt/data/IronMan2_G34_Kaynak_Harita/G34_B_SEHIR_MERKEZI_ORJINAL_KOORDINAT.png`
  - `/mnt/data/IronMan2_G34_Kaynak_Harita/G34_C_24_ORIJINAL_PVR_ATLAS_GALERISI.png`
  - `/mnt/data/IronMan2_G34_Kaynak_Harita/G34_D_EKSIK_SHADER_MATERYAL_ISI_HARITASI.png`
  - `/mnt/data/IronMan2_G34_Kaynak_Harita/G34_E_ORIJINAL_MATERYAL_EKSIK_MESH_12_KONTAK.png`
  - `/mnt/data/IronMan2_G34_Kaynak_Harita/G34_370_BRES_OZGUN_MESH_KOORDINATLARI.csv`
  - `/mnt/data/IronMan2_G34_Kaynak_Harita/G34_663_CLARA_OZGUN_KONUM_DONUSUM.csv`
  - `/mnt/data/IronMan2_G34_Kaynak_Harita/G34_KAYNAK_MATERYAL_EKSIK_LISTESI.csv`
  - `/mnt/data/IronMan2_G34_Kaynak_Harita/g34_sahne_doku_inceleme.py` (reproducible script using previous G32 and G23 source outputs).
  - ZIP `/mnt/data/IronMan2_G34_Orijinal_Harita_Koordinatlar_Dokular.zip` size 1,558,407 bytes SHA256 `a149e043231b622c175805aecbe675e2e33a80e0890afcc8851ffb5689be8e90`.
  All local conversation paths must be VERIFIED again if asked in a new container session. Do not pretend these are public GitHub artifacts.

## Newly narrowed genuine 2010 shader/texture problem — KEY

Source material positive-PVR / UV statuses by REAL original source triangles:
- 18,568 true standard PVR+UV, 206 true Expo40 PVR+UV = **18,774 textured candidate (81.9%)**.
- 1,861 UV-positive / nonstandard shader missing standard diffuse; 2,152 neither source standard PVR nor useful UV; 132 standard PVR reference but no mesh UV = **4,145 non-standard source diffuse triangles**.
- **ALL 4,145 unresolved triangles are in only TWO native environment geometry families:** **3,382 / 3,382** authentic `C1L1_light_001..003` source triangles; plus **763** nonstandard `C1L1_obj_001..004` urban source triangles. Original ground (3,280) and vehicles (5,116) are NOT in this 4,145 unresolved category. `light` is a **BRES SOURCE MODEL group/family**, NOT the four CLARA Sun Light objects.
- Material `c1l1_3building` = **1,683** missing standard PVR-link triangles (920 BRES light + 763 urban). The same-named material has different original per-BRES native property data across source resource files; cannot universally assign one missing atlas by material-name matching.
- `Material__20` **408** source-light nonstandard triangles with no useful source diffuse+UV; from exactly two original BRES meshes `C1L1_light_002_87` and `C1L1_light_003_51` each **204** true source faces, visually source-built hemispherical domes in contact E.
- `c1l1_3building` first 2 prominent authentic light arches `C1L1_light_001_69` and `C1L1_light_003_47` each **460** real source triangles, UV-positive yet no standard sampler link.
- Native `Material__17` 384 source triangles; `Material__19` 296; `Material__21` 290; `Material__46` 288; `Material__13` 254 +118; `Standard_16dd` has 132 PVR-linked but no UV (all source light family). These need actual shader family flags/40/60B properties and native engine code semantics; don't paint guessing RGBA or repurpose the 16 unreferenced atlas names.
- The four actual CLARA Sun Light class objects are **separate** from BRES light polygon category, to avoid false engine semantics.

## Root placement problem still not solved
The Vita M1 rendered the recovered **raw BRES vertex coordinates** with authentic source atlas pixels but without the source engine's model resource owner/instance transforms. Existing CLARA 663 local transform record registry is real, but no authoritative object ID ↔ BRES mesh join yet. G33 earlier observed 40 mesh raw AABBs entirely outside the aggregated native ground AABB (28 urban, 7 vehicle, 5 light) and this is **not proof** the original game placed 40 props incorrectly; missing original hierarchy/scene resource manager may be responsible. Do not guess a correction offset or translate assets merely toward the green ground.

## Map-only NEXT
1. Search authentic 2010 level source resource manager / level placement tables and **original BRES model record identifiers** (not naive `.bdae` string lookup in CLARA, shown absent), solve exact per-model source-to-CLARA links / parent world matrices. Preserve already loaded 370/663 coordinate provenance.
2. Rebuild original nonstandard shader properties for `C1L1_light` and `c1l1_3building` / Material__20 and use evidence-graded corrections only where semantics are proven. Treat truly missing textures separately from mesh polygons intended for non-PVR shader/vertex colors.
3. Produce a NEW static native-source visual each stage (PNG/A-B/isolated meshes). User's iOS app doesn't reliably support interactive HTML, so static preview preferred. No VPK/performance/culling task requested now.
4. Save map completion milestone only after actual authentic first scene positions, materials, texture bindings and camera confirmed; user wants later animation/combat/audio/cutscenes retained in roadmap but not current focus.
