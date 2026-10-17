# G172 — Özgün War Machine Aim_M_Ground 10 animasyonunun tek Vita motoruna kaynak-düzeyinde bağlanması

**Tarih:** 18 Ekim 2026  
**Depo/dal:** `Gh0sTRX/Iron-man-2-os` / `feature/b24-unified-gameplay`  
**Durum:** Kaynak dosyaları ve opt-in CI testi depoda; bu devir notu yazılırken CI sonucu ve fiziksel Vita testi ayrıca doğrulanmamış. **Yeni VPK hazırlanmamıştır.**

## Doğrudan doğrulanan kaynak olgu

`research/B18_COMPLETE_304_PLAYER_ANIMATIONS_CATALOG_TR.md` içindeki özgün Gameloft iOS 2010 War Machine ailesinde 10 gerçek `Warmachine_Aim_M_Ground_*` klibi vardır:

| Animasyon kökü | Normal süre (ms) | Saldırı `_Att` süresi (ms) |
| --- | ---: | ---: |
| `idle` | 1600 | 1600 |
| `move_F` | 1600 | 866 |
| `move_B` | 1600 | 1399 |
| `move_L` | 1600 | 866 |
| `move_R` | 1600 | 866 |

Önceki G83 yönlendiricisi War Machine `AIM_M_UNCLASSIFIED` durumunu hedeflenen `Aim_M_Ground` bankasına değil genel `Aim_Ground` bankasına yönlendiriyordu. Bu özgün mevcut kliplerin seçici üzerinden çağrılamaması gerçek bir kapsama eksikliğiydi.

## Değişiklikler

- `research/b24_unified/g172_native_warmachine_ground_m/b24_g172_wm_ground_m_source.h`: 10 özgün klip adı, her birinin katalog süresi, sınır kontrolü ve bilinmeyen klipte sıfır süre dönen fail-closed yardımcılar.
- `research/b24_unified/g172_native_warmachine_ground_m/g172_add_true_wm_m_ground_source_to_single_g83_NO_VPK.py`: B18 tablo satırlarını tekrar karşılaştırır; ancak önceki G165–G171 tek `work/` oyun motoru üretildikten sonra G83'ün War Machine grounded `AIM_M_UNCLASSIFIED` dalına 10 klibi kaydeder. `B24_G172_WM_NATIVE_M_GROUND_BANK` seçeneği varsayılan olarak OFF'tur. B14 hareket entegratörü ve G8/G83 tek animasyon sahibi korunur.
- `research/b24_unified/g172_native_warmachine_ground_m/test_g172_real_2010_WM_M_ground_10_clips.c`: Beş yönün normal/saldırı seçimi, özgün klip süreleri, temel ground aim, hover ve Rush regresyonları için C11 testi.
- `.github/workflows/g171-2010-source-sculpture-false-wall-ground-walk-G169-full-ARM-NO-VPK.yml`: G171 kaynak düzeltmesinden sonra G172 yaması; gerçek `.im2v` bankasında 10 dosyanın bulunması, `IM2V` başlığı/uzunluk/duration kontrolü ve **yalnız Vita ARM ELF** hedefi. VPK üretme komutu yoktur.

## Kanıt sınırları ve engeller

1. `M` uzantısının orijinal oyunda hangi silaha/2010 native input olayına karşılık geldiği **kanıtlanmadı**. Kullanıcının istediği özgün roket/omuz gatling davranışı `M` harfinden türetilip uydurulamaz.
2. Mevcut `G84` gerçek ana oyun input bağlayıcısı `AIM_HAND` durumunu yalnız eldeki port repulsor + L nişan ile seçiyor; canlı `AIM_M_UNCLASSIFIED` tetiklemesi henüz yoktur. **G172 yönlendirici genişletmesi ≠ bu 10 animasyonun fiziksel Vita'da erişilebilir olması.**
3. Real `.im2v` dosyalarının sahnede başarıyla oynatılması, doğru WM kemik/silah socket'i, silah isabet olayı, gerçek 2010 `_Att` animasyon tetik zamanı ve donanım FPS henüz doğrulanmadı.
4. G168 zırh ayak yerleşimini düzeltir ancak özgün CLARA parent world scale ile araç/karakter oranın kesin doğruluğunu kanıtlamaz. G171 yalnızca `c1l1_diaosu` görsel mesh'inin kanıtsız tamamlayıcı duvar kabulünü geri çeker; özgün iOS heykelinin fiziksel geçirgenliği kanıtı değildir. G66C gerçek kaynak authored collider bozulmaz.
5. Orijinal gece skylinesi/ay için gerçek materyal-alpha sıralaması, ışıklandırma/gölge, roket–Uni-Beam native weapon bağlamı, 13-state melee/hit window, ilk bölüm Mission000 QTE/cutscene/gerçek spawn **ayrı açık iş** olarak kalır.

## Bir sonraki kaynak-kanıtlı çalışma

Özgün iOS Mach-O attack enum/native input `AttackType`/StateDatabase ile `Aim_M` animasyon geçişi ilişkilendirilmeden oyun içi `AIM_M_UNCLASSIFIED` bind açma. Ardından touchHLE gerçek ilk bölüm karşılaştırması, gerçek WM orijinal rig/Gun01–04 eşlemesi, tek G83 akışı ve oyuncu hareket/zemin cihaz kanıtı. Entegre gerçek input kanıtı elde edilmeden yeni VPK **yok**.
