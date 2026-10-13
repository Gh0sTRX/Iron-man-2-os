# B24 / B17'DEN BUGÜNE GELEN TÜM EKSİK İŞLERİN TEK CANLI İZLEME KAYDI
**Karar (14 Ekim 2026):** Kullanıcı özellikle **yeni VPK İSTEMİYOR**. Araştırma, kaynak kurtarma, gerçek GPU motor geçişi ve eksik/yarım animasyonları düzeltmeye odaklan. `feature/b24-unified-gameplay` aktif geliştirme dalıdır. B15/B17 iyi hareket referansı ve C1/C2 başarısız fiziksel testleri tarihi korunur. Herhangi bir GitHub CI/audit bu dönemde sadece **host kaynak testi** ve **VitaSDK .o obje dosyası derlemesi** yapabilir; `vpk`, Vita executable, yayın veya release **OLMAYACAK** (kullanıcı yeni test istediğinde ayrı onay ve build).

## Kanıtlı BUG/İstek kaydı — yanlışlıkla 'bitti' denemez

| Alan | Önceki B17→B24 istekleri / kalan işler | Doğrulanmış durum | Tamamlanma şartı |
|---|---|---|---|
| C2 acil giriş | *Her* tuşun Pause açması | **SOURCE FIX + HOST PASS**, gerçek Vita doğrulanmadı | yalnız START pause, Circle resume; SELECT gerçek suit, Dpad altitude/weapon, R fire, Square melee; gerçek cihaz |
| GPU ana motor | B17 CPU 480×272 raster + SDL_UpdateTexture ~29ms | B24 yeni C1G2 orijinal indeksli mesh exporter + GPU draw adapter var; VitaSDK objesi derleniyor/derlendi; **gerçek context/present henüz yok** | tek VitaGL GXM context, gerçek z-up projection, 3D env+5 skinned armor+HUD depth GPU; CPU framebuffer kalktı; cihaz FPS |
| Chapter 1 model | C1L1 kaynak binalar/araçlar tam görünsün | 370 B11 mesh → **37946 vtx / 22919 tris / 68757 uint16 indices / 4 draw groups**, kaynak PASS; B24-C2 365 tri + 4×4 CPU debug başarısız | gerçek batched GPU geometri ve doğru dünya spawn+frustum+collision; cihazda görünür sokak |
| C1L1 texture/material | 2010 orijinal oyun şehir dokuları | B12 39 exact texture refs / 42 PNG, B11 GLB **TEXCOORD_0 YOK** | gerçek BDAE UV0/lightmap UV1, material-to-texture ID, texture atlas shader/draw |
| 3D uçuş | hover→Stage2 full stick→RUSH, gerçek yukarı/aşağı eğim, sağ/sol yatış | B22.2 host sim, B17 Z-up model root'a **tam bağlanmadı** | gerçek B17 actor state tek authority, quaternion root pose, z-up camera & HUD, pitch climbs/dive & bank device |
| Uçuş kamerası | ground/hover sağ omuz, Stage2 tam arka, RUSH zoom/FOV; sağ stick serbest, bırakınca takip | B22.3 ve B24 rear follow source math var, C2 Pause nedeniyle cihazda denenemedi | kamera-çapraz-zırh-bone tek view/proj ve smooth recenter; collision wall |
| Stage VFX | hover sadece 2 ayak; Stage2 el+ayak; **RUSH** iki sırt ek, motion streak ve soft blur | host thruster/FX math var, orijinal nozul animation socket + GPU parçacık render yok | per-frame rig socket, sahnede 2/4/6 on-screen doğru particles ve yalnız RUSH sırt |
| Çapraz nişan HUD | W/M visor stiller, füze dışında LOCK kapalı, merkez uyumu | B22+B23 module var; B17 legacy HUD ile çift/yanlış screen coordinates | uçuşta gerçek merkez reticle, omuz aşamasında offset, raycast+HUD aynı projection |
| Repulsor | tüm zırhlarda **yalnız sağ kol kalksın**, yürüyüş sürerken sağ elden ateş; doğru aim | random `shots%3` kaldırıldı; **right arm masked genuine animation yok**; yeni `b24_weapon_aim` math kaynak modülü | bone/rig mask + özgün sağ hedefe bakış klibi, aim hold+fire+recover, animated right palm socket, no reentry |
| Unibeam | chest reactor origin, hedefe öne doğru doğru ışın | C2 rastgele geriye yayıyor; yeni b24_weapon_aim doğru world basis **host** | real chest animated bone socket + world target ray + GPU line / effects + device |
| Melee | Ground Combo1/2/3/Power, hit windows, yakın dövüş kamerası center | B15 **304 sadece kaynak adı**, B24 **59 baked**; melee klipleri baked+hooked değil | ham .anim keyframes recovery, 5 suit compat bake, authored hit timing, enemy focus |
| War Machine | yavaş doğal walk, iyi hover korunur, uçuşta anormal bacak kalkmasın, inişte gereksiz kol kalkmasın | 56 original named source WM / bazı retarget B24, real wrong transitions | genuine source and verified compatible fallback retarget, pose-by-pose device |
| İniş/zemin | temas olmadan iniş anim başlamasın | b18 landing gate host, C1L1 original collision chưa connected | C1L1 floor/body physics, hit/contact+velocity gate |
| Dövüş ve görev | B19 düşman 2 wave, projectiles, original first level | host AI proto + C1L1 original static geo; `level1.bclara` spawn/objectives not parsed | original enemy model/HP/hit positions + C1L1 mission logic |
| Ses ve UI | orijinal VFX/SFX, pause selectable coherent HUD | çoğu placeholder veya asset missing | gameplay audio emitter/mixer/UI navigation, GPU HUD, performance profiled |

## Yeni gerçek kaynak kodları ve testler (14 Ekim)
- `export_b24_c1_gpu_mesh.py`: doğrulanmış B11 GLB kaynak, **TÜM 370 submesh ve 22.919 özgün triangle** korunarak 16-bit indexed `C1G2` 4 materyal kategorili GPU batch formatına derleniyor; eski 365 tri/4×4 CPU sampling kullanılmıyor. Asıl UV/lightmap yok, gerçek materyal gibi gösterilmez.
- Kaynak düğüm matrisleri gerçek CI ile incelendi: **370 child mesh node'un tümünde -90° X görsel GLB Y-up dönüşümü** var, raw accessor koordinatları BDAE **Z-up** olarak saklanıyor. GPU exporter bu geçici görüntü dönüşümünü **B17 orijinal Z-up pozisyonuna ikinci kez uygulamıyor**. Bu, önceki map rendering karmaşasının gerçek veri açısından güvenli açıklamasıdır; C2 bloklarının tek nedeni olduğunu iddia etme.
- `b24_c1_gpu_mesh.[ch]`: tam vtx/index/batch doğrulayan sınır kontrollü loader.
- `b24_c1_gpu_vitagl.c`: gerçek OpenGL tipleriyle tek `glVertexPointer/glColorPointer` ve dört `glDrawElements` materyal renk geçişli çizim. **Aktif VitaGL context/view/proj ve swap dışarıdan gereklidir; henüz çalışan renderer değildir.**
- `b24_weapon_aim.[ch]`: doğrulanmış rig konumundan **sağ palm** ve **chest unibeam** dünya-uzayı shot origin/direction, kamera karakteri önden gösterince yanlışlıkla geriye ateşlememe ve yürüyüşten bağımsız üst kol aim weight protokolü. **Bugünkü runtime'a ve gerçek orijinal animasyon klibine bağlı değil**.
- `.github/workflows/b24-gpu-source-lab.yml`: sadece 2010 iOS private kaynak arşivinden PC manifest, mock GL host call test, gerçek `arm-vita-eabi-gcc` ile obje compile ve weapon/camera host regression. **NO VPK**. JSON manifest orijinal game geometry binary'yi dışarıya vermez.
- 304 original animation name /59 baked clip audited in `.github/workflows/b24-audit-only.yml` CI `38478323072`; START source fix PASS. Raw 304 clips henüz erişilebilir / baked kabul edilmez.

## Öncelik ve bağlanma kapıları
1. Önce single-GPU-context ownership, SDL GPU conflict araştırması, B17 gerçek renderer source owner, draw order `C1L1→5 armor→FX→HUD→swap`; actual Vita SDK object code pass yeterli değil.
2. Aynı anda B11/B12 authentic UV+material atlas; önce gerçek 22 araç submesh UV referansı, sonra şehir; source authenticity and no fake textures.
3. 304-name vs 59-baked tabloda **raw keyframe availability**; eksik Ground Combo, Upper right arm aim/repulsor, WM, landing ve Stage2/RUSH pose baker B13. Uydurma dosya "original" diye etiketlenemez.
4. Giriş/hud/reticle/flight real world math ve efekt soketlerini gerçek B24 input+pose single authority'ye bağla; Stage2 sırt daima off.
5. Oyun oynanabilir ve gerçek GPU render yoluyla fiziksel doğrulamaya layık hâle gelene kadar **hiç VPK release etme**. User bu kuralı değiştirdiğinde yeni test paketi hazırlanabilir.

**Günlük ilerleme etiketi:** HOST PASS / VitaSDK SOURCE OBJECT PASS / GPU ACTIVE RUNTIME NOT DONE / FULL ANIMATION NOT DONE / HUMAN PS VITA NOT TESTED on new code.


## B24 gerçek render sahibi — yeni kaynak denetimi PASS
- Source-only CI run `38480294916`: gerçek B17+B24 yeniden kurulmuş C ağacı üzerinden **412 satırlık `src/main.c` / 522 satırlık `src/renderer.c`** denetlendi; sonuç GitHub CI'daki JSON raporunda, hiçbir VPK üretilmedi.
- **Gerçek CPU→SDL sunum zinciri:**
  - `main.c:102–107` `SDL_CreateRenderer` → `SDL_CreateTexture(..., SDL_TEXTUREACCESS_STREAMING, 480x272)`;
  - `main.c:392` `im2_render(pixels,zbuffer,&model,&camera,...)` CPU zırh/şehir raster;
  - `main.c:393` `b24_unified_draw_overlay(...)` ikinci HUD CPU çizimi;
  - `main.c:395` `SDL_UpdateTexture(display,NULL,pixels,...)` tüm CPU yüzeyini video sistemine taşır;
  - `main.c:397–400` `SDL_RenderClear/SDL_RenderCopy/SDL_RenderPresent` **eski SDL video render sahibi**;
  - `main.c:146` `SDL_Init(SDL_INIT_VIDEO|SDL_INIT_GAMECONTROLLER|SDL_INIT_TIMER)`, `main.c:147` `SDL_CreateWindow`; kontrolcü okuması `main.c:243–270`. Bunu yeniden yazarken donanım kontrolcü eşlemesi kaybedilmemeli.
  - `renderer.c:306` `b24_c1_scene` eski piksel CPU harita, `renderer.c:392` `im2_render` dışa sunulan frame render.
- **Gerçek GPU geçiş programı:** Önce B24 render owner için **compile-time opt-in** VitaGL single-context create/init + tek `vglSwapBuffers` ile CPU `SDL_UpdateTexture/SDL_RenderPresent` hattının birbirini dışlayan iki seçenek olduğundan emin ol. Ardından gerçek `IM2Camera` Z-up view/proj ile `b24_gpu_c1_draw_vitagl` city indexed draw ve 5 IM2T/IM2V per-frame original suit GPU geometry; sonra VFX, 2D HUD ve pause aynı frame'e. Son CPU overlay'i GPU HUD olmadan atılırsa arayüz kaybolacağı için **ikisini birlikte taşı**.
- VitaGL kaynak sözdizimi resmi upstream'den teyit edildi: `vglInitExtended(int legacy_pool, int width, int height, int ram_threshold, SceGxmMultisampleMode msaa)`; `vglSwapBuffers(GLboolean has_commondialog)`. GPU draw source gerçek VitaSDK object build `38479901595` PASS; **tek GPU runtime henüz bağlı değil, Vita FPS yok.** vitaGL homebrew cihazda `libshacccg.suprx` shader compiler gerektirebilir, kullanıcıda olup olmadığı henüz cihazda kontrol edilmedi.


## Sonraki somut kod ve test ilerlemesi (14 Ekim, VPK ÜRETİLMEDİ)
- Yeni `b24_gpu_camera.[ch]`: B17 otoriter **Z-up** dünyadan tek 960×544 gerçek GPU view/projection matrisi ve `world_to_screen`; HUD missile/aim ve GPU sahne aynı ray üzerinden projeksiyon mümkün. 20.000 random kamera testinden geçti. Hazır kamera world.x/y/z kaynaklarından bu matrise aktarma henüz gerçek B24 ana döngüsünde etkin değil.
- Yeni `b24_gpu_owner.h`, `b24_gpu_owner_vitagl.c`: `vglInit` ve scene→armor→HUD→`vglSwapBuffers` sırasını tek sahipli kabul eden GPU render state machine; canlı `SDL_Renderer` varsa GPU context başlatmayı reddeder; sahne+zırh+HUD eksikse swap reddi, her frame yalnız 1 present. VitaGL sunum bağlamı kodla örneklendi/gerçek VitaSDK OBJ derlendi, **B24 src/main.c içinde mevcut SDL renderer fiilen henüz değiştirilmedi**, shader/texture, gerçek Vita ekrandaki sonuç yok.
- Yeni `b24_gpu_suit.h`, `b24_gpu_suit_vitagl.c`: 2010 orijinal `IM2T` 20-byte (x,y,z,u,v) mesh + 6-byte indices, kurtarılmış gerçek RGBA atlasını suit değişiminde **bir kez** glTexImage2D yükler; `B14/B16` kaynak animasyonun her frame değişen vertex'lerini `glDrawElements` ile çizme adaptörü. Dünya poz dönüşümü `b16_model_palm` ile birebir işaret uyumlu. Host mock ve **gerçek VitaSDK obje derlemesi PASS**, ancak video owner'a gerçek callback olarak takılmadı.
- Yeni `b24_gpu_suit_im2_adapter.[ch]`: VPK'yi derlemeden real reconstructed `work/src/renderer.h` içindeki `IM2Model` yapısıyla ABI uyuşumu kontrol edildi; B14/B16 animated `model.vertices` + original UV/triangle/atlas *aynı* GPU suit staging'e aktarılır. Strict aliasing riskine karşı kalıcı buffer'a frame başına yalnız bir `memcpy`; 480×272 yazılım raster yerine geometrinin kopyalanması. Orijinal model suit değişince boyut/atlas güncelleme güvenlik kapıları var. Reconstructed header ile host PASS + arm-vita-eabi-gcc obje PASS.
- Yeni `apply_b24_right_arm_source_only.py`, `test_b24_right_arm_patch.py`: original `src/main.c` atış `shots&1` sebebi sağ/sol sırayla ateş bug'ı kesin çözüldü **SADECE kaynak yamasında**; `palm_r` her iki oynanış/beam HUD noktası, `b16_attack_begin(...hand=0)` sabit; `b16_action.c` orijinal arm_mask bind-frame sağ/sol bilinen palm vertices'den ayırarak yürüyüş animasyonunu sağ-kol blend ile korur. Kaynak host/C11 compile PASS. **Henüz game runtime/B24 VPK/donanım PASS değil**, onu gerçekten çalıştırılmış gibi anlatma.
- SOURCE-ONLY CI GitHub `38481668392`: GPU owner + original suit streaming + GPU camera + original C1L1 indexed scene + right/Unibeam socket matematiği; mock GL ve **real VitaSDK object compile PASS**, VPK yok. `38482256186`: actual reconstructed B24 IM2Model→GPU stream + right-arm patch + 304/59 clip inventory host PASS ve **VitaSDK object compile PASS**, VPK yok.
- Canlı B24 ana döngüsünde gerçek `SDL_UpdateTexture` yolu HÂLÂ aktif. Sonraki en büyük iş mevcut CPU renderer'ı kaynak ağacında *tek* gerçek vitaGL görüntü bağlamına taşımak; `IM2Model` original suit adapter'ı + original C1L1 GPU batches ve GPU 2D HUD aynı viewport/proj içinde **oynunda** çizilmeli. Mevcut C1L1 geometry UV yok; 2010 BDAE UV+39 B12 atlas eşlemesi hâlâ çözülmeli. Bu kod GPU görüntüsü Vita'da oynanmış veya FPS iyileşmiş sayılmaz.
- Proje kuralı değişmedi: kullanıcı **ŞİMDİLİK VPK YOK** dedi; tam GPU runtime ve animasyonlar tamamlanıncaya kadar özel VPK build pipeline açılmayacak, yalnız kaynak/host/VitaSDK object CI.
