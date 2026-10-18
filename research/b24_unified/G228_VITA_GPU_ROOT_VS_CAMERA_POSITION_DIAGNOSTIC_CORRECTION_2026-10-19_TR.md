# G228 — Vita yürüyüş telemetrisinde yanlış kamera/kök teşhisinin giderilmesi

**19 Ekim 2026 — `feature/b24-unified-gameplay` — kaynak kod düzeltmesi; VPK üretilmedi.**

## Kanıtlanan hata (G227 teşhis modülü, orijinal oyun mekaniği değil)

G227 `camera.cam_x/y` değerini `camera_target_x/y` alanına koyuyor ve bir karede kameranın dünya aktöründen `0.5` birim uzakta olmasını `WORLD_MOVES_CAMERA_DIFFERS` olarak etiketliyordu. Fakat bu iki alan **kameranın pozisyonu** için kullanılıyor, bakılan hedef için değil. Üçüncü şahıs kameranın karakterden uzakta bulunması beklenen durumdur: tek kare uzaklığından kamera lag/follow çıkarılamaz.

Daha kritik olarak, G227 bir önceki uygulamasında **GPU root ile collision-resolved world uyuşmadığında** bile sonucu kamera farkı olarak etiketliyordu; böylece tam teşhis edilmesi gereken ayrı render-transform hatası kaybolabiliyordu.

## Depoya uygulanan G228 kaynak değişikliği

- `b24_g227_vita_ground_world_render_probe.h`: `B24_G227_WORLD_MOVING_GPU_ROOT_SYNCED` ve `B24_G227_GPU_ROOT_TRANSFORM_MISMATCH` ayrı sonuçlar. `root_err = hypotf(gpu.x-resolved.x, gpu.y-resolved.y)` eşiği **0.005 geçici QA toleransıdır**, orijinal iOS hareket sabiti değildir. Kamera konumundan tek karelik takip/lag iddiası kaldırıldı.
- `test_g227_ground_world_root_qa_C11.c`: GPU root doğru iken uzak üçüncü şahıs kamerasının senaryosunu ve GPU root gerçekten yanlışken farklı kararı kapsar; önceki analog/B14/no delta/G75 collision/uçuş/NaN testleri durur.
- `g227_install_passive_real_main_Vita_world_actor_root_diagnostic.py`: logda `camera_TARGET` yerine **`camera_POSITION`**, ayrıca gerçek `camera.cam_x/y` veri sahibi yorumu bulunur.

Bu değişiklikler **oyuncu dünya konumunu, hızını, zırh boyutunu, collision alanını, G8 animasyonlarını, silahı, HUD'u, GPU draw zincirini DEĞİŞTİRMEZ.** G227 isteğe bağlı derlenen tanı mekanizmasını doğrultmak içindir. Kaynak dosyaları GitHub'da değiştirilmiştir; **bu commitlerde yeni CI/VitaSDK/PS Vita çalışma testi yapılmadı**. Önceki G227 CI başarısı G228'i otomatik olarak doğrulamaz.

## Doğrulama komutu (NO VPK)

```bash
cd research/b24_unified/g227_vita_walk_world_collision_gpu_qa
gcc -std=c11 -Wall -Wextra -Werror -pedantic -O2 -fsanitize=address,undefined test_g227_ground_world_root_qa_C11.c -lm -o /tmp/im2_g228_probe_test
/tmp/im2_g228_probe_test
```

Gerçek Vita oyununda G227 günlüklemesini etkinleştirip ölçerken ayrı olarak analog XY, B14 önerilen XY, G75 collision sonrası XY ve GPU root XY karşılaştırılmalı. Tek kare snapshot **kamera takibinin kanıtı değildir**. Bir sonraki kaynak iyileştirmesi G229'da 120 ardışık karelik kamera/dünya yer değiştirmesi ve ortam landmarkı karşılaştırması olmalıdır.

## Değişmeyen eksikler

Vita'da fiziksel kullanıcı gözlemi olan yerinde yürüme/harita hareketi, karakter-araba gerçek ölçeği, gerçek C1L1 environment ışığı/gölge/sky/ay, War Machine omuz silahları, özgün touch input/AttackType event 0–3 semantiği, melee hit frame ve Mission000 QTE/cutscene/oyun tam bölüm ilerlemesi çözülmüş değildir. Tam özgün IPA çözümünü veya cihaz QA'sını iddia etmiyoruz.
