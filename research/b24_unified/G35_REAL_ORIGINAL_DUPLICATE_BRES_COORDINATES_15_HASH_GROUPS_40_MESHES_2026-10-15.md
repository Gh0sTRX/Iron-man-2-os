# G35 — 15 byte-exact 2010 BRES repeated-geometry clusters, coordinate ownership proof (2026-10-15)

User directive: MAP ONLY: original C1L1 world placement, correct native model positions and source textures / source renderer semantics; no performance profiling, no VPK, no guessed model repositioning.

## Exact independently source-checked original BRES triangle duplicate evidence
Using recovered original owner G32 source `37,946×float32 XYZ` with **22,919 3-index triangles**, together with original 460 per-mesh material batches, we computed each one of 370 BRES mesh's exact ordered triangle-vertex position byte stream (FLOAT32 three coordinates × 3 vertices × faces), hashed with SHA256, compared full 370 original native geometry.
- **345 distinct source-native ordered-geometry byte hashes** out of 370 mesh records.
- **15 groups of exact byte-identical triangle geometry**, totalling **40/370 original BRES mesh records**.
- The exact repeated raw coordinates are source-local-data facts; they are NOT scene-instance/world-transform proofs or a reason to artificially move a mesh.
- Critical native original PVR-missing light dome **`C1L1_light_002_87`** and **`C1L1_light_003_51`** each have 204 original faces and EXACT same ordered 2010 float32 triangle positions, same raw bbox center **(0.016550,0,0)** and same source-shader `Material__20`. Their original true parent/world placement is NOT decoded. M1 draws both original geometry at the same original raw coordinates; if the original game draws separate instances, it must provide authoritative transforms elsewhere. This is a strong lead, **not proof of two game-world dome positions**.
- Two original arches `C1L1_light_001_69` vs `C1L1_light_003_47` are NOT identical source triangles (both 460 faces); they have authentic raw centers ~(-163.590,195.780,-32.659) vs (210.256,49.651,-28.129). Do not apply a presumed symmetric transform from these alone.
- Other repeated source-original pairs: `C1L1_light_002_86` and `C1L1_light_003_46` (145 authored faces each), several 2–7-element duplicate geometry groups. The complete 15 groups including authentic XYZ source centers and original mesh names were exported as CSV.

## Reproduced actual pictures / data generated in this user conversation
- Source `/mnt/data/IronMan2_G34_Kaynak_Harita/g34_sahne_doku_inceleme.py` re-reads private original-derived G32 WebGL source data and G23 native CLARA inventory, generates G34 static previews and G35 SHA256 ordered native FLOAT32 triangle group comparison; verified 15 groups of 40 original meshes.
- Source-image `/mnt/data/IronMan2_G34_Kaynak_Harita/G35_AYNI_HAM_KOORDINATLI_MESH_KUMELERI.png` has 15 distinct authored source shape groups, original centers; no guessed placement.
- `/mnt/data/IronMan2_G34_Kaynak_Harita/G35_15_TEKRARLANAN_ORIJINAL_GEOMETRI_KUMESI.csv` is exact source shapes, location and group membership.
- Combined verified ZIP `/mnt/data/IronMan2_G34_G35_Koordinatlar_Dokular_ve_Tekrarli_Meshler.zip` size 1,643,304B SHA256 **993bcbf11dff39428e3ebb4f8ab2120bc76dc32d7dc3c6f3afb023d9a5ffcc5a**, includes G34 5 PNG, G35 PNG, 370 original mesh coordinate CSV, 663 original CLARA local transform CSV, 15 repeated group CSV, 24 atlas picture and source script. Paths must be reverified in next container session before linking.

## NEXT genuinely solve original scene
Search static environment BRES native scene/matrix/mesh instance table, original scene-level resource-ID name↔file and CLARA root parent transforms; determine whether original engine instantiates similar static mesh into more than one world position. Independently prove each target instance world matrix then render source geometry transformed as original. Do not confuse the CLARA four classed Sun Light source nodes with the 211 BRES `C1L1_light` environment geometry meshes (all 3382 faces non-standard diffuse/UV). Original `Material__20` and `c1l1_3building` require actual 2010 shader semantics.

Do not claim C1L1 map completed.
