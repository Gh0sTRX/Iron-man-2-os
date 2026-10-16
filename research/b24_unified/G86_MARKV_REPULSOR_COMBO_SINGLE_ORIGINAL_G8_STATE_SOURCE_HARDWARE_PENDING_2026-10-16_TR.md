# G86 — Mark V gerçek repulsor ve 3'lü kombo hareketlerinde kaynak regresyonu

**G85 kaynak oyun mevcut; yeni VPK üretilmedi.**

## Gerçek tespit edilen G85 hatası

G85'in ilk 248 gerçek Mark V `.im2v` kaydı ile Vita ARM linkinin başarılı olması, ateş animasyonunun normal gameplay durumunda mutlaka çalışacağı anlamına gelmiyordu. G8/G84 kaynak zincirini incelediğimizde **Mark V repulsor** için iki özgün hata bulundu:

1. Repulsor klip adı `ironman_ironman_aim_ground_idle_att` önce `suitcase_ironman_aim_ground_idle_att` haline getiriliyor, ardından genel Mark V çeviricisi **ikinci kez** `ironman_` öneki bekleyerek işlemi başarısızlığa götürüyordu. Şimdi G8'in silah/melee önceliği özgün IronMan klip adı üzerinde yürütülüyor ve **tek kez** gerçek Mark V `suitcase_` adına dönüştürülüyor.
2. `desired==shot` işaretçi eşitliği, klip adının yeni dizeye kopyalanması sonrası geçersiz hâle geliyordu. Bu yüzden `whole_body_repulsor_active` yükselmiyor, saldırının zamanında tamamlandığı anlaşılmıyordu. Şimdi kabul edilmiş kaynak saldırı olayı **isim dönüşümünden önce** saptanıyor ve G8'e tek davranış sahibi olarak bildiriliyor.
3. Mark V'in 629v kaynak saldırı klibi, tuşa basma zamanından bir sonraki karede başlıyor. Orijinal authored klibi bir kare erken kesilmesin diye Mark V'e özel tamamlanma zamanı `stream` açıldığı `a->started_ms` üzerinden ölçülüyor; Mark VI/War Machine eski G8 zamanları değişmedi.

İlk durum iki kez ad dönüştürülmesini gideren GitHub Actions testinde başarıyla seçilmişti. Yeni regresyon en baştan gerçek G75/G68/G84/G85 animasyon dünyasını kurar ve **Mark V atış animasyonunu gerçek kaynak dosyasından** açar. Gerçek yerel G8 C koduna verilen 629 vertex tamponuyla bir kabul edilmiş shot, kaynak authored clip süresi, bitiş ve ikinci accepted shot, FPS/tampon/pose kaydırması olmadan denetlenir.

**G86 repulsor gerçek animasyon testi başarılı:** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38953786211

## G86B gerçek orijinal Mark V üçlü yakın dövüş

Yeni ayrı `test_g86_markv_original_3_combo_animation.c` testi eski G8'in gerçekten açtığı animasyonlarla:
- `suitcase_ironman_ground_combo_1` (266 ms)
- `suitcase_ironman_ground_combo_2` (300 ms)
- `suitcase_ironman_ground_combo_3` (500 ms)
- bitince `suitcase_ironman_ground_idel`

durumlarını orijinal kaynak model üzerinde gerçek 629 vertex tamponuyla test eder. `b24_g8_motion_melee_trigger` yalnız bir kullanıcının melee kenarıdır; basış tamponu test edilir, sentetik düşman öldürme/hit-window veya sahte silah hasarı yaratılmaz.

## Tam oyun kaynağı korunuyor

**G85 ana oyun CMake:** `-DB24_ENABLE_GPU=ON -DB24_ENABLE_NATIVE_HUD=ON -DB24_G68_CITY_BACKEND=ON -DB24_G75_SOURCE_CAPSULE=ON -DB24_G84_ORIGINAL_MOVESET_ROUTER=ON -DB24_G85_NATIVE_MARKV_629=ON` ile `im2_beta` native ARM hedefi derlenir, *VPK üretme hedefi çağrılmaz*. Aktif G73 oyun korunur. Orijinal 248 `suitcase_ironman_*.im2v` dosyası sahnede tek B14 fizik/tek G8 hareket sahibi; G76/G77/G82 hasar/temas CPU matematiği bağımsız olarak hazır.

**Henüz tamamlanmadı:** Mark V 248 hareketinin tüm oyun durum geçişleri, orijinal iOS combat isabet aktif kareleri, her `AttackEntity` özgün hasar sayısı, düşman AI + spawn, orijinal ses bağlantıları, dokunmatik oyun girişleri, touchHLE tam gameplay ve gerçek Vita QA. Bu aşamada VPK **kesinlikle oluşturulmayacak**. Önceden doğrulanan G68 şehir ve G75 kamera/yer/ışık düzeltmeleri korunacak.

## Doğrulanmış son G86B kaynak + native link sonucu

[GitHub Actions run **38954026551**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38954026551) **SUCCESS**:
- **248 / 248** orijinal 2010 IronMan→Mark V 629v akışı G8 ile açılıp XYZ örneklendi; üç özgün sıfır-süreli klip doğru tek kare olarak korundu.
- **G86 repulsor**: Gerçek kaynak G8 `suitcase_ironman_aim_ground_idle_att` ile tek kabul edilmiş atış, tam özgün süre, normal idle'a dönüş ve ikinci geçerli atış başarılı.
- **G86B üçlü kombo**: Orijinal dosyalar `suitcase_ironman_ground_combo_1/2/3` üzerinden 266/300/500 ms ardışık hareketleri, buffer girişi, normal idle'a dönüş ve ateşlemenin çift tetiklenmemesi başarılı.
- Mevcut G75/G68 Stark Expo haritası korunarak **G84 + G85** gerçek oyun kaynakları PS Vita ARM derleyicisiyle `im2_beta` hedefinde **bağlandı**; sadece ELF hedefi, VPK/eboot paketlemesi **YOK**.
- Kullanıcı gerçek PS Vita'da henüz bu yeni sürümü test etmedi. **HIT FRAME, silah hasarları, NPC AI ve özgün hikâye** hâlâ eksik; bu nedenle VPK üretme yasağı sürüyor.
