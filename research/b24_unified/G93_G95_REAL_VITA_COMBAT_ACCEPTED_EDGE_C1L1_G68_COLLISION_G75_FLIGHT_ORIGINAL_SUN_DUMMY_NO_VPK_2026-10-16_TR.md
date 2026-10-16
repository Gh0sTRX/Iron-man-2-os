# G93–G95 — Eksikleri kapatma: G8 saldırı olayı, gerçek B14 hareket testi, orijinal G68 dummy zemini, dört Sun kaynaklı ışık

**2026-10-16, `feature/b24-unified-gameplay`.** Kullanıcının hedefi: gerçek kaynaktan Mark V karakter, yürüyüş/uçuş/nişan/melee, Stark Expo haritasında bir sabit hasarsız dummy ve orijinale yaklaşan ışıklandırma. Önizleme **VPK OLMADAN**; orijinal 2010 hitframe/hasar kesinliği yoksa asla gerçek düşman hasarı iddiası yok.

## G93 gerçek battle-integrasyon hatası giderildi

G92'nin ilk sürümü eğitim dummy'sine temas göstermek için normal oyun saldırı girdisini `b24_unified_should_melee(&b24_game)` üzerinden **ikinci kez ayrı yokluyordu**. Bu, saldırı olayını tekrar tüketebiliyor veya gerçek G8 saldırı hareketi ile test kutusu tepkisini birbirinden ayırabiliyordu.

Kaynak patch `g91_offline_integrated_preview/g92_patch_single_real_vita_main_static_dummy_NO_VPK.py` artık **mevcut tek `b24_g8_motion_melee_trigger(...)` kabul edilmiş kaynak olayının olduğu satırda** `g92_debug_accepted_melee_edge=1` debug latch işaretliyor; ana B24 oyun döngüsünde yalnızca bu kabul edilmiş olayın sonucunu `b24_g11_practice_melee_hit(...)` kullanıyor ve latch'i her frame **bir kez sıfırlıyor**. Yeni `b24_unified_should_melee` çağrısı üretilmez; original `main.c` üzerinde zaten bulunan **üç kaynak giriş referansı** aynen korunur (bunların üç ayrı aktif gameplay darbe olduğunu söylemek mümkün değil). `b24_g8_motion_melee_trigger` çağrı sayısı hâlâ **1**, `b14_world_tick` **1**, `b24_g83_timeline_tick` **1**, `b24_g8_motion_tick_g84` **1**. Tek hareket sahibi / tek orijinal G8 animation player korunur.

Bu değişiklik yalnızca debug dummy olayını doğru mevcut girişe bağlar; kaynak `G89/G90` orijinal 0x824 kombo switch'i *otomatik olarak G8'in üç combo klibiyle birebir eşleşmiş* değildir. Dummy gerçek `AttackEntity` hasarı uygulamaz.

## G94 gerçek orijinal haritada sanal olmayan dummy destek yüzeyi

`g91_offline_integrated_preview/test_g94_real_source_G68_dummy_actual_floor.c` yeni bağımsız kaynak C11 testi:
- Gerçek eski G68 kullanıcının iOS'tan çıkarılmış **1.910 özgün collision triangle / 1.690 authored wall** veri dosyasını `b24_g70_g68_collision_load` ile RAM'de açıyor.
- G92'nin gerçek fizik yerleştirme rutinindeki dört aday xy koordinatını, kaynak zemini `b24_g75_floor_crossed` ile tarıyor. Gerçek kaynaktan support bulunmadığında dummy uydurma havada açılmayacak.
- Seçilen XY için kaynak yüzeyine tekrar ray/floor query yapıp `dummy.z-1.f` ile gerçek yüzey Z eşitliğini doğruluyor.
- Dummy aynı orijinal G10/G11 C fonksiyonlarında ölümsüz kalıyor; G11 flash yalnız yakınlık için, silah/hp değişmiyor.
- G92 iş akışı restore edilmiş gerçek G68 asset `work/assets/G66_original_collision.g66c` ile bu testi çalıştırır; kaynağın kendisi VPK'ya yeni paketlenmez.

## G93 mevcut gerçek B14 hareket + G75 G68 collision replay

Önceden hazırlanmış G75 testleri artık **aynı G92 gerçek full game source CI çalışmasında**, gerçek yeniden oluşturulmuş `work/src/b14_world.c` ile host C11 olarak tekrar çalışıyor:
- 0.96s grounded, run, stage2 uçuş, stage3 RUSH dünya deplasman karşılaştırması, ivmeli durma/yavaşlama ve yukarı/aşağı kamera açısı;
- `b24_g75_source_capsule` gerçek kaynak 1.910 yüzeyi, 0.22 birim substep, katmanlı roof collision, otantik üstten destek, kaynak harita sınır ve NaN hataları;
- bunlar **PC host kaynak fiziği regresyonu**, gerçek Vita FPS ya da orijinal Gameloft uçuş hızı iddiası değildir.

## G95 kaynak konumlarından opt-in native VitaGL ışık

G75'in daha önce kaynakta bulunmasına rağmen varsayılan `OFF` olan deneysel `B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE` ana kaynak G92 derlemesinde artık **ON**. Bu, gerçek 2010 ilk Level1 CLARA'dan gelen dört authored `Sun001...Sun004` pozisyonunu kullanıp özgün `b24_gpu_g68_city.c` mesh vertex RGBA renklerinin RGB'sine diagnostic illumination uygular, **gerçek PVR dokularını, UV ve orijinal alpha kanalını değiştirmez**. `test_g75_sun_light_host.c` farklı kaynak sun noktasında uzaklık/factor ve alpha korunmasını test eder. Native derleme opt-in; eski Vita kurulu G73 değiştirilmedi.

**Önemli:** G95 renk/falloff denklemleri bizim test shader heuristiğimiz, 2010 Gameloft engine native shader matematiğinin **kesin çözülmüş aynısı değil**. G58 tarayıcı ışığı da ayrı host shader. Gerçek Vita cihazında görüntü/FPS performansı ve fiziksel global light parity halen doğrulanmamış.

## GitHub Actions kanıtları / VPK gate

- G93/G94 gerçek host + Vita ARM FULL `im2_beta` native ELF link başarılı: [run 38966964553](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38966964553). Orijinal 248 Mark V source IM2V, G68 Expo, G75 B14, G83, G84, G87, G92 ve G93 tek B24 ana oyun kaynaklarına bağlandı. Hiçbir `vita_create_vpk`, `eboot.bin`, paket veya yeni `*.vpk` yok.
- G95 G75 orijinal Sun kaynak aydınlatma `ON`, G93/G94 1910 fizik/dummy doğrulama, tam Vita ARM ELF link: [run 38967068698](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38967068698); **SUCCESS doğrulandı:** tüm G93/G94/G95 host kaynak testleri ve birleşik gerçek VitaSDK ARM `im2_beta` link testi geçti. VPK yok.
- Son indirilebilir Chrome orijinal BRES/PVR kaynak animasyon sahnesi ve foto QA, G91C [run 38964509174, artifact 12073289399](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38964509174/artifacts/12073289399). Aynı tarayıcı smoke iş akışı sonraki G91 kod değişikliklerinde de koşar.

## Asıl kalan ciddi blokajlar (tam oyun seviyesinde)

1. Kaynak 2010 C++ gerçek attack active frame/swing hit/cancel, `MainCharacter::UpdateMeleeAttackState` 0..12 state switch'in iOS kullanıcısı gerçek input/hit evrelerine doğru eşlemesi; hareket selection'a script birebir parity.
2. Gerçek 26 `AttackEntity` / 13 `Weapon` typed numeric `damage`, repulsor, missile, Unibeam etkileri, projectile geometry+sound. G76/G77/G80/G82 araştırması bu sayıların tipini henüz kesin doğrulamadı; onları sırf görüntü için uydurma.
3. Orijinal drone/NPC model/rig/hit/hurt/death/wave AI/mission event bağları (şu an tek DEBUG dummy).
4. Orijinal 338 player clip bütün riglerde oynanması ve 248 Mark V'in gerçek Vita cihazında bütün durumlar için uygulama testi.
5. Gerçek iOS touchHLE input/attack/flight/lighting camera source karşılaştırması (eski mutex-block halen açık), harita görünmez colliderlar/kamera/day night shader parity.
6. En sonunda kullanıcı açıkça izin verince gerçek PS Vita ilk test build/VPK. Kullanıcı henüz izin **VERMEDİ**; kesinlikle oluşturma.

**Bu alt adımda G93/G94 kaynak sorunu giderildi; oyunun tümü bitmiş değildir.** Katı `g83_final_vpk_gate/READINESS_STATUS.json` 1/11 doğrulanmış kabul kanıtında kaldı. Bu sayı genel oyun bitmişlik yüzdesi değildir.

## G96 browser source yere basma/önden kamera kalite düzeltmesi — Chrome QA SUCCESS

Önceki G91/Mark V browser sahnesi orijinal `level1.bclara` typed `MC` local transform Z≈25'i **oynanabilir başlangıç konumuymuş** gibi çiziyor, bu yüzden karakter zeminden kopuk durabiliyordu. G94'ün gerçek 1.910 kaynak G68 yüzey testinde kanıtlanan tek destek düzlemi üzerindeki **oyuncu test XYZ=(0,0,0.072501)** ve **ölümsüz dummy=(0,10,1.072501)** host önizlemesine aktarıldı. Kamera ilk açılışta oynanabilir oyuncuya yakın ve omuz arkası eğime benzeyen *tanısal* görüntüye yaklaştırıldı; özgün iOS kamera state eşiği olduğu iddia edilmiyor.

**Tam Chrome WebGL2 yeniden çizim ve orijinal 2010 Mark V PVR/UV + G83 hareket/kombo testi SUCCESS:** [G96 run 38967469107](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38967469107), [indirilebilir HTML + ekran görüntüsü + kaynak QA artifact 12075890983](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38967469107/artifacts/12075890983). Gerçek PS Vita cihazında henüz bu yeni alt sürüm kurulup açılmadı. Browser hareket hızı, gerçek G75 collision duvarı, orijinal düşman hasarı hâlâ tam gameplay değildir.
