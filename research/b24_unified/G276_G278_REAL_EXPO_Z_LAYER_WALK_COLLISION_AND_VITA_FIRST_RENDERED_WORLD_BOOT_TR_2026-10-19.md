# G276–G278 — Özgün Expo'da zemin katmanı yürüyüşü belirliyor; gerçek Vita ilk 3 render kare için B14→G66C→GPU başlangıç XYZ ölçümü

**19 Ekim 2026 · `feature/b24-unified-gameplay` · Yeni VPK yok · Fiziksel PS Vita cihaz testi yapılmadı.**

## Doğrulanmış G276/G277 test sonuçları

[**G276 SUCCESS — gerçek özgün Expo 1910 G66C triangle host testi**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39283072821). Veri kaynağı özgün ilk bölümün G68 tarihî CI paketinden salt-okunur `assets/G66_original_collision.g66c`. G275 source-authentic `Mission000_OnStart` `MC` ID1062 → `PD_IM_jump_goal` ID1892, authored `Position1` child1893 yerel `(-0.493,-28.062,3.705)` ve MC authored `(-1.319,-6.747,25.054)` test edilir. Baseline G75 authored-world **tek adım** 8 yön, gerçek cihaz/input/son oyuncu root değil.

| Kaynak XY/Z konum **hipotezi**, dünya başlangıcı kanıtı DEĞİL | Orijinal G66C yakın floor | Yerde 8 yön kabulu | Havada 8 yön kabulu |
|---|---:|---:|---:|
| Original script `PD_IM_jump_goal` ilk `Position1` **local** `(-0.493,-28.062,3.705)` | Z3.5504 | **8/8** | 8/8 |
| Orijinal MC authored **local** `(-1.319,-6.747,25.054)` | bulunmadı | **0/8** | 0/8 |
| MC XY, özgün en düşük G66C destek Z0.0725 | Z0.0725 | **0/8** | 0/8 |
| MC XY, gerçek özgün orta G66C destek Z2.82955 | Z2.8296 | **8/8** | 8/8 |

Özellikle *aynı MC XY* üzerinde Z0.0725 → Z2.82955 konum değişince 0/8 → 8/8 olması, **zemin katmanı/duvar hacmi etkileşiminin** yerinde saymaya yol açabilecek güçlü kaynak olgusu olduğunu gösterir. **Özgün iOS'da spawn 2.82955 idi** veya **Vita'da oyuncuyu Z2.82955'e taşıdık** iddiası YOK. Orijinal G66C wall715 korunuyor; rastgele ışık/geometry/teleport yapılmadı.

[**G277 standalone C11 SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39284501192) ve [**G277 tam gerçek VitaSDK ARM ELF derlemesi SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39284230476). G277 özgün biricik Vita `B14→G75→GPU` koduna sadece **read-only** `candidate_wall_reject`, `candidate_no_source_support`, `candidate_unsupported_step_height`, `candidate_accepted`, `sweep_substeps` sayaçları ekledi. G277 son collision sweep sonucu `G277_GROUND_REJECTION_BREAKDOWN` olarak her 120 gerçek **başarılı render frame'de** G227/G229 yanında çıktı verebilir. CI success fiziksel Vita cihaz çalıştırması değil; VPK yapılmadı.

## G278 — Motorun gerçekte kullanacağı ilk Vita dünya XYZ'sini teşhis etme

`research/b24_unified/g278_vita_true_rendered_world_boot_xyz_source_floor/` içinde:
- `g278_install_first_rendered_Vita_world_and_original_G66C_support_probe_NO_VPK.py`: gerçek birleşik Vita `work/src/main.c` dosyasına G277/G229/G227'den sonra **tek defalık** `B14World world; b14_world_init()` kaynak başlangıç koordinatlarını kaydetme ve **ilk 3 başarılı gerçek GPU render frame'inde** `G278_INITIAL_BOOT_WORLD` kaydı ekler: `B14_initial`, `resolved_WORLD`, `original_G66C_ready`, `near_native_floor`, `native_floor_Zup`, `GPU_actor`, `camera_player`, `grounded`, `flight_stage` ve son özgün G75 sweep wall/no-floor/step/accepted sayaçları. Çarpışma verisi hâlâ `b24_original_walls` tam 2010 original 1910 face city; `b24_g74_near_original_floor` sorgusu salt-okunur. Bu logger karakter pozisyonuna, kameraya, state, G8 veya çarpışma sonucuna yazmaz.
- `.github/workflows/g171-2010-source-sculpture-false-wall-ground-walk-G169-full-ARM-NO-VPK.yml`: zaten **gerçek VitaSDK tek oyun `im2_beta` ARM ELF (VPK yok)** oluşturan tam G171/G229/G277 akışına G278 kurulumunu son aşama olarak ekler. Tek `b14_world_tick`, tek `b24_g75_capsule_reconcile`, tek `b24_gpu_runtime_draw` sayıları korunur. `B24_G227_WALK_ROOT_DIAGNOSTIC=ON` ile logger derlenir; normal kod/GPU dışına ek bir hareket motoru konmaz.
- `g278_test_boot_probe_source_injection_unique_and_negative.py`: isolated host kaynağında tek ana kod yolunu bozmadığını, üç örnekten fazla log oluşturulmadığını, gerçek G66C değişkeni yoksa ve ikinci kez patch denendiğinde reddedildiğini test eder. [**G278 host source PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39296387038).
- [**G278 tam birleşik Vita ARM ELF CI SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39296350474): özgün tek oyun kaynak bütünleştirmesi, G277 ve G278 kurulumları geçti; VitaSDK ARM `im2_beta` derlemesi `[100%] Built target im2_beta` ile tamamlandı. **Fiziksel PS Vita cihazında ilk 3 frame ölçümü yapılmadı**, gerçek `G278_INITIAL_BOOT_WORLD` logu henüz yok; VPK YOK.

## Kalan karar

G276 aynı XY'nin farklı gerçek authored Z katmanlarında 0/8 veya 8/8 hareket ürettiğini ispatladı; G277 reddetme tipini, G278 ilk dünya/zemin/GPU XYZ'sini gerçek Vita kodunda ölçmek üzere **sadece gözlem** ekledi. Yürüyüşün gerçek Vita kullanıcı cihazında düzeldiği iddiası yok. Gerçek ilk boot logu çıktığında MC'nin asıl başlangıç konumu ve kaynak zemin arasındaki fark açıklanarak **yalnız kanıtlanmış gerçek sebep** düzeltilir.

**Kullanıcı tarafından sabit sıralama:** 1 ground MC boot→2 walk/hover/Stage2/rush→3 G8/War Machine anim→4 authentic combat/hit→**5 Expo ölçek + dört özgün Sun, çevresel/armor/araç/şehir aydınlatma, gerçek gölgeler/sky/alfa ve HUD**→6 Mission000 QTE/ses/NPC→7 aynı commit tek Vita ARM ELF + host bütünleşik QA, sonra tek VPK, cihazda gerçek test. Kaynak 7 tam kabul kapısı henüz 7/7 değil; kaynak kanıtı tamamlık yüzdesiyle oynanabilir oyun yüzdesi farklıdır.
