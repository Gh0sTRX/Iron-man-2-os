# G248–G249: gerçek Expo B14→G75 yer/uçuş 8-yön kök neden testi — doğrulanmış kaynak, Vita donanım hükmü yok

**19 Ekim 2026 · `feature/b24-unified-gameplay` · gerçek kullanıcı 2010 C1L1 şehir geometri/çarpışma varlıkları + Vita portunun tek B14/G75/G159/G160/G171 motoru · yeni VPK YOK.**

## G248 gerçek original city host+Vita ARM CI — PASS

[**G248 full-original-source G171/G239 Vita ARM ELF-only pipeline SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39233498774).

Bu kez hareketin yalnız ileri yönde çalışabildiğini göstermekle yetinilmedi: gerçek oyun kaynakları kullanılarak **8 yön × 3 gerçek kaynak konum hipotezi × yerde/uçuş × 120 kare = 5.760 kaynak hareket karesi** yeniden oynatıldı. Her test karesi `b14_world_tick` → özgün 1910 G66C çarpışma üçgeni/1690 dik duvar + 2010 kaynak G66M road G159 ve spatial G160 + G171 sculptor retraction uygulanmış **tek G75 capsule reconcile** kullandı. İkinci hareket motoru, uydurma çarpışma yüzeyi, sabit düşman vuruşu veya Vita donanım yürüyüş sonucu YOK.

| Başlangıç kaynak konum hipotezi | 8 yönden yerde bir miktar hareket kabul edilen | 8 yönden uçuşta bir miktar hareket kabul edilen |
|---|---:|---:|
| B14 port initial source `(0,0,0)` | **8/8** | **8/8** |
| Orijinal G66M road kaynak test `(-160,-160,2.6937)` | **8/8** | **8/8** |
| Orijinal CLARA `MC` yerel `(-1.319,-6.747)`, özgün en alt G66C destek `Z=0.0725` | **0/8** | **3/8** |

Özellikle alt MC kaynak konumunda **yer 8/8 yön tamamen reddediliyor**: B14 world her bir 120 karenin hepsinde XY hareketi önerirken G75 çözümü 0 kabul edip 120 reddediyor. Buna rağmen bazı yönlerde uçuş dünya XY'ye çevrilebiliyor. Bu, kullanıcının **yürüme animasyonu yerinde, uçuş hareket ediyor** gözlemiyle *aynı tipte kaynak testi vakası*dır, fakat **fiziksel Vita'daki hatanın kesin sebebi değildir**: cihazın gerçek spawn/world XYZ ölçümü yok; MC scene transform `(-1.319,-6.747,25.054)` **kanıtlanmış runtime spawn değildir**.

Bu test ayrıca eski yanlış `G108` görünür heykel katmanı yerine orijinal 2010 G66C duvarını korur. G171 önceden MC alt yerel XY'de **gerçek orijinal G66C wall face ID 715** teması tespit etmişti. Yalnızca oyuncu bu noktada durduğunda hareketi kabul edecek yerel açık alan bulunmadığı kaynak semptomudur; authored wall715 kaldırılmamalıdır.

G248 source:
- `research/b24_unified/g248_original_vita_ground_8dir_source_replay/test_g248_G171_real_grounded_8way_input_collision_Flight_source.c`
- `.github/workflows/g171-2010-source-sculpture-false-wall-ground-walk-G169-full-ARM-NO-VPK.yml`: real full game source reconstruct + true city host movement replay + PS VitaSDK `im2_beta` ARM ELF-only. Her test host, gerçek cihaz değil.
- Sonraki G249 kaynak genişletmesi aynı orijinal MC XY `Z=0.0725`, `Z=2.82955`, `Z=6.673064` ve gerçek authored `MC Z=25.054` ayrımını sınamak için eklendi. Üç ilk konum + 3 yeni yüksekliğe göre **96 adet 120-karelik** ayrı yer/uçuş senaryosu; önceki 48-case kaynak testine sadık.

## Kök neden için henüz kanıtlanması gereken iki konu

1. Gerçek Vita demo açılışında `world.x/y/z` ve `world.flying` kaç? B14 ilk state `(0,0,0)`, ama fiziksel cihazın sahne/anlık durumunu kaynak const ile karıştırmamak gerekir. G239 opt-in `G229_WALK_WINDOW` günlüğünün fiziksel cihazdan gelmesi gerekir: 120 ardaşık grounded GPU render frame, analog, B14 önerisi, G75 çözümü, GPU root, kamera pozisyonu.
2. `MC` scene local transform konumu **orijinal hikâye spawn kanıtı değildir**. Orijinal Mission000 `SetCamera`, C1L1 `SpawnPoint000...015`, `SetPlayerState` ve native scene aktör yerleşimi üzerinden gerçekte kullanılacak spawn/tavan alanı bulunmalı. Yalnızca yürüsün diye `G66C` wall715'i silme, uydurma hız veya karakter/harita scale değiştirme.

**Bu turda yeni Vita gameplay fiziği, sky, silah, animasyon, NPC veya görev davranışı değiştirilmedi; gerçek Vita'da yürüyüş düzeldiği iddiası yok, VPK YOK.**
