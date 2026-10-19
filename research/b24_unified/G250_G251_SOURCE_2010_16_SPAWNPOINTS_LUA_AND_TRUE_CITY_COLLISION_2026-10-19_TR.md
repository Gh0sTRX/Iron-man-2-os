# G250–G251 — Orijinal 2010 C1L1 SpawnPoint sınıfı, Mission000 statik Lua bağlantıları ve gerçek G66C hareket alanı denetimi

**19 Ekim 2026 · `Gh0sTRX/Iron-man-2-os` / `feature/b24-unified-gameplay`.** Yeni Vita VPK üretilmedi. Gerçek Vita donanımında yeni oyun testi/telemetri alınmadı. Bu belgedeki konumlar *C1L1 kaynak kayıtlarıdır*, karakterin çalışırken gerçekten nereye doğduğu değildir.

## G250 — 16 özgün kaynak spawn sınıfını 71 gerçek Lua callback'ine çapraz bağlama

[**G250 özgün 2010 iOS kaynak CI SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39236682307).

- Gerçek orijinal kullanıcı IPA'sı **248.613.763 byte**, özgün `level1.bclara` tam **339.733 byte** olarak özel GitHub Actions runner'da geçici okundu. Dosya CRC ve kaynak sayıları doğrulandı; telifli oyun varlığı hiçbir GitHub dosyasına veya artefaktına aktarılmadı.
- G19'un **tam 16 adet** `SpawnPoint000–SpawnPoint015` özgün tagged position(12 byte), quaternion(16 byte), unit-scale(12 byte) kayıtları tekrar incelendi. G25'in 587 typed kayıt tablosunda bütün bu 16 nokta gerçekten özgün C++ **`SpawnPoint`, `class ID 71`**. Sırf adında `SpawnPoint` geçiyor diye sınıf tahmini yapılmadı.
- G27'nin **71 gerçek original Lua 5.1 callback ve 1.035 statik `CALL` opcode** çapraz eşlemesiyle bu 16 noktanın toplam **24 kaynak typed entity-arg callsite referansı** tespit edildi. `Mission000_OnStart` içinde **bu 16 noktaya doğrudan bağlı kaynak callsite sayısı 0**.
- Bu, oyuncunun hangi `SpawnPoint` düğümünde doğduğu anlamına GELMEZ; doğrudan Lua callback bulunmaması, motorun başka native mekanizmayla bir noktayı oyuncu spawn yapmadığının da ispatı DEĞİLDİR. Birçok `SpawnPoint` oyun AI/spawn scriptlerinin parçası olabilir.
- Özgün kaynak sınıfı ve orijinal veri güvenilir, ama **node transform → parent dünya dönüşümü → oyun içi ayak XY/Z → Mission000 oyuncu başlangıç** zinciri açık. G250 yalnız kaynak JSON ve 16 satırlık C11 test header'ı üretir; oyun motoruna runtime teleport yazarak ilerleme taklidi yapmaz.

### Tam 16 adet özgün konum

| Ad | Orijinal scene ID | Kaynak XYZ |
|---|---:|---|
| SpawnPoint000 | 1168 | (-5.293, -184.602, 0.000) |
| SpawnPoint001 | 1171 | (-5.295, -190.379, 6.097) |
| SpawnPoint002 | 1595 | (187.251, -17.795, 1.433) |
| SpawnPoint003 | 1174 | (122.435, -205.013, 0.000) |
| SpawnPoint004 | 1177 | (157.643, -209.187, 10.207) |
| SpawnPoint005 | 1180 | (-3.349, 169.086, 0.000) |
| SpawnPoint006 | 1183 | (6.418, 166.922, 0.000) |
| SpawnPoint007 | 1186 | (18.156, 165.407, 0.000) |
| SpawnPoint008 | 1598 | (226.273, 58.644, 0.000) |
| SpawnPoint009 | 1604 | (-144.033, -82.305, 0.000) |
| SpawnPoint010 | 1607 | (-156.261, -93.549, 0.000) |
| SpawnPoint011 | 1610 | (-204.148, 177.331, 0.000) |
| SpawnPoint012 | 1613 | (-196.871, 57.943, 0.000) |
| SpawnPoint013 | 2117 | (209.572, -141.573, 0.000) |
| SpawnPoint014 | 1601 | (112.049, 65.555, 0.000) |
| SpawnPoint015 | 1616 | (-246.341, 42.068, 0.000) |

`SpawnPoint` kaynak `Z=0` çok yerde var; bu **doğrudan ayak tabanı yüksekliğinin sıfır** olduğunu kanıtlamaz. Üst parent transform ve oyun native Actor başlangıç state'i çözülmedi.

## G251 — Özgün konumları G171 source gerçek G66C'ye güvenli, salt-okunur yüklemek

Test kaynağı: `research/b24_unified/g251_real_source_16_spawn_collision_matrix/test_g251_true_2010_16_spawn_XYZ_against_real_G171_B14_G75_collision.c`.

Orijinal G250 tam 16 kaynak adayından otomatik üretilen C header gerçek G171 `im2_beta` birleştirme/test işine `actions/download-artifact@v4` ile girer. Her node için: orijinal G66C **1.910** collision triangle/**1.690** duvar, G159 gerçek G66M yol/ G160 spatial optimizasyon, G171 gerçek doğrulanmamış heykel duvar kaldırma, tek B14 movement integratoru + G75 capsule resolver; gerçek kaynak `SpawnPoint XYZ` başlangıç *aday* verisi; 8 yön × grounded/stage2 flight × 60 kare = **16×8×2×60 = 15.360** gerçek kaynak host simülasyon karesi. Kaynak metrikleri node adında `native-G66C floor near raw-Z`, B14 proposals, G75 resolved accepted directions, collision reject frames. `SpawnPoint` değerleri oyuna yazılmaz.

CI run: [**G251 G171 gerçek Vita ARM ELF-only kaynak zinciri**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39236897754).

**Donanım/oynanış sınırı:** Test host C11 native geometry B14/G75 replay'dir; VitaSDK ELF derlense bile Vita cihazında G229 logu henüz yok. Başka 3B oyun dosyasından farklı yükseklik/zırh rigini taklit etmez. Gerçek oyuncu başlangıcı, orijinal damage/hit, Win/Level1 QTE, tam scene lighting ve doğru araç/karakter ölçeği **bilinmiyor/tamamlanmadı**.

## Hâlâ yapılacak teknik iş: G252 yönlendirmesi

`Mission000_OnStart` node referansları ile asıl `MainCharacter::Init` / `GS_GamePlay::LoadEntities` / `SceneImpl::SetEntityPosition` kaynaklarındaki 2010 actor spawn/transform atamalarını ve `SpawnPoint` class ID 71'nin orijinal native *entity registration/AI kullanım semantiğini* doğrula. Bir noktaya görünüşte yürünebiliyor diye orijinal player spawn ilan etme, G66C wall715'i silme, B14 hız/scale değiştirme. G229 gerçek Vita 120-frame grounded root kaydı olmadan donanım sorunu çözüldü iddia etme.

**VPK YOK, source-parity çalışma ve CI var.**
