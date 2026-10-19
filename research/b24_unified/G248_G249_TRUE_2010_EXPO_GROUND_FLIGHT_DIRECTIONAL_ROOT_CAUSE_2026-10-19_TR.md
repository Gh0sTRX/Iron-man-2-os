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


## G249 genişletilmiş kaynak sonucu — **tamamlandı / CI SUCCESS**

[**G249 gerçek tek Vita oyununun yeniden kaynak kurulumu, 96-senaryo 11.520 çarpışma/hareket kare host testi ve Vita ARM `im2_beta` ELF SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39234051299).

Aynı `(-1.319,-6.747)` gerçek `MC` lokal XY kaynak konumunun birden fazla orijinal geometrik dikey katmanı vardır. Orijinal `G66C` destek yükseklikleri ve gerçek `MC` authored transform `Z=25.054` ayrı hipotez olarak incelendi. **Her 8 test yönünde en az 1/120 karenin G75 tarafından kabul edilmesi** başarı sayılır; tüm 120 kare boyunca engelsiz yol/çalışır son kullanıcı gameplay demek değildir.

| Kaynak site hipotezi (tamamı 8 yön) | Yer: hareket kabul edilen yön | Uçuş: hareket kabul edilen yön |
|---|---:|---:|
| Homebrew B14 `(0,0,0)` | **8/8** | **8/8** |
| 2010 G66M source road `(-160,-160,2.6937)` | **8/8** | **8/8** |
| Orijinal MC XY, en alt G66C `Z=.0725` | **0/8** | **3/8** |
| Orijinal MC XY, orta G66C `Z=2.82955` | **8/8** | **8/8** |
| Orijinal MC XY, üst G66C `Z=6.673064` | **0/8** | **0/8** |
| Orijinal MC authored 3B `(-1.319,-6.747,25.054)` | **0/8** | **0/8** |

**En kritik gerçek ayrı veri:** MC alt kaynak yüksekliğinde ileri stick `(0,+1)` ve diğer 7 yön, B14 tarafından her 120 karede kaynak hareket önerisi oluşturuyor ama kaynak G75 **120/120 reddediyor**. Aynı XY'nin **orta `Z≈2.82955` katmanında** sağa ve sola yerde hareket `120/120` kabul ediliyor; ileri `2/120`, geri `15/120`, diagonallerde G75'nin gerçekten kabul ettiği XY hareketi var (bazı framelerde duvara teğet kayma ve eksen kilidi). Bu kuvvetle **zemin katmanı/duvar teması / kapsül mevcut başlangıç wysokołu** bulgusudur; kaynak kodda B14 movement hiç gitmiyor veya G8 animasyon kareleri dünya root'una kesin müdahale ediyor gibi genellenmemeli.

- Orijinal kaynak **G66C face `715`** bu düşük MC XY ayak yüksekliğinde kapsüle değiyor. Test gerçek `b24_g156_exact_vertical_triangle_contact` ile bunu ayrıca `assert` ediyor. Yüzey orijinal `G66C` verisidir; **duvarı silmek doğru değildir**.
- Orijinal authored MC `Z=25.054` eşzamanlı bir şüpheli spawn olabilir ancak **gerçekte Mission000 başlangıç XYZ'si olduğu kanıtlanmadı**; B14 testi bu kaynak seviyeyi geçerli yere basma yüksekliği şeklinde zorlayıp kıyaslar, native iOS actor giriş akışı bundan çıkarılamaz.
- İki G249 bağlanması da gerçek C1L1 kurulum+ VitaSDK ARM `im2_beta` ELF-only zincirinde geçti, tamamı host statik simülasyon/test sonucu; **fiziksel cihaz donanımında G229 telemetri henüz alınmadı**.
- Statik grafik yerel olarak hazırlanmıştır, GitHub raporu test metaverisi sağlar; sahne ekran görüntüsü/gerçek Vita görüntüsü değildir.

**Önerilen G250:** `Mission000_OnStart` gerçek native source initial spawn ve orijinal `SpawnPoint000..015` transformu bağlantısı; fiziksel kullanıcı `G229_WALK_WINDOW` source analog/B14/native collision/GPU root kaydı. Gerçek spawn/ayak dünya koordinatı çözülünce yalnız orijinal G66C etkileşimi veya source-authentic boot izni düzeltilecek; uydurma 2.82955 konumuna sürekli teleport, source wall silme, körlemesine ground speed yükseltme yapılmayacak. **VPK halen yok.**
