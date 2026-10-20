# G297 — 2. aşamaya geçiş: Stage 2 / Rush özgün uçuş animasyonuna hayalî hit olayı bağlama (NO VPK)

**20 Ekim 2026; dal:** `feature/b24-unified-gameplay`.

## Kısa konum

1. **Ground:** G171 gerçek B14 → özgün Expo G66C/G75 host yürüme testi geçmiş; G277/278/279/296 gerçek Vita koduna ilk render-frame, 120-kare çarpışma/zemin/GPU/joypad gözlemcisi bağlı. **Eski G161 PS Vita'da yürüyüş yerinde sayıyordu, G171/G296 gerçek Vita cihazında denenmedi; yürüyüş tamam değildir.** Device gate açık kalır.
2. **Flight:** B14 uçuş fizik hareketi ile G83 özgün 2010 `ironman_ironman_fly_f/b/l/r`, `fly_ftol/ftor/ltof/rtof`, `fly_f_rush` ve Stage1 hover klipleri source-only şekilde mevcut; G248/G249 8-yön kaynak çevre/çarpışma regresyonunda uçuş test edildi. **Orijinal iOS input/permission semantiği ve gerçek Vita flight rendering henüz doğrulanmadı.**
3. **Animations/combat:** G8 klip akışı, G82 combo/önceki accepted B16 repulsor event ayrı sahipler; War Machine ve Uni-Beam bazı özgün kaynak bağları var ama tüm cihaz çıktısı doğrulanmamıştır.
4. **Map/lighting, mission/sound:** Henüz tamamlanmamıştır. Expo'da özgün lighting, ambient, shadows, sky, alpha, hero/car scale ve HUD gerekli, atlanamaz.

## G297 gerçek C dosyası düzeltmesi

`research/b24_unified/g83_full_motion_aim/b24_g83_unified_movement_aim.c` içindeki `b24_g83_select_original_motion()` önce, `accepted_weapon_event` girdisi bir uçuş, Rush, transition veya desteklenmeyen rig kaydına rastlasa da **`needs_2010_hit_event = fire`** işaretliyordu. Oysa G83 aynı dalda uygun hit/ateş animasyonunu **hiç seçmiyordu**. Bu yalnızca bir kaynak animasyonu yönlendirmesidir; ikinci bir gerçek vurma olayı çıkarmak için kanıt değildir.

G297 bu isteği artık yalnız **gerçekte kaynak `stem` seçilmiş, geçiş olmayan, ground/hover, aim açık ve kabul edilmiş fire** durumuyla sınırlar. Gerçek combo G82 kendi önceki önceliğiyle `needs_2010_hit_event` set edebilir. **B16 gerçek silah olayı/damage sistemi değiştirilmedi, Stage2/Rush ateşinin özgün iOS koşulları keşfedilmiş gibi yapılmadı, uydurma mühimmat/anim/hit eklenmedi.**

`test_g83_original_movement_aim_combat.c` ile flight forward, Rush, F→L kaynak yön animasyonu, dodge için **hayalî ikinci hit işareti yok**; yer aim-fire için mevcut işaret korunuyor; bütün özgün locomotion/War Machine/Mech combat testleri çalışıyor.

**Kaynak host özgün G83 test CI başarılı:** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39489660777

**G297 tüm oyun VitaSDK ARM ELF-only / G171 kaynak CI:** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39489741248 (son çalışma sonucunu GitHub Actions üzerinden doğrula; sonuç kontrol edilmeden SUCCESS yazma).

## Sıradaki somut çalışma

- Flight state giriş/çıkışı ve gerçek GPU root/clip bağları ile Stage1→Stage2→Rush→hover yolunun kaynak ve sonra PS Vita çalışmasını doğrula; G106 `fly_att_s` ile B16 repulsor ilişkisinin **deneysel** olduğu korunmalı, özgün native weapon ID çözülmeden kesinleştirme.
- G296 kullanıcının gerçek cihaz G279 telemetrisini bekler; aynı şüpheli G66C duvarını sürekli değiştirip sahte çözüm üretme.
- Sonraki aşamalar sırası değişmez: özgün G8/War Machine anim, combat, **orijinal Expo aydınlatma/gölge/sky/alpha**, görev/audio/NPC, sonra 7/7 kaynak gate + tek VPK.

**Agentların okumaları:** `AGENTS.md`, `CLAUDE.md`, `research/b24_unified/G296_REAL_ORIGINAL_G66C_WALK120_FLOOR_SAMPLE_CI_AND_CLAUDE_CODE_HANDOFF_2026-10-20_TR.md`. G295 default GitHub Vita3K host Vulkan exception aynı ortamda yineleme.
