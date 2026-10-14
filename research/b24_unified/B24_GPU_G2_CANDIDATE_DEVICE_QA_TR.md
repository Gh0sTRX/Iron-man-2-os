# Iron Man 2 PS Vita — GPU B24 G2 Adayı / Gerçek Cihaz Testi (14 Ekim 2026)

**Kanonik ilk GPU-donanım adayı, tamamlanmış oyun değil.** Kullanıcının 14 Ekim talebi üzerine eski NO-VPK politikası açıkça kaldırıldı. B24 GPU G1 başarılı derlendi fakat gerçek Vita'da test edilmedi. G2 aynı tek oyun motoruna mevcut B17/B24 animasyon, kontrol, HUD ve şehir + ilk gerçek GPU-only render yoluyla original Z-up armor root pitch/bank ekledi.

## Gerçek üretim bilgisi ve güvenlik
- Private kaynak dalı: `feature/b24-unified-gameplay`
- Gerçek VitaSDK CI başarılı G2: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38537388262
- Artifact: `IronMan2_GPU_B24_G2_Candidate_VPK`; artifact ID **11880193587**
- VPK: `IronMan2_GPU_B24_G2.vpk`, tam dosya **13,914,976 bayt**
- SHA256 (VPK, zip-artifact dışındaki gerçek kurulum dosyası): `dfe4741558bb1c749f5ed67b129778040f45a4edd68418c7cf9cba202f0ad5ad`
- `TITLE_ID=IM2G00027`, `TITLE=Iron Man 2 - GPU B24 G2` — B15, B17, B24-C2 ve G1'in yerine yazmaz.
- Source-only JET/overlay test: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38537217557 PASS (G2 armor matrix valid, original B17 no-animation-duplication).
- Combined VPK build 5 original-derived armor .im2t and **59** .im2v incl. B13/B15/B16 originals/retargets; **304** original named source clips are inventory, NOT all baked.
- Reproducible C1L1 assets included: `maps/C1L1_environment.c1g2`, `.c1uv`, `.c1ma`, diagnostic old `.im2map`. 37,946 source vertices, 22,919 triangles; no false original diffuse mapping. Genuine B12 vehicle atlas `.c1tx` is **not in this VPK**, currently other than five textured suits city still diagnostic category color.
- True `-DB24_ENABLE_GPU=ON -DB24_ENABLE_NATIVE_HUD=ON`; GPU-only main excludes old SDL window/render/update/present; single VitaGL GXM frame owner; original CPU physics, input, B14/B16 skin/animation data stream remain authoritative. GPU build link **PASSED**, real Vita graphics/FPS **NOT VERIFIED**. Shader compiler dependency `libshacccg.suprx` may need device check if boot fails.

## 5-minute TEST (after user chooses to install; no false success claim)
1. **Cold boot:** Does app reach scene? A photo of screen and any error/hang. If startup fails, note whether immediate exit/black screen and how long. Do NOT delete older B17 backup.
2. **GPU city:** one image at starting camera: see original full-scale roads/structures vs all-black screen/culling/oversized blocks; should NOT be 4x4 CPU C2 pixels. City material colors remain diagnostic until source shader sampler restoration. Mention sky/texture orientation of suit if reversed.
3. **Input isolation:** Press face buttons, triggers, D-pad ONE BY ONE. Only START may pause; Circle should resume; SELECT should cycle armors. If any other button pauses, mark P0 regression immediately.
4. **Armors and walking:** screenshot of Mark VI then War Machine (optional other three), move left stick forward/back, observe legs/arms and whether B17 locomotion feel preserved.
5. **Fly and bank:** Circle takeoff/land, start forward Stage2; direction changes and RUSH Triangle; screenshot of armor while right stick changes camera pitch / left steering changes yaw. Observe *visually* whether stage2/RUSH armor pitches/banks, whether camera follows after releasing right stick. A GPU root pose turning does NOT prove actual pitch-driven 3D acceleration.
6. **Combat:** R should fire; ensure no wrong left arm alternation, shoot while walking; Unibeam should originate from chest but G2 animated bone socket/genuine beam trajectory remain unverified. Square melee remains incomplete actual original combo clips, do not call it full melee.
7. **Pause/UI:** readable `PAUSED`, start/circle resume, right/left suit switch? pause should freeze world, no overlapping double visor, reticle aligned with view; missile lock only if missile mode. `CROSS OPTIONS` is a current display placeholder, NOT evidence of a functional submenu.
8. **Performance:** record perceptual responsiveness or HUD FPS if present, plus any CPU/UP timings explicitly shown. Shader/GPU busy and VSync wall are distinct; claim no GPU FPS improvement until actual hardware evidence.

## Unfinished and non-negotiable acceptance gates
- FULL native B24 GPU render must become real working PS Vita frame with no crash and reasonable measured fps; bad B24 C1/C2 physical output remains previous baseline.
- Original CITY 94 triangle material IDs/39 texture names -> actual sampler diffuse/lightmap binding, B12 original car atlas, authentic original UV orientation, sky/color/shadows/collision/spawn. City now 4 material *category* GPU draws and diagnostic color only.
- True B17-Z-up stage2/3 climb/dive velocity and directional body orientation alignment with camera, landing contact gate, collision. GPU G2 root pitch/bank is VISUAL ONLY; Stage1/2/3 jets still missing proper animated bone socket mapping and rendered particles. Back jets RUSH ONLY (mandatory).
- Original player 248 Iron Man/56 War Machine named animations vs 59 B24 streams, original Ground_Combo1/2/3/Power full bake, genuine right-arm repulsor walking overlay, original chest Unibeam socket, War Machine fly/land normalization, hit sync, B19 rendered mission enemies/AI + first mission objectives, coherent pause menu/audio. No falsely completed checklist entries.

**Next development from this record:** Based on first *physical* GPU render report, fix startup/culling/texture/GXM first; if GPU actually draws, prioritize original B12 vehicle atlas and reverse BRES material diffuse slot, then pursue keyframe/rig and full 3D movement. Avoid blindly piling VPKs on broken GPU builds.
