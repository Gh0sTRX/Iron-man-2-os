# Iron Man 2 iOS → PS Vita C1L1 | G25–G28 original class, scripting, camera source handoff

**15 October 2026** · Branch `feature/b24-unified-gameplay` · Original game asset ownership/private GitHub preserved.

## Hard boundary: original map is NOT finished

The source has original scene geometry and class/node/event data but we have not reconstructed complete C1L1 scene-world parent transform chain, visual material shaders, asset-to-node model bindings, lighting/blend effects, original camera poses, executable event runtime, collision and full VitaGL visuals/FPS. G27 is a source-derived debug/schematic HTML, not genuine iOS gameplay or 3D engine.

## G25 original 2010 native class dictionary (SUCCESS)

- Run: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38747950175 artifact 11978444268.
- 193 exact native class templates, 587 original classed named scene instances out of 601 source string/name-ID candidates. G24 baseline 663/663 original 12/16/12-byte transform records linked to authentic parent IDs (G24 run https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38746502974).
- Crucial exact source **MC original class ID112 == MainCharacter**, source original ID 1062. Its local xyz=(-1.319,-6.747,25.054), no proof actual first runtime spawn or untransformed world origin.

## G26: 71 complete embedded original Lua5.1 script chunks in original 339733-byte C1L1 CLARA (SUCCESS)

- Run: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38749278130 artifact 11980254123.
- 71/71 real original embedded Lua 5.1 binary chunks parsed (full format, no bytecode execution, no changes to game).
- All 71 callback names resolve exactly to original typed CLARA instance IDs:
  - Mission: 45 callbacks
  - Trigger: 17
  - InteractiveObj: 5
  - SpawnPoint: 4
- Early original source handlers: Mission000_OnStart, Mission000_OnComplete, Mission_Go_to_attack_OnStart etc. Original function-name constants include real SetCamera, CutsceneIn/Out, PlayAnim, PlaySFX, PlayVoice, PlayMusic, MoveEntityToEntity, FaceTo, SetInputEnabled, MissionPause/Resume.

## G27: native callsites and exact original scene entity class links (SUCCESS)

- Run: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38750892057 artifact 11981161210.
- 1035 static `GETGLOBAL + CALL` source candidates identified in actual 71 scripts. This is **static opcode/program-counter order**, NOT a reconstructed control-flow graph, verified executed call order, or complete cutscene timeline. Control-flow branches/loops NOT interpreted. Do not claim game engine executed any of these.
- Overall statically observed original callsites include 53 SetCamera, 39 PlayAnim, 48 PlayVoice, 14 CutsceneIn, 14 CutsceneOut, 36 MoveEntityToEntity and 19 PlayMusic.
- Exact source introductory `Mission000_OnStart` instruction mapping:
  - `SetState(1062, "idle")` → MC (MainCharacter)
  - `Show(1456)` → InteractiveObj_QTE
  - `Enable(1808)` → Deco_man1, `Enable(1813)` → Deco_man2 and other eight original Deco_man numbered instances
  - `SetCamera(1864,0)` → Camera_start_show (CameraPreset)
  - `SetCamera(1868,7000)` → Camera_start_show2 (CameraPreset).
- Do not interpret numeric `7000` as a confirmed duration or an entity pointer without engine semantic evidence. SetCamera role-specific arg slot0 is source-ID-verified, other arg slots ARE NOT node ID binding. Music, voice, animation indices currently not tied to original files.
- Owner's offline self-contained **HTML G27 source inspection interface** was built/tested in conversation at `/mnt/data/IronMan2_G27/G27_C1L1_HARITA_KAMERA_GOREV_BETIKLERI.html`. It contains original 2010 source BRES 370-mesh 22919-face top-down city PNG from G19, 587 typed original scene classed objects, selected 71 source Lua handlers, and 1035 static call candidates. Click a Lua call to see its sourced CLARA entity ID info (actual pin shown only if typed transform exists). ZIP: `/mnt/data/IronMan2_G27_Ilk_Harita_Gorev_Kamera_Analiz_Paketi.zip`; paths are valid only in original conversation runtime, not guaranteed in later chats. Script for native CI in repo: `research/b24_unified/b24_g27_original_source_lua51_native_global_call_sites.py`.

## G28: camera class source structure prevents fake camera placement (SUCCESS)

- Run: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38751648926.
- All **57/57** actual original CameraPreset class instances have 3 exact nested native typed child/parent links: tag 0x018D, tag 0x002C, tag 0x0134 (171 nested source records total).
- All 57 contain precisely **18 native tagged vec3 float records** (1026 records), **all are zero**. This is a class-specific raw data proof, not camera world XYZ. The camera movement/relative offset/LookAt scene derivation remains unknown.
- Both intro source IDs 1864 Camera_start_show and 1868 Camera_start_show2 are genuine CameraPreset instances with this nested structure.
- Next camera task: decode CameraConfig (e.g., CC_FollowMC) and CameraPreset nonzero typed fields / actual engine look-at + parent scene relation. Only then display actual authored source 3D camera frusta and cutscene preview.

## User directive (keep always)

**Finish authentic first map and a useful, source-backed preview/testing UI before declaring map complete, reinstalling VPKs repeatedly, or adding new combat/flight mechanics.** Once first map baseline is genuinely usable, restore *actual original* missing armor animations and all ground/flight/combat styles, then start audio extraction/linking (earlier private source audit has 803 RIFF/WAVE candidates) and original cutscene/voice/movie/camera reconstruction for first playable mission. Later missions include distinct on-rails/side-steering mode versus free-traversal scenes. Preserve all variants and build a reusable original scene loader, completing game step by step. Sound/cutscene work queued, not forgotten.

Next map technical priorities:
1. CameraPreset nonzero/CameraConfig pose semantics and initial scene cameras.
2. Original BRES geometry ↔ CLARA node binding, material shader (G13 Expo texture correction; G14-G16 actual CHANNEL1; 4013 original source triangles not yet standard diffuse mapped), node parent world matrix, true scene rendering.
3. Then source-faithful host 3D map with per-material visual comparisons and one unified VitaGL hardware verification.
4. Then original animation/combat plus sound and cutscene bindings for authentic first playable demo.

No new VPK. No original Lua scripts were executed on Vita. Do NOT call project finished.
