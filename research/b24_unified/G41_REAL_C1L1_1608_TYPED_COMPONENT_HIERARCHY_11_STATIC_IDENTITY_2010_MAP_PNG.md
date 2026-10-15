# G41 source C1L1 typed component scene hierarchy and honest current map PNG (2026-10-15)

The user requested to **continue finishing the map with hierarchy** and get a PNG preview of how the actual system's map looks now. NO new VPK, NO performance, NO fake placement.

## What source shows (G41 actual native CLARA)

- Source original `level1.bclara` hash `31c794a0140d607c1abd43e463a02cab73d5e2cbbc8495d7cc96f55876aead3c`.
- 601 source type-1 printable name/ID candidate records, but 594 unique candidate numeric IDs; 14 not classed, and **587 actual classed named scene instances** (G25 validated). Do **not** call all 601 actual unique actors.
- **1,608 native CLARA typed-component child records**, linked to **494 native candidate named owner IDs**. Their **1,608 child IDs are all unique and NONE is a top-level named actor ID**, so this is a **classed scene component/owner graph**, NOT evidence that every linked child is an independently rendered actor with parent world matrix. Evidence includes exact native `u16 tag, u8(1), childID, u8(0), ownerID`.
- Of the 1,608 typed components, **685 have native `0x005C` type prefix**, but only **663 have rigorously validated source 12-byte XYZ, 16-byte quaternion, 12-byte scale triple**. Other 22 native 0x005C records have NOT been resolved as full rigid transforms — do not force-decipher them.
- The 663 valid native rigid subcomponents are attached to 389 distinct named owner nodes: **252 named nodes have exactly 1**, **137 classed `PositionDummy` nodes each exactly 3**, and **212 name candidates have none**. G25 independently validates the 137 are true `PositionDummy` class instances.
- G38 native model index→original 207-entry original `models` archive proves 53 `Deco` actual class instance→true .bdae source. Each Deco owns a native source `0x004D` resource component AND a `0x005C` rigid-transform component. G39 geometric source proves 41 placed local nonorigin actors with 10,379 authentic original source triangles.
- **CRITICAL NEW SOURCE CONSTRAINT:** All **11 `C1L1_*.bdae` original static environment model `Deco` nodes** (`ground_001`, `light_001..003`, `obj_001..004`, `car_01..02`, `sky_001`) have exactly **(0,0,0) source local position, identity quaternion and (1,1,1) scale**. The 12th identity-origin Deco is `Deco_Direction`→`direction.bdae`. The original displaced/off-slab source city polygons seen on the physical Vita must **NOT** be "fixed" by arbitrarily offsetting these static Deco objects; investigate original BRES per-mesh author positions, root transforms, class asset runtime visibility/scene state/cutscene layer. The actual final runtime root-world matrix not yet resolved.
- Native CameraPreset 57 nodes have 51 true references to three-component `PositionDummy` nodes and 6 `0xffffffff` null targets; all have separate config reference to `CC_FollowMC` native ID 587. Camera→PD and Camera→CC are TWO INDEPENDENT references, not a literal Camera→PD→CC parent chain. Raw transforms do not establish original eye/look-at or timeline.
- Source 370 BRES static meshes = 22,919 original triangles. Authentic original 2010 PVR+UV candidate coverage from G32 18,774, remaining 4,145 source triangles unresolved special shader/diffuse state, not necessarily missing source image.

## Durable repository work

- Reproducible source-only parser + G39/G40 original asset PNG compositor:
  `research/b24_unified/b24_g41_original_C1L1_native_scene_1608_component_hierarchy_and_png.py`
- Standalone GitHub CI:
  `.github/workflows/g41-original-2010-CLARA-1608-component-hierarchy-map-PNG.yml`
- G41 first successful run https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38791418042, artifact **12000601865**, source-derived genuine BRES/actor map PNG, original PVR contact sample, structured JSON and CSV for 1608 typed components, 663 rigid, 53 source Deco models and 57 camera→PD refs. Second run after extra original static identity-local transform strict audit starts at https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38791679656 .
- Current session user-requested **explicit 16:9 native source snapshot** verified PNG path: `/mnt/data/IronMan2_G41_Sahne_Hiyerarsisi/G41_LEVEL1_MEVCUT_HARITA_HIYERARSI_16_9.png`, built from G39 original 370 static mesh and 41 placed original Deco instances + G34 original PVR sample and correct component schematic. **Not an original game screenshot or true final 3D shader.**
- Current session ZIP `/mnt/data/IronMan2_G41_Sahne_Hiyerarsisi_ve_Anlik_Harita.zip` (preview PNG, 1608/663/53/57 CSV, strict evidence JSON, Turkish readme). Sandbox path valid only in present session; verify in future before linking.

## Next source question (IMPORTANT)

Find actual **runtime activation/visibility flags** and optional **scene root coordinate transform** for the original static ground/obj/car/light asset groups. All original environment `Deco` local transform records identity, so the missing slanted/floating/side clusters on real Vita may be objects genuinely outside currently active mission area, mesh-internal authored different origins, sky/light shader not decoded, or stage-specific hide/show/cutscene activations. Prove from original CLARA class property tags and original 71 Lua mission scripts, and original ARMv6 renderer if needed. No invented corrective translations. User wants updated PNG previews as source evidence accumulates; no VPK/performance until map complete.
