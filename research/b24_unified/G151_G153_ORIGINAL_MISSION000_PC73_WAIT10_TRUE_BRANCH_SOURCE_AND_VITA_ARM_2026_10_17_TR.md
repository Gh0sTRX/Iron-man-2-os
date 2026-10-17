# G151–G153: Iron Man 2 iOS 2010 ilk görev, gerçek Lua öğretici bekleme döngüsü

**17 Ekim 2026 · Gh0sTRX/Iron-man-2-os · feature/b24-unified-gameplay · YENİ VPK YOK.**

## Kaynağa dayalı G151 gerçek bytecode çözümü

G150 orijinal iOS 2010 Level1 Mission000_OnStart 937 Lua5.1 komutundaki PC73 EQ R0 ile sabit false karşılaştırmasını ve PC74/78 dallarını doğrulamıştı. G151 aynı kullanıcı 1.0.0 IPA'sını GitHub CI'da geçici olarak açıp PC68–85 özgün talimat metadata'sını yeniden kanıtladı. **[G151 Actions SUCCESS #39039625630](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39039625630).**

| Özgün Lua PC | 2010 asıl bytecode ve argument | Semantik |
|---|---|---|
| 68–70 | GETGLOBAL PlayVoice / LOADK 320 / CALL | Önceki JARVIS ses oynatımı |
| 71–72 | GETGLOBAL IsTutConfirmed / CALL (1 dönüş, R0) | Öğretici onay durumunu sorgula |
| 73 | EQ A0, B R0, C K35 = false | Onay verilmedi mi? |
| 74 | JMP sBx=+4 → PC79 | Onay varsa ileri |
| 75–77 | GETGLOBAL Wait / LOADK 10.0 / CALL | Onay yoksa gerçek kaynak Wait(10) |
| 78 | JMP sBx=-8 → PC71 | Onayı tekrar sorgula |
| 79–80 | GETGLOBAL StopVoice / CALL (0 arg) | Kaynak ses durdurma olayı |
| 81–85 | GETGLOBAL ShowTut / LOADK 340,1,1 / CALL | Bir sonraki gerçek öğreticiyi aç |
| 86+ | Bu turda gerçek runtime yürütülmedi | Ek koşullar ayrıca çözülmeli |

**Bekleme parametresi 10.0 gerçektir; bu sayının milisaniye, frame veya başka kaynak motor birimi olduğu HENÜZ KANITLANMADI.** Bu yüzden kodda native Wait(10) gerçek callback olmadan zamana dayalı ilerleme yok.

Native GamePlayUI ShowTut ikinci argümandan 1 çıkardığı için kaynak ShowTut(340,1,1) UI mode0/third1 olur. G148 StringMgr 14 bölüm/1213 ID kanıtına göre orijinal Lua ID340, chap1 locale index84, native packed ID **0x1054**. Orijinal 2010 İngilizce metin ve gerçek Vita TextBox/glif çizimi bu G152 modülünde aktif değil.

## G152 gerçek Lua doğrulama ve durumu

**[G152 Actions SUCCESS #39039881009](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39039881009)**. Kod ve host testi:
- research/b24_unified/g152_source_original_tutorial_condition_runtime/b24_g152_source_tutorial_loop.[ch]
- test_g152_original_PC73_Wait10_StopVoice_ShowTut340.c

G149 kaynak PC72'de geçerli false boolean dönüşünü native callback başarısızlığından ayırır. G152 bu dönüşü source PC73 EQ koşuluna bağlar: false durumunda native Wait(10) callback gerçekten başarılıysa WAIT_NATIVE_10 durumuna geçer; gerçek dış/native Wait tamamlanma sinyali gelene kadar hiçbir frame sayacı veya uydurma ms ile PC71'e dönmez. True sonucunda önce gerçek native StopVoice ack, sonra ShowTut(340,1,1) renderer ack bekler. Bu işlemler eksikse tamamen **fail closed**. PC85 tamamlandı kabul edilse bile **PC86'dan sonrası bu modül tarafından yürütülmez**. Host test callbacks **mock**, cihazda gerçek duyulur ses veya dokunmatik ekran gösterimi değildir.

## G153 tek oyun entegrasyonu ve özgün görev retry kusuru

Önceki G137/G145 kaynak oyun main yalnız ilk açılış tick'inde Mission000 source prefix dispatch çalıştırıyordu. PC6 InteractiveObj_QTE1456 renderer eksik olduğunda hata journal doğru PC6'yı tutuyor, ama sonraki tick'lerde aynı adım tekrar denenmediğinden bir gün callback bağlansa bile kaynak görev harekete geçmiyordu.

G153 opt-in Python patch G147 ve G149 üzerine G152 modülünü tek kaynak oyun motoruna bağlar, tamamlanan PC1 ve PC3 olaylarını tekrar çağırmadan **yalnız BLOCKED_NATIVE_SCENE_BINDING durumunda** kaynak Lua cursor'ından sonraki tick'te tekrar dispatch dener. PC73'e ulaşılmış ve G137 gerçek 24 prebranch event ACK edildiyse G152 typed state yalnız gerçek native callback varsa ilerler. Tek B14 world tick / G83 anim timeline / b24_unified_tick sahibi korunur. QTE renderer, source Wait scheduling, StopVoice ve HUD340 callback'leri şu an **NULL**, bu sayede yeniden deneme oyun görevini sahte şekilde açmaz.

- Entegrasyon: research/b24_unified/g153_source_original_mission_resume_retry_one_vita/g153_integrate_G149_G152_PC73_and_retry_into_one_G147_Vita_main_NO_VPK.py
- Tam asıl Vita ARM ELF-only CI: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39040191350
- CI sonucu yalnız gerçekten tamamlanınca SUCCESS olarak değerlendirilmeli; başarı olmadan ARM bağlandı denmeyecek.

## Eksikler / bundan sonrası

1. Özgün InteractiveObj_QTE ID1456 / Material_QTE 2367 / CameraPreset 1495 ve 2541 gerçek 2010 kaynak renderer/geometry/textures ve touch gesture. **İlk ana gameplay kapısı PC6.**
2. Orijinal ShowTut339 native ID0x1053 TextBox/font/HUD gerçek VitaGL çizimi (PC67), gerçek kullanıcı onayı.
3. Wait(10) native orijinal ARM callback semantiği ve zaman birimi; doğru gerçek Vita timer/mission coroutine bağlamak.
4. StopVoice orijinal voice index/state ve ShowTut340 gerçek UI. Ardından aynı kaynak Lua 937 opcode PC86 sonrası, diğer koşullar ve gerçek conditional PC914/927, PC935 MissionResume. Hiçbiri otomatik açılmadı.
5. Gerçek PS Vita donanımında grafik, ses, çarpışma, FPS ve görev akışı testi. YENİ VPK HÂLÂ ÜRETİLMEDİ.

Bu dosya kullanıcıya ait orijinal IPA, 803 ses dosyası, kaynak görsel, telifli İngilizce tam 1213 metin/bytecode içeriği olmadan yalnız metadata ve kendi C/Python kodunu tutar.
