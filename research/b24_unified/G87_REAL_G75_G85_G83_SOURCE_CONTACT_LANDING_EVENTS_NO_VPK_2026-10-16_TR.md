# G87 — G75 gerçek C1L1 harita desteğine bağlı G83 uçuş/iniş animasyon olayları (VPK YOK)

Tarih: **2026-10-16**. Kaynak dal: `feature/b24-unified-gameplay`.

## Düzeltmenin nedeni (kanıtlanmış G84 kaynak boşluğu)

G84, G83'ün yürüyüş/hover/uçuş yön animasyonlarını G8'e geçiriyordu; ancak `g84_input.transition` değerini hiç doldurmuyor ve `g84_input.grounded_contact_verified=0` olarak sabitliyordu. Böylece doğrulanmış özgün `Ground_Float`, `Fly_Start`, `Fly_End`, `Fly2Ground` geçişleri gerçek ana döngüde hiçbir şekilde oluşmuyordu. Bu, **G83 kataloğunun varlığına rağmen oyun entegrasyonu eksiğiydi**.

## G87'de yazılan gerçek C kaynak

- `research/b24_unified/g87_source_transition_events/b24_g87_transition_events.{c,h}`: B14'ün **tek** fizik sahibinden gelen GROUND/HOVER/FLIGHT/RUSH modlarının kenar değişimini takip eder. İlk örnekte hayalî kalkış tetiklemez, paused iken state tüketmez, armor değişince sıfırlar, iki kalkış arasında eski iniş olayını iptal eder.
- `GROUND → HOVER`: G83 `GROUND_TO_HOVER`. `HOVER → FLIGHT`: G83 `FLY_START`. `FLIGHT → HOVER`: G83 `FLY_STOP`. `FLIGHT/RUSH → GROUND`: **doğrudan animasyon değil**; iniş bekleme durumuna girer. Yalnız kaynak C1L1 polygon zeminiyle doğrulanmış ayak teması görülürse `FLY_TO_GROUND` üretir; hover-only inişlerinde yanlış flight klibi uygulanmaz.
- `g87_apply_authored_collision_gated_events_to_G85_main_NO_VPK.py`: sırasıyla **G75 → G84 → G85** ile yeniden kurulmuş gerçek `work/src/main.c` ve CMake kaynaklarına G87'yi **opt-in** (`B24_G87_REAL_TRANSITION_EVENTS`, varsayılan OFF) bağlar. Tek B14 world tick, tek G83 timeline, tek G8 IM2V stream player, tek B16 repulsor ve tek melee input callsite korunur.
- `B24_G75_SOURCE_CAPSULE=ON` ise gerçek G68/G75 triangle collider üzerinde `b24_g74_near_original_floor(...)` çağrısının verdiği destek yüksekliğine, oyuncunun fizik sonrası ayak Z farkının **en fazla 0.08 kaynak birimi** olmasına ve `!world.flying` olmasına birlikte bakılır. Bu eşik **yeni emniyetli kaynak-entegrasyon adayıdır**, 2010 Gameloft iniş toleransı diye iddia edilmez. G75 source capsule devre dışıysa sahte yere temas üretilmez.

## Test kapsamı ve delil

- `test_g87_original_surface_transition.c`: kalkış, hover, stage2, rush, geri hover, gerçek zemin teması gecikmesi, pause, suit reset, yeniden kalkış ve hatalı enum rejimleri. Host GCC C11 -Wall -Wextra -Werror -pedantic.
- GitHub Actions `g87-real-original-flight-land-transition-G85-source-NO-VPK.yml`, run **38955414033**: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38955414033 .
- Aynı test gerçek önceki G8/WM/G68 ve G85 248 türetilmiş kaynak animasyon artefaktlarını yeniden birleştirir, gerçek B24 ana C kaynaklarını host syntax testinden geçirir ve **Vita ARM im2_beta** tek hedefini linklemeyi dener. `vita_create_vpk`, eboot/ALL ve cihaz kurulumu kesinlikle yapılmaz.

## Özellikle iddia edilmeyenler

G87 eski G73 VPK'sını değiştirmez. Karakterin iniş animasyonlarının gerçek PS Vita'da oynandığını, animasyonların 2010 iOS giriş semantiğini bütünüyle çözdüğümüzü veya 0.08 eşik değerinin Gameloft'un orijinal sabiti olduğunu söyleyemeyiz. WM'nin kaynakta olmayan geçişlerini Mark VI rigine zorlamıyoruz. Oyun VPK yayın kapısı: özgün aktif melee/vuruş kareleri, WeaponDB gerçek attack hasarları, düşman entity/AI, silah SFX/FX, touchHLE canlı gameplay olayları ve PS Vita donanım QA olmadan **KAPALI**.

## Sonraki mühendislik aşaması

G83/G87 hareket ve uçuş geçişlerini, G8'in tek gerçek rig oynatıcısını ve G82'nin tek kombo/aralıklı input olaylarını bozmadan sürdür; yerel orijinal Lua `SetAttackTypeEnabled`/GameState kontrollerinden doğrulanabilir combat izinleri ve `AttackEntity` aktif isabet zamanları için kanıta dayalı gerçek 2010 source çözümlemesine dön. Rakam uydurma ve VPK yapma.
