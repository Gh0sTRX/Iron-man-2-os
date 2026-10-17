# G150 — Orijinal 2010 ilk görev PC73 Lua 5.1 EQ koşulu kesin kaynak çözümü

17 Ekim 2026 · Gh0sTRX/Iron-man-2-os · feature/b24-unified-gameplay · YENİ VPK YOK.

Başarılı orijinal iOS kaynak CI: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39039112454

Kullanıcıya ait gerçek 2010 iOS v1.0.0 248.613.763 bayt IPA, mevcut G135 tarafından doğrulanmış ephemeral Google Drive download akışıyla CI içinde açıldı, daha sonra silindi. Gerçek Level1 Mission000_OnStart fonksiyonundaki 937 Lua 5.1 bytecode instruction kaynak metadata okundu. Telifli IPA/oyun bytecode'u/metin/PCM GitHub'a yüklenmedi.

## Kesin doğrulanan orijinal Lua instruction akışı

- PC71: GETGLOBAL IsTutConfirmed. Native Lua CALL sonucu register 0'da.
- PC72: CALL, tam bir Lua dönüş değeri (C=2).
- PC73: EQ A=0, B=R0, C=gerçek kaynak sabit #35 = boolean FALSE. Kaynak kıyaslaması IsTutConfirmed() == false.
- Lua 5.1 EQ davranışı: equal(R0,false) != A olduğunda sonraki PC74 JMP komutu atlanır.
- Native IsTutConfirmed FALSE ise eşitlik TRUE, A=0: PC74 atlanır, PC75'e gidilir; PC78 gerçek JMP sBx=-8 ile PC71'e geri döner. PC75–77 içindeki bekleme native olayları henüz bu turda çalıştırılmadı.
- Native IsTutConfirmed TRUE ise eşitlik FALSE, A=0: PC74 gerçek JMP sBx=4 ile PC79'a gider. Bu, onay bekleme döngüsünden çıkış; otomatik MissionResume veya bütün ilk görevin oynandığı anlamına GELMEZ.

G149 kaynak modülü PC72 native API fonksiyonunun başarılı FALSE dönüşü ile callback başarısızlığını ayırır. G150 ise gerçek iOS PC73 koşulunun R0 vs FALSE karşılaştırmasını ve iki kesin dalı çözüyor.

G150 kaynak read-only forensics; Vita main gameplay'e otomatik branch patch yapmaz. Özgün InteractiveObj_QTE #1456 Show PC6, ShowTut(339,13,0) PC67 renderer/font/touch hook henüz eksik. G137 Lua görev motoru sırf source PC73 bulundu diye PC914 SetInputEnabled(2,true), PC927 SetInputEnabled(6,true) veya PC935 MissionResume'u çalıştırmayacak.

Sonraki kaynak adım: özgün PC75–77 bekleme/opcode'larını çözerek PC73 için fail-closed Lua evaluator, ondan sonra gerçek tek G145/G147 Vita oyunu main içine opt-in source integration ve bütün Vita ARM ELF testleri. Fiziksel Vita testi olmadan VPK üretilmedi.
