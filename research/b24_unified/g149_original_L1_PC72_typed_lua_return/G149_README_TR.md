# G149 — Gerçek Lua PC72 Boolean sonucu ve kaynak olay ACK ayrımı

17 Ekim 2026 · Iron Man 2 iOS 2010 → Vita · feature/b24-unified-gameplay · YENİ VPK YOK.

G137, gerçek Mission000_OnStart kaynak Lua PC1–PC72 çağrılarını yalnız uygulandığında başarılı sayarak PC73 ilk koşuluna kadar işler. G147 gerçek 2010 iOS IsTutConfirmed() ARM mantığını doğruladı: global_override OR GamePlayUI(+0x1E38) == -1. Native fonksiyonun false dönmesi, başarısız bir olay değil, geçerli Lua Boolean dönüşüdür. Eski protokol ise native çağrı başarı kodu ile Lua Boolean sonuç değerini ayıramıyordu.

G149 yeni b24_g149_capture_original_PC72_boolean fonksiyonunda bağımsız result_is_valid ve lua_boolean alanlarını kullanır. Gerçek kaynak ShowTut(339,13,0), packed native text ID0x1053, original UI mode12 ve renderer ACK kapıları aynen korunur. Açık tutorial için ACK+false; source override için ACK+true; orijinal UI ID=-1 için ACK+true döner. Eksik renderer, hatalı Lua opcode, PC, ID veya doğrulanmayan argüman bloklanır.

g149_integrate_typed_lua_boolean_PC72_to_G147_one_main_NO_VPK.py yalnız kanıtlanmış G145→G146→G147 tek PS Vita im2_beta oyun main'ine opt-in source gate B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE ekler. G137 PC73 Lua EQ koşulunda beklemeye devam eder. İlgili true/false değer saklanır, henüz kaynak PC73 operand/jump yürütülmez. G149, UI çizimi, doğru QTE dokunmatik onayı, uçuş yetkileri veya MissionResume yaptığını iddia etmez.

Host testleri G147 kaynak C ve G137 header ile C11 derlenir; yerel patch fixture testi tek gameplay owner korunduğunu ve tekrar patch engelini kontrol etti. GitHub Actions host C11 test akışı eklendi. Henüz bütün Vita ARM ELF veya fiziksel cihaz G149 testi yok.

Sonraki gerçek engeller: InteractiveObj_QTE1456 özgün GPU render + gesture (PC6), ShowTut339 gerçek font/HUD (PC67), Mission000 937 opcode kaynak Lua PC73 EQ operand ve branch, ardından koşullu PC914/927 input2/6 ile PC935 MissionResume. GitHub'a telifli ses, IPA, materyal veya 1213 tam metin tablosu eklenmedi. YENİ VPK YOK.
