# G158 — İlk bölüm gerçek yol yüksekliği ile mevcut Vita zemin fiziği uyuşmazlığı kanıtı

**17 Ekim 2026 · `feature/b24-unified-gameplay` · G155 WIP=1 orijinal ilk C1L1 harita/fizik. Yeni VPK YOK.**

## Mevcut engeli neden araştırdık?

G104 gerçek Vita testinde oyuncunun binaların/geometrinin içine girebildiği bildirilmişti. G156 kaynak kodu üç yüksekliğe bölünen duvar-kapsül testini düzeltti, ancak bina/floor varlıklarının tamamı gerçekten katı mı kanıtlamadı. G157 orijinal G104 kaynak dosyalarındaki **G66M 22.441 gerçek render üçgeni** ile **G66C 1.910 collision üçgenini** dünya koordinatı ve yükseklik bazında karşılaştırdı; Z≈2,82955 katmanında görsel var/native nonwall yok **628 XY test noktası** buldu. G158 tam olarak bu 628 noktanın nedenine bakar, yeni özellik eklemez.

## G158 iki ayrı orijinal 2010 kaynak varlığını birleştirdi

Salt-okunur **G104** zaten başarıyla oluşturulmuş kullanıcı oyun verileri: `assets/G66_city.g66m`, `assets/G66_original_collision.g66c`, özgün `G66_city_tex_XX.g66t`. Ardından salt-okunur gerçek **G64** BRES/PVR kaynağı: `G64_SOURCE_REAL_UV_PVR_RECOVERED_VIEWER.html` içinde orijinal 24 isimli PVR RGB(A) kaydı. PVR Atlas ID ile iOS native dosya adını sıradan indeks eşleme ile TAHMİN ETMEDİK: her 2010 G66T atlasın 16B header'ı ardından **RGBA piksel yükünün SHA256 + boyutunu** orijinal G64 adlandırılmış PNG decode'ları ile birebir eşleştirdik. **24/31** tam RGBA kaynak izi aynı, kalan 7 PVR G65'te ilaveten kazanılmış olabilir; eşleşmeyene isim uydurmadık.

**Orijinal 2010 kaynak isimleri, birebir piksel kanıtı:**

- **G66 çizim grubu 12 / atlas12 = `c1l1_road.tga`.** 628 şüpheli noktadan **548 tanesini** kapsıyor, bu grupta 30 özgün üçgen bu noktalardan en az birine değiyor. En büyük devamlı Z-XY cluster (X: −160..−32, Y: −160..−48) **548** noktayı kapsıyor.
- **G66 çizim grubu 17 / atlas17 = `c1l1_flower_bed.tga`.** **54** örneğe değiyor, iki kaynak-XY doğrusal seri: X=−16 veya X=16, Y=−160..−56, her biri 27 nokta.
- Kalan 26 örnek başka orijinal çizim gruplarıyla ilişkili; yer yer gruplar çakışabildiğinden grup toplamları bölünmüş tekil üçgen adetleri değildir.

## Yeni fizik kök-neden kanıtı: gerçek G75 C fonksiyonunu bizzat çalıştırdık

548 kaynak yol örneğinin **tamamında** hesaplanan render yol yüzeyi **Z=2,6937**. Aynı XY'deki en yakın bizim şu anki G75 nonwall collision kaynağı **Z=0,0725**. Fark **+2,6212 kaynak dünya birimi**, sabit. Bu, yeni taş döşeme veya rasgele bir yol modeli üretme önerisi değil; iki farklı kaynağın gerçekten bu yüksekliklerde bulunduğu kanıtıdır.

Üstelik sadece iki JSON'u kıyaslamadık: `test_g158_true_road_G75_native_source_ground.c` gerçek kaynak G104 `G66C` dosyasını okuyor, **mevcut Vita tek B14 motorunun kullandığı gerçek `b24_g74_near_original_floor` native C fonksiyonunu** çağırıyor. Kaynak G66 road örnek koordinatı **XY=(-160,-160)** için:

- Görünür gerçek yol Z=2,6937 feet beklentisiyle `b24_g74_near_original_floor(...)` **0 (yer desteği yok)** döndürüyor.
- Özgün mevcut G66C native collision yüzeyi Z=0,0725 feet beklentisiyle aynı fonksiyon **1 ve Z=0,0725** döndürüyor.
- **G158 GitHub Actions bütün adımlar SUCCESS [#39049316919](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39049316919)**, gerçek G75 kaynak fonksiyonunun C11 host testi. [Özgün kaynak malzeme+yükseklik SVG/CSV/JSON dosyaları ve test fixture'ı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39049316919/artifacts/12106992663).

Bu fizik testi şu anki **portumuzun** yol yüksekliğinde zemini desteklemediğini **kanıtlar**. Bu, orijinal iOS oyununun da bozuk olduğu, road'ın orijinal engine'de mutlaka G66C tarafından taşındığı veya kaynak PVR/mesh'in yanlış konumda olduğu anlamına gelmez. **CLARA parent-world transforms / fizikle orijinal gerçek floor material solidity ve collision object ownership hâlâ çözülmeli**. Tek x/y C testi 548 noktadaki tüm dünya/oyun kamera koşulları için Vita davranışını kanıtlamaz.

## Genel ürünü etkileyen karar, rastgele teknik kazı değil

**Düzeltilmesi gereken sorunu artık özellikle adlandırabiliyoruz: Vita G75 native yürünebilir zemin sorgusu, render edilen gerçek 2010 yol seviyesini takip etmiyor.** Bu yüzden ilk oynanabilir C1L1 hedefinin harita/çarpışma kapısı hâlâ AÇIK. 628 noktayı otomatik collider olarak işaretlemiyoruz; flower bed ve yüksek platformların iOS kaynak solidity'si henüz kanıtlanmadı. Tek başına G156 duvar triangulation fix'i ile birinci bölüm harita katmanının hazır ilan edilmesi yanlış olur.

**Sıradaki engel odaklı iş:** `C1L1_ground_001`, `C1L1_floor_001`, `C1L1_col_01`, `C1L1_building_col` ve `Deco` source class parent/world transform + fizik kaynağı ilişkisinin özgün iOS/CLARA/BRES içerisinden tekrar doğrulanması. Çıkan sonuca göre runtime tek B14/G75 owner'ında gerçek kaynak road-ground support'unu açık/kapalı ve test edilebilir şekilde düzeltmek. Bu kanıt olmadan bütün görünür yol/çiçeklik üçgenlerini katı saymak YASAK.

**Cihaz kabulü ve geniş resim:** G106 gökyüzü/alfa + G156 çarpışma + G158 yol hizalaması + Mark V flight/repulsor tek anlamlı Vita QA paketinde test edilmeli; diğer level/audio/Lua ve QTE ayrıntı kazılarını şimdilik genişletme. G155 7 zorunlu kabul alanı `BLOCKED`. Yeni Vita VPK oluşturulmadı; bu sadece gerçek source-gameplay host C fonksiyonunda doğrulanan yeni engel.

### Kaynak ve CI

- [G158 material/XY hotspot kaynak kodu](g158_original_source_building_material_gap/g158_group_real_C1L1_visual_only_by_original_material_NO_VPK.py)
- [G158 orijinal isimlere piksel eşleştirme](g158_original_source_building_material_gap/g158_match_G66_atlas_to_G64_real_PVR_names_read_only_NO_VPK.py)
- [G158 gerçek native `G75` C yürüyüş zemini kaynak testi](g158_original_source_building_material_gap/test_g158_true_road_G75_native_source_ground.c)
- [Doğrulanmış kaynak CI #39049316919](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39049316919)
