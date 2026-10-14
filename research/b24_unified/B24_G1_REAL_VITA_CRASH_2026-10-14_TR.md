# B24 GPU G1 — GERÇEK PS VITA CRASH RAPORU (14 EKİM 2026)

## Kullanıcı doğrudan gerçek cihaz fotoğrafı
- PS Vita ekranı, **"Iron Man 2 - GPU B24 G1"**, `C2-12828-1`, **"Saved Core File Succeeded"**; core konumu `ux0:data/psp2core-...-eboot.bin.psp2dmp`. User image reported 14 October 2026. Fotoğraf doğruluyor: **GPU G1 gerçek cihazda ÇÖKÜYOR**, oynanabilir/çalışan GPU VPK iddiası yanlıştır.
- G1 title `IM2G00026`, GitHub CI `38536434628`, actual VPK SHA256 `0b24bcd7d214a78370789677782d3766787f431652fa025aabeeb64adcde1328`. CI derleme başarısı sadece SDK build; Vita runtime crash doğrulandı.
- Bu fotoğraf G2 değildir. `IM2G00027` G2 gerçek cihaz sonucu **bilinmiyor**; G2'yi başarılı/başarısız sayma.
- Crash yeri (PC/LR/DFAR), VitaGL init vs GPU frame vs SDL input **bilinmiyor**. Görsel başlangıç zamanını tam göstermiyor; yalnız title/crash/core kaydı. `libshacccg.suprx` gereksinimi vitaGL upstream README tarafından doğrulandı ama konsoldaki varlığı/yokluğu **kontrol edilmedi**; bu da yalnız bir hipotez.

## Kesin bulunmuş farklı kaynak hatası (G2 uçuş, doğrudan G1 crash sebebi değildir)
G2 kodu `b24_gpu_runtime_draw` içinde `frame_pose.pitch,frame_pose.roll` atıyor fakat `b24_runtime_armor_draw` callback'i `B24GpuSuitPose` struct'ına yalnız dört eski alanı kopyalıyordu. C aggregate geri kalanları sıfırlıyor. **Bu nedenle G2 görsel Stage2/RUSH pitch/bank pose'un gerçek GPU modeli üzerine hiç ulaşmaması kesindi**. `research/b24_unified/b24_gpu_runtime.c` içinde altı alanla source fix yapıldı, CI regresyon bekleniyor. Bu G1 exception kaynağına kanıt değildir.

## Yeni opsiyonel boot breadcrumb altyapısı
- `b24_gpu_boot_trace.[ch]`: yalnız `-DB24_ENABLE_GPU_BOOT_TRACE=ON` olduğunda `ux0:data/IronMan2_GPU_BOOT.txt` dosyasına kapanıp flush edilen aşama kayıtları (SDL init, model load, C1G2, C1UV/C1MA, VGL init, ilk scene/armor/HUD/swap).
- GPU mode normalde trace OFF; eski B17 ve G1/G2 paketleri geriye dönük değişmez. Bu **gelecek debug build** için hazırlanmıştır; mevcut crash için dosya yoktur.
- Diagnostic trace savunmacıdır: çekirdek `.psp2dmp` kadar detaylı değildir ve tek başına exception PC'sini söyleyemez. **Do not blindly ship new VPKs without actual G1 dump analysis or clear test-purpose approval**.
- 14 Oct Source-only CI `b24-audit-only.yml` source/regression/real VitaSDK object compilation scheduled. Link/runtime/device success ayrı ele alınacak.

## Kullanıcıdan gerekli dosya
VitaShell → `ux0:/data/` → fotoğrafta adı görülen `psp2core-...eboot.bin.psp2dmp` dosyasını USB/FTP ile PC'ye kopyalayıp ChatGPT'ye **dosya olarak yükle**. Diğer eski crash dump ile karıştırma; dosya tarihini kontrol et. VitaDB Downloader/VitaGL kullanan başka uygulama mevcut mu ve `ur0:data/libshacccg.suprx` / `ux0:data/libshacccg.suprx` var mı sorulabilir; eksik olduğunu varsayma.

### Sonraki teknik işlem
- `TibixDev/vita-crashdump` veya `xyzz/vita-parse-core` ile Vita core içindeki thread PC/LR/DFAR stop reason incele. G1 aynı kaynak commit `cb8d76e46c61919e3a92eb98f7579e92130011d8` için unstripped VitaSDK `.elf` gerekir (G1 CI normal artifact içinde sadece .vpk sağladı; dump olmadan adres uydurma).
- Eğer PC vitaGL/SceShaccCg içindeyse runtime/shader dependency/GL state, `main` içindeyse SDL/no-video init ya da original suit load, upload ise texture/vertex pointers; bunu **dump kanıtıyla** ayır.
- O zamana kadar G1/G2'yi `hardware verified playable` diye sunma. Mevcut B15/B17 ve başarısız C2 fotoğrafları tarihsel referans olarak sakla.

## 14 Ekim 2026 — Kullanıcı 6 CORE dosyası yükledi, G1 iki kez birebir aynı hatayı verdi
- Dosyalar gzip açıldı, ELF32 ARM `PT_NOTE` / `MODULE_INFO`, `THREAD_INFO`, `THREAD_REG_INFO` yapıları bağımsız çıkarıldı (Sony Vita formatı, topluluk parser offsetleriyle kontrol).
- **G1 doğrulandı:** `psp2core-1791971340-0x0001a23c7b-eboot.bin.psp2dmp` ve `psp2core-1791971369-0x0001812d2d-eboot.bin.psp2dmp` içindeki ana thread **`IM2G00026`**. İKİSİNDE DE ÇÖKEN `vitaGL Splashscreen` thread, **Data abort `0x00030004`**, `PC=0xE00ADF88` = **`SceGxm@1+0x1E638`**, `DFAR=0xFFFFFFFF`, `DFSR=0x000008F5`, `r1=0xFFFFFFFF`, `lr=0x00000001`. İki dökümün tüm GPR, SP/LR/PC/DFAR değerleri birebir eşit. G1 ana thread **`SceLibKernel@1+0x6854`** PC `0xE000E824` stop reason 0; vitaGL GC başka bir bekleyen thread. **Hata oyun oynanışı yerine ayrı vitaGL splash thread'i / SceGxm codepath.**
- G1 dump modül listesi `SceShaccCg` modülünü içeriyor; shader derleyicisi modülünün tamamen eksik olmasına dair önceki varsayım artık desteklenmiyor. Shader sürümü veya initialization uyumsuzluğu yine açık.
- Diğer 4 yükleme G1 DEĞİL: 3 `vitaos` (`store` thread, undefined instruction `0x00030002`) ve 1 `BetterHomebrewBrowser` eski eksik `.tmp`. Bu dökümler G1'e karıştırılmamalı.
- Gerçek upstream `Rinnegatamante/vitaGL` `source/splashscreen.c` içinde `sceKernelCreateThread("vitaGL Splashscreen",...)` kullanıyor; `source/vgl.c` içindeki `invoke_splashscreen()` tam olarak `#ifndef SKIP_SPLASHSCREEN` koşulu altında. Resmî Makefile `NO_SPLASHSCREEN=1` => `-DSKIP_SPLASHSCREEN`. Dolayısıyla **statik libvitaGL yeniden derlenerek splash thread yok etmek** en hedefli workaround. Sadece ana oyun C dosyasına makro yazmak yeterli değil.
- Yeni `.github/workflows/b24-gpu-nosplash-candidate-g3.yml` gerçek B24 gameplay hedefini pinned upstream VitaGL commit `a85cb8d0a8d0ed5b9d8f6acdebab5b37cef8a9da` + `NO_SPLASHSCREEN=1` ile linkleyerek **G3 `IM2G00028`** yalıtılmış GPU adayı üretmek için başlatıldı; `B24_ENABLE_GPU_BOOT_TRACE=ON`, G2 altı-alanlı armor pose fix de dahil. CI run `38547766577`: durum kontrol edilmeden başarılı deme. Eski G1/G2'nin SHA/kimlikleri korunacak. Vita gerçek açılış/FPS onayı yine gerekli.
- Kullanıcı dump ham içeriği TTY ve çalışma belleği taşıdığı için **GitHub'a yüklenmedi**, yalnız bu metadata/analiz aktarıldı. G1 neredeyse kesin splash bug tetikleniyor ama SceGxm'in içindeki ilk kötü parametrenin tam kaynağı doğrulanmış değil.
