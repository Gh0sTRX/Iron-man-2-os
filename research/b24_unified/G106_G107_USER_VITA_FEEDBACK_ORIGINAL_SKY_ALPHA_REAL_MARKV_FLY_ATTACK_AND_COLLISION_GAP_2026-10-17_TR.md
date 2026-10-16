# Iron Man 2 PS Vita G106–G107 — GERÇEK VITA KULLANICISI GERİ BİLDİRİMİ ve yeni beta

**17 Ekim 2026 / feature/b24-unified-gameplay.** G104 ilk defa gerçek Vita'da kullanıcı tarafından test edildi; onaylanan cihaz gözlemi: **ground walk ve hover animasyonunda gözle görünür hata yok**. **Stage 2 ve Rush modunda repulsor ateş animasyonu bozuk**, çevrenin/binaların içine girilebiliyor, alfa/kesilmiş şeffaf olması gereken direkler arası yazılı PNG/PVR paneller siyah, gökyüzü tamamen siyah ve ışıklandırma fark edilmiyor. Kullanıcı **eski animasyon kullanılıyormuş** izlenimi aldığını söyledi. Bu raporda yalnız bu gerçekten bildirilmiş durum kanıttır; otomatik Chrome/ARM CI FPS veya gerçek on-device yeni G106 sonuçları henüz YOK.

## Root cause bağımsız kaynak doğrulama

**Alfa:** G104 gerçek Vita SDK derlemesinde daha önce yazdığımız **G71 `B24_G71_ALPHA_PASSES` KAPALI**. 31 gerçek 2010 kaynak G66T atlasında alfa bilgisi zaten mevcut; 7 atlas (ID 1,6,7,9,15,19,20) opak olmayan gerçek pixels ve 1282 rendered triangle içeriyor. G70 varsayılan renderer tüm yüzeyleri aynı blend+depth ile çizerek görünmez card'ların derinliği yanlış kapatmasına imkân veriyordu. G106 **G71 ON**: opaque first depth write ON; translucent second `glDepthMask(GL_FALSE)`, `glBlendFunc(SRC_ALPHA,ONE_MINUS_SRC_ALPHA)`. Gerçek Vita karelerinde düzelip düzelmediği henüz görülmedi. Alfalı kaynak dokuların bütün combiners/shaders orijinal sürümü hâlâ ayrıştırılmadı.

**Sky:** G73'e ait **GERÇEK 2010 `C1L1_sky_001` BRES, 6 kaynak mesh batch / 288 vertices** ve iki 256×256 owner orijinal PVR sky `G73_original_sky_tex_00/01.g66t` daha önce çözülmüş, ancak G104 `B24_G73_REAL_SKY=OFF` ve 3 kaynak sky dosyası VPK içinde **yoktu**. G106 kaynak artifact 38902510114'ten kaynakları indirip ana scene runtime'da render path `G73_REAL_SKY=ON`, sky öncelikle draw -> then actual G68 city; sources in VPK validated. **Sky shader/material ID per batch ↔ exact iOS original sampler mapping hâlâ candidate; kullanıcıda doğru görüneceği garanti değil.**

**Light:** G104 `B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE=ON` ama `b24_gpu_g68_city_open` orijinal RGBA texture atlaslarının `material_has_alpha[]` değerlerini henüz doldurmadan geometrinin sunlight bake kararını veriyordu. G106 gerçek kaynak `research/b24_unified/b24_gpu_g68_city.c` içinde source texture upload ve 31 gerçek RGBA alpha scan **ışık verisi sınıflandırma döngüsünden ÖNCE** çalışacak şekilde değiştirildi. Aynı source-colour α aynen korunuyor, mat alpha shade edilmiyor. Bu deneysel **Sun001–Sun004** kaynak node pozisyonlarına dayanan tangent/normal/falloff heuristic; **Gameloft native shader'ı değil**.

**Stage2/RUSH accepted repulsor:** mevcut G8 `b24_g8_motion_repulsor_clip(suit,stage)`, cruise/rush için NULL → `repulsor_pending` iptal, G83 gerçek fly/rush clip ile eski B16 upper-arm attack overlay karışıyordu. G106 248 gerçek owner source G85 bankını bizzat tarayarak **`suitcase_ironman_fly_att_s.im2v` 629 gerçek Mark V skinned vertex × 33 frame, 20 Hz, 1600 ms** varlığını kanıtladı, [G106 inventory CI 38982266158](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38982266158). G106 yeni CMake `B24_G106_SOURCE_FLY_ATTACK_MARKV=ON` altında bu klibi Mark V'in **kabul edilmiş B16 repulsor olayında** Stage2/RUSH için G85 tek G8 hareket sahibi içinde oynatıyor; source ateş süresi sonunda G83'ün özgün gerçek fly veya rush pozuna tek seferlik dönüyor. **[G106 real host C11 source play/return test](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38982565536) SUCCESS**. `fly_att_s` gerçek orijinal kaynak klip ama özgün iOS `AttackType`/repulsor event'e 1:1 bağlandığı henüz kanıtlanmadı; geçici görsel eşleme. Gerçek hitframe/damage değişmedi.

**Eski hareket hissi:** G104/G106 tek G8 pose owner gerçekten 248 gerçek Mark V G85 streamlerini dosyadan okuyabiliyor. **248 dosyanın varlığı = 248 klibin tamamının native gameplay state'e bağlandığı anlamına GELMEZ.** Sadece G83 ve G8 key route ve accepted fire/melee'de eşleştirilmiş altküme otomatik kullanılır. Suit 0/2 sahneleri orijinal G8 MarkVI/WM kaynaklarını, diğer zırh slotları eski B13 legacy animasyonlarını da kullanmaya devam ediyor. Orijinal `UpdateMeleeAttackState` 13-state/8 branch ve 26 typed damage hâlâ native runtime'a tam bağlanmadı.

## G106 GERÇEK PS Vita VPK — üretildi ve CI başarıyla doğrulandı

- **GitHub CI:** [G106 gerçek VitaSDK ARM ELF+SELF+VPK build SUCCESS, 38982565536](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38982565536)
- **İndirilebilir G106 beta VPK + QA JSON:** [GitHub artifact 12081497316](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38982565536/artifacts/12081497316)
- **Dosya:** `IronMan2_B24_G106_Alpha_Sky_Sun_FlightAttack_StarkExpo_MarkV248_Dummy_TEST.vpk`
- **Boyut:** 94.800.524 bytes / 94.8 MB
- **SHA256:** `7fcadbe7aa5e721c7c27587955597210a2e5103e0c9e77a60eed3f922fda1d66`
- **Yeni TITLE_ID:** `IM2G10601` — G104 `IM2G10401` eski kurulumu EZMEZ.
- Artifacts içinde exact SFO identity, 31 gerçek scene atlas, gerçek 1910 G68 collision, 248 gerçek Mark V 629v source im2v, gerçek G73 sky geometry ve iki sky source atlas, G92 old one immobile debug target, `eboot.bin`, testzip ve full VitaSDK unsigned ELF → SELF iş akışı doğrulanmıştır.
- G106 kodlar `research/b24_unified/g106_visual_repair/` ve workflow `.github/workflows/g106-device-feedback-alpha-sky-sun-flight-fire-test-VPK.yml`; G106 internals ayrı VPK'da, G104 binary değiştirilmedi.
- **G106 gerçek Vita donanımda henüz kullanıcı tarafından çalıştırılmadı**, FPS/çizim sorunsuzluğu iddiası yok. Kaynak dosyalarının varlığı, Vita'da gökyüzünün orijinal göründüğünün kanıtı değildir.

## G107 — Neden yine duvarların içinden geçilebiliyor?

Bağımsız **[G107 SUCCESS real original VPK source visual-vs-collision 38982668069](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38982668069)** [G107 ayrıntılı fizik-görünüm karşılaştırma raporu, artifact 12082200515](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38982668069/artifacts/12082200515). Gerçek G104 G68 kaynak binary:
- 22.441 orijinal çizilen triangle,
- sadece 1.910 gerçek collision triangle (bunların 1.690 steep wall olarak sınıflanıyor),
- 12.100 kaynak orijinal opaque steep visual triangle,
- **4.594 görsel dik triangle merkezi**, mevcut gerçek fizik duvarı AABB'sine 0.8m tolerans yakın;
- **7.506 görsel dik triangle merkezi** bu testte yakın fizik duvarı eşleşmesi göstermiyor.
Bu **sadece yaklaşık AABB taraması**: görsel triangle "fiziksel olarak katı olması gerekir" demez, bir triangle'ın geçilebilir olduğunu tek başına kanıtlamaz; görüntüde duvar olarak görülen hangi orijinal paketlerin collider eksikliği doğurduğunu tespit etmek için eksik source geometry ve Vita oyuncu konumu ölçülmeli.

**G106'da tüm collision face sayısı değişmedi; haritanın içinde geçmeyi G106'nın düzelttiği iddia edilmemeli.** Sıradaki G108: G68 source visual opaque steep katı geometriyi renderer batch/material bilgisine göre ayıran konservatif collision candidate ve spatial grid/BVH; gerçek original native G68 1910 colliderlarla fizik regresyon; kullanıcı Vita koordinat/screenshot kanıtından başlayıp staged rollout, yapay çatılar/gökyüzü/dekor sabit duvar haline getirme. Hem room/roof ve scene waterfall paterni hem düşey capsule sweeps incelenmeli.

## Tekrarlanabilir gerçek kaynak / kontrol statüsü

G106 native test host body attack `test_g106_authentic_2010_markv_flight_fire_real_source.c`, rendering lighting patch `research/b24_unified/b24_gpu_g68_city.c`, G106 source patch `g106_apply_original_stage2_rush_fire_source_only.py`, G106 packer `g106_pack_stark_sky_alpha_light_feedback_beta.py`. G107 gap parser `g107_compare_visible_2010_world_vs_original_1910_physics.py`.

Katı orijinal 2010 full combat `READINESS_STATUS.json` kapıları henüz 1/11; G106 kullanıcı onaylı deneysel beta var, hiçbir real enemy AI/hitframe/damage parity kanıtlanmadı.
