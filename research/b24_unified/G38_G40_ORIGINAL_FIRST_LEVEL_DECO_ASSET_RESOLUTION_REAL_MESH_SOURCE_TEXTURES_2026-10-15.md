# G38–G40 — Original 2010 C1L1 Deco model ID, real mesh placement and source texture atlas (2026-10-15)

**Highest project priority: build faithful first level map, no performance/VPK/UI/gameplay work until user changes it.**

## G38: PREVIOUSLY UNKNOWN DIRECT MODEL RESOURCE LINK — PROVEN
- CI **SUCCESS** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38786432234 artifact **11997223243**.
- Original owner iOS 2010 IPA `Payload/IronMan2.app/models` is a **207-entry Gameloft named archive**, ordered as authored. Original class `Deco` 0x4D resource ID in `level1.bclara` is a **ONE-BASED** index into the archive, model index = CLARA field − 1.
- Nine independent C1L1 car/light/obj name relationships verified **9/9** at shift −1; shift 0 and +1 scored 0/9. Therefore **53/53** original source Deco node resource refs resolved directly to exact original .bdae source archive members; **25 distinct resource files**.
- Ground model `Deco002` ID14→`C1L1_ground_001.bdae`; sky `Deco001` ID22→`C1L1_sky_001.bdae`. City obj 18–21 and light 15–17 matched exactly.
- **Important reused model**: `Deco_fence` and `Deco_fence1–6` all raw ID44→`C2L1_fense.bdae` (genuine cross-stage model reuse). Enemy type 134→`Enemy_spider.bdae` (11 Deco nodes); type136→`explosion.bdae` (10 Deco nodes); man/citizen models follow exact source archive names (`man1/man2/woman1/Woman_3`, etc). `Deco004/005`→`expo_crash.bdae`.
- Original Level1 BCLARA still has no literal asset filename because it stored its **one-based numeric model archive indices**, explaining G33 problem. This is the actual missing model/resource manager link, not arbitrary name guessing.
- Source script `research/b24_unified/b24_g38_original_models_pack_index_to_CLARA_deco_exact_binding.py`, private source-only workflow `.github/workflows/g38-native-original-2010-Deco-to-models-index.yaml`.

## G39: AUTHENTIC 2010 DECOR ACTOR TRIANGLES × NATIVE SOURCE POSES — PROVEN
- CI **SUCCESS** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38787260135 artifact **11997169276** (real source PNG and JSON).
- Reimported actual **25/25 authentic BRES 0.0.0.133 models** (private `B11_C1L1_Source_Parser.zip`), none failed.
- Applied exact `level1.bclara` per-Deco source XYZ translation + normalized source quaternion + native scale to source model vertex coordinates. **41/41 original nonorigin `Deco` node instances contain real 2010 model triangles**, totaling **10,379 instance triangles**. Rendered original geometry over previously recovered 370 static authentic BRES city models/22,919 source faces in reproducible PNG. No guessed meshes.
- Origin/identity 12 source-model Deco instances are NOT drawn twice over already included static authored environment BRES; source model identity and origin preserved in JSON registry. G39 (25 unique models, 41 positioned) does NOT establish runtime visibility/cutscene activation or complete parent-world transform chain.
- Original `C2L1_fense.bdae` is actually 2 source triangles per instance. Seven fences have original native transforms including orientation and anisotropic scale. Actors like `Enemy_spider.bdae` are 350 original triangles each; `explosion.bdae` is 318 each; civilian models have 200–316 each.
- `research/b24_unified/b24_g39_original_C1L1_53_Deco_authentic_meshes_local_placement_map.py`, `.github/workflows/g39-original-model-Deco-local-placements-source-PNG.yaml`.

## G40: SOURCE MATERIAL / PVR RECONSTRUCTION CROSS-CHECK — PROVEN BOUNDARY
- CI **SUCCESS** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38788023201 artifact **11998528077**, PNG contact sheet and structured JSON.
- All 25 source `.bdae` models accept native 2010 shader/material 60-byte property parser. **25 unique actual original TGA image names** referenced by authenticated indexed material property values are all **present in owner 2010 textures archive**, and **25/25 original PVR** decode successfully to source-derived real pixel preview. Includes `CAHP01_c_expo_building.tga`, `C1L1_grass`, `building4`, `Vehicles`, road, window materials.
- CRITICAL: Actor/dynamic noncity `Enemy_spider`, `woman1`, `man1`, `explosion`, `C2L1_fense`, `expo_crash`, `bomb` have **no direct 60B standard native TGA diffuse sampler** proven in this decoder. The 25 genuine source TGA names come mainly from C1L1 static environment ground/obj/light/car. Do NOT invent actor textures. Their render routes (vertex colors, sprite/skin channel, special shaders, global texture bank) need further native reverse engineering.
- G40 `research/b24_unified/b24_g40_source_2010_first_level_Deco_authentic_BRES_PVR_shader_material_atlas_audit.py`, workflow `.github/workflows/g40-first-level-original-Deco-BRES-PVR-atlas.yaml`.

## Actual present conversation downloadable user evidence (sandbox must be verified in future sessions)
- `/mnt/data/IronMan2_G38_Model_Resource_Kaniti/G38_53_DECO_ORIJINAL_MODELI_KOORDINATLARI.csv` (all 53 exact source names, original archive model filenames and native local XYZ)
- `/mnt/data/IronMan2_G39_Gercek_Model_Yerlesimleri/G39_ORIGINAL_C1L1_53_DECO_MODEL_PLACEMENT_SOURCE_PREVIEW.png`
- `/mnt/data/IronMan2_G40_Gercek_Dokular/G40_REAL_DECO_NATIVE_2010_PVR_ATLAS_PREVIEW.png`
- Consolidated technical preview `/mnt/data/IronMan2_G38_G40_Sahne_Birlesimi/G38_G40_HARITA_GERCEK_MODELLER_DOKULAR_BIRLESIK_16_9.png`
- All source-derived files with JSON and docs `/mnt/data/IronMan2_G38_G40_Sahne_Model_Doku_Birlesim_Paketi.zip`

## NEXT critical, source-first goal
Resolve actual 2010 actor/scene world-parent transform matrix and visibility + actor animation/skin shader binding; do not misreport 41 source local instances as a completed in-game map. Prior incomplete 4145 static triangles require separate original light/color/alpha shader semantics (G14–G16). Original C1L1 geometry far outside square on real Vita M1 still needs world placement, level-specific model membership and 2010 culling/runtime parent transforms. Keep PS Vita performance work deferred per user.
