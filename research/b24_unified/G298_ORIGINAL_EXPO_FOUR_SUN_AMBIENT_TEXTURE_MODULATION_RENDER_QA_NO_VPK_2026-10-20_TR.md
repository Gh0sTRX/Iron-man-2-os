# G298 — Expo çevresel aydınlatma: gerçek VitaGL dokulu şehir çiziminde G95 ışık RGB'sini kaybetmeme

**20 Ekim 2026 · `feature/b24-unified-gameplay` · G298 kendisi yeni VPK üretmez · fiziksel Vita lighting testi yapılmadı.**

## Somut render sorunu / çözüm

Orijinal C1L1 `level1.bclara` içinde **Sun001..004** tipli dört özgün `Light` nesnesinin konumları ve ham sayısal alanları çözüldü (G30). Ancak kaynak `0xFFBEAEFF` benzeri renk, `0.3/1.0` scalar ve `0/2` light türlerinin **Gameloft 2010 shader anlamı HENÜZ kanıtlanmadı**. G95 `b24_g75_original_sun_lighting_candidate.h` bu *gerçek yerel konumları* kullanır ama yoğunluk/falloff/hemisphere ambient **deneysel** olup kaynak-Gameloft parity değildir.

Mevcut `research/b24_unified/b24_gpu_g68_city.c` G95 açıkken 31 özgün G66T RGBA atlası yüklendikten sonra yalnız *tam opak* atlas batch vertex RGB'sini tek kez CPU'da modüle eder; geometrinin XYZ/UV'si, orijinal alfa baytları ve 31 atlas korunur. Asıl çizim `glEnableClientState(GL_COLOR_ARRAY)` kullanır, ancak daha önceki renderer/HUD `GL_REPLACE` texture mode bırakırsa bu renkler **G68 dokulu sahnede tamamen görünmez**.

**G298** tam aynı G68 VitaGL rendererında yalnız `B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE` aktifken:
1. `glGetTexEnviv(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,...)` ile o ana kadarki texture mode'u saklar;
2. şehir desenli geometry/dokuları çizerken `glTexEnvi(...,GL_MODULATE)` ile özgün atlas örneklerini G95 vertex RGBA ışık rengiyle birleştirir;
3. render sonunda önceki texture mode'a dönerek sonraki **armor/HUD** geçişlerini değiştirmez.

**Yeni ışık değeri, shader, sahne nesnesi, per-frame CPU ışık döngüsü, draw call, VRAM texture ya da VPK eklenmedi**. G95 hâlâ yalnızca kaynak konumlara dayanmış deneysel statik aydınlatmadır, karakter/araç özel materyal gerçek zamanlı illumination veya shadow değildir.

## Regresyon ve gerçek düzey

`research/b24_unified/g298_expo_ambient_vitagl/` içinde gerçek `b24_gpu_g68_city.c` dosyası, yalnız **GPU çağrılarını taklit eden C host shim** ile derlenip çağrılır. Sentetik (gerçek IPA varlığı olmayan) **67323 vertex / 32 batch / 31 atlas** G66M-G66T benzeri dosya oluşturulur; ilk RGB=200,150,100, alpha=173. Tam opak atlas batch RGB'nin G95 tarafından değişmesi, kaynak RGBA alpha değerinin **bütün 67323 verteks** boyunca değişmemesi, alfa içeren atlas RGB'nin bozulmaması, G71 transparent geçişinin `GL_BLEND` açık + depth-write kapalı olması, çizim sırasında `GL_MODULATE`, ardından HUD öncesinde eski `GL_REPLACE` değerinin geri yüklenmesi doğrulanır. Gerçek oyun verisi mock dosyaya kopyalanmaz.

- [**G298 host gerçek VitaGL G68 renderer kod testi — SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39492824279). Bu bir PS Vita GPU görüntüsü değil.
- [**G298 birleştirilmiş oyun VitaSDK ARM ELF-only CI**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39492921146). Kesin sonucu GitHub Actions durumundan kontrol edin; tamamlanmadan geçti yazmayın.
- VitaGL upstream `source/vitaGL.h` GL_TEXTURE_ENV_MODE, GL_MODULATE, glTexEnvi ve glGetTexEnviv arayüzlerini bildirir: https://github.com/Rinnegatamante/vitaGL/blob/master/source/vitaGL.h

## Otomatik VPK üretimini önleyen ayrı güvenlik düzeltmesi

G298 `b24_gpu_g68_city.c` ilk source commit'i, eski **G106-VPK iş akışının `push.paths` tetikleyicisine** denk geldi; GitHub Actions eski tarihî test paketini otomatik derleyip bir özel artifact oluşturdu. **Bu kullanıcı tarafından yeni VPK talebi değildir ve dağıtım/Vita donanım testi yapılmadı.** Durum tespit edilince `.github/workflows/g106-device-feedback-alpha-sky-sun-flight-fire-test-VPK.yml` içinden otomatik `push` tetikleyici kaldırıldı, yalnız manuel `workflow_dispatch` bırakıldı ve ilk adım **G255 yedi orijinal kaynak hazır olma şartı geçmedikçe işlem başlatmayan `--require-ready` fail-closed** kontrolü eklendi. Eski artifact'i kurmayın; kullanıcı bir sonraki VPK'yı bütün sistemler hazırken **tek** pakette istiyor. Bu aşamada **7/7 kaynak gate hâlâ tamam değil**.

## Uçuş sırası ve eksikler

Ana aşama **2: Hover -> Stage2 -> Rush -> Hover** devam ediyor. Önceki G297 özgün uçuş animasyon seçiminin ikinci uydurma isabet olayı üretmesini engelledi; G298 kullanıcı isteğiyle görsel aşama 5 üzerinde **sırasını değiştirmeyen destek işi**. Yürüyüşün fiziksel Vita doğrulaması, bütünleşik kaynak orijinal mission-spawn, tam War Machine rig clip, orijinal weapon rules, gerçek Gameloft ışık shader/renk/depth/gölge, sky/moon eşlemesi, gerçek GPU karşılaştırması hâlâ **açık**.

Yeni test VPK için şart `research/b24_unified/g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json`: 7 doğrulanmış kaynak kapısının tümü açık olmalı. Bu G298 ile lighting tamamlandı sonucuna geçilmedi.
