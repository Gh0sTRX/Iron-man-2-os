# G280 — Iron Man 2 / GitHub Actions Vita3K entegrasyonu

Tarih: 20 Ekim 2026. Dal: feature/b24-unified-gameplay.

## Doğrulanmış çalışma

- Resmî Vita3K 4206 x86_64 Linux AppImage indirildi. Resmî SHA256: f3e5e93c074237b83f12a1dbd2bd728bf0616cb349a640409ea11499e3e3b001. Hash uyuşmazsa kod çalıştırılmaz.
- GitHub Actions Ubuntu 24.04 ortamında Xvfb ve Mesa ile emülatörün komut satırı gerçekten çalıştı: Vita3K v0.2.1 4206-287accff.
- [G280 başarılı orijinal gerçek CI](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39379626921). Başarılı olan emülatör yükleme/CLI testidir; oyun boot veya FPS başarısı iddia edilmiyor.
- Yeni VPK oluşturulmadı, firmware veya kullanıcıya ait iOS IPA/VPK GitHub kaynaklarına kopyalanmadı.

## Eski G161 VPK ile isteğe bağlı oyun denemesi

GitHub Actions ekranında G280 Vita3K official pinned Linux emulator CI smoke akışını aç. Run workflow seçeneğinde feature/b24-unified-gameplay dalını seç ve existing_g161_archive seçeneğini aç. Bu manuel mod geçmişte zaten oluşturulmuş G161 paketini [G161 run 39053725183](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39053725183) özel artifact arşivinden indirir, yeni bir paket DERLEMEZ.

Eski paketin eboot.bin, sce_sys/param.sfo, ZIP bütünlüğü ve IM2G16101 başlığı doğrulanır. Ardından Vita3K altında en fazla 60 saniyelik izole başlatma denenir. Deneme oyun içinde C1L1 haritası çizildiğini, G171 kaynak düzeltmesini, gerçek Vita hareketini, G279 CSV kaydını veya FPS değerini kanıtlamaz. Eski G161 VPK sonraki G279 kaynak kodunu içermez. Vita3K'nin ilk kurulum/firmware gereksinimi nedeniyle paket gerçekten açılmayabilir.

Bu modun raporu game_boot_confirmed=false, rendered_frame_confirmed=false ve hardware_tested=false gibi dürüst alanlar kullanır. Süreç 60 saniye açık kaldı diye oyun başarıyla boot edilmiş sayılmaz. Dosyalar yalnız geçici CI diskinde kalır; kullanıcıya ait VPK, IPA veya firmware geri yüklenen artifact raporunun parçası değildir.

## Kodlar ve sonraki şartlar

- .github/workflows/g280-vita3k-isolated-emulator-smoke-NO-NEW-VPK.yml
- research/b24_unified/g280_vita3k_ci/g280_prepare_pinned_vita3k.py
- research/b24_unified/g280_vita3k_ci/g280_existing_vpk_optional_probe.py
- research/b24_unified/g280_vita3k_ci/test_g280_vita3k_bootstrap_contract.py
- research/b24_unified/g280_vita3k_ci/test_g280_existing_archive_validation.py

Sonraki gerçek kabul testi için izin verilen tek bütünleşik G171/G279 güncel Vita paketi, yasal firmware, gerçek GPU gameplay ekranı, karakter konum/çarpışma doğrulaması ve son olarak gerçek PS Vita cihaz kontrolü gerekir. Emülatör gerçek donanımın yerini tam olarak tutmaz. Kullanıcının iş sırası ve özellikle sonradan gelecek gerçek ışıklandırma maddesi değiştirilmedi.

Upstream kaynaklar: https://github.com/Vita3K/Vita3K ve https://github.com/Vita3K/Vita3K-builds/releases/tag/4206
