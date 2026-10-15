# G14 / G15 | Iron Man 2 iOS 2010 original C1L1 shader evidence

15 October 2026. SOURCE-ONLY analysis. No Vita VPK and no gameplay build.

## Verified milestones

- G14 run: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38724149555 — SUCCESS. Artifact 11966329661, searchable offline HTML and full native source JSON.
- G15 run: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38724650777 — SUCCESS. Artifact 11967711006, raw native shader parameter record JSON.
- 10 authenticated source 2010 BRES scene models, 370 real meshes, 22919 triangles.
- Two actual Material__20 meshes C1L1_light_002_87 and C1L1_light_003_51 have 408 original triangles TOTAL: no source UV candidate and no verified standard diffuse PVR.
- Two actual c1l1_3building curved arch meshes C1L1_light_001_69 and C1L1_light_003_47 have 920 original triangles TOTAL: positive UV candidate, no verified standard diffuse PVR. Do NOT substitute guessed c1l1_building.tga.
- 132 Standard_16dd light triangles have source PVR but NO source UV candidate; UV and diffuse original light mesh-level intersection is ZERO.
- Urban c1l1_3building material has 871 triangles, 108 of which have an exact source diffuse sampler (obj003), others do not. Exact file-qualified material identity matters.
- Urban original Expo material orig_07___Default has 206 faces, authentic 2010 source UV and CAHP01_c_expo_building.tga.

## G15 native shader record findings

194 original native per-file material records classify into SIX raw 88-byte shader flag families:
- 154 records: signature [1,0,0,2,2], original PVR-linked.
- 24 records: signature [0,1,1,2,2], no original PVR link (includes Material__20).
- 9 records: signature [0,0,0,1,1], no original PVR link (includes c1l1_3building).
- Remaining 7 records across three rarer families.

Non-PVR c1l1_3building source shader property block is 40 bytes, beginning in raw uint32 with 0xFF000000. Material__20 source shader property block is 60 bytes and starts with 0xFF959595. These bit patterns look like possible packed colors but their R/G/B/A meaning, blend/emissive usage and original rendering effect are NOT proven. Do not render gray/black as an exact original shader or call it a recovered light effect.

Crucial: c1l1_3building in C1L1_obj_003 uses 60B sampler-linked property with c1l1_building.tga; same material name in other 2010 BRES files uses 40B no-PVR. A name-only global bind will corrupt real shader semantics.

## Next map-only work

1. Cross-reference native ARMv6 engine shader/color/render-state callsites and 2010 BRES source property types before interpreting RGBA/alpha, do not copy later BDAE v779 struct meanings without proof.
2. Probe level1.bclara original scene authored transformations, spawn and original camera. G10 0,0 is prototype only.
3. Once verified, add shader family-specific scene stage to host *with explicit proof status* and compare unchanged original mesh+UV scene camera. No fabricated geometry/materials.
4. Stage one combined real VitaGL full G13+original-authored renderer test when visuals are source-traceable, rather than repeated VPK installs.
5. Preserve parked gameplay/flight/weapon mechanic features and previously verified B24 firmware results without falsely calling a rebuilt native iOS port.

G14 and G15 code: research/b24_unified/b24_g14_original_2010_c1l1_shader_material_fingerprints.py and b24_g15_original_shader_parameter_family_native_bytes.py. Both GitHub Actions runs passed. No new VPK.