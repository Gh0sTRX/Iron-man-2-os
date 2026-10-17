# Iron Man 2 iOS → PS Vita — G161 tek donanım testi

**17 Ekim 2026 · TITLE_ID IM2G16101 · Gerçek kaynak C1L1 Stark Expo · Yalnız deneysel Vita beta**

## Kurulum
- GitHub Actions G161 çalışması SUCCESS olduğunda tek G161 VPK artefaktını indir. ZIP içindeki IronMan2_iOS_PS_Vita_G161_StarkExpo_RoadWallsSkyFlight_DeviceQA_TEST.vpk dosyasını çıkar. ZIP'in kendisini VitaShell'e VPK olarak verme.
- VitaShell ile .vpk dosyasını kur. Yaklaşık birkaç yüz MB boş alan önerilir; gerçek sıkıştırılmış dosya büyüklüğü QA JSON'dadır.
- IM2G16101 ayrı uygulama kimliği kullanır; G104/G106 önceki testleri üzerine yazılmamalıdır.
- Bu tam orijinal Iron Man 2 oyunu değil, VitaSDK homebrew bir kaynak beta sürümüdür.

## 1. Görseller: şehir, gökyüzü ve transparan materyal
- Oyun açılıyor mu? Siyah ekran, texture kaybı, hata kodu veya crash varsa ekran görüntüsü al.
- G104'e kıyasla kaynak Stark Expo yol/binalar doğru yerde mi? G73 gerçek sky hâlâ simsiyah mı?
- G71/G106 şeffaf panellerde siyah kutu, yanlış alpha ya da ışık hatası var mı?
- Mümkünse iki farklı kamera açısından fotoğraf al.

## 2. G159/G160 yol ve G156 duvar çarpışması
- Görünen gerçek yol üzerinde zırh ayakları batıyor ya da karakter aşağı düşüyor mu?
- Düz yol, köşe, yokuş/çatı yakınında yürümeyi dene. Yanlış yükseklikte zıplıyor/ışınlanıyor mu?
- Katı olması beklenen bina duvarına önce yürüyerek sonra hover/Stage2/RUSH modunda yaklaş. İçinden geçiyor mu?
- Gerçekten açık geçitten yürümek mümkün mü? Sahte engeller oluştu mu?
- Her koşulu mümkünse birkaç kez tekrarla ve kısa video çek.

## 3. Mark V Stage2/RUSH hareket ve ateş
- Yürüyüş / hover / Stage2 uçuş / RUSH ayrı çalışıyor mu? Omuz üstü kamera ve crosshair konumları doğru mu?
- Stage2 ile RUSH sırasında repulsor ateş animasyonu eski G104'ten farklı, daha doğru mu? El/kol animasyonunu mümkünse ayrı ayrı kaydet.
- Kontrollerin pause ekranını yanlışlıkla sürekli açması gibi eski hatalar tekrarlıyor mu?

## 4. FPS / kararlılık / orijinal ilk görev
- Yerde, hover'da ve RUSH sırasında yaklaşık 30'ar saniye dene. HUD varsa FPS aralığını yaz, tek bir screenshot sayısını sürekli FPS sanma.
- Kilitlenme, donma, grafik kaybı, çökme veya bellek baskısı var mı?
- Orijinal Mission000 PC6 QTE1456 native scene callback henüz doğrulanmadığı için görev ilerlemesinin bloklu kalması beklenebilir. Tam özgün bölüm bitişi veya AI burada iddia edilmiyor.
- G145 gerçek ses kaynağı, cihazda ux0:data/ironman2/audio içinde ayrı PCM dosyaları gerektirebilir; sessizliği kesin ses başarısızlığı olarak sınıflandırma.

## Tek mesajlık geri bildirim
**Açılış:** geçti/kaldı · **Gökyüzü:** geçti/kaldı · **Alpha:** geçti/kaldı · **Yol:** geçti/kaldı · **Duvar:** geçti/kaldı · **Stage2 ateş:** geçti/kaldı · **RUSH ateş:** geçti/kaldı · **FPS:** gözlenen aralık · **Crash:** var/yok.

Ekran görüntüleri veya kısa video çok yardımcı olur. Açılmazsa Vita hata kodunu ve son görünen ekranı bildir. Böylece sonraki düzeltme tek odaklı ve kanıtlı olur.

**Not:** GitHub testinin yeşil olması gerçek PS Vita'da deneyin başarılı geçtiğini göstermez. G155 ilk oynanabilir görev kabul kapısı fiziksel test yapılmadan BLOCKED kalacak. Deneysel G159 yol katılığı birebir orijinal iOS fizik kuralı olarak kanıtlanmadı.
