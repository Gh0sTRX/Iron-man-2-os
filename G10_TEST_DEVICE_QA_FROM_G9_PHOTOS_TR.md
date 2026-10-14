# IRON MAN 2 PS VITA — G10 TEST (G9 gerçek cihaz fotoğrafı sonrası)

## Derleme doğrulandı
- G10 test VPK: `IronMan2_GPU_B24_G10_TEST.vpk`
- G10 TITLE_ID: **IM2G00035**, G9 IM2G00034 ve G8 IM2G00033 korunur.
- VitaSDK 2026.08 + sabitlenmiş splashless vitaGL ile gerçek eboot bağlantısı **başarılı**, [Actions 38640696707](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38640696707).
- Kurulum dosyası **157,462,182 bytes**, SHA256 `bde878b578951e144b7d37ec0b72ecb4022c2785471e049738d23833cfb6c22f`, artifact [11930865329](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38640696707/artifacts/11930865329).
- Arşivde G9'un eski 59 animasyonu + 304 owner-authentic Mark VI/War Machine kaynak animasyonu + **Mark IV, Stealth, Suitcase için ayrı 248'er orijinal 2010 kaynak skinned animasyon** (744) = **1.107 IM2V**. 6 War Machine rigid Gun01-04 IM2K. Beş eski orijinal suit modeli, C1L1 22.919 GPU/1.908 CPU collision tri, C1TX araç atlası.
- Özgün 2010 kaynak BRES inverse-bind ile ayrı suit rig bake [38637615568](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38637615568) **SUCCESS**; Suitcase 629 vertex, diğer source suitler 802. 248'er dosyanın tamamı oynanabilir formatta fakat **her 248 aksiyon için farklı özel gameplay inputu yoktur**.

## G9 gerçek PS Vita raporundan düzeltmeler
- G9 kaynakta Mark VI boşta hovering bile `Aim_Float_idle` kullandığı için sürekli repulsor'a hazır/ateş hareketinde duruyordu. G10 dört Iron Man armor ailesi boşta hover için gerçek **`IronMan_Move_Float`** klibini seçer; gerçek `*_Att` sadece kabul edilen atış olayında oynatılır. Orijinal 2010 hareket geçişi 800 ms; **loop davranışı Vita'da test edilmedi.**
- Mark IV / Stealth / Suitcase: kaynak harekete, sola/sağa hover + fire, orijinal Mark VI 3'lü combo animasyonlarına ve özgün dolaşma/flight kayıtlarına kendi fiziksel modeliyle girer. 248 dosyanın orijinal state machine dalları **tam çözülmedi**, source `states` Lua/level1 `clev` analizi devam.
- Mark VI gerçek 3-hit mevcut ve G9 fotoğrafında iyi; Power Combo a/aa/aaa/aab/ab/aba/abb ve repulsor ile karma input kombinasyonları **henüz canlı oyun tuş sırasına bağlanmadı**.
- C1L1 G9 fotoğraflarında düz renkli yol/binalar, siyah gökyüzü, bazı yüzen kareler, görünmez duvarlar, zemine gömülen ayaklar gözlendi. G10 `b24_c1_true_source_floor.c` G9 kaynak **3.280 özgün yol üçgeninden** gerçek XY barycentrik Z sorgular; `b24_g10_original_foot_contact.c` yerini modelin gerçek en alt vertexine göre VitaGL kamera+zırh görselliğinde ayarlar. Bu **görsel ayak-teması düzeltmesidir; B14 fizik Z çarpışması hâlâ tam değil**, 1.908 C1WC duvar çarpışmaları korunur. 2010 şehir sahnesi node'ları sadece -90° export-viewer eksen dönüşümü taşır, ekstra kayıp world translation doğrulanmadı.
- **Kalıcı eğitim hedefi**: harita test merkezi orijinal gerçek yol zemini üstünde x0,y10 konumunda cyan GPU wireframe kutu. HP azalmaz, gerçek bölüm düşmanı olarak sunulmaz. G10 kaynak `B24_G10_PRACTICE_TARGET_ID=910`. **L basılı tutulduğunda repulsor dahil silahlarda hedef kilidi** için B23 gözlemi ve HUD bağlanır; hedef oyunda doğrulanana kadar bitmiş hedefleme gibi gösterme. Hedef model başka bir yerde görünüyorsa veya HUD kilidi seçmiyorsa ekran görüntüsü çek.
- War Machine orijinal `Aim_Float_move_L/R` ve `*_Att` beden akışları mevcut; 6 IM2K silah hareket düğümü eş zamanlı. **Otomatik makinalı tüfek, gerçek füze parçacıkları ve düşman hasarı yok** (muzzle ve düşman actor gerçek bağlantısı daha sonra).
- **Özgün nişangâh değiştirilmedi.** iOS `window` arşivinde 23 gerçek PNG, özel `sprites` arşivinde 13 girişli binary kaynak var; tam orijinal lock/crosshair resminin hangisi olduğu henüz ispatlanmadı. HUD mevcut native B24 nişangâh olarak kalıyor.
- **Harita materyal çözülmedi:** C1L1 gerçek `C1L1_road...`, `C1L1_building...`, `C1L1_sky...` PVR doku kaynakları ve BRES referansları keşfedildi fakat original `C1MA` 94 materyal ID→gerçek örnekleyici diffuse atlas eşleştirmesi kodlanmadı. Araç atlası hâlâ orijinal B12, diğer kategoriler düz renk. C1L1 görev başlangıç koordinatı ve AI/yapay zekâ eksik. `level1.bclara` özgün `SpawnPoint` ve `NodeMaterials` alanları; source `states` 55 Lua51 chunk ile devam eden araştırma.

## Fiziksel cihazda öncelikli test
1. G10 VPK'yi VitaShell ile G9'un yanına kur; açılış/menu çalışıyor mu, FPS kaç, mevcut siyah gökyüzü ve düz yüzeylerde beklenen fark var mı?
2. Mark VI yer hover yaparken **hiç ateş etme**: sağ kol hâlâ kalkık mı, geçiş tekrarlıyor mu? Sonra R ile ateş et. Durgun+ateş farkının görsel/video kaydı çok yararlı.
3. Mark IV, Stealth ve Suitcase ile **sağ/sol hover** ve **sağ/sol ateş**; Mark VI 3'lü combo Square; her modelde kol-bacak geometrisi kopuyor mu?
4. Harita merkezindeki açık renk **cyan wireframe eğitim hedefine** yaklaş; L basılı tutarak kilit simgesi geliyor mu? Denemeden önce repulsor; ardından füze modu. Hedef asla hasar almamalı.
5. Ground ayakta duruşu: Mark VI'nın bacakları zemin içine giriyor mu? Farklı eğimli bölgelerde. Hata devam ediyorsa foto + konum ve uçuş durumu.
6. Görünmeyen collider/duvara takılma konumu ve çevredeki nesnelerin fotoğrafı; G10 henüz bu collision filtrelerini değiştirmiyor. Stok CPU/GPU FPS 30sn/1dk ölçümü.

**Sahada onaylanana kadar** tüm yukarıdaki özellikler “kaynak entegre ve derleme başarılı” olarak değerlendirilir, “Vita’da kesin çalışıyor” değildir.
