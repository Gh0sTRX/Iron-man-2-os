# Iron Man 2 (2010 iOS) G126/G127: özgün StatesMgr::GetState fonksiyonunun Vita C portu

17 Ekim 2026, branch feature/b24-unified-gameplay. YENİ VPK YOK.

## Gerçek iOS kaynak bulgusu
Orijinal iOS 2010 ARM Mach-O Native C++ sembolü StatesMgr::GetState(int), adres 0x9F910. G126 tüm 64 byte / 16 ARM komutunu özgün kullanıcı IPA içinden açıp metot imzası ve register access kontrolünü doğruladı.
CNPC::isAttackState 0xE1A20 bu metodu (this+0x2BC, -1) çağırıp dönen source State+0x0C enum'unu 4 veya 5 ile karşılaştırır.
StatesMgr::GetState -1 dahil negatif indexlerde current pointer +0x0C döndürür; pozitif indexlerde önce current_group_index +0x14 test eder, <0 ise NULL; source groups +0x08[current_index], source group+0x2AC count ile index kıyası; index<count ise group+0x2B0[index] source state pointer'ı, aksi halde +0x0C current pointer'a döner. 64-bit host test ve 32-bit Vita kaynak için pointer güvenli C mantıksal veri düzeni kuruldu. Özgün serialized Level1 NPC instance bağlantıları HENÜZ yok.

## Uygulama ve doğrulama
research/b24_unified/g127_native_owner_StateMgr/b24_g127_authentic_2010_states_mgr.h ve .c gerçek C kaynak davranışını portladı. test_g127_true_2010_source_states_mgr.c: -1/-9, grup index 0/1/2, fallback, null guard, 4/5 native attack state ve undefined source durumlarında UNKNOWN kontrolü.
g127_integrate_original_2010_states_mgr_get_state_into_ONE_Vita_game_NO_VPK.py gerçek birleşik B24 kaynak oyununda B24_G127_ORIGINAL_STATESMGR_SOURCE=ON CMake bayrağını ekledi. İkinci fizik/savaş owner veya fake NPC üretilmedi. G127 kaynak kodu G124 CNPC cooldown+priority, G111 original actor+melee combat guard, G108 sourced world collisions, G83/G85 true original Mark V animation ile aynı REAL PS Vita ARM im2_beta ELF içinde linkleniyor.
Gerçek kaynak ARM analiz [G126 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39021185906). Tam native Vita ARM ELF + kaynak host test [G127 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39021131457). ZERO VPK.

## Tamamlanmayan durumlar
Orijinal 2010 CNPC instance allocator, StateSet script/AI source, full UpdateStateAttack/Hurt/Die, 26 Attack gerçek Damage TLV numeric alan eşlemesi, hit-active windows, Level1 original mission/wave waves, GPU material/lighting 1:1 ve gerçek cihaz parity bitmiş DEĞİLDİR. G92 mevcut tek hedef debug dummy, gerçek NPC AI değil.
G125 resmi touchHLE source-built + headless PulseAudio ile original app ARM GDB socket açıldı ama orijinal runtime halen thread 1 already unlocked panics; 0 gerçek damage/melee hit breakpoint yakalandı. [G125](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39020686622). Orijinal 26 attack damage sayıları buna dayanarak ASLA üretilemez.
YENİ VPK KESİNLİKLE YOK. Kullanıcı açık izin verene kadar yalnız host/vita ARM ELF testi.
