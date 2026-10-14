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
