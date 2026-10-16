# G84 — G75/G68 gerçek Stark Expo oyun motoru + G83 özgün moveset entegrasyonu

**16 Ekim 2026 · kaynak testi doğrulandı · yeni VPK oluşturulmadı.**

## Somut yapılan iş

Eski çalışan **G9/B24** gerçek oyun gövdesi, **G68'in özgün Stark Expo şehir geometrisi**, **G75 kamera/uçuş/çarpışma kaynak yamaları** yeniden birleştirilip G83'ün özgün yürüyüş, hover, yönlü uçuş, RUSH ve nişan hareketi seçicisi gerçek **`work/src/main.c`** oyun döngüsüne eklendi. Bu, yalnızca bağımsız G83 test kodu değil: Vita ana oyun girişine yazılan gerçek kaynak entegrasyonudur. CMake seçeneği **`B24_G84_ORIGINAL_MOVESET_ROUTER` varsayılan OFF**: çalışan G73'ü ve eski G8'i etkilemeden, ileride kapı kontrolleri geçince açılabilir.

**Tek sistem sahibi:**
- **B14** yalnızca bir kez `b14_world_tick(...)` çağrısıyla sahneye yürüme, uçuş, kamera, fizik ve hareketi sağlar. Mevcut G75 hareket hızlarını kaynak adlarından çıkarılmış özgün iOS hızları gibi göstermiyoruz.
- **G8** tek `IM2V` mesh vertex/pose streamer; gerçek 2010 dosyalarını kareye göre oynatır. G84, eski `b24_g8_motion_tick` ABI'sini wrapper'la koruyup opt-in `b24_g8_motion_tick_g84` işlevi üzerinden **G83 kaynak animasyon adını** verir.
- **B16 kabul edilmiş sağ repulsor tetiklemeleri ve G8 özgün melee kombo** hâlâ tektir; G83 bunları yeniden ateşlemez. Gerçek mermi hasarı ve düşman olmadığı için sahte hit yapılmaz.
- **G83** MarkVI/WarMachine özgün klip yönlendirmesi ile oyun içindeki opt-in L aim (PROTOTYPE kontrol eşlemesi, touchHLE orijinal L tuşu değildir), yürüyüş, koşu, 4 yön hover, uçuş, RUSH, yön dönüşü ve kaynak kare süresi tutma. `B24G83Aim_M` gerçek füze semantiği hâlâ kanıtlanmadığı için doğrudan missile moda bağlanmadı.
- **G82/G77/G76** ek CPU combat referans kaynakları CMake'ye bağlandı ancak gerçek hasar sayı/active hit frame olayları *doğrulanmadığından* oyun içinde hasar uygulamak üzere açılmadı.

## Yeni özgün dosya kapsama testi

`g84_real_109_original_clip_stream_coverage.py` gerçek G9 yeniden oluşturulmuş `work/animations` ile `g83_unified_movement_aim.c` seçici kaynak isimlerini karşılaştırdı:
- **109 / 109 özgün IM2V** yönlendirme dosyası doğrudan bulundu; **eksik 0**.
- G9'daki toplam özgün oyuncu akış dosyası: **363**.
- Bu sayı **363 animasyonun tümünün Vita'da ayrı ayrı canlı test edildiği anlamına gelmez**. 109 dosyanın fiziksel bulunurluğu, doğru mesh ile animasyon oynatımı veya gameplay davranışı ile eşdeğer değildir.

## Kaynak test sonucu

GitHub Actions **SUCCESS**: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38948092792

1. Gerçek G75/G70/G9 kaynak birleştirmesi tamamlandı; orijinal G68 şehri ve G8 animasyon alt sistemi mevcut.
2. Tek B14 fizik integratörü, tek G8 eski repulsor ve tek G8 melee tetikleyicisi, bir G83 frame-time selector çağrısı assert edildi.
3. **G84 gerçek kaynak bileşenleri masaüstü C11 strict syntax** testinden geçti.
4. G83'ün kullandığı **109 özgün animasyonun 109'u da gerçek 363 IM2V kaynak pakette mevcut**.
5. G83/G82/G8 birleşimi **PS Vita ARM nesne derlemesinden**, ayrıca oyunun gerçek `work/src/main.c` dosyası G84 macro AÇIK durumuyla **Vita ARM syntax-only** denetiminden geçti.
6. **Oyunu Vita donanımında başlatmadık, ELF/VPK oluşturmadık**, FPS veya gerçek combat gameplay doğrulanmadı.

Kaynak yamayı tekrar uygulama (GitHub Actions aynı süreci uygular):
`research/b24_unified/g75_device_qa/g75_reassemble_old_real_game_NO_VPK.py` → `research/b24_unified/g84_main_loop_integration/g84_apply_original_g83_to_G75_G9_MAIN_NO_VPK.py`.

## Eksikler ve VPK'ya izin verilmemesinin gerekçesi

- G84 özelliği varsayılan **OFF**, kaynak kodunda birleşik ama çalıştırılmış Vita ELF'i olmadığı için gerçek cihaz oynanışı doğrulanmadı.
- Kaynak animasyonları ve süreleri var; **orijinal 2010 touchHLE oyun içi yürüyüş/uçuş/nişan tuş-giriş eşlemeleri** hâlâ doğrulanmadı. touchHLE orijinal menü ve Level1 Media Mayhem brifingini gösterdi ama devamında mutex hata denemesi var.
- **Orijinal 338 oyuncu zırh klibi** var fakat 109'dan fazlası G83'e yönlendirilmedi; MarkV/MkIV/Stealth için doğrulanmış bütün 3D kaynak rig animasyon eşlemesi henüz yapılmadı. Kullanıcının istediği Mark V ilk görev eksiksiz değil.
- **WeaponDB özgün hasar değerleri, real hit frame/cancel windows, NPC AI, tüm combolar/dövüşler/reaksiyonlar, FX/ses eşlemeleri** oyun döngüsünde tamamlanmadı.
- G75 ışık/sky/ground collision hatalarının Vita donanım testi hâlâ bekliyor.

**Kullanıcının net kuralı: BÜTÜN MOVEMENT + COMBAT tamamlanmadan veya gerçek Vita oynanabilirliği doğrulanmadan YENİ VPK ÜRETME.** G84 sadece kaynak artefaktı üretti.
