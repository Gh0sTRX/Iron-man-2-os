# G284–G286 — Kullanıcının PS Vita 3.74 sistem yazılımıyla gerçek Vita3K testi

Tarih: 20 Ekim 2026. Önceki G280–G283 testleri: resmî Vita3K 4206 Xvfb/Linux komut satırı ve gerçek önceki G161 VPK arşivinin varlığı başarıyla kanıtlandı; fakat emülatörde firmware olmadan açılış/oynanış doğrulanamadı.

## Kullanıcının sağladığı gerçek dosya
- Drive kaynağı: kullanıcının özel projesine gönderdiği PSP/Vita sistem dosyası; adı PSVUPDAT.PUP, **133834240 byte**.
- Başlık SCEUF (PS Vita firmware PUP); SHA-256 **6ef6dc8da6db026f28647713e473486d770087a605c52a8d751bfca7478386cf**. Hash, yalnız aynı kullanıcı tarafından gönderilen materyalin bütünlük pinidir; Sony imzasının kriptografik doğrulandığı iddia edilmez.
- Gerçek Vita3K G285 firmware çıkarım logu: **Firmware Version 0x3740000 = PS Vita 3.74**, **Build Number 571880**, **36 files**, **10→20→30→70→100%** ilerleme.
- Vita3K Main PUP kurulumu sonunda **çıkış kodu 0**; otomatik testte `os0`, `vs0`, `sa0`, `pd0` bölüm klasörleri kaydedildi.
- Kullanıcıya ait Sony PUP dosyası G284 GitHub Actions ephemeral runner klasöründe indiriliyor; kullanıcı IPA/VPK/PUP GitHub kaynak geçmişine veya sonuç artifact dosyasına konulmuyor. Bütün hassas dosyalar CI bitmeden siliniyor.
- **Ayrı font PUP henüz yüklenmedi**. Sistemin 3.74 ana PUP'u kuruldu; font ve fiziksel Vita testi hâlâ ayrı işlerdir.

## Testte fiilen yapılanlar
1. **G284** ilk gerçek firmware CLI kurulum denemesi cold-first-run `boost::filesystem::create_directories: Invalid argument`, işlem kodu `-6` hatasıyla bitmişti. Bu koşul oyunun hatası değil, Vita3K ilk kullanıcı dizini hazırlama hatasıydı. İlk GitHub run yeşil olsa bile firmware başarıyla kurulmamıştı: **olumsuz G284 koşulu açıkça kayda geçirildi**.
2. **G285** aynı pinlenmiş resmi Vita3K x86_64 Build4206 AppImage altında ilk ekran bootstrap ekledi. Firmware kurulumu gerçek G285 CI'da **başarılıdır**: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39480876371
3. G285 ardından önceki G161 VPK'yı başlatma denemesinde 10,25,45 saniyelik screenshots hâlâ Vita3K **Welcome** gösterdi. Başarı kriteri **C1L1 gameplay değil**.
4. **G286** için XDG_CONFIG_HOME / CACHE / DATA tamamen geçici özel runner içerisine kapatıldı ve G283 gerçek ekranda gözlenen Welcome/OK + eksik font uyarısı yalnız bu başlıklar varsa bir defa geçilecek şekilde yeniden kuruldu. Sonuç CI/artifact incelenmeden oyun açıldı denemez.

## GitHub kod ve sınırlamalar
- Workflow: .github/workflows/g284-user-drive-PSVUPDAT-main-firmware-existing-G161-NO-NEW-VPK.yml
- Kod: research/b24_unified/g284_user_drive_firmware/g284_install_firmware_and_probe.py
- Kullanıcı tarafından sağlanan G161 **eski VPK** kullanıldı: GitHub Actions run 39053725183, IM2G16101. **G171 / G279 güncel hareket kodu bu tarihî pakette yoktur.**
- Vita emülatörü ürün garantisi değildir: grafikler/GPU gerçek Vita'da farklı, fps ve gerçek yürüyüş doğrulanmadı.
- **Yeni VPK üretilmedi**, kaynak hareket/flight/combat/map/lighting görev sırası değiştirilmedi.

## Devam kapıları

1. Firmware ile Welcome ekranını doğru sırada tamamla.
2. Vita3K G161 game process ARM modülünü gerçekten yükledi mi? Kaynak log, gerçek GPU ekran, gerektiğinde emülatör renderer ile doğrula.
3. G161 görüntü artık geliyorsa gözlemleri yalnız eski G161'e atfet; G171 yeni yürüyüş ve G279 CSV'ye teşmil etme.
4. G171/G279 ve orijinal combat/anim/ışık/misyon iş sırası tamamlandıktan sonra **planlanan tek birleşik final VPK** → hem Vita3K hem fiziksel Vita test.

Kaynak bilgi: Vita3K desteklenen firmware kurulumunda `--firmware PSVUPDAT.PUP` CLI ve başlangıç kurulumunda ikinci font PUP gerekebileceği: https://vita3k.org/quickstart.html
