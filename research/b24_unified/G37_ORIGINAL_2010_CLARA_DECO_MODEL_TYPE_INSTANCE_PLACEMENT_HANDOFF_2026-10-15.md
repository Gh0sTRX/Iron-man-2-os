# G37 · Gameloft Iron Man 2 (2010) first level REAL CLARA Deco resource numbers and local placements — 2026-10-15

**FIRST MAP NOT COMPLETE. ZERO new VPK, ZERO performance optimization.** Physical M1 Vita screenshots showed missing scene binding and scattered mesh groups; latest user wants original placed models, textures and source-authentic preview. This milestone directly targets source static scene instance/resource relationship.

## NEW SOURCE-BINARY BREAKTHROUGH (stronger than G36 names)

Private archival owner source exact first level `level1.bclara` size **339733**, SHA256 `31c794a0140d607c1abd43e463a02cab73d5e2cbbc8495d7cc96f55876aead3c`.

**G37 GitHub Actions verified SUCCESS** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38780288693; artifact **11996100529**. Reproducible source parser `research/b24_unified/b24_g37_original_C1L1_Deco_resource_type_scene_instances.py`; workflow `.github/workflows/g37-original-C1L1-53-deco-native-source-type-links.yml`.

- Independent source class schema (`Deco` class ID **89**) gives **53 authentic named original Deco objects**. ALL 53 have a structured native `0x004D` child-parent record exactly 46 source bytes after node name, parent matches actual Deco source numeric ID, `0x000B, 0x0004` typed native resource-like `uint32` at child record +24; a distinct native 4-byte secondary field at +30. Both ORIGINAL source bytes, not inferred by filename.
- ALL 53 also have original `0x005C` source transform child IDs with native tags `12-byte XYZ + 16-byte xyzw quaternion + 12-byte scale`; original source entity ID/quat/position/scale verified, and previous G34 CSV independently cross-checked all 53.
- **25 distinct native primary source type codes, 41 entities have nonzero local XYZ, 12 have (0,0,0)**. The 12 near-origin nodes are not automatically called renderer instances; likely resource/prototype declarations, role still being researched. Do NOT create 12 extra visible city instances just because they are named Deco.
- Concrete repeated source-code evidence: ALL seven `Deco_fence` through `Deco_fence6` use primary **44** and seven different real scene XYZ; **11** enemy source `Deco` use primary **134**, with distinct secondary integer values **385/386/387**; **10** enemy source objects use primary **136**, all with second integer **403**. So original static source defines source object/resource reuse across distinct positions. These are not original game live engine execution proof.
- Nine high-confidence source name resource-FAMILY correlations from G36 also have a STRUCTURED primary source type code: `Deco_car001`=10 ↔ `C1L1_car_01`, car002=11 ↔ car_02, light001..003=15..17 ↔ `C1L1_light_001..003`, obj001..004=18..21 ↔ `C1L1_obj_001..004`. Crucially this is **not yet an engine-verified integer→BRES archive table**. Final per-instance vertex/world transforms NOT proven, do not apply guesses. The original `Deco` class schema around byte 9088 contains original `Model` + `Object` + `Animation` property name definitions; determine exact binary property binding from this typed schema next.
- Additional original 2010 native codes include 3=Deco_bomb, 14=Deco002, 22=Deco001, 44=fence, 121=Deco_Direction, 134/136 enemies, 137 other props, 139 Explosion, 162..165/205..207 civilians. Original CLARA authored local positions can now be mapped for 41 actual nonzero Deco records, independent of inferred model resource world placement.

## Actual user-viewable static visual/source files created in same active container

Under `/mnt/data/IronMan2_G37_Kaynak_Instance/`:
- `G37_A_53_DECO_ORIJINAL_KONUM_HARITASI.png` actual prior original 2010 BRES polygons and PVR centroid samples with 41 exact class Deco source-local XYZ overlays and evidence legend; original shading, entity-to-mesh world matrices not claimed.
- `G37_B_AYNI_KAYNAK_FARKLI_YERLESIM_28_NESNE.png` visualizes all 7 fence + 11 enemy134 + 10 enemy136 source positions / original local XYZ listing alongside true-source city map.
- `G37_53_ORIJINAL_DECO_KAYNAK_TURU_KOORDINAT.csv` 53 typed class Deco original ID, native model-like type/secondary field, raw file offsets, xyz/quat/scale, origin/placed flags, G36 provisional family and explicit no engine BRES proof.
- `G37_25_KAYNAK_TUR_GRUBU.csv` type histogram and member original names.
- `G37_ORIGINAL_DECO_INSTANCE_KANIT_RAPORU.json`, `G37_OKU_BENI_TR.md`.
- ZIP `/mnt/data/IronMan2_G37_Kaynak_Instance_Tek_Paket.zip`. Links only valid if paths verified in current container.

## Next source-only priorities, absolutely NOT VPK/performance
1. **Resolve integer native resource model ID 10/11/15–21 to actual BRES source objects/meshes and find separate original BRES per-object root local→world matrix;** no name-only assumption. The high-confidence nine source labels now triangulated with real typed numeric source fields.
2. Recover source runtime instances and parent matrix computation using `Deco` class original `Model/Object/Animation` property schema; secondary 385/386/387/403 roles unknown. Differentiate 12 origin records from 41 nonzero local positions.
3. Once binary validated, apply genuine local-to-world placements to original city models and produce image snapshots showing actual geometry, not dots alone; decode material category for 4,145 remaining no-standard-PVR shader triangles, especially original `lights` and `urban`.
4. Map is unfinished; animation/combat and original audio/cutscene stage comes only after faithful usable first map, as user ordered.

CI only parsed original source, no user device test, no engine execution. Preserve private archival assets and older M1/M2 separate builds.
