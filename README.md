# Iron Man 2 (2010) iOS → PS Vita — Tersine Mühendislik ve Port Projesi

**Projenin hedefi:** Gameloft'un özgün **Iron Man 2 iOS (2010, sürüm 1.0.0)** oyununu, kaynak oyun geometrisi, materyalleri, animasyonları ve görevleri korunarak PS Vita'da çalıştırmak. Mevcut çalışma **özel araştırma/deneysel homebrew** aşamasındadır; henüz tamamlanmış bir oyun portu **değildir**.

> **Güncel durum — 16 Ekim 2026 (G56 özel light geometri sınıflandırması doğrulandı; özgün runtime haritası hâlâ tamamlanmadı):** Öncelik yalnızca **ilk bölümün (C1L1) özgün haritasını doğru oluşturmak**. Yeni VPK, FPS optimizasyonu veya combat ekleme çalışmalarına geçmeden önce haritanın gerçek yerleşim ve çizim davranışı çözülecek.

## Hızlı durum özeti

| Alan | Kaynakla doğruladıklarımız | Açık kalan kritik işler |
|---|---|---|
| **İlk bölüm 3B çevre** | **370 özgün BRES mesh / 37.946 vertex / 22.919 üçgen**, gerçek model isimleri | 296/370 mesh G55 gerçek kaynak zincirinde yerleştirildi; runtime scene root, kalan 74 mesh ve doğru çizim/görünürlük açık |
| **Sahne nesneleri** | CLARA içindeki **53 `Deco` model referansı** özgün **207 dosyalık** model arşivine kesin bağlandı; **41** model için sıfırdan farklı kaynak yerel konum var | Runtime parent/world matrisi, sahne etkinlik durumları |
| **CLARA sahne kayıtları** | **587** sınıflandırılmış nesne, **1.608** typed alt-bileşen kaydı, **663** doğrulanmış XYZ+quaternion+ölçek dönüşümü | Alt bileşen ağını nihai oyun dünya matrisi sanmadan gerçek motor semantiğini çözmek |
| **Özgün görseller** | C1L1 çevresinin gerçek **PVR/UV** kaynak bağlantıları ve ayrı doku atlasları; pek çok dokulu yüzey doğrulandı | Kubbe/kemer/ışık gibi standart diffuse olmayan materyallerin **shader, alpha ve blending** kuralları |
| **BRES node/pivot keşfi** | **G55: 670** özgün BRES node/TRS kaydı; **296/370** mesh özgün `parent → -node_PIVOT → mesh` ilişkisi; 16/16 zemin, 121/121 şehir, 22/22 araç doğrulandı | G55 kısmi kaynak dönüşümü mevcut; kalan 74 özel mesh, üst seviye runtime root, görünürlük, PVR shader |
| **İlk görev betikleri** | Özgün **71 Lua callback**; ilk `Mission000_OnStart` koşulsuz bölümündeki **9 Enable + 3 Disable** nesne komutu | Tüm görev koşulları ve özgün runtime görünürlük |
| **PS Vita testleri** | Kaynak modelleri gösteren **M1/M2 MapViewer** VPK'ları gerçek PS Vita'da test edildi | Test edilen sürümde **çok düşük FPS ve yanlış/eksik harita görünümü**; kaynakta yapılan sonraki analizler Vita'da henüz doğrulanmadı |

**Önemli:** Çözümlenmiş model/texture sayısı, ilk haritanın oynanabilir veya özgün oyunla aynı görünümde olduğu anlamına gelmez. G55 ile özgün kaynak zemin/şehir/araç mesh'lerinin yerel node zinciri ve host 3B önizleme oluşturuldu, fakat üst runtime sahne kökü, görünürlük ve özel efektlerin özgün çizim davranışı henüz tamamlanmadı. Bu nedenle “harita tamamlandı” iddiasında bulunmuyoruz.

## G57 — Özgün C1L1 haritasının 2010 PVR/UV dokularıyla ilk gerçek giydirilmesi (16 Ekim 2026)

**G57 kaynak kodu GitHub'da, GitHub Actions testi başarılı:** [G57 CI 38814440599](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38814440599) • [yeniden üretilebilir Python betiği](https://github.com/Gh0sTRX/Iron-man-2-os/blob/feature/b24-unified-gameplay/research/b24_unified/b24_g57_g55_native_TRS_plus_g32_source_PVR_UV_offline_preview.py). G55'in 2010 BRES native parent→pivot dönüşümünü, G32'nin **gerçek iOS BRES mesh sırası, özgün UV ve 24 özgün PVR diffuse atlasıyla** aynı geometri üzerinde birleştirir. **296 mesh (37.089 vertex / 22.441 triangle)** için orijinal model ve yüz sırası tekrar kaynak B11 ile eşleştirilip doğrulandı. **18.774 üçgen özgün PVR+UV diffuse dokulu**, **3.667** üçgen bilinmeyen materyal tanısal renkli, **74** henüz ana zincire bağlanmamış özel mesh gizli. Üretim: çevrimdışı WebGL2 **etkileşimli HTML**, kaynaktan dokulu **3B GLB**, JSON. Ayrı yerel CPU orijinal-PVR/UV rasterlayıcı, şehir detay ve tüm haritanın **gerçek veri PNG** görüntülerini üretti. AI ile çizilmiş fotoğraf kullanılmadı.

**Doğrulanmayanlar:** kaynağın gerçek orijinal iOS uygulamasında touchHLE ile açıldığı **henüz bu projede doğrulanmadı**; G57'nin host görüntüsü gerçek Gameloft shader/render-state/camera/alpha blending değildir. Hâlâ üst sahne kökü, özel 74 mesh, görünürlük, FX shader, oyuncunun harita üstündeki özgün başlangıcı ve Vita FPS'i açık. **Yeni VPK oluşturulmadı.** Bir sonraki hedef: özgün touchHLE ilk C1L1 gameplay görüntüsüyle G57 kaynak modellerinin sahne ve ışık/alpha doğruluğunu karşılaştırmak.

## G55 (16 Ekim 2026) — Haritada gerçek kaynak hiyerarşisi

**Bağımsız G55 GitHub Actions SUCCESS:** [G55 CI ve 2010 kaynak geometri GLB/PNG/JSON](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38811387146). BRES v0.0.0.133 formatının doğrulanan çocuk sayısı alanı `+52`, ilk çocuk kaydı işaretçisi `+56` bayt ofsetindedir. G51/G52 bunları `+56/+60` olarak okuduğundan eski `382 node/4 child` teşhisi superseded: doğru ayrıştırıcı **670** native node kaydı tespit ediyor.

**296** özgün aynı isimli `-node → -node_PIVOT → -mesh` kaydı, kaynak pointer'ıyla eşleşiyor: 16/16 zemin, 121/121 şehir, 22/22 araç, 137 özel light. **22.441/22.919 üçgen ve 37.089/37.946 vertex** için özgün parent/pivot TRS bileşik dönüşümleri kaynak temelli üstten harita PNG'si ve 3B GLB şeklinde üretildi. 74 küçük/özel mesh (478 üçgen) ve runtime root, özgün görünürlük, materyal/alpha ve kamera davranışı henüz tamamlanmadı.

Bu çıktı **özgün iOS uygulamasının gerçek çizimi, touchHLE'den alınmış oyun ekranı veya PS Vita testi değildir**; source-authentic host geometri önizlemesidir. Yeni VPK yok, eski sürümler etkilenmedi. Kod: [G55 native BRES map source parser](https://github.com/Gh0sTRX/Iron-man-2-os/blob/feature/b24-unified-gameplay/research/b24_unified/b24_g55_2010_C1L1_true_native_BRES_parent_pivot_scene_reconstruction.py). Öncelik: gerçek iOS ilk görev referans görüntüsüyle doğrulama, root/visibility, kalan ışık/özel mesh ve materyaller.

**G56 kaynak ayrımı:** [CI SUCCESS — 74 özel mesh](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38812301376). `_PIVOT` bulunmayan **74/74** özel light mesh'inin özgün `-node` kaydı var. Bunlardan **49'u kaynak bounding-box olarak orijin merkezli**, **25'i kaynakta önceden farklı konuma yerleşmiş (baked-offset)** durumda; toplam **478** orijinal üçgen. **Bu iki sınıfın gerçek iOS world dönüşümü kesinleşmedi**, dolayısıyla tümüne tek tip ebeveyn konumu eklenmeyecek. Kaynak kodu [`b24_g56_C1L1_special_light_missing_pivot_raw_source_geometry_audit.py`](research/b24_unified/b24_g56_C1L1_special_light_missing_pivot_raw_source_geometry_audit.py) (`feature/b24-unified-gameplay` dalında).

## Haritanın neden hâlâ tamamlanmadığı

- **Ham koordinat ve özgün sahne çizimi farklı:** Şehir grubundaki **11.141** üçgenin **11.048**'inin *kaynak ham* merkezi `Z < 0`; üstelik özgün CLARA `PositionDummy` verilerinde de bu seviyelere yakın kayıtlar var. Bu, tüm binaları rastgele `+36 Z` taşımamız gerektiğini **göstermiyor**.
- **Pivot, haritadaki nihai pozisyon değil:** **295** mesh için kaynak `_PIVOT` XYZ değerleri ham model bounding-box merkezinin hemen hemen negatifi (ortanca hata **0,00007**). Pivotu tek başına uygulamak binaları orijine yığabilir. G55 ile **296 mesh için gerçek yerel parent→pivot dönüşümü** çözüldü; eksik olan runtime üst sahne kökü, kalan 74 özel mesh ve iOS render doğrulaması.
- **Görev betiği her çevreyi yönetmiyor:** 11 sabit `C1L1` çevre modelinin hiçbiri, bulunan 71 Lua callback içinde doğrudan `Enable/Disable/Show/Hide` hedefi değil. Sadece NPC görünürlüğünü düzeltmek bina haritasını tek başına onarmıyor.
- **Bazı modeller standart PVR diffuse kullanmıyor:** `lights`, kemerler ve özel yapılar özgün shader/alpha davranışı gerektirebilir; geçici tek renkli host görünümü özgün oyunla eşdeğer değildir.

## En önemli yeni dış araştırma: Gerçek orijinal oyun + BDAE node sistemi

**[touchHLE](https://github.com/touchHLE/touchHLE)** uyumluluk veritabanında [Iron Man 2 iOS 1.0.0](https://appdb.touchhle.org/apps/451) için yüksek uyumluluk raporu bulunuyor. Kullanıcının özgün IPA'sındaki `Info.plist`, bağımsız G48 analizinde **tam olarak `com.gameloft.IronMan2`, 1.0.0** olarak doğrulandı. **Bu belirli IPA'nın touchHLE üzerinde bizim tarafımızdan başarıyla açıldığı henüz doğrulanmadı.** Sonraki adım, gerçek ilk görev görüntüsünü / mümkünse OpenGL draw-state izini elde edip Vita sahnesiyle karşılaştırmak.

**[oac-bdae-viewer](https://github.com/fata1error404/oac-bdae-viewer)** açık kaynak Gameloft BDAE ayrıştırıcısı, model içi **node ağacı, parent, XYZ/quaternion/ölçek ve `_PIVOT`** yapısının yeniden kurulmasına örnek sağladı. Ancak bu çalışma daha yeni BDAE sürümlerini hedefliyor; **bizim 2010 BRES 0.0.0.133 için adres/alan düzeni ayrı ayrı doğrulanmadan doğrudan kopyalanmayacak.**

Diğer ilgili projeler: [Shadow Guardian Vita](https://github.com/MetalSyntax/Shadow-Guardian-vita), [Backstab Vita](https://github.com/v-atamanenko/backstab-vita), [9mm Vita](https://github.com/iwannagooutside/9mm-vita). Bunların Android ARMv7 `.so` port yaklaşımı **iOS ARMv6 Mach-O dosyamıza doğrudan uygulanamaz**, ancak VitaGL / grafik ve motor çalışma yöntemleri incelenebilir.

## Bundan sonraki sıra

1. Özgün **Iron Man 2 1.0.0** sürümünü touchHLE'de açıp ilk bölümün gerçek harita ve kamera görüntüsünü kaydetmek; mümkünse draw-call/model-view/depth/blend durumunu karşılaştırmak.
2. G55'in **296 mesh için gerçek native parent→pivot zincirini** özgün iOS runtime görüntüsüyle karşılaştırmak; kalan **74** özel ışık/efekt mesh'inin bağlantılarını ve nihai root dönüşümünü kanıtlamak. *Tahmini bina kaydırma yapılmayacak.*
3. Gerçek sahne koordinatlarını, görünürlük katmanlarını ve özel materyalleri özgün oyunun çıktısıyla karşılaştırarak **doğru ilk bölüm haritasını** derlemek; önce kaynak temelli PNG/3B ön izleme, ardından tek bir anlamlı Vita cihaz testi.
4. **Harita tamamlandıktan sonra:** eksik karakter animasyonları, uçuş ve combat stilleri, temel oyun mekanikleri; ardından ilk görev için özgün **ses dosyaları, cutscene'ler ve görev akışı**. Bu sıra kullanıcı isteğiyle belirlendi.

## Kaynak kodu, testler ve devir notları

- **[G48–G50 harita/node/pivot teknik devir dosyası](https://github.com/Gh0sTRX/Iron-man-2-os/blob/feature/b24-unified-gameplay/research/b24_unified/G48_G50_TOUCHHLE_ORIGINAL_2010_BRES_NATIVE_NODE_PIVOT_EXTERNAL_ACCELERATION_2026-10-15.md)**
- **[G55 — 296 özgün parent→pivot→mesh sahne zinciri ve kaynak 3B GLB/PNG](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38811387146)**
- [G53 — ham düğüm referans indeksleme](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38809483236)
- [G52 — önceki çocuk alanı yorumunun tanısal negatif testi; G55 ile superseded](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38809220617)
- [G51 — eski +56/+60 ofset yaklaşımı, G55 ile düzeltilmiştir](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38807992014)
- [G50 — 370 mesh adı ↔ özgün pivot kayıt testi](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38806041866)
- [G49 — 596 özgün pivot işaretçisi kontrolü](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38805353380)
- [G48 — orijinal IPA sürüm ve BRES düğüm testi](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38805142991)
- [G47 — gerçek kaynak PVR/BRES 3B katman karşılaştırması](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38799872031)
- [G43 — ilk görevin dokuz açıkça etkin nesnesi](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38795548903)
- Ana teknik devir belgesi: [`PROJECT_CONTINUE_LATEST.md`](PROJECT_CONTINUE_LATEST.md). Ayrıntılı kaynak incelemeleri, `feature/b24-unified-gameplay` dalındaki `research/b24_unified/` klasöründedir.
- Orijinal oyunu Windows'ta başlatma yardımcısı: [`touchHLE` referans BAT dosyası](https://github.com/Gh0sTRX/Iron-man-2-os/blob/feature/b24-unified-gameplay/research/b24_unified/touchhle_original_reference/IRONMAN2_ORIJINAL_2010_TOUCHHLE_WINDOWS_BASLAT.bat). Kullanıcıya ait orijinal IPA ve resmi emülatör ayrıca gereklidir.

### Derleme ve sürüm ayrımı

Mevcut **`main`** dalında eski **Asset Beta** denemesi (`source/IronMan2_Vita_GitHub_Ready_CI.zip`) ve ilgili `Build Iron Man 2 Vita Asset Beta` GitHub Actions iş akışı bulunur. Bu, dört zırh modelini gösteren ayrı bir deneysel görüntüleyicidir; **bugünkü C1L1 harita analiziyle veya tamamlanmış portla karıştırılmamalıdır**.

Yeni C1L1 araştırma betikleri ve kaynak-only GitHub Actions testleri **`feature/b24-unified-gameplay`** dalındadır. G48–G57 testleri yeni cihaz VPK'sı oluşturmaz. Sonraki gerçek Vita sürümünün FPS'i veya sahne doğruluğu cihazda yeniden test edilmedikçe kesin kabul edilmez.

## Lisans / içerik notu

Oyun, karakterler, sesler, özgün modeller ve dokular ilgili hak sahiplerine aittir. Bu depo özel araştırma içindir. Orijinal IPA'yı, oyun varlıklarını veya telifli içerikleri izinsiz kamuya açık dağıtmayın.
