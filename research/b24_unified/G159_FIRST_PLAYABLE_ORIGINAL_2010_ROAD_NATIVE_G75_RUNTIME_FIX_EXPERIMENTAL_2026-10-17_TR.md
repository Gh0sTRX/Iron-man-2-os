# G159 — İlk oynanabilir C1L1: gerçek 2010 yol üçgenleriyle tek G75 zemini destekleme düzeltmesi

**17 Ekim 2026 / `feature/b24-unified-gameplay` / G155 tek WIP: world_render_collision_hardware_parity. YENİ VPK YOK.**

## Somut ürün ilerlemesi

Önceki G157/G158 analizinin belirlediği açık: gerçek orijinal C1L1 G66M `c1l1_road.tga` yol yüzeyi (G66 city atlas12 özgün PVR RGBA'nın G64 gerçek ada SHA-256 birebir eşlenmesi) örnek (-160,-160)'da Z 2.6937, mevcut G75 native C1L1 G66C nonwall Z 0.0725. Arada +2.6212 kaynak dünya birimi bulunuyor. Mevcut G75 `b24_g74_near_original_floor` gerçek oyun C fonksiyonu orijinal yolun gösterildiği yükseklikte taban bulamıyordu, alt native collider'da buluyordu. Birinci bölümü gerçeğe yakın oynanabilir yapmadan diğer görevlerin Lua/Wait/Co-op tarafına dalmak kapsam hatası.

G159 artık yalnız kaynak analizi değildir: **yeni C modülü gerçek 2010 orijinal G66_city.g66m batch12 yol üçgenlerini doğrudan Vita runtime'da okuyor ve G75 mevcut zemin sorgusuna koşullu yedek kaynak olarak bağlıyor.** G159, 2010 özgün G66M geometri batch12 içinde **753 gerçek yol üçgeni** doğruladı. Bu motor yeni polygon/model, düz dünya ızgarası, sabit yeni yerçekimi veya zemin üretemez; native kaynak mesh rakamlarını değiştirmez.

## Oyun koduna yerleştirdiğimiz davranış

- `b24_g159_real_source_road.[ch]` — exact G66M 2010 67.323 vertex 32 batch 31 source atlas byte header doğrulanır; gerçek batch12/atlas12 parse edilir ve 753 sahici kaynak 3D üçgen sabit UV/RGBA/XYZ'den okunur. Her bir source triangle XY barycentric hesapla doğru Z'de yatay destek adayına dönüşür. Bir tane `calloc`, hiçbir render/VitaGL GPU VBO değişimi yok.
- `g159_integrate_authentic_road_source_into_one_G156_Vita_NO_VPK.py` — G156 tek mevcut B14/G75 kaynak oyununda G75'in var olan `b24_g74_near_original_floor` native ilk önceliğini korur; normal destek bulunamazsa gerçek road source destek adayı kullanılır, yalnız ayak Z'sinden -0.50 ile +0.45 dünyabirimi civarında. Eski roof/floor native source geçişi korunur, aşağı hareketle **gerçek yol yüzeyi** kesiliyorsa G75 `floor_crossed` geri bildirir. Kaynak mesafe olmayan XY/Z'de varsayılan native engine değişmez.
- `B24_G159_ROAD_FLOOR_CANDIDATE=ON` VitaSDK CMake açık **opt-in**. Orijinal G66C kaynak fizik 1910 yüzü eksiltilmez; G156 gerçek 3D wall collision, G108 7.487 aday opak steep wall, G134 uzun kare atlamama, G83 hareket/animation sahibi, G137/G153 gerçek Mission000 Lua kodu ve HUD/GPU çizimi korunur. **Tek `b14_world_tick`, tek `b24_unified_tick`**.
- `test_g159_real_original_road_and_native_floor.c`: gerçek G66M/G66C binarisinde original road XY -160,-160 Z2.6937 yakalanıyor; alt native Z0.0725 native-first kalıyor, global destek icat edilmez, yukarıdan aşağı doğru inince gerçek yola vurulur. C11 host test.
- `test_g159_one_native_G75_capsule_with_true_city.c`: yalnız ayrı modül değil, **aynı oyun kodunda G75 kapsül API'sı** gerçek source G108/G159 dünyası üzerinde gerçek oyun hareket çözümlemesine girer, yol Z ve eski alt native Z bozulmaz. C11 host, cihaz QA değildir.

## Kanıtlar

- [G158 original atlas/named PVR exact RGBA ve G75 failure #39049316919](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39049316919).
- [G159 gerçek tam tek-Vita ARM ELF derleme SUCCESS #39050387456](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39050387456). Bu run'ın host C11 gerçeğin 753 triangle source destek ve alt native koruma testleri geçti. Sonrasında eklenen gerçek G75 kapsül entegrasyon testi ve tekrar tam ARM derlemesi [#39050573076](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39050573076) ile takip edilir; koşu sonucunu görmeden cihazda kesin başarı iddiası yok.

## Kullanıcıya dürüst durum

Kaynak `c1l1_road.tga` varlığı, piksel kimliği ve çizilen dünya koordinatı **gerçek**. Bu yola fizik desteği atamak port çözümü olarak **mantıklı bir deneysel tercih**; orijinal iOS motorunun native CollisionEntity yol katılığı/ebeveyn world transform ilişkisini birebir kanıtlamış değiliz. Yani G159 uygulanmış Vita'da oyuncunun fiziken düzgün yürüyeceğinin veya original oyundaki collision davranışının aynısının gerçekleşeceğinin garantisi yok. G104 cihazda gözlenen bina geçişi için G156/G159 tek başına mutlak nihai çözüm olamaz.

Yeni VPK üretmedik. CPU maliyeti 753 road triangle'a kadar kontrol olabilir; buna dair gerçek Vita FPS/headroom ölçümü yok, G69 screenshot 237/256 MB kullanım gözlemi sebebiyle özenli test gerekir. Tam ilk oynanabilir bölüm 7 zorunlu kabul alanında G155 hâlâ `BLOCKED`.

**Sıradaki pratik adım:** İzinli bir sonraki **tek anlamlı cihaz QA paketinde** gerçek Vita ile road foot contact, önceki native alt katman, bina yaklaşma/uçuş, G106 gökyüzü/alfa ve G83/MarkV Stage2 ateş görüntüsünü birlikte karşılaştır. G159 deneysel ROAD seçeneğini gerekirse aynı derleme içinde kapatma olanağı korunur; ikinci zemin/fizik sahibi yazma. Kullanıcıya sadece rapor biriktirerek değil, gözle görünür ilk bölümle ilerleme göster.
