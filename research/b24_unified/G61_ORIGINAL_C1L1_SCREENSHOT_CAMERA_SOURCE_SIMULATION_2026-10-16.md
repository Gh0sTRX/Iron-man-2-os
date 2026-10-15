# G61 — C1L1 reference camera source-only render (2026-10-16)

Reference: user-supplied Iron Man 2 iOS screenshot, EXPO globe with Iron Man foreground. **This is NOT a touchHLE gameplay capture**; software-rendered host QA only. The 1280x720 diagnostic render was created locally using original model/UV/PVR data and exported with a reusable Python renderer as a conversation artifact.

## Grounded data
- G57 static source geometry: 296 native TRS-linked meshes / 22,441 real BRES triangles / 18,774 true source UV+PVR textured triangles / 24 original PVR atlases.
- Actual Mark VI textured GLB found in user's private `research/B11_C1L1_Source_Parser.zip` under `assets/Iron_man_mark6_textured.glb`: 802 vertices / 970 triangles. This is **not** proof that the screenshot's armor Mark V and pose are reproduced.
- Two C1L1 sphere pairs: `C1L1_light_002` (about x=0.8, y=-241, z=29.8), `C1L1_light_003` (about x=-3.4, y=48.5, z=29.8). Each includes two source node meshes: outer ~145 triangles / 54–55 units wide, inner ~204 triangles / 50 units wide.
- The actual source BRES records for the two original `C1L1_light_002` sphere shells have `Material__21` and `Material__20`, **zero native UVs**, no proven sampler/PVR diffuse, and unknown shader/cubemap/render semantics. Their dull gray appearance in the host render is a source-missing-shader issue: do not falsely replace with guessed `earth.tga` as if authentic.
- The screenshot's EXPO flag/sign position relative to this sphere, full native sky/moon, original armor pose, runtime camera, HUD, light shader and actual mission state have **not** been reproduced.

## Camera test
- Approximate eye `(-55, -265, 1.6)`, target `(5, -254, 29.5)`, vertical FOV `68°`.
- Diagnostic Mark VI actor root `(-52.3, -264.6, 1.4)`, yaw `4.71 rad`.
- Host-only nighttime ambient, perspective-correct triangle UV mapping, depth buffer, original 2010 source PVRs and sourced Mark VI GLB.
- Original G57 static mesh world coordinates, faces, original UVs/PVR pixels remain unchanged; no runtime textures or game animation inferred, and no new VPK.

## Reproduction
The current-conversation G61 ZIP contains:
`g61_original_C1L1_reference_camera_source_renderer.py`,
`G61_REFERANS_KAMERA_DOGRULANMIS_KAYNAK_RENDER.png`,
`G61_REFERANS_KAMERA_DOGRULANMIS_KAYNAK_RENDER.json`,
`G61_ORIJINAL_VS_KAYNAK_RENDER_KARSILASTIRMA.jpg`, and its technical notes.
To run, provide the owner's private B11 archive and verified G57 source HTML; Python dependencies are `numpy pillow numba trimesh scipy`.

## Next source-first action
Investigate `Material__20/21` native light/globe shader and alpha, actual source environment sphere/EXPO sign relationships, original shot camera/pose, and capture real original touchHLE OpenGL draw state before claiming same frame.
