# G256 — Tek Vita test VPK öncesi mevcut oyuna gerçek Z-up grounded telemetry (read-only)

**19 Ekim 2026 · `feature/b24-unified-gameplay` · gerçek G171 kaynakta derlenen `im2_beta`, VPK YOK.**

## Neden bu gerekli?

G248/G249 özgün iOS 2010 C1L1 Expo collision üzerinde `MC` orijinal yerel XY `(-1.319,-6.747)` civarında aynı yatar koordinatlarda farklı Z katmanlarına göre **yer hareket 0/8 ↔ 8/8** değiştiğini gösterdi. G251 orijinal `SpawnPoint001,002,004` için 0/8 yer / 8/8 uçuş kaynak semptomu üretti; ama bunların orijinal `SpawnPoint` sınıfı G252 gerçek native kodunda düşman dalga çağrılarını tutar ve gerçek player spawn kanıtı değildir. 2010 `MainCharacter` load root Dünya Z değeri G254'te **henüz kanıtlı değil**. Yürüyüşü körlemesine `Z=2.82955` seviyesine taşımak orijinal geometriye aykırı olur.

## Bu turdaki gerçek Vita C kaynak değişikliği

**G227** `b24_g227_vita_ground_world_render_probe.h` içine `proposed_world_z`, `resolved_world_z`, `gpu_actor_world_z` salt-okunur yükseklikleri eklendi; orijinal C1L1'nin **Z-up** olduğunu not ettik; üç değer de `isfinite` kontrollerine eklendi.

**G227 installer** `g227_install_passive_real_main_Vita_world_actor_root_diagnostic.py`, tek `b14_world_tick` hemen ardından `world.z` kaynak teklifi ve tek gerçek `b24_gpu_runtime_draw` başarılı olduktan sonra `world.z` (G75 collision sonrası) ile `b24_gpu_rt.frame_pose.z` (GPU gerçek render actor root) okuyup **G227_WALK_ROOT** satırına `Zup_B14`, `Zup_G75`, `Zup_GPU` yazar. Aynı gerçek dünya/camera/G8/weapon owner değişmez, konum atama/teleport yok.

**G229** `b24_g229_ground_trajectory_window.h` 120 ardışık **başarılı yerde render kare** için `first_world_z,last_world_z,min_world_z,max_world_z` tutar. `g229_install_window_into_real_vita_main.py` `G229_WALK_WINDOW` logu bunları ve **son gerçek actor GPU Z** değerini ekler; eski 120-frame analog/B14-collision world-XY/GPU-root/camera position karar zinciri korunur.

**Host C11 regression** `g229/.../test_g229_ground_trajectory_window.c` içine, G249 kaynak yerel alçak `Z=0.0725` ve orta `Z=2.82955` yükselme *synthetic fixture* olarak 120 kare boyunca izlenip `first/last/min/max` doğrulanır. Bu gerçek PS Vita ölçümü değildir.

[**G256 actual G229 host source CI SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39239934085).

**Gerçek tek Vita oyun ARM ELF bütün derlemesi** `.github/workflows/g171-2010-source-sculpture-false-wall-ground-walk-G169-full-ARM-NO-VPK.yml` `g227` ve `g229` değişikliklerini restore edilen özgün kaynak/anims/sky/audio/NPC/mission, tek gerçek GPU render ve collision ile birleştirip yeniden çalıştırır, yeni VPK yapmaz. Kaynak CI run: [G256 real full Vita ARM ELF CI](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39239981629). Bu raporun oluşturulduğu anda ayrıca finale dair GitHub run status doğrulanmalıdır.

## Bütünleşik tek VPK kuralı G255 (iki faz, kilitsiz)

[**G255 gerçek source/test çift aşamalı CI SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39239447197).

- **ÖNCE** `g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json` içindeki gerçek kaynak **7/7** (original MC boot/collision, ground/flight, gerçek G8 rig/state/WM, özgün combat/WeaponDB hit/damage, source-city-scale/sky/light/HUD, Mission000 QTE/audio/enemy-wave/finish ve aynı gerçek Vita ARM ELF+host QA) tamamlanıp tek test VPK üretilir.
- **SONRA** bu test VPK Vita cihazında doğrulanır ve `g83_final_vpk_gate/READINESS_STATUS.json` **12 gameplay/hardware parity test** güncellenir. Bir VPK olmadan gerçek Vita cihazda kod çalıştırma QA zorunluluğu getirip yayın sürecini kilitleme yok.
- Şu an source preflight 0/7 tamamlanmış (ara işler var, tam gates değil), post-VPK test parity 1/12 (yalnız original 972/972 source indexed); bu rakamlar motor veya oyunun toplam yüzdesi DEĞİLDİR.

**AÇIK:** gerçek `MainCharacter` runtime spawn ve dünya-yer Z, scale versus cars, original damage/WeaponDB index mapping, full 338 player clip rig, gerçek sky/alpha, genuine Chapter1 mission/gameplay donanım testleri. Tek bir VPK oluşturulmadı; içeride yalnız gerçek Vita ELF derlemesi ve gözlem araçları var.
