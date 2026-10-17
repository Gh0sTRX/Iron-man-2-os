# Iron Man 2 PS Vita — G155 ilk oynanabilir odağı ve kapsam disiplini

17 Ekim 2026. Kullanıcı süreç düzeltmesini açıkça istedi: yalnız ayrıntı kazısı değil, sonuç odaklı, gerektiğinde yeni özelliklere itiraz eden ilk bölüm planı. Bu belge gelecekteki oturumlar için proje karar kaydıdır.

## Tek ürün hedefi

Orijinal C1L1/Stark Expo ilk bölümünü gerçek PS Vita üzerinde görsel, fizik, animasyon, görev ve ses ile **baştan sona oynanabilir** bir sürüm hâline getirmek. Daha fazla G-numarası ve CI başarı sayısı, kullanıcıya gösterilebilen çalışan oyun yerine geçmez.

## WIP sınırı ve bağlayıcı öncelik

**WIP=1 — aktif iş: world_render_collision_hardware_parity.** G104 kullanıcı cihaz gözleminde siyah gökyüzü, alfa pano kusuru, binaların içinden geçme, uçuş saldırısı animasyonu problemi bulundu. G106/134/136B/G153 kaynak düzeltmeleri ve tam PS Vita ARM ELF başarıları fiziki Vita regresyonu değildir. Bu nedenle harita/çarpışma/hareket bütünlüğü şu an önceliklidir.

Önce mevcut G153 birleşik renderer, world collision ve Mark V animasyonunu tek gerçek sahnede doğrulanabilir yap; gerekliyse bir tane anlamlı ve izinli Vita donanım deneme derlemesi. **Araya sırf farklı bir değişiklik test etmek için VPK sokma.** Sonra gerçek QTE1456/Vita touch HUD PC6 ve tutorial339 PC67; ancak bundan sonra G145 ses ve G149–G153 Lua bekleme zincirini özgün görev akışıyla cihazda çalıştır. Sonra PC86 sonrası, enemy/mission completion, donanım fps/çökme kabulü. Bunlardan önce ikinci görev, yeni zırh, co-op veya Iron Man 3 araştırmasına geçme.

## Gözlemlenebilir tamamlanma ve doğrulama

Kaynak özgün iOS'tan doğrulanmış olabilir ama Vita runtime'da görünmeyebilir. Host C11 mock ve VitaSDK ARM ELF derlemesi fiziksel cihazdaki gerçek çizim, ses veya FPS kanıtı değildir. Donanım sonucu belirli commit, cihaz, tarih, tekrar testi ve kaynak raporla belgelenmelidir. G155 makine okunur yedi kabul alanı: dünya görseli, çarpışma, hareket/combat, QTE/HUD, ses/olay, görev tamamlanması, cihaz performansı.

Somut koruma: first_playable_gate/first_playable_status.json ve verify_first_playable_gate.py sahte READY, eksik donanım kanıtı, kapsam atlama, paralel WIP>1 ve otomatik VPK sürüm ilanını reddeder. Bu test yeni sistemin yalnız bir parçasıdır; GitHub'ın diğer tüm eski derleme işlerini otomatik engelleyen global izin politikası değildir.

## Sonraya alınanlar

Özgün Wait(10) zaman birimi için sınırsız tersine mühendislik, 1.0.3 genel audio farkları, diğer level/rail mission mapping, ek zırh, ek silah, PSP görevleri, co-op, Iron Man 3. Bir öneri bu ilk oynanabilir hedefi geciktiriyorsa açıkça **hayır, sırası değil** yanıtı verilecek; nedeni ve hangi kabul maddesinden sonra döneceği belirtilecek.

Her çalışma sonunda dört cevap: **Hangi kullanıcıya görünen engel kalktı? Hangi ölçüm kaynak test, hangisi cihaz testi? Bir sonraki en kritik eksik ne? Yeni fikir ürünü hızlandırıyor mu yoksa dikkati mi dağıtıyor?** Yüzde ilerleme ancak gerçek ürün düzeyinde ölçülebilirse raporlanır.

Başlangıç kanıtları: G104 gerçek kullanıcı gözlemi, G106/G107 ayrımı, G153 tam Vita ELF run 39040191350, G154 native Wait araştırması kesin sonuca ulaşmadı. Yeni VPK yok.
