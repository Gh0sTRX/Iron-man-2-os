# Güncel kaynak cihaz testi — 28 Ekim 2026

Kullanıcı bu oturum sonunda bir test VPK'sı açıkça istedi. Bu tek tanılama
paketi, önceki yeni-VPK yasağının kapsamlı bir istisnasıdır. Yedi tam-port
kabul kapısı değiştirilmez. Kurulum veya firmware işlemi yapılmaz; özgün
kaynaklar ve VPK Git'e, herkese açık depoya veya CI çıktısına yüklenmez.

Paket kimliği: **IM2DG0001 / Iron Man 2 - Source Test / 00.02**. Asıl oyun
başlığından ayrıdır. Önceki IM2DG0001 tanılamasının yeni sürümüdür.

## Derleme ve paket doğrulama

Eski G171 üretilmiş kaynak/ELF akışı kullanılmaz. Yardımcı güncel `src/` ağacında
özgün-verili host testlerini, ASan/UBSan testlerini ve tam Vita ARM ELF derlemesini
kendisi çalıştırır; sonra SDK ile SELF/SFO üretir ve tek VPK oluşturur.
Kaynak temiz bir commit olmalıdır. Girdi ve çıktı checkout dışında tutulur.

```bash
export PATH=/workspace/im2-tools/bin:$PATH
python3 tools/device_test/build.py --diagnostic-current-state \
  --asset-root /workspace/im2-private-assets \
  --baseline-manifest /workspace/im2-current/authorized-device-test-55f3392/manifest.json \
  --output /workspace/im2-current/source-test-2026-10-28
```

Çıktı klasörü önceden mevcut olmamalıdır. Önceden doğrulanmış 669 kaynak
model/animasyon/harita/doku girdisinin dosya kümesi ve SHA256'ları karşılaştırılır.
Doğrulanmış `data/source_tables.im2d` de eklenir: toplam 670 kaynak dosya.
SDK'nin SELF/SFO çıktıları, ZIP CRC, yinelenen/güvensiz yollar, tam dosya kümesi,
tüm kaynak hash'leri ve başlık/sürüm doğrulanır. `manifest.json`, `SHA256SUMS`
ve üç derleme/test günlüğü paketle aynı dış klasöre yazılır.

Yüklenen 1.0.0 IPA, bu oturumda 32 MiB dosya aktarım sınırına takıldı ve okunmadı.
Bu paket yeni özgün ses kayıtları içermez. Dört efekt kanallı oynatma altyapısı
bulunsa da özgün efekt olayları ve fade süreleri tamamlanmış değildir. G298/G299
ışığı deneysel adaydır; özgün ışık/gölge eşliği kanıtlanmış değildir.

## Vita üzerinde test sırası

1. Asıl oyunu silme. Test VPK'sını VitaShell ile kur; **Source Test** başlığını aç.
2. Şehir, zırh, gökyüzü, doku saydamlığı ve kamerayı gözle.
3. Sol çubuğu ileri 15 saniye tut; ardından sağ/sol/geri dene. Dünyada ilerleme
   ile yerinde animasyonu ayır. Başlangıç dünya/ayak konumu hâlâ kabul bekler.
4. Yerde START → Circle: kendiliğinden kalkış olmamalı. Circle ile kalk;
   havada START → Circle: kendiliğinden iniş olmamalı.
5. Havadayken yön tuşları yukarı/aşağı, Triangle basılı rush ve sağ kamera
   çubuğunu dene. Önceki yüksek zeminden kalkış/45 cm iniş düzeltmeleri dahildir.
6. SELECT ile beş zırhı karşılaştır; Mark IV/Stealth paylaşılan animasyon bankası,
   War Machine ve Mark V'nin ayrı bankalarını gözle. R ateş, kare yakın dövüş,
   yön tuşları sağ/sol silah seçimi mevcut deneme davranışlarıdır.
7. Tekrar başlatmadan önce VitaShell ile şu dosyaları koru:
   `ux0:data/ironman2_g279_walk.csv`,
   `ux0:data/ironman2_frame_profile.csv`,
   `ux0:data/IronMan2_GPU_BOOT.txt` (oluşmuşsa).

Bu paket host/derleme doğrulamalı bir cihaz tanılamasıdır. Fiziksel Vita açılışı,
gerçek GPU görünümü, FPS, özgün görev/QTE/savaş tamamlanması test edilmedi.
