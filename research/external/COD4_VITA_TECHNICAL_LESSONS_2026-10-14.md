# COD4 Vita -> Iron Man 2 PS Vita: teknik aktarım ve doğrulama planı
**Tarih:** 2026-10-14 (Europe/Istanbul)
**Durum:** harici açık kaynak araştırma notu; **Iron Man 2'ye kod/optimizasyon UYGULANDI anlamına gelmez**.
**Kullanıcı talebi:** COD4 Vita'dan öğrenilebilecek somut GPU, CPU, belleğe yerleşim, paketleme, render ve doğrulama yöntemlerini Iron Man 2 B24 unified projesinde ileriki sohbetlerde aktif olarak öner. Bu referansı PROJECT_HANDOFF.md üzerinden her devam oturumunda bul. VPK otomatik üretme; kullanıcı tarafından raporlanan gerçek Vita sonuçlarını daima öncelikli al.

## Kaynakların ayrı kimlikleri; FPS iddialarını birbirine karıştırma
1. **JarvisUltronSlop/cod4-vita — orijinal COD4 offline multiplayer Shipment portu:** https://github.com/JarvisUltronSlop/cod4-vita ; kamuya sunulan kaynak (2026-10-03), son repo commit e9ef7f16220a68cd0ef9a36fdbafee0afb97feb9 (2026-10-03). Ana README https://github.com/JarvisUltronSlop/cod4-vita/blob/main/README.md ; durum devri https://github.com/JarvisUltronSlop/cod4-vita/blob/main/docs/STATUS.md ; derleme https://github.com/JarvisUltronSlop/cod4-vita/blob/main/BUILDING.md ; lisans https://github.com/JarvisUltronSlop/cod4-vita/blob/main/THIRD_PARTY.md . Gerçek donanımda tarihsel ~10 FPS; son yayınlanan run91/Shipment recovery yapılandırması fiziksel olarak nitelendirilmedi. 30 FPS iddia **etmiyor**. Temel hedef **offline FFA/Shipment**, kampanya ve online kapsam dışı.
2. **Başka geliştiricinin 2026-10-09 performans gönderisi:** https://www.reddit.com/r/VitaPiracy/comments/1x1wmra/cod4_on_vita_update_optimization/ . Bu geliştirici kendi değişiklikleriyle Shipment'ta **27–30 FPS** bildirdi; bu iddia BİR GELİŞTİRİCİNİN BEYANI, bağımsız tekrarlanmış donanım benchmark'ı ya da yukarıdaki GitHub main dalının FPS'si değildir. Açıklaması: çözünürlüğü önceki sürümün yaklaşık yarısına indirmek; dünya ve silah için iki ayrı yüksek maliyetli çözünürlük/render katmanı yerine aynı çözünürlükte çizim; CPU/GPU asset/memory optimizasyonları; en yüksek overclock hızlarını varsayan profil. Geliştiriciler birleşik depo düşüncesi konuşmuş, ancak 2026-10-14 itibarıyla bu optimize kodun özgün repoya entegre edildiği doğrulanmadı. Kullanıcının izlediği özgün YouTube demosu https://youtu.be/A08zMfo94Nk ; **videodan güvenilir FPS okunamadı**.
3. **Farklı kapsamda ayrı COD4 Vita campaign kanıtı:** https://github.com/NDRWhun/COD4VITA ; native sceGxm, offline shader conversion (README 609 shader iddiası); halen kararsız/oynanamaz ve CPU/memory sorunları bildiriliyor. Bunu Jarvis multiplayer deposu veya optimize Reddit sürümüyle karıştırma. Potansiyel alternatif teknik referanstır, doğrudan başarı kanıtı değildir.

## Jarvis repo'da doğrulanabilen mimari
- KisakCOD kaynak C++ oyun mantığını PS Vita'ya uyarlama: kaynak dosyalar `kisakcod/src/vita/vita_source_session.cpp`, `vita_source_registry.cpp`, `vita_script_services.cpp`; yerel döngüsel sunucu/istemci mesajları, silah ve oyuncu durumu, oyun mantığı.
- `kisakcod/src/gfx_vita`: VitaGL grafik yolu. Yayınlanan candidate: **world 720x408 Balanced**; **weapon/HUD 960x544**; basit dünya ışıkları, stok saatler. Bu orijinal repodaki seçenektir. Ayrı Reddit optimize edicisi bunun aksine ayrık silah/world render maliyetini azaltmayı anlattı; farklı revizyonlardır.
- `kisakcod/tools/vita_asset_prep`, `tools/prepare_owned_content.py`, `prepare-owned-content.ps1`: özgün sahibi olunan English Steam COD4 2007 dosyalarından offline exporter ve paket dönüştürme. Engine VPK, oyun verisi `ux0:data/CODVIT001` altında ayrı.
- **KVAP**: sabit-genişlik, pointersız serialize edilmiş kayıtlar; chunk CRC; common + harita paketlerinin sürüm/generation uyumu. Cihazda header/TOC/size/CRC ve short-read tanısı; PC host readback PASS fiziksel Vita decode PASS değildir. Yayınlanan adayda typed asset decode öncesi hata kalmış.
- Shipment texture **resident**, büyük haritalarda deneysel sayfalama; bounded texture index, immutable model index paylaşımı, lease/backing storage, allocation pressure recovery; menü/font/buton texture'ları teardown sonrasında korunacak.
- `kisakcod/tests/vita_portable` + Python tests: parser/allocator/renderer policy/lifetime/failure handling; Vita gerçek FPS ve sorunsuz load/exit/reload ayrıca test edilecek.
- Açık kaynak motor GPLv3, orijinal ticari COD4 asset ve Sony modüller depoda yok. **Yöntemi incelemek serbest; kaynak kodu kopyalamak GPLv3 uyumu ve dağıtım yükümlülükleri analizi gerektirir.** Iron Man 2 özel repo orijinal IPA materyalleri içerdiği için kaynakların yayımlanması ve hukuki kapsamı ayrıca değerlendirilmeli. Tercih: yöntemlerden bağımsız uygulama.

## Iron Man 2 B24'e somut transfer hipotezleri — uygulanmış özellik DEĞİL
**Ön koşul/hard blocker:** `PROJECT_HANDOFF.md` en güncel durumunu izle: B24-C2 gerçek cihazda ~12–14 FPS, yanlış render, tüm tuşlar pause; G1 gerçek cihazda C2-12828-1 crash/core dump; G2 derleme başarılı ama Vita'da henüz doğrulanmadı. G1 orijinal `ux0:data/psp2core-...eboot.bin.psp2dmp` ve debug sembolleriyle crash triage öncelikli. COD4 teknik bulguları herhangi bir G1 crash nedeni için delil değildir. Yeni paket veya çalışan oyun iddiası ÜRETME.

### P0 — Önce mevcut GPU sürümünü gerçek cihazda doğrula
- G1 core dump: gerçek PC/LR/exception/DFAR, link-adres rekonsiliasyonu ve evre trace'i; hipotezle gerçek nedeni karıştırma.
- G2/B24 tek oyun yolu; hiçbiri test edilmeyen GPU kodu 'çalışıyor' kabul edilmesin. B17 hareket kazanımları B24 içinde korunsun. Ayrı boş GPU demo B24 önceliğini bölmesin.
- Kullanıcının her tuş pause hatası kaynakta START-only korumasıyla ele alındı, ancak yeni cihaz testi olmadan kapatıldı deme.

### P1 — Ölçümlü GPU performansı ve render mimarisi
- Dünya, orijinal zırh, VFX, skybox, HUD için ayrı CPU update/render submission ve GPU frame toplamını gerçek frame interval ve wait/swap süreleriyle ölç. 30 FPS = **33.33 ms toplam frame budget**; 60 FPS = 16.67 ms, hedef/dilek değil ölçüm. VSync/LCD FPS, game tick, application submitted/completed frame, shader cost ve asset-load stutter ayrıştır.
- **A/B matrisini** oluştur: native 960x544 vs yaklaşık 720x408 3D sahne; 3D zırh/world aynı dünya çözünürlüğü vs zorunlu iki ayrı 3D pass; HUD için ayrı düşük maliyetli native-çözünürlük 2D kompozisyon; texture filtreleme ve FBO maliyeti. HUD'ı blur yapmadan GPU masrafını azaltmayı hedefle. COD4 Reddit 'tek çözünürlük' mimarisini birebir alıp oyun hud'unu rastgele küçültme.
- B24 sahnesi için draw-call/material state batch, original texture-atlas binding, visibility/frustum/distance culling, sahne materyal anahtarları, tekrar eden verinin kopyasını önle; performansı ölçmeden 'FPS +X' vaat etme. B24 94 materyal etiketi/22,919 indexed C1L1 triangle gerçek diffuse texture bağlandığı kanıtı **değil**; B12 atlas G2'ye dahil değil. Önce doğru UV/material ve GPU texture sağlamlaştır, sonra kalite/perf değiştir.
- Zırh animasyonlarında orijinal 304 katalog vs gerçek baked 59 ayrımını koru; CPU mesh rebuild/skin yerine ölçülü GPU-friendly rig/skinning, cache ve gerekirse level of detail dene. GPU "bütün CPU işlerini üstlensin" değil; CPU gameplay, animasyon state, culling, kaynak yönetimi ve submit; GPU çizim/uygun işler.

### P2 — Paketlerin bütünlüğü, belleğe yerleşim ve hata kurtarma
- Modeller/texture/animasyonları portable pointer-free offline formatta hazırlamayı değerlendir; küçük test seviyesinde stable packed payload + layout manifest, map/armor/atlas **aynı generation**. CRC, declared vs actual size, header/TOC and endian alignment checks, I/O short-read breadcrumbs, typed parser diagnostics.
- Menü font/HUD/icon tekrar açıldığında yaşasın; mission reload/exit/gpu-context yeniden kurma sonrasında leak/double-free ve stale GPU handles testleri.
- Küçük C1L1 mission atlas ve temel zırh bankını mümkünse memory-resident, ihtiyaç dışı/uzak varlıkları gerektiğinde lazy/stream; stok bellek bütçesi ve fiziksel Vita memory peaks ölçülmeden her texture'ı zorla resident yapma.
- CPU staging ve GPU vertex/index buffers ayır; immutable model geometry paylaş, bounded allocation ve açık reclaim planı kullan. "Paket hazırlanıyor / fiziksel yükleniyor / çiziliyor" ayrı test aşamaları.

### P3 — Reprodüksiyon ve CI/gerçek donanım QA
- Host fixtures: input START-only, analog, camera, weapon switch; crash-safe boot phases; typed asset deserialization CRC mismatch, pack-generation mismatch, missing texture, OOM, bad length/endian, exit/reload, double asset-reference tests. Native VitaSDK smoke builds + CI **gerçek cihaz testi değildir**.
- Test manifest: commit sha, IPA kaynak sürümü, converter version, build config, title ID, B24 branch, map and armor packs' SHA256/CRC, GPU resolution, clocks, screenshot, action path, FPS frame-time p50/p95 and memory peak, fail gate/log. Önce G1 core ve G2 eksik gerçek cihaz geribildirimini çöz.
- 27–30FPS dış iddiasını sadece fikir kaynağı olarak kullan, başka donanım/clock/çözünürlükte **Iron Man 2 FPS tahmini yapma**.

## Önceliklendirilmiş kısa backlog — sonraki Iron Man 2 sohbeti için
1. **G1 çökme delili** ve mevcut B24-G2 fiziksel sonuçlarını `PROJECT_HANDOFF.md`nin son kayıtlarından oku. Kod/trace/CI başarılarını gerçek cihaz sonucu sanma.
2. Güncel B24 renderer'ı ve GPU suit/HUD kodunu gerçek dosyalarda incele; bottleneck için ölçüm ekle (frame presentation, CPU update, command submit, GPU waits, texture upload, draw batches).
3. Güvenilir B24-GPU çalışınca karşılaştırmalı low-res world / native HUD / unified world+armor 3D pass testini uygula; A/B'de görsel sadakat ve frame interval logla.
4. C1L1 gerçek atlas/material/UV bağlantısını tamamla; kaliteyi sadece hızlı olsun diye feda etme.
5. Offline asset exporter + typed validation + package generation integrity yöntemleri için prototip ve host testleri; doğrudan KVAP kodunu kopyalama.
6. Reload/leak/OOM/texture residency, uygun shader ve animation bank optimizasyonlarını gerçek ölçüme bağlı uygula.
7. Sonraki sohbette **gerekçeli öneri + aday kod değişimi + test beklentisi + tamamlandı/taslak/cihaz doğrulandı ayrımı** ile ilerle; user requests may override priority.

## Link kılavuzu ve erişim
- Original repo: https://github.com/JarvisUltronSlop/cod4-vita
- Original handoff: https://github.com/JarvisUltronSlop/cod4-vita/blob/main/docs/STATUS.md
- Original README: https://github.com/JarvisUltronSlop/cod4-vita/blob/main/README.md
- Original build: https://github.com/JarvisUltronSlop/cod4-vita/blob/main/BUILDING.md
- Original source example: https://github.com/JarvisUltronSlop/cod4-vita/blob/main/kisakcod/src/vita/vita_source_session.cpp
- 27–30 FPS external developer claim and rationale: https://www.reddit.com/r/VitaPiracy/comments/1x1wmra/cod4_on_vita_update_optimization/
- Historical original demo: https://youtu.be/A08zMfo94Nk
- Separate sceGxm campaign R&D: https://github.com/NDRWhun/COD4VITA

**Handoff instruction:** Bu dokümandaki teknik bilgileri sonraki sohbetlerde kullan; sohbetler arası otomatik insan-benzeri hafızaya güvenme, repodaki bu kalıcı notu oku; kullanıcı başka bir şey istemedikçe geliştirme odağı mevcut B24 birleşik oyun ve gerçek Vita kanıtları olsun.
