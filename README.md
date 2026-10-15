# Iron Man 2 (2010) iOS → PS Vita — Tersine Mühendislik ve Port Projesi

**Projenin hedefi:** Gameloft'un özgün **Iron Man 2 iOS (2010, sürüm 1.0.0)** oyununu, kaynak oyun geometrisi, materyalleri, animasyonları ve görevleri korunarak PS Vita'da çalıştırmak. Mevcut çalışma **özel araştırma/deneysel homebrew** aşamasındadır; henüz tamamlanmış bir oyun portu **değildir**.

> **Güncel durum — 16 Ekim 2026 (G51 kaynak testi başarılı; özgün harita hâlâ tamamlanmadı):** Öncelik yalnızca **ilk bölümün (C1L1) özgün haritasını doğru oluşturmak**. Yeni VPK, FPS optimizasyonu veya combat ekleme çalışmalarına geçmeden önce haritanın gerçek yerleşim ve çizim davranışı çözülecek.

## Hızlı durum özeti

| Alan | Kaynakla doğruladıklarımız | Açık kalan kritik işler |
|---|---|---|
| **İlk bölüm 3B çevre** | **370 özgün BRES mesh / 37.946 vertex / 22.919 üçgen**, gerçek model isimleri | Motorun nihai sahne kökü, mesh/node dönüşüm zinciri ve doğru çizim/görünürlük |
| **Sahne nesneleri** | CLARA içindeki **53 `Deco` model referansı** özgün **207 dosyalık** model arşivine kesin bağlandı; **41** model için sıfırdan farklı kaynak yerel konum var | Runtime parent/world matrisi, sahne etkinlik durumları |
| **CLARA sahne kayıtları** | **587** sınıflandırılmış nesne, **1.608** typed alt-bileşen kaydı, **663** doğrulanmış XYZ+quaternion+ölçek dönüşümü | Alt bileşen ağını nihai oyun dünya matrisi sanmadan gerçek motor semantiğini çözmek |
| **Özgün görseller** | C1L1 çevresinin gerçek **PVR/UV** kaynak bağlantıları ve ayrı doku atlasları; pek çok dokulu yüzey doğrulandı | Kubbe/kemer/ışık gibi standart diffuse olmayan materyallerin **shader, alpha ve blending** kuralları |
| **BRES node/pivot keşfi** | **596 `_PIVOT` kayıt izi**; **295/370** mesh ismi tekil özgün pivot/TRS ile eşleşiyor; **G51'de 382 node/TRS kaydı ve 4 doğrudan doğrulanmış parent→child bağlantısı** çıkarıldı | Gerçek node→parent→mesh kümülatif dönüşümü; pivotun yanlışlıkla tek başına uygulanmaması |
| **İlk görev betikleri** | Özgün **71 Lua callback**; ilk `Mission000_OnStart` koşulsuz bölümündeki **9 Enable + 3 Disable** nesne komutu | Tüm görev koşulları ve özgün runtime görünürlük |
| **PS Vita testleri** | Kaynak modelleri gösteren **M1/M2 MapViewer** VPK'ları gerçek PS Vita'da test edildi | Test edilen sürümde **çok düşük FPS ve yanlış/eksik harita görünümü**; kaynakta yapılan sonraki analizler Vita'da henüz doğrulanmadı |

**Önemli:** Çözümlenmiş model/texture sayısı, ilk haritanın oynanabilir veya özgün oyunla aynı görünümde olduğu anlamına gelmez. Özellikle zemin, şehir ve özel efektlerin doğru sahne bileşimi henüz tamamlanmadı. Bu nedenle “harita tamamlandı” iddiasında bulunmuyoruz.

## Haritanın neden hâlâ tamamlanmadığı

- **Ham koordinat ve özgün sahne çizimi farklı:** Şehir grubundaki **11.141** üçgenin **11.048**'inin *kaynak ham* merkezi `Z < 0`; üstelik özgün CLARA `PositionDummy` verilerinde de bu seviyelere yakın kayıtlar var. Bu, tüm binaları rastgele `+36 Z` taşımamız gerektiğini **göstermiyor**.
- **Pivot, haritadaki nihai pozisyon değil:** **295** mesh için kaynak `_PIVOT` XYZ değerleri ham model bounding-box merkezinin hemen hemen negatifi (ortanca hata **0,00007**). Pivotu tek başına uygulamak binaları orijine yığabilir. Eksik olan **tam node/parent dönüşüm zinciri**.
- **Görev betiği her çevreyi yönetmiyor:** 11 sabit `C1L1` çevre modelinin hiçbiri, bulunan 71 Lua callback içinde doğrudan `Enable/Disable/Show/Hide` hedefi değil. Sadece NPC görünürlüğünü düzeltmek bina haritasını tek başına onarmıyor.
- **Bazı modeller standart PVR diffuse kullanmıyor:** `lights`, kemerler ve özel yapılar özgün shader/alpha davranışı gerektirebilir; geçici tek renkli host görünümü özgün oyunla eşdeğer değildir.

## En önemli yeni dış araştırma: Gerçek orijinal oyun + BDAE node sistemi

**[touchHLE](https://github.com/touchHLE/touchHLE)** uyumluluk veritabanında [Iron Man 2 iOS 1.0.0](https://appdb.touchhle.org/apps/451) için yüksek uyumluluk raporu bulunuyor. Kullanıcının özgün IPA'sındaki `Info.plist`, bağımsız G48 analizinde **tam olarak `com.gameloft.IronMan2`, 1.0.0** olarak doğrulandı. **Bu belirli IPA'nın touchHLE üzerinde bizim tarafımızdan başarıyla açıldığı henüz doğrulanmadı.** Sonraki adım, gerçek ilk görev görüntüsünü / mümkünse OpenGL draw-state izini elde edip Vita sahnesiyle karşılaştırmak.

**[oac-bdae-viewer](https://github.com/fata1error404/oac-bdae-viewer)** açık kaynak Gameloft BDAE ayrıştırıcısı, model içi **node ağacı, parent, XYZ/quaternion/ölçek ve `_PIVOT`** yapısının yeniden kurulmasına örnek sağladı. Ancak bu çalışma daha yeni BDAE sürümlerini hedefliyor; **bizim 2010 BRES 0.0.0.133 için adres/alan düzeni ayrı ayrı doğrulanmadan doğrudan kopyalanmayacak.**

Diğer ilgili projeler: [Shadow Guardian Vita](https://github.com/MetalSyntax/Shadow-Guardian-vita), [Backstab Vita](https://github.com/v-atamanenko/backstab-vita), [9mm Vita](https://github.com/iwannagooutside/9mm-vita). Bunların Android ARMv7 `.so` port yaklaşımı **iOS ARMv6 Mach-O dosyamıza doğrudan uygulanamaz**, ancak VitaGL / grafik ve motor çalışma yöntemleri incelenebilir.

## Bundan sonraki sıra

1. Özgün **Iron Man 2 1.0.0** sürümünü touchHLE'de açıp ilk bölümün gerçek harita ve kamera görüntüsünü kaydetmek; mümkünse draw-call/model-view/depth/blend durumunu karşılaştırmak.
2. Eski BRES formatındaki **node/parent/pivot zincirini** kaynak baytlar üzerinden çıkarmak ve **370 özgün mesh** ile doğrulamak. *Tek başına pivot / tahmini bina kaydırma uygulanmayacak.*
3. Gerçek sahne koordinatlarını, görünürlük katmanlarını ve özel materyalleri özgün oyunun çıktısıyla karşılaştırarak **doğru ilk bölüm haritasını** derlemek; önce kaynak temelli PNG/3B ön izleme, ardından tek bir anlamlı Vita cihaz testi.
4. **Harita tamamlandıktan sonra:** eksik karakter animasyonları, uçuş ve combat stilleri, temel oyun mekanikleri; ardından ilk görev için özgün **ses dosyaları, cutscene'ler ve görev akışı**. Bu sıra kullanıcı isteğiyle belirlendi.

## Kaynak kodu, testler ve devir notları

- **[G48–G50 harita/node/pivot teknik devir dosyası](https://github.com/Gh0sTRX/Iron-man-2-os/blob/feature/b24-unified-gameplay/research/b24_unified/G48_G50_TOUCHHLE_ORIGINAL_2010_BRES_NATIVE_NODE_PIVOT_EXTERNAL_ACCELERATION_2026-10-15.md)**
- [G51 — özgün BRES node kayıtları ve ilk 4 kaynak parent→child bağı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38807992014)
- [G50 — 370 mesh adı ↔ özgün pivot kayıt testi](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38806041866)
- [G49 — 596 özgün pivot işaretçisi kontrolü](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38805353380)
- [G48 — orijinal IPA sürüm ve BRES düğüm testi](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38805142991)
- [G47 — gerçek kaynak PVR/BRES 3B katman karşılaştırması](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38799872031)
- [G43 — ilk görevin dokuz açıkça etkin nesnesi](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38795548903)
- Ana teknik devir belgesi: [`PROJECT_CONTINUE_LATEST.md`](PROJECT_CONTINUE_LATEST.md). Ayrıntılı kaynak incelemeleri, `feature/b24-unified-gameplay` dalındaki `research/b24_unified/` klasöründedir.
- Orijinal oyunu Windows'ta başlatma yardımcısı: [`touchHLE` referans BAT dosyası](https://github.com/Gh0sTRX/Iron-man-2-os/blob/feature/b24-unified-gameplay/research/b24_unified/touchhle_original_reference/IRONMAN2_ORIJINAL_2010_TOUCHHLE_WINDOWS_BASLAT.bat). Kullanıcıya ait orijinal IPA ve resmi emülatör ayrıca gereklidir.

### Derleme ve sürüm ayrımı

Mevcut **`main`** dalında eski **Asset Beta** denemesi (`source/IronMan2_Vita_GitHub_Ready_CI.zip`) ve ilgili `Build Iron Man 2 Vita Asset Beta` GitHub Actions iş akışı bulunur. Bu, dört zırh modelini gösteren ayrı bir deneysel görüntüleyicidir; **bugünkü C1L1 harita analiziyle veya tamamlanmış portla karıştırılmamalıdır**.

Yeni C1L1 araştırma betikleri ve kaynak-only GitHub Actions testleri **`feature/b24-unified-gameplay`** dalındadır. G48–G51 testleri yeni cihaz VPK'sı oluşturmaz. Sonraki gerçek Vita sürümünün FPS'i veya sahne doğruluğu cihazda yeniden test edilmedikçe kesin kabul edilmez.

## Lisans / içerik notu

Oyun, karakterler, sesler, özgün modeller ve dokular ilgili hak sahiplerine aittir. Bu depo özel araştırma içindir. Orijinal IPA'yı, oyun varlıklarını veya telifli içerikleri izinsiz kamuya açık dağıtmayın.
