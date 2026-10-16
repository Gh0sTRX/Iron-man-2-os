# G83 — Orijinal 2010 Iron Man 2 yürüyüş / uçuş / nişan / dövüş moveset birleşimi (VPK yok)

**Tarih:** 2026-10-16. **Korunan kurallar:** G73'te çalışan gerçek Stark Expo haritasını değiştirme, B14 tek fizik/simülasyon sahibi, G75 kaynak ayarlarını kaybetme, G82 özgün 3'lü kombo ve gerçek C++ menzil/hasar referansını tek yerde tut, bütün gameplay/touchHLE/Vita sistemleri doğrulanmadan VPK üretme.

## Yaptığım (gerçek kod ve test)

**G83 kaynak seçici:** `research/b24_unified/g83_full_motion_aim/b24_g83_unified_movement_aim.c/.h`
- Orijinal 2010 iOS B18/G81 kayıtlarından seçilen **109 benzersiz gerçek IronMan/WarMachine animasyon klip adı**; tümü özgün katalogdaki 248 IronMan + 56 WarMachine kaydıyla bağımsız kaynak/ad doğrulamasından geçti.
- Mark VI hareketler: ground idle, dört yöne walk, tam analog koşu modu seçimi (bu yönlendirici B14 hareket hızına dokunmaz), rahat idle/4-yön air hover, dört-yön flight, RUSH, ileri-sağ/sol ve sağ/sol-ileri uçuş geçişleri, ground→hover, fly start/end, fly→ground/run, right/left dodge.
- Ground/hover aimed 1-handed, 2-handed idle, left-hand idle, dört yöne hareket hâlinde aim ve yalnızca **gerçek silah modülünün kabul ettiği** repulsor/aim fire clip seçimleri.
- `_Aim_M_` kaynak klip ailesi de ayrı mod; **M'nin 2010 oyunda gerçek füze tanımlayıcısı olduğu kanıtlanmadı**: `B24G83_AIM_M_UNCLASSIFIED`. Gerçek kaynak adını kullanır fakat sahte füze atış semantiği iddia etmez.
- War Machine: 4-yön native aim_ground, hover, aim_m_float, accepted aim-fire variants, native flight. Orijinal kaynakta WM relaxed ground/WM RUSH isimli klip kanıtlanmadıysa `NULL` dönerek mevcut güvenli G8 fallback'ini korur, hiçbir MarkVI iskeleti WM'ye yanlış uygulanmaz. Mark V gibi mevcut kaynak MarkVI/WM vertex eşleşmeyen zırhlarda da `NULL` (ileride ayrı rig retarget yapılmalı).
- Destek: `b24_g83_select_combined` G82'nin özgün `Ground_Combo_1/2/3` zincirini hareket/nişan animasyonunun önüne koyar. **G82 yakın dövüş hitbox modeli ve orijinal 2 havuzlu hasar aritmetiği kaynak düzeyinde bağlanmış durumda**, ama özgün vuruş kareleri/WeaponDB numeric damage hâlâ kapalı kapıda.
- Uçuş/iniş için `grounded_contact_verified` zorunlu. Kamera/poz ve B14 fizik güncelleme döngüsünü yeniden yazmıyor.

**Gerçek animasyon süreleri:** `b24_g83_authentic_2010_source_durations.h` B18'in orijinal 2010 304 kayıt dizininden otomatik oluşturulan 109 erişilebilir özgün animasyonun kaynak süresini içerir. Kullanıcı tarafından yüklenen gerçek 2010 iOS IPA'ya dayanan 304 kaydı etiket ve süreleri ile yeniden doğrulandı.
- Hızlı yön geçişi `Fly_FtoL`: 800 ms; `Fly_LtoF`: 800 ms
- `Fly_Left/Right_dodge`: 699 ms
- `Fly2Ground`: 633 ms
- Aim-Ground-Move-F-Att: 866 ms
- G82 Combo 1/2/3: 266 / 300 / 500 ms

**Yeni kaynak süre yöneticisi:** `b24_g83_authentic_timed_router.c/.h`. Bir atış, dodge, iniş veya uçuş yön değişikliği tetiklenince özgün klibin gerçek süresi kadar seçili tutulur; sonraki karede yanlışlıkla yürüme pozuna geri düşmez. Kayıtlı `accepted_weapon_event` yalnızca saldırının ilk olayında kullanılır; **tutulan animasyon her karede mermi/hasar üretmez.** 3'lü melee zinciri atış animasyonunun önüne geçer. Pause ve doğrulanmış yere temas kontrolleri var. Frame-hit zamanı, hasar ve B14 uçuş hızı bu sürelerden **türetilmemiştir**.

**GitHub Actions G83 host+Vita ARM source CI:** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38945292570 — **SUCCESS**. Derlenenler gerçek C G8 melee + G76 native durability reference + G77 authentic 0.5 melee bbox + G82 source combat + G83 full motion/aim route & timed route. Bütün 109 hardcoded clip adı source B18 katalogla assert edildi. Önceki ve en son örnek hareket/aim testleri geçti. Yalnızca gerçek PS Vita ARM **nesne derlemesi** yapıldı, birleşik büyük oyun ELF/VPK yapılmadı. C11 native/PS Vita ARM warning'leri düzeltildi; G73 çalışır VPK'ya dokunulmadı.

## Gerçek 2010 IPA + touchHLE deneysel karşılaştırma

Bu oturumda kullanıcıya ait **248,613,763 bayt** `IronMan2_1.0.0_ios_2.2.1.ipa` Drive dosyasından alınarak yerelde doğrulandı. Tam `anims` bankasına doğrudan ham kaynak ikili parseri uygulandı:
- **972/972** kaynak `.anim` kaydı XYZ ve quaternion kanal dizileriyle okunabildi, `anims` SHA-256 **`daf843660a2ddc66e2189683961e020335c88d3edc522bfd03db444acc85113b`**.
- Önceki orijinal isim grupları: **248 IronMan + 56 WarMachine + 34 UnderwaterArmor = 338** oyuncu-zırh animasyon adayı; ek 9 UnderwaterObject klibi oyuncu sayısına dahil değildir. Enemy/drones/boss ve diğer çevre animasyonları da toplam 972'de bulunur.
- Yerel doğrulama kaydı `G81_original_moveset_evidence/G81_2010_ORIGINAL_972_ANIMS_338_PLAYER_METADATA.json`, CSV dosyaları `G81_338_ORIGINAL_ARMOR_MOVESET.csv`, `G81_972_ANIMATION_CATALOG.csv` şeklindedir. Bunlar **ham tescilli 3B mesh dosyaları değil**, özgün kayıtlardan türetilmiş teknik meta veridir.
- **touchHLE v0.3.0 resmi sürümünün daha önce başarılı Linux derlemesi** G62'den alındı (GitHub Actions 38827381546). Orijinal dosya Xvfb/mesa üzerinde çalıştırıldı: **orijinal ana menü ve Level 1 – Media Mayhem açılış brifingi göründü.** İlk bölümde gerçek tuş hareketleri/kombo event frame ölçümleri **yapılamadı**. touchHLE emülatörünün bu makinedeki v0.3.0 denemesi `src/environment/mutex.rs:212` içindeki “Attempted to unlock non-error-checking mutex … already unlocked” panic'ine gitti (kaynak `touchhle_newgame.log`). Bu, oyunun her sürümde oynanılamadığı kanıtı değildir; sadece **bu koşuldaki test engeli**.
- touchHLE gerçek nişan/uçuş kombo davranışını test edilmeden, sadece kaynak klip isimlerini 2010 canlı input state geçişi kabul etmiyoruz.

## BİTMEDİ (VPK üretme bariyeri)

1. B24 gerçek Vita oyununun G8 IM2V oynatıcısına yeni G83 selection/timeline **ana döngü callsite bağlantısı ve tam B24/G75/G68 kaynak birleştirme derlemesi** henüz yapılmadı; G83 ayrı test edilmiş CPU modülleridir.
2. Orijinal 338 hareketin tümü Vita üzerinde oynanabilir ve iskelet uyumlu değil: daha önce MarkVI 802 vertex ve WM 1292 vertex subset; Underwater yardımcı 29 vertex parent bağlantıları eksik; her eski sürüm MarkV/diğer zırhlar yeni retarget istiyor.
3. Native C++ `AttackEntity` ve `ProjectileEntity` veri şeması, doğrudan ve splash damage yolları çözülmeye başladı ancak silah başına **özgün nihai hasar sayı tablosu**, kombo hit-box aktif kareleri, düğme buffer/iptal pencereleri, NPC AI, tüm silah sesleri gameplay eşlemesi tamamlanmadı.
4. Eski G73'ün sağlam şehir çarpışma/harita ve G75 yer gömülmesi, görünmez duvar, doğal ışıklandırma/gökyüzü henüz cihaz testinden geçmedi; G82/G83 kaynak testleri cihaz üzerinde yapılmış oynanış değildir.
5. touchHLE menüden gerçek live game anim/attack kontrol davranış karşılaştırması ve sonrakı PS Vita kabul/performans testi bekliyor.

**Sert kullanıcı isteği:** Bu beş kapı tamamlanmadan, gerçek bütün orijinal moveset + combat bir araya gelmeden, **yeni test VPK'sı ÜRETME**. Sadece GitHub kaynak sürümünü geliştir, tam oyun test derlemesini gerektikçe ayrı yap ama VPK paketleme yapma.
