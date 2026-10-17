# G147–G148 · Orijinal 2010 iOS QTE öğretici ve 1213 kaynak metin, PS Vita tek oyun ELF

**17 Ekim 2026 · dal `feature/b24-unified-gameplay` · Kullanıcı isteği devam et · YENİ VPK YOK**

## Önceki G145 / G146 doğrulanan kaynak zemin

G145 özgün `Mission000_OnStart` + orijinal 2010 ses kimlikleri **Music88 m_pre_cutscene_intro** ve **Voice320 vfx_intro_level1_jarvis_1** kaynak WAV→PCM ayrı Vita BGM+MAIN port iş parçacıkları tek `im2_beta` ARM oyununa bağlandı, [tam Vita ARM ELF run 39032629075 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39032629075). Gerçek 2010 `Game+0xEC` BGM ilk değer -1 kaynak senaryosu boş-müzik durdurmayı dikkatli kaynak eşdeğeri olarak ele alıyor, kaynağın tüm VoxEngine durdurma davranışı kanıtlı değil. Kaynak görev ilk `InteractiveObj_QTE` actor `Show(1456)` PC6'ya geldiğinde gerçek renderer/gesture eksik olduğundan görev duruyor.

G146 özgün `InteractiveObj_QTE` ID1456 class94, transform child1458, orijinal yerel XYZ ve quaternion değerleri, `Show` ack için gerçek renderer callback şartı [run39032970978 SUCCESS tam birleşik ARM](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39032970978). **QTE'nin gerçekten iOS'a uygun çizildiği / dokunmatik işlendiği veya tam birinci bölümün oynanabildiği kanıtlı DEĞİL.**

Bu turda ayrı alternatif G145 CI denemesi canonical mevcut G145/G146 ile çakıştığından doğrulanmış canonical pipeline korundu; gereksiz alternatif workflow ve script silindi, gereksiz başarısız CI tekrarlanmayacak.

## G147 — *gerçek* original iOS ARM öğretici UI C mantığı

Orijinal 1.0.0 ARM `IronMan2` Mach-O'dan `llvm-objdump` gerçek talimatları:

1. `ShowTut(lua_State*)` **0x18818**: Lua'dan ilk **5** tam sayı argument okur. `Mission000_OnStart` orijinal kaynağı PC67 `ShowTut(339,13,0)` (arg4/arg5 default0). İsim/metin ID339 **doğrudan ekrana basılmıyor**: `StringMgr::strIDClara2Real(int*)` VM **0xCE8CC** çağrısıyla özgün ID dönüştürülür. İkinci arg **13 - 1 = 12** olacak şekilde `GamePlayUI::ShowTutorial(int,int,int,bool,int,int)` VM **0x1E1F8** ile bağlı.
2. `GamePlayUI::ShowTutorial` ARM 0x1E210, 0x1E224, 0x1E22C/0x1E238 native UI alanlarını doldurur: çevrilmiş text index **UI+0x1E38**, tutorial türü **UI+0x1E3C**, kaynak arg3 **UI+0x1E40**. TextBox::Init ve özel UI draw dalları ayrık; font ve gerçek Vita draw henüz eşleşmiş değil.
3. `IsTutConfirmed(lua_State*)` **0x187BC–0x1880C** gerçek native kısa metodu Lua bool döndürür. `CameraMgr/GetGamePlay/GamePlayUI` üzerinden `UI+0x1E38` aktif tutorial ID alınır. Kaynak global override byte sıfırdan farklıysa **true**; değilse yalnız `UI+0x1E38 == -1` iken **true**, aksi hâlde false. Bu **kontrol sorgusu** kaynak Lua PC72 -> PC73 conditional için; tek başına `MissionResume` çağrısı DEĞİL.
4. Kod `research/b24_unified/g147_genuine_2010_tutorial_ui_gate/b24_g147_authentic_tutorial_actor.[ch]` ve host test `test_g147_original_2010_tutorial_gate.c`. Native `ShowTut` yalnız kaynak metin çeviricisi ve gerçek renderer callback başarılıysa ACK olur. `IsTutConfirmed` özgün OR mantığını izler, ama G137 düz scene event callback henüz Lua VM return value + branching desteklemediği için PC72 ve PC73'ün *canlı* akışını sahte tamamlamaz.
5. `g147_attach_original_ShowTut_And_IsTutConfirmed_to_G146_single_Vita_game_NO_VPK.py` opt-in `B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE=ON` ile canonical başarılı G146 tek B14 hareket/248 source MarkV/gerçek scene/audio Vita ELF'e bağlandı. **[G147 full ARM im2_beta ELF + tüm host regresyonları run 39037174036 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39037174036)**. Güncel native StringMgr kaynak çözümü sonrası **[G147A full ARM CI run 39037598095 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39037598095)**.

## G147A / G148 — gerçek 2010 kaynak İngilizce metinleri de çözüldü

Özgün iOS `Payload/IronMan2.app/text_english` özel 16-offset/14-name pack'i gerçek UTF-8 içerikli `u16 recordCount + (u16 byteLength, exact text)` formatında, **14 bölüm / 1213 tek tek eşleşmiş kayıt**. Bölüm sırası `about, chap1, chap10, chap2, chap3, chap4, chap5, chap6, chap7, chap8, chap9, global, init, menu`; kayıt sayıları sırasıyla `255,90,73,92,118,79,17,108,1,48,8,33,5,286` = **1213**.

Özgün native `StringMgr::strIDClara2Real` **0xCE8CC** ARM **338=339−1** değerinin `about` 255 satırını aşınca `chap1` source bölümüne ve **yerel indeks 83**'e geçtiğini doğrular. Kaynak native return `(section1 << 12) | local83 = 0x1053`. Orijinal 2010 İngilizce `chap1.english[83]` JARVIS dizgesi: **“Are you ready to face the crowd, sir?”**. G147A yeni `b24_g147_source_native_StringMgr_translate` yardımcıyı ve exact source English 0x1053 string fonksiyonunu C ile uyguladı; sahne callback bu doğrulanmış çeviriciyi kullanıyor ama gerçek oyun TextBox renderer henüz yoksa ACK etmez.

Kullanıcının özel `/mnt/data/IronMan2_G148_Original_1213_English_Text_ID_Map.zip` dosyası **ilk oyunun 1213 gerçek kaynak Lua ID ↔ native packed ID ↔ özgün İngilizce metin** CSV tablosunu içeriyor; orijinal IPA'dan model çalışma ortamında bytewise kontrolle üretildi. ZIP kaynak özel, GitHub'a 1213 telifli metin/IPA yüklenmedi. Yeniden üretilebilir IPA-only analiz scripti `research/b24_unified/g148_original_2010_english_text/g148_extract_authentic_2010_1213_Lua_Source_ID_StringMgr_pack_NO_VPK.py` repoya eklendi.

Ayrı kaynak tanıklık: orijinal birinci bölüm `chap1` metinlerinde hareket/dokunmatik/repulsor/missile/Unibeam öğreticileri bulunurken orijinal `chap2` ilk görevi `Hover up to a higher place` metni içerir. Bu, **ilk bölüm suitcase Mark V'in uçuşa kısıtlı olabileceği kullanıcı hipotezini destekleyen bağlamsal işarettir**, fakat **doğrudan runtime no-fly source capability bayrağı hâlâ çözülmedi**; bu yüzden özgün Vita kaynakta uçuş yasağını körlemesine uygulamıyoruz.

## Birebir oynanabilir ilk bölüm için kalan engeller

- Gerçek kaynak `InteractiveObj_QTE` #1456 uygun HUD/sprite/textbox çizimi ve gesture/confirmation Vita hook; bundan önce PC6 kaynak görev fail-closed.
- Gerçek `StringMgr` kaynak metin #339 native ID0x1053 ve GamePlayUI::ShowTutorial TextBox kaynak glyph/font, original English content bu turda bulundu ama ekran/GPU render yok.
- Lua source PC72 boolean return and PC73 conditional evaluator; original `ShowTut`/tutorial user input completion correct; koşullu `MissionResume`, UI2/6, stage1 MarkV yetkileri.
- Diğer görevlerde mission-specific `levelN.bclara` callbacks, entity IDs, actor state machine, enemy spawns, combat hit windows; G148 localization tüm diğer bölüm metinlerini çözmenin yöntemidir ama tüm diğer görev motorlarını otomatik çözmez.
- Kaynak render alpha sky lighting ve solid authored colliders gerçek Vita handheld testi, total game motion/camera.
- **NO NEW VPK** kullanıcı bunu tekrar istemedikçe. Kaynak ve tam Vita ARM ELF başarılarının kullanıcı üzerinde çalışan gerçek Vita demosu anlamına gelmediğini koru.
