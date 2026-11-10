# B24-C1 — İlk Bölümün ÖZGÜN C1L1 Harita Geometrisiyle Birleşik PS Vita Oynanış Testi
Tarih: 2026-10-13. Onaylanan yön: B17'ye dönme; **B24'ün mevcut uçuş/kamera/HUD/savaş/RUSH özelliklerini bırakmadan**, tekrarlanan 121 renkli CPU kare-zeminini orijinal C1L1 harita sahnesiyle değiştir. Bu bir **aktif entegrasyon görev listesi**; henüz haritalı Vita VPK'sı üretildiği veya gerçek Chapter 1 görev script'inin çözüldüğü anlamına GELMEZ.

## Gerçek varlıklar: artıkları yeniden extract/decrypt etmemize gerek yok
1. `research/B11_C1L1_Source_Parser.zip` (1.038.815 B): tam olarak 15 orijinal `C1L1_*.bdae`, `bdae_scene_parser.py`, `build_scene.py`, `exports/geometry_manifest.csv`, orijinal Mark VI GLB. Orijinal dosyalar Gameloft 2010 iOS v1.0.0 IPA'sından; BRES/BDAE 0.0.0.133 formatı, uçuş sistemi dosyalarıyla karıştırma.
2. `research/B11_C1L1_Scene_GLBS.zip` (860.300 B): `exports/IronMan2_C1L1_Environment_Geometry.glb` (1.048.112 B, 370 submesh) ve `exports/IronMan2_C1L1_Original_Geometry_With_MarkVI.glb` (1.404.904 B, + zırh). 10 çevre modeli, 37.946 görünür vertex / 22.919 görünür üçgen; toplam 15 modelde 24.925 doğrulanmış tri. Mevcut GLB'nin düz renkli çevre materyalleri **geçici tanılama renkleridir**, orijinal doku değil.
3. `research/B12_ORIGINAL_C1L1_TEXTURE_RECOVERY.md`: doğrulanmış 190 BDAE doku kaydı / 39 farklı referans / 39 orijinal IPA'da bulundu; 42 PNG dönüştürüldü, ancak ortamın difüz+lightmap materyal eşleşmesi tamamlanmadı. **Drive özel ZIP** `[private Google Drive link redacted]` (7.679.708 B) erişilebilir. `C1L1_car_01/02` için gerçek atlas ve UV eşleştirilmiş 22 alt mesh'li araç GLB'i araştırmalarda var. PVRTC decoder deneysel olduğundan renk doğruluğu gerektirir.
4. `research/Original_Level_BCLARA_Audit.zip`: orijinal `level1.bclara`…`level10.bclara` metadata ve şema etiketleri (`Mission`, `Objective`, `SpawnPoint`, vb); gerçek instance/karakter spawn/trigger henüz decode edilmedi. `C1L1` ↔ `level1.bclara` eşlemesi **doğrulanmadı**. Topluluk longplay'de ilk bölüm `Media Mayhem` diye geçer, BCLARA ispatı değil.
5. `research/b24_unified/*`, `.github/workflows/unified-b24.yml`: kaynaklar tek VitaSDK `im2_beta` hedefinde, önceki B24 run `38436839457` başarılı; bu başarı C1L1 sahnesinin ekranda çizildiğini kanıtlamaz.

## Asıl ürün kabul sözleşmesi
**B24-C1 = B24 aynı zırh ve input/HUD/RUSH prototipi + ekranda gerçek C1L1 kaynaklı bina/yol/araç/zemin geometrisi + gerçek yüzeyle uçuş/iniş kontrolü + GPU render ölçümü.** Sadece GLB dosyasını VPK ZIP içine atmak veya boş ekranda C1L1 yazmak BAŞARI sayılmaz.

### Sıralı uygulama görevleri ve kontrol kapıları

**[P0] Özgün C1L1 kaynak doğrulaması ve malzeme atlası**
- [ ] B11 GLB ZIP'ini ve BDAE kaynaklarını CI'de `sha256`/ZIP CRC ile doğrula; 370 görünür submesh, 22.919 tri, 37.946 vertex bekleniyor. Sayıların doğrulandığı kurulum sürümü dışındaki varyantlarda rapor ver.
- [ ] `C1L1_ground_001`, `C1L1_obj_001–004`, `C1L1_car_01/02`, `C1L1_light_001–003`, `C1L1_sky_001`, `C1L1_floor_001`, `C1L1_col_01`, `C1L1_building_col` kaynaklarını rollere göre ayır; fiziksel collision mesh ile görünür dekoru karıştırma.
- [ ] Şimdilik orijinal geo + tanısal materyal; doğrulanmış doku eşleşen alt-meshlerde gerçek atlası bağla, gerisine sahte "orijinal doku" verme. 39 doku referansını B12 materyal tablosuyla eşleştir.

**[P0] Offline statik harita derleyicisi (PC üstünde CI)**
- [ ] `B11_C1L1_Scene_GLBS.zip` içinde `Environment_Geometry.glb` dosyasını CI'de çıkart, glTF JSON/BIN accessor/offset/primitive listesini denetle. `With_MarkVI.glb` içindeki ikinci zırhı sahneye *ayrıca* ekleyip çift Iron Man göstermemek için çevre GLB'i seç.
- [ ] C1L1 geometrisini Vita için `.im2map` (veya isimlendirilmiş sürümlü eşdeğer) veri formatına çevir: grup/batch, index `uint16` uygun olduğunda, interleaved pos/uv/color, material id, bounding box, pakette kaynak hash. Farklı GLB mesh node transformlarını bake et.
- [ ] B11 GLB standart **Y-up**'tır, B17 dünya/renderer **Z-up**'tır. Eski orijinal BDAE kaynakları Z-up; dönüşüm GLB içinden inverse-rotate edilerek uygulanmalı. Otomatik ölçek/yön tahmin etme.
- [ ] Mesafe/camera frustum veya ekran görünürlük filtresi, obje gruplama ve 2–3 kademeli LOD. 370 submesh = 370 GPU draw call zorunluluğu değil; materyal/atlas grupları ile batch. İlk karede 22.919 trianglenin hepsini piksel CPU raster yapma.
- [ ] Tekrarlanabilir host test: veri bounds, out-of-range index 0, node transform determinant/normali, orijinal dünya bbox karşılaştırması, crash/wild-memory toleransı.

**[P0] B24 gerçek GPU render hattı (ayrı demo DEĞİL)**
- [ ] B24 mevcut SDL software renderer'dan farklı, **tek sahibi** olan Vita GPU context + present/swap çalıştır. SDL_Renderer context + vitaGL context'i rastgele birleştirme. İlk geçerli kare: GPU derinliği test edilen orijinal zırh + orijinal C1L1 statik çevre.
- [ ] CPU `b17_world_floor` 11×11 tekrarlı piksel zemin çizimini **map modunda kapat**; eski B17 modunu sadece açık debug fallback seçeneği olarak sakla. 480×272 tüm framebuffer `SDL_UpdateTexture` + CPU tüm-model raster yolunu GPU modunda artık kullanma. Gerekirse HUD'ı ayrı 2D GPU quad/batch overlay çiz.
- [ ] Zırhın dinamik IM2V pozisyonlarını GPU vertex buffer update/skinning planına bağla, orijinal texture UV/material gl shader/depth uygula. Tek render owner'da `scene -> armor -> VFX -> HUD` sıralaması.
- [ ] Hem CPU frame time hem GPU submission/present hem FPS'yi Vita üstünde ölç. Yalnız CI derlendi diye FPS iyileşti deme.

**[P1] Harita üzerinde gerçek hareket, iniş ve çarpışma**
- [ ] Chapter 1 sahnesinde kaynak-konumu **orijinal spawn doğrulanmadığı için** açıkça **TEST SPAWN** belirle; spawn altında yere raycast yap, collision geo üzerinden yükseklik oku, zırhın ayak dünya pozisyonunu/zemin normalini ölç. Test spawn orijinal görev başlangıcıymış gibi sunulmaz.
- [ ] Ground/hover/Stage2/RUSH hareket hissi B17/B24'ten kalır, Stage2 tam analog/hysteresis şartı korunur. Haritada yatay/uçuş çarpışması, tavan/yükseklik, test sınırını aşınca kontrollü reset; yüzeye değmeden landing clip oynatılmaz.
- [ ] B22.3 omuz→arkadan chase kamera, B22.6 yakın dövüş focus ve füze lock dünya projeksiyonunu aynı map view/projection matrisiyle güncelle; kamera clipping duvar raycast'ı sahne collision geo'ya bağlanır.
- [ ] RUSH Stage3 foot+palm+iki back emitters **yalnızca RUSH**; modelin gerçek bone anim socket pozları olmadan sahte GPU jetleri "original" etiketlenmez. Stage2 back = 0 invariant test.

**[P1] Düşman/test arayüzü ve görev katmanı**
- [ ] Harita modeline eşlenmiş gerçek B19 enemy world entity, projectile, health, missile lock, attack/muzzle ve combo hit olaylarını ekle; B17 eski basit spherical target yerine doğru dünya objeleri kullan. İlk testte tek açıkça **TEST** dummy düşman olabilir.
- [ ] Çevre modeli gerçek, ancak original `level1.bclara` gerçek trigger/waypoint/objective/spawn script tam decode olmadan "Media Mayhem restore edildi" dememek. İlk sürüm kapalı bir C1L1 arena değildir: mümkün sahne içi gezilebilir alanı koru ve düşük FPS varsa LOD ile sınırla.
- [ ] Orijinal bina, tabelalar, aydınlatma atlası ve çevre doku eşleşmelerini ilerleyerek devreye al. Gerçek Chapter 1 hikâye görevi ancak BCLARA instance decode sonrası.

**[P2] CI/Vita QA**
- [ ] `B24-C1` kaynakları `feature/b24-unified-gameplay` branch üzerinde; aynı TITLE_ID `IM2B00024` ile oyun sürümü güncellenir ya da testleri ayırmak istenirse ayrı sürüm TITLE_ID seçilir, hiçbir durumda mevcut B17 paketi overwrite edilmez.
- [ ] Native host GLB/IM2MAP converter + basit sahne camera/frustum/draw regression ve B24 20k input tests + VitaSDK link + VPK ZIP/asset manifest/hash gate.
- [ ] Vita üzerinden 5 zırh, yürüyüş, hover, full-stick Stage2, RUSH, kamera, GPU zemin ve binalar, no-pixel tiles, gerçek yüzey landing, repulsor/HUD hedefleme testi; ekran kaydı/foto ve 15–30 sn sabit FPS ölçümü.
- [ ] Yalnız harita dosyasının paket içinde bulunması değil: **cihazda görülen orijinal bina/yol/araç + zırh + oynanabilir flight** başarı koşulu.

## Net sıradaki somut mühendislik çıktısı
**Birinci kod işi:**  B11 `Environment_Geometry.glb` → Vita-friendly `C1L1_environment.im2map` offline exporter + indeks/bbox testleri; `C1L1_col_01`/building collision ayrımı. **İkinci kod işi:** B24 gerçek GPU model/world draw owner/viewport ve scene-loading hookup. **Üçüncü iş:** dünya colliders/spawn ve bitmiş kullanıcı testi. Bunları GPU-only ikinci oyun yerine **B24-C1 birleşik sürümün** parçaları olarak yapacağız.

## Bugünkü doğrulama ve sınırlamalar
- Gerçek GitHub arşiv ZIP central-directory incelemesi: `B11_C1L1_Scene_GLBS.zip` 860300 B, içinde `IronMan2_C1L1_Environment_Geometry.glb` 1048112 B ve `...With_MarkVI.glb` 1404904 B. `B11_C1L1_Source_Parser.zip` 1.038.815 B, 15 named C1L1 *.bdae, parser/script/geometry_manifest dosyalarını içeriyor. Bu, **paket sahipliği ve önceki decode kanıtı**, yeni cihaz çizimi anlamına GELMEZ.
- Google Drive'dan `IronMan2_B12_Original_C1L1_Texture_Atlases.zip` 7.679.708 B metadata'sı doğrulandı. Tam `Iron Man 2 iOS 3.0.ipa` 275.580.565 B metadata doğrulandı; tek-fetch >256MiB indirme sınırı devam ediyor, ama **B11/B12 eski kaynakları ilk map testi için yeterli**.
- B24 run 38436839457 tek-oyun VitaSDK SUCCESS, haritasız geliştirme VPK. B24-C1 harita+GPU içeren yeni VPK HENÜZ üretilmedi ve Vita ekranında hiç denenmedi.

## B24-C1 ilk somut uygulama sonucu (GitHub Actions kaynak audit PASS, 2026-10-13)
- Yeni `research/b24_unified/prepare_c1l1_assets.py` B11 private ZIP'lerini **gerçek CI Linux runner'ında açıp** GLB magic/version/chunk ve indeks/accessor uyumluluğunu doğruladı. `C1L1_environment.glb` ve 14 özgün `C1L1_*.bdae` görünür+collision kaynaklarını geçici iş dizinine çıkartıp SHA256 kaynak `C1L1_source_manifest.json` yazdı.
- CI run `38440619865` `https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38440619865`, job PASS. Log: **370 mesh/primitives; 37.946 accessor vertex; 22.919 indexed triangle; 14 staged model** ve `C1L1_col_01.bdae`/`C1L1_building_col.bdae`/`C1L1_floor_001.bdae` collision adayları. Eski GLB raporuyla birebir eşleşti.
- Manifest doğru olarak `gpu_renderer_integrated=false`, `original_level_spawn_decoded=false`, `c1l1_to_level1_bclara_verified=false` kaydediyor. Test **yeni Vita VPK üretmedi**, statik sahne/çarpışma kaynaklarını hazırladı; gerçek GPU çizimi ve sahne dolaşımı sonraki kapı.

## B24-C1 VPK başarıyla oluşturuldu — cihaz testi bekleniyor
- 13.10.2026: GH Actions run [38443725792](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38443725792) tamamı PASS; `IronMan2_Unified_B24_C1_VPK` artifact `11836468851`, [indirme](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38443725792/artifacts/11836468851).
- Paket: `IronMan2_Unified_B24_C1.vpk`, 13.589.692 bytes, SHA256 `027a50cbf71c379dcd8405d3dfed7b502b449cee40b34a0e85bfdd22dd918ef8`, TITLE_ID `IM2C00024` (legacy B24/B17 ayrı tutulur).
- 370 özgün GLB çevre mesh'i, 22.916 dejenere olmayan kaynak üçgeni, 1.008.320 B `maps/C1L1_environment.im2map` dosyası pakette ve runtime C1L1 map loader + renderer'e bağlandı; CI map dosyasının ZIP member byte-for-byte doğruluğunu sınadı.
- CPU render geçici yerel LOD sınırı ile çalışıyor; tamamen özgün dokular, gerçek GPU, gerçek harita çarpışması ve görev spawn/script **yok**. Vita ekranındaki görüntü ve FPS henüz test edilmedi, kaynak verisi/derleyici testi bunların kanıtı değildir.
- İlk cihaz geri bildirimi: orijinal şehir geometresi görünür mü, hangi pozisyondan açılıyor, kamera ve hareket nasıl, FPS tahmini, çökmeler var mı; screenshot/screen recording en iyi kanıt. Eğer eski kare zemin görünürse özel harita dosyası açılmadığına işaret edebilir. Çarpışma hâlâ düz B17 test semantiği.
