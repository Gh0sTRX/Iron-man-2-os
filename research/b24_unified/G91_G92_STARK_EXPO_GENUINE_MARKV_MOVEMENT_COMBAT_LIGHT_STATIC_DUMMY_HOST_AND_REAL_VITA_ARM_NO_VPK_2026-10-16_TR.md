# G91–G92: Hedef sahnemiz — özgün harita, hareket/uçuş, saldırı pozları, ışık ve bir sabit dummy (VPK YOK)

Tarih: 2026-10-16. Dal `feature/b24-unified-gameplay`. Bu, kullanıcının talebi üzerine hazırlanmış **birleştirilmiş VPK'sız test sahnesidir**. Tüm kaynak iOS saldırı hasarları, isabet aktif kareleri ve düşman AI çözülmediği için tam oyunun bittiği iddia edilemez.

## G91 — Gerçek 2010 kaynaklardan çevrimdışı 3B tarayıcı önizlemesi

Kod: `g91_offline_integrated_preview/g91_build_genuine_markv_world_host_viewer.py`. GitHub Actions workflow: `.github/workflows/g91-real-2010-world-markv-motion-light-static-dummy-webgl-NO-VPK.yml`.

- Gerçek G58A/G57 özgün kaynak C1L1 Stark Expo **296 parented BRES mesh**, **22.441 kaynak üçgen**, **24 özgün PVR atlas** ve malzeme/UV görünümünü koruyan dev çevrimdışı WebGL2 harita.
- G58A sun/ambient/evening/fog host tanısal ışıklandırması; gerçek native iOS 2010 shader'ının ayrıştırılmış kesin eşdeğeri değildir.
- Gerçek IPA `suitcase.bdae`: **629 özgün Mark V weighted skin köşesi**, doğrudan özgün BRES üçgenleri, özgün köşe UV, 512×512 orijinal `MC_SuitCase.tga` PVR'den decode edilmiş kaplama. Kaynak model renklendirilmiş basit kutu değildir.
- G85'in özgün 2010 `ironman_` ANIM kanallarının Mark V'in gerçek B13 ağırlıklı rigine aktarılmış **20 Hz IM2V kaynak akışları**. Tarayıcıda hareket/nişan/uçuş /rush ve 3 ayrı `ground_combo_1/2/3` kaynak pozları. C11 `g91_export_real_g83_host_routes.c` doğrudan mevcut özgün G83 C hareket seçici fonksiyonunu çalıştırıp 40 gerçek durum kombinasyonunun animasyon adlarını sağlar; JS'de elle uydurulmuş alternatif hareket kataloğu yok.
- Bir tane yerde sabit duran neon çizgisel eğitim hedefi; gerçek iOS NPC modeli ya da düşman AI'sı değildir. Yalnızca tanısal mesafe kontrolüyle kısa sarı isabet geri bildirimi veriyor; **gerçek hit-active frame, WeaponDB hasarı, HP/ölüm, yer değiştirme veya mission tamamlanması uygulamaz**.
- Browser kontrol prototipi WASD yön, H hover, F uçuş, Shift rush, L aim, J kombo, K repulsor poz; mobil ekrandaki dört yön tuşu, oyuncuya kamera yaklaşma ve özgün BRES sun/evening/fog host kontrolleri. **Bu klavye/touch, kodun mevcut PS Vita B14 fiziği veya orijinal iOS touchHLE input semantiği değildir.** Tarayıcıda sadece hareketin görsel/animasyon bütünlüğünü kontrol ediyoruz; fizik testine Vita gerçek sürümünde geçebiliriz.

Birleştirilmiş HTML ve JSON/artifact, başarıyla üretilmiş özgün iOS haritası/animasyon varlıklarını içerir, fakat tam kullanıcı IPA dosyasını içermez. Sunucu gerektirmez: ZIP'i indirip tek `.html` dosyasını Chromium tabanlı modern tarayıcıda aç. Kaynak HTML'in kesin olarak aynı dosya olduğuna dair QA JSON bulunur.

**Gerçek CI G91B** texture ve mobil controls hazır: [38964076350](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38964076350). **G91C ayrıca Google Chrome'da WebGL2 gerçek render, GPU error, atlas yüklenmesi ve screenshot QA** adımını ekledi; 38964202375 ilk çalışmada tüm canvas/atlas GPU kontrollerinden geçti, fakat 266 ms süren gerçek `ground_combo_1` klibinin browser screenshot gecikmesinde bitmesini hatalı negatif saydığı için test koşulu yeniden düzenlendi; yeni run GitHub'da doğrulanmalı. Derleyici veya kaynak klip sorunu değildir.

## G92 — Aynı eğitim hedefi gerçek mevcut PS Vita B24 ana oyun kaynaklarına eklendi

Kod `g91_offline_integrated_preview/g92_patch_single_real_vita_main_static_dummy_NO_VPK.py`.

G75 gerçek ilk harita collider/capsule → G84 tek B14 physics + G83 hareket seçici → G85 Mark V 248/248 özgün klip → G87 orijinal kaynak zeminden doğrulanmış iniş olayları sırasından **sonra** var olan gerçek `work/src/main.c`, `b24_gpu_runtime.c` ve CMake'e **opt-in** kaynak enjekte edilir.

- Bir adet özgün G10 `b24_g10_practice_target` hedefi önce gerçek G68/G75 zemini `b24_g75_floor_crossed` ile doğrulamadan ortaya çıkarılmaz; model G10'u önceden yazılmış native VitaGL world pass içinde oynatımsız/gövdesiz, yalnız çizgisel sabit hedef olarak çizer.
- Önceden var olan G11 `b24_g11_practice_melee_hit` geri bildirimi, şimdilik orijinal iOS isabet anı çözülemeyen yerde **explicit DEBUG RANGE** içindir. Hedef ölümsüzdür; WeaponDB, düşman canı ve mission eventleri değiştirilmez.
- `B24_G92_STATIC_DUMMY_SOURCE_PREVIEW=OFF` varsayılan. ON olduğunda gerçek G75 kaynak zemin/collider, G87 transition, G85 Mark V rig ve GPU zorunluluğu CMake üzerinden doğrulanır.
- G92 yeni ikinci B14 tick, ikinci G83 timeline, ikinci G8 kaynak oyuncu/repulsor event yaratmaz.
- Native C11 host `test_g92_authored_world_static_dummy_no_damage.c` eski gerçek G10/G11 C işlevlerini kullanıp `WHIFF`, `HIT DEBUG FLASH`, cooldown, uçuşta iptal, dummy invulnerability değişmezliğini denetler.

**GERÇEK G92 ARM DERLEME / BAĞLAMA KANITI:** [GitHub Actions run 38964076412 — SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38964076412). Gerçek tam Vita kaynak `im2_beta` ELF ARM hedefi, G68/G75/G84/G85/G87/G92 ve 248 `suitcase_ironman_*.im2v` derlenip bağlandı; `vita_create_vpk` / eboot paketi veya `*.vpk` çıkarılmadı. Bu **gerçek donanımda çalıştırıldığı** iddiası değildir.

## Henüz doğrulanmamış gerçek oyun hedefleri

- G89/G90 kaynak native 0..12 combo state ID ve 8 gerçek kod bloğu çözülmüş olsa da, G92'nin tüm özgün native durum makinesini kullanıp vuruşları doğru kaynak pencere/hasarla uyguladığı **iddia edilmez**.
- 2010 gerçek melee hit-active start/end, 26 AttackEntity WeaponDB typed numeric damage, repulsor/missile/unibeam projectile collision, NPC 2010 AI/rig/hasar/ölüm, Lua misyona bağlı melee/weapon permission eksik.
- G58 host güneş/atmosferi gerçek Gameloft shader değildir; gerçek VitaGL kaynak harita ışıklandırması ve ay/gökyüzü fiziksel QA gerekiyor.
- Browser hareket WASD ve kamerası, orijinal iOS joystick/touch veya gerçek Vita B14 hareket fiziğiyle birebir eşdeğer değil. Fizik/çarpışma/yer/duvar testleri PS Vita cihazında yeni oyun sürümü oynanmadan doğrulanamaz.
- Kullanıcı yalnızca **VPK'sız önizlemeyi onayladı**, yeni VPK'yı **halen yasakladı**; release `g83_final_vpk_gate/READINESS_STATUS.json` 11 nesnel kapıdan sadece 1'i doğrulanmış: özgün 972/972 animasyon katalog kaydı.

## Devam edilmesi gereken gerçek entegrasyon

Önce G91C screenshot Chrome smoke sonucunu ve artifact'i tamamla; ardından G92 native oyunda gerçek `b24_g75_floor_crossed` çağrısı ve tek hedef koordinatlarının G68 kaynak collider'a göre hesaplanmasını ilave host testlerle QA et. Orijinal 2010 native `UpdateMeleeAttackState` 0x824/0x828 source branch graph'ı ve `AttackEntity` numeric schema'yı çıkararak G92'nin temas eylemi için kaynağa dayalı gerçek damage/hit windows elde edilene kadar **G92 debug flash'ı gerçek hasar diye değişiklik yapma**. Gerçek hardware test kullanıcı onayına bağlı; **VPK oluşturma**.
