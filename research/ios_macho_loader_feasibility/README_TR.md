# Iron Man 2 iOS ARM Mach-O -> Vita: uygulanabilirlik kapısı

**28 Ekim 2026.** Şu an kaynak ve sentetik host doğrulama aşaması. Özgün IPA üzerinde bu yeni denetim çalıştırılmadı. Yeni VPK, emülatör başlatma veya gerçek cihaz testi yok.

## Yaklaşım
Ana oyun kaynağı src/main.c ve src/b24/ korunur. Alternatif araştırma, 2010 tarihli 32-bit ARM Mach-O kodunun Vita belleğinde çalıştırılıp çalıştırılamayacağıdır. Başka Gameloft iOS oyunu için örnek: https://github.com/MetalSyntax/Zombie-Infection-vita ve başlangıç altyapısı https://github.com/MetalSyntax/ios-loader-boilerplate . Bu projelerin başarısı Iron Man 2'nin aynı yöntemle başlatılabileceği anlamına gelmez.

## Eklenen araç
tools/audit_ios_macho.py sahibin yerel, yetkili IPA'sını yalnız okur; Payload/IronMan2.app/IronMan2 üyesinin SHA-256'sını ve tüm IPA hash'ini mevcut 2010 1.0.0 referanslarıyla karşılaştırır. ARM32 Mach-O başlığı, load command sınırları, segmentlerin VM/dosya boyutları, dylib yolları, giriş ve symbol table varlığı, encryption cryptid alanlarını raporlar. Dışarı asset, IPA veya executable kaydetmez; orijinal veriyi değiştirmez. Statik önkoşullar karşılandığında bile runtime/Vita uyumluluğunu FALSE olarak raporlar.

Kullanım (IPA mutlaka repo dışında):
    python3 tools/audit_ios_macho.py --ipa /external/owner.ipa --out /external/diagnostics/macho.json

Sentetik test:
    python3 -m unittest discover -s tests -p test_ios_macho.py -v

Test ayrıca tools/test_host.sh ile CI host OFF/ON yapılarına bağlandı. Sentetik test, özgün oyun uyumluluk kanıtı değildir.

## Sonraki teknik kapılar
1. Sahibin 2010 1.0.0 IPA'sında gerçek cryptid, CPU subtype, segment ve dylib değerleri raporla. G113 eski Mach-O audit aracıyla çapraz kontrol et. Farklı sürümü sessizce doğru sayma.
2. Load/rebase/relocation, dyld binding, Objective-C mesajları, C++ constructor ve thread altyapısı için eksik importları gerçek binary üzerinde doğrula.
3. UIKit, Foundation, OpenGL ES, audio, input, dosya ve save arayüzlerini eksik/fonksiyonel/çalışır olarak ayrı ayrı sınıflandır.
4. Vita bellek sınırları, shader/texture, sahici GPU kare ve kontrol davranışı ancak gerçek Vita testiyle kanıtlanabilir.
5. Yeniden-kurma motorunun yerini ancak orijinal motorun gerçek cihazda açıldığı doğrulanırsa tartış. Şimdilik iki dal paralel; yedi pre-VPK kabul kapısı false.

Mevcut iş sırası (özgün root, flight, G8 animation, combat, orijinal lighting, mission/audio) aynen korunur.