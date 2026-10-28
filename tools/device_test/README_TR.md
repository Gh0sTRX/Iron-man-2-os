# Güncel çatışma cihaz testi — 29 Ekim 2026

Kullanıcı bu oturum sonunda bir test VPK'sı açıkça istedi. Bu tek tanılama
paketi, önceki yeni-VPK yasağının kapsamlı bir istisnasıdır. Yedi tam-port
kabul kapısı değiştirilmez. Kurulum veya firmware işlemi yapılmaz; özgün
kaynaklar ve VPK Git'e, herkese açık depoya veya CI çıktısına yüklenmez.

Paket kimliği: **IM2DG0001 / Iron Man 2 - Combat Test / 00.03**. Asıl oyun
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
  --output /workspace/im2-current/combat-test-2026-10-29
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
5. R'ye basılıyken START ile duraklat. Menüde ateş/enerji tüketimi ve animasyon
   ilerlemesi olmamalı; R'yi bırakıp devam ettiğinde beklemiş bir atış olmamalı.
   Dönüş/saldırı animasyonu duraklatma süresi kadar atlamamalı.
6. Havadayken yön tuşları yukarı/aşağı, Triangle basılı rush ve sağ kamera
   çubuğunu dene. Önceki yüksek zeminden kalkış/45 cm iniş düzeltmeleri dahildir.
7. SELECT ile beş zırhı karşılaştır; Mark IV/Stealth paylaşılan animasyon bankası,
   War Machine ve Mark V'nin ayrı bankalarını gözle. R ateş, kare yakın dövüş,
   yön tuşları sağ/sol silah seçimi mevcut deneme davranışlarıdır.
8. Tekrar başlatmadan önce VitaShell ile şu dosyaları koru:
   `ux0:data/ironman2_g279_walk.csv`,
   `ux0:data/ironman2_frame_profile.csv`,
   `ux0:data/IronMan2_GPU_BOOT.txt` (oluşmuşsa).

Bu paket host/derleme doğrulamalı bir cihaz tanılamasıdır. Fiziksel Vita açılışı,
gerçek GPU görünümü, FPS, özgün görev/QTE/savaş tamamlanması test edilmedi.

## Bu oturumun doğrulanmış çıktısı

`/workspace/im2-current/source-test-2026-10-28/IronMan2_Source_Test_00.02.vpk`
94.835.736 bayt, kaynak `bccac1c`, 670 kaynak varlık.
SHA256: `b32029e2af3f7314ab66e8cb5769bdd57637bbee6960d802b3bd2b8338abe856`.
24/24 host kontrolü + 7 Mach-O birim testi ve ASan/UBSan tekrarı; tam ARM ELF,
SELF/SFO ve paket bütünlük doğrulaması geçti. Fiziksel cihaz sonucu yok.
Manifest ve bütün günlükler aynı dış dizinde. Bu paketi yeniden üretmeden koru.
Sohbet eki teslimi mevcut araçlarla doğrulanamadı; çalışma alanı yolu bir ek
indirildiği anlamına gelmez. Ağ taslağındaki GitHub API/yükleme izinleri hâlen
çalışan ortamda etkin değil. Herkese açık dağıtım yapma.

## Yeni istek: 00.03 çatışma tanılaması

Kullanıcı özgün düşman modeli bulunmadığı açıklanınca mevcut özgün Mark IV
modeliyle, açıkça etiketli **test rakibini** seçti. Özgün düşman AI'sı değildir.
Bu onayla, önceki düzeltmelerden sonra yeni **00.03 / Combat Test / IM2DG0001**
paketi hazırlanır;00.02 korunur. Başlangıç oyuncu konumu değiştirilmez.

Test rakibi doğrulanmış zemin, gövde açıklığı ve kaynak görüş hattı bulunan bir
noktaya yerleşir. Kendi canı ile oyuncunun test canı ayrıdır; görev tamamlanması,
yeni dalgalar veya özgün NPC kurtarımı iddia edilmez. Rakip sabittir, yakından
saldırır. Kaynak boşta/darbe/yakın dövüş/düşme klipleri kullanılır.

- R: seçili prototip repulsor/unibeam/füze; yön tuşları sağ/sol silah seçimi.
- Kare: desteklenen Iron Man zırhlarında yakından test hasarı.
- L+SELECT: rakibi ve test canı/enerjisini sıfırla; SELECT tek başına zırh değişimi.
- Kaynak çarpışma duvarının arkasında hedef canı azalmamalı.
- START menüsünde atış, rakip saldırısı, animasyon ve sayaçlar durmalı.
- Oyuncu veya hedef test canı bitince L+SELECT ile tekrar dene.
- Yeni yüzey aydınlatmasını zırh döndüğünde ve animasyon sırasında karşılaştır.

Füze çizgisi/işareti ve hasar sayıları prototiptir. Özgün ses bankası yoktur;
özgün düşman AI'sı, orijinal shader/gölge ve gerçek cihaz/FPS eşliği çözülmedi.
Bu sürüm önceki Mark V/iniş/duraklatma düzeltmelerini de içerir.

## Doğrulanmış00.03 çıktısı

`/workspace/im2-current/combat-test-2026-10-29/IronMan2_Combat_Test_00.03.vpk`
94.842.544 bayt; kaynak `8c0d567`; IM2DG0001/00.03/Combat Test.
SHA256 `7a6b113a7279377a1e6f46ab4494bf2f8abb938f121e0ac269dc9095ebcbe63a`.
35/35 host ve ASan/UBSan kontrolü,7 Mach-O testi,93 dosyalı ARM ELF, SELF/SFO ve
paket CRC/tam dosya kümesi/hash doğrulaması geçti. GitHub CI40780136879 başarılı.
670 özgün kaynak girdisi korunur; Mark IV modeli ve dört test animasyonu pakette.
Yerel testte güncel tanılama başlangıcından(0,5,.0725) noktasında kaynak zemin,
gövde açıklığı ve görüş hattı doğrulandı. Bu özgün senaryo başlangıcı değildir.

Kendi test canı, sabit yakın dövüş rakibi, hasar/düşme, nişangâhla aynı kamera
ışını, kaynak çarpışma engelleri, prototip atış izi/füze işareti ve L+SELECT reset
bu sürümdedir. NPC özgün düşman AI'sı değildir; aydınlatma deneysel geometrik
adaydır. Ses bankası ve yerel cihaz doğrulaması yok. Önceki dört Mark V/iniş ve
duraklatma düzeltmesi00.03'e dahildir. Manifest ve günlükler aynı dış klasördedir.
Sohbet eki teslimi hâlen doğrulanmadı; mevcut paketi tekrar üretmeden koru.
