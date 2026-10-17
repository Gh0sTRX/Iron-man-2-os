# G154 — 2010 iOS Mach-O Lua Wait native kayıt taraması: sonuç BELİRSİZ

**17 Ekim 2026 · Orijinal Iron Man 2 iOS v1.0.0 · YENİ VPK YOK**

[GitHub Actions #39040558689: SUCCESS (analiz çalıştırma)](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39040558689)

Kullanıcı orijinal 248.613.763 bayt IPA'nın içinde 7.480.208 bayt gerçek ARM Mach-O incelendi. Geçici orijinal oyun IPA'sı analiz sonunda silindi, özgün telifli veriler GitHub'a commit edilmedi.

G151 gerçek ilk görev Lua PC75–77 kodunda tam olarak `Wait(10.0)` bulundu; fakat **bu sayı için motorun kullandığı gerçek zaman birimi henüz kanıtlanmadı**.

G154, Mach-O LC_SEGMENT file↔VM haritasını ayrıştırır, özgün `Wait` C string izlerini ve bilinen doğrulanmış Lua handler VM adresleri `ShowTut 0x18818`, `IsTutConfirmed 0x187BC`, `PauseMusic 0x17ECC`, `PlayMusic 0x18000`, `PlayVoice 0x18A04` ile eşleşen *(ad pointer, native function pointer)* tablosu arar. Çalıştırma sonucu:
- `Wait` doğrudan 32-bit VM name-pointer **0 adet doğrulanmış referans**;
- Bağımsız bilinen handler çift kayıt **0**;
- Güvenilir kaynak kayıt ofseti / pointer stride **bulunamadı**;
- Native `Wait` handler adresi ve **10.0 zaman birimi çözülemedi**.

Bu **Wait native handler yok demek DEĞİL**: kaynakta isimler PC-relative addressing, farklı pointer encoding, runtime string copy, registered table generation veya başka veri konumunda olabilir. G154 ilk doğrudan 32-bit pointer tablo hipotezini kanıtlayamadı. Sonraki araştırma: orijinal `Wait` string ofsetleri ve xrefs, ARM PC-relative literal/string başlangıcı, 2010 Lua C registration setup, olası coroutine yield ve mission frame scheduling kodu, gerçek touchHLE Wait davranışı.

**G152/G153 güvenlik ilkesi korunacak:** gerçek native Wait bitiş callback'i gelmeden hiçbir sanal zamanlayıcı/otomatik onay yazılmaz, PC73→PC75 loop ve PC79 StopVoice sahte başarılı sayılmaz. G154 hiçbir mevcut Vita oyun gameplay kodunu değiştirmez, yeni VPK üretmez.
