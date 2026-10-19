# G276–G277 — Gerçek Expo çarpışma ile özgün görev hedefinin karşılaştırılması, Vita'daki yerinde yürüme için duvar/zemin/adım nedeni gözlemi

**19 Ekim 2026. `Gh0sTRX/Iron-man-2-os` → `feature/b24-unified-gameplay`. VPK oluşturulmadı.**

## G276 — Özgün hareket hedefi, gerçek C1L1 G66C kaynağında host karşılaştırma

Özgün iOS 2010 `Mission000_OnStart` statik Lua: `MoveEntityToEntity(1062,1892,3000)`; özgün hedef `PD_IM_jump_goal`, `Num=0`, `Position1` authored ilk child1893 yerel `(-0.493,-28.062,3.705)`. Kullanıcının asıl MC sahne authored local `(-1.319,-6.747,25.054)`. **Bu iki kaynak konumundan hiçbiri doğrulanmış Vita oyuncu başlangıç *world feet* XYZ değildir.**

Yeni `g276.../test_g276_true_original_Mission000_Position1_local_vs_G66C.c`, eski G68 başarılı user-source VPK arşivini **yalnız özgün collision varlığı `assets/G66_original_collision.g66c` kaynağı için** salt-okunur kullanarak **1910 G66C triangle ve 1690 steep wall** üzerinde grounded/flight 8 yönkü küçük aday hareketleri karşılaştırır. Kaynak collision hazır değilse uydurma atlas/mesh oluşturmaz, CI fail eder; kendi başına gameplay düzeltmesi değildir. [G276 Action](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39283072821). Oluşturulduğu anda **GitHub kuyruğunda; PASS denemez**.

## G277 — gerçek oyunun biricik B14→G75 çarpışma karar zincirini *değiştirmeyen* okunur teşhis

`g277_vita_real_ground_collision_reason_counter/`:

- `b24_g277_real_c1l1_ground_reject_reasons.h` G227 opt-in koşulunda bir adet G75 son sweep sayaç özeti: `candidate_wall_reject`, `candidate_no_source_support`, `candidate_unsupported_step_height`, `candidate_accepted`, `sweep_substeps`.
- `g277_install_original_G75_wall_floor_step_reject_probe_after_G229_NO_VPK.py` yalnız **G171 bütünleşik Vita kaynak oyun derlemesi** sonrasında ve **G227/G229** gerçek G8/GPU 120-frame gözlemlerine ek olarak `work/b24/b24_unified/b24_g75_source_capsule.c` mevcut `wall_clear`, `g159_authoritative_first_native_then_source_road`, `h<z-.35/h>z+.45`, ve accepted branch noktalarına **opt-in salt-okunur sayıcı artırımı** ekler. Süpürücü hareket/duvar konumları/zemin/animasyon/Actor/GPU root dönüşümü aynıdır.
- Gerçek `work/src/main.c` 120 başarılı render frame'de `G277_GROUND_REJECTION_BREAKDOWN` satırını `G227_WALK_ROOT` ve `G229_WALK_WINDOW` yanında yazar: `wall_reject`, `missing_floor`, `step_height_reject`, `accepted`, `sweep_substeps`, `world_Zup`, `actorGPU_Zup`, `grounded`. **Ölçülen sayaç en son bir G75 sweep içindir**, tüm 120 frame toplamı değildir; yanlış yorumlanmaz. Bütün 120 frame penceresine ilişkin analog/B14/GPU root bilgisi hâlâ G229'dadır.
- `g277_test_host_wall_floor_step_diagnostic_fixture.py`: oyun dünyasıymış gibi sunulmayan *izole yapay üçgenler* ile kontrollü `no nearby floor`, `wall`, `low floor step`, `flight` değişkenleri sınanır; gerçek kaynak G75 collision kodu aynı matematiği kullanır; bu host diagnostik fixture **gerçek Vita veya Expo ilk spawn test sonucu değildir**.
- `.github/workflows/g171-2010-source-sculpture-false-wall-ground-walk-G169-full-ARM-NO-VPK.yml` mevcut tam gerçek Vita oyunu kurulumunda G227 ve G229'dan sonra G277 yükleyicisini çağıracak şekilde güncellendi. Tek `b14_world_tick`, tek `b24_g75_capsule_reconcile`, tek `b24_gpu_runtime_draw` hâlâ kalmalı. [G277 full Vita ARM ELF pipeline](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39284230476). Ayrıca [G277 isolated C11 host](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39284501192). İkisi de bu kayıt oluşturulduğunda **GitHub kuyruğunda**, henüz PASS/gerçek cihaz testleri YOK.

## User-facing kalan gerçek işler, değişmeyen sıra

1. Gerçek fiziksel Vita ya da özgün iOS runtime için `MC` ilk world feet XYZ, mevcut G229/G277 analog/world/GPU/çarpışma gerçek logu → yürüyüş kök sebebi.
2. Gerçek ground/hover/Stage2/rush geçişleri.
3. G8 tüm zırh/War Machine StateMgr ve orijinal animasyon root.
4. WeaponDB gerçek combat/melee/hit/hasar/dummy, lock-on/missile.
5. **Özgün Expo harita/ölçek + çevresel ışık, Sun001–Sun004, armor/araç/şehir shader ışığı, gölgeler, gece gökyüzü ve PNG alfa, HUD/kamera**. İş sırası değişmedi.
6. Mission000 QTE/intro/cutscene/düşman/özgün ses/bitirme.
7. 7/7 aynı-commit kaynak QA + tam Vita ARM ELF sonrasındaki **TEK VPK**, sonra fiziksel PS Vita kabul testleri.

Şu an 7 kaynak kabul aşamasının **0 tanesi tüm alt şartlarıyla tamamlanmış**. Bu bir motor çözümleme yüzdesi değildir. Kaynak kanıtının ilerlemesi, Vita'da *tam oynanabilir demo* değildir. Kesin kalan gün/yüzde objektif ölçülemiyor.
