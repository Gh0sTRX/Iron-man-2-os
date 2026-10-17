# G133–G135 — İlk gerçek görevde kontroller 2/6, ince duvar çarpışması ve 2010 Lua görev zinciri (17 Ekim 2026)

**Proje:** `Gh0sTRX/Iron-man-2-os`, dal `feature/b24-unified-gameplay`. Kullanıcının talebi: 2010 iOS'ın özgün Mark V ilk bölüm kurallarına uygun hareket, kesinsiz uçuş varsayımı yapmama, Stark Expo katı duvar sorununu bitirme. **Yeni VPK yok.**

## G133 — gerçek 2010 iOS GamePlayUI key2/key6/key14 ARM switch

- Gerçek iOS 2010 Mach-O `GamePlayUI::SetUIKeyEnabled(int, bool)` VM `0x1D260` **143 gerçek ARM komutunun tamamı / 572 byte** çözüldü.
- Native switch (r1 key, r2 bool) adresi 0x1D280. 2 girişi `0x1D3FC` üzerinden `GamePlayUI+0x17AC` widget'a; 6 girişi `0x1D41C` üzerinden `GamePlayUI+0x1BC8` widget'a gidiyor. Her ikisi `0x1D3B0` ortak etkinlik yazım yolunu kullanır. 14 ise `0x1D2D8` birden fazla widget'a dokunan özel dal.
- `SetInputEnabled(lua_State*)` 0x18494 genel 14=false girişte Input::ResetKeys/ResetTouches/SetEnabled(0,bool), GS_GamePlay::GetMC, Actor::Stop + HUD SetUIKeyEnabled yolunu çalıştırır (G132). **14 bit maskesi değildir**, ve 2/6 farklı UI öğeleridir. Bunları doğrulamadan flight/hover yetki bayrağı diye çevirmemeliyiz; özel Level1 Mark V suit yetki satırı kanıtlanmadı.
- [**G133 native original iOS 2010 ARM CI BAŞARILI**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39025439094); artifact ID 12098705451; orijinal executable GitHub'a eklenmedi.

## G134 — gerçek B14 + G75 swept-capsule uzun frame delikten geçme ENGELİ: uygulandı / ARM derlendi

- Eski `b24_g75_capsule_reconcile` bir tek B14 hareket adımının `ceil(max(|dx|,|dy|,|dz|)/.22)` örnekleme sayısını max80 yapıyor AMA tüm uzun hareketi 80 parçaya bölüyordu. Örneğin 100 kaynak birim delta → 80 defa **1,25** kaynak birim örnek; 0,35 yarıçaplı karakter x=10.6 düz duvarın tam iki geçiş örneği arasından atlayabilir.
- `research/b24_unified/g134_true_original_collision_sweep/g134_patch_2010_source_world_substeps_NO_VPK.py` gerçek full B24 G108 G75 kaynak dosyasındaki **tek** `b24_g75_capsule_reconcile` hareketi aşırı frame'de 80×.22=17.6 kaynak birim ile sınırladı. Darbe/hasar üretmiyor, yeni fizik sahibi yaratmıyor; gerçek kaynağa güvenli kapsül geçişi uygular.
- `test_g134_long_frame_2010_source_wall_tunneling.c` özgün collision struct ABI'siyle sentetik ince duvar x10.6 stres testinde aşırı 100 birim tek frame harekete engel olduğunu doğruladı. Test geometry **sentetiktir**, gerçek level1 obje olarak iddia edilmez. G75 gerçek kaynak **1910 authored triangle**, G108 **7487 visual-derived candidates**, G128 tüm source world limit ve G93 G94 testleri de aynı CI'de yeniden başarıyla çalıştı.
- **[G134 FULL gerçek PS VitaSDK ARM `im2_beta` ELF-only derleme + kaynak host C11 test BAŞARILI](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39025687354)**. G127 2010 NPC, G111 combat gate, G106 MarkV flight pose, G71 alpha G73 sky G95 sun, G92 dummy hâlâ aynı tek gerçek main'e bağlı. **VPK yok; cihazda G134 henüz test edilmedi.**
- Daha önce kaydedilen G128 kaynağı: gerçek G66 rendered scene AABB X[-761.034,649.194] Y[-773.510,586.695], eski hardcoded model-world sınırlarında kaybolmuş 374 dik üçgen merkezi, toplam 7487 aday duvar. Gerçek iOS solidity bayrakları bu G108 görsel adayları için hâlâ kanıtlanmış değil.

## G135 — `Mission000_OnStart` TRUE iOS Lua 5.1 kontrol akış grafiği

- Orijinal kullanıcının 2010 `level1.bclara` içindeki 71 callback arasından `Mission000_OnStart` özgün Lua 5.1 **937 gerçek sanal makine komutu** parse edildi. Conditional/unconditional Lua jump, FORLOOP/FORPREP, TEST, TESTSET, LOADBOOL atlama vb. denetlenerek gerçek düzeyde **66 koşul/dal komutu** ve bunların gerçek PC successor grafiği, dominatör noktaları hesaplandı.
- Source `Mission000`: `SetInputEnabled(14,false)` PC50, `SetInputEnabled(2,true)` PC914, `SetInputEnabled(6,true)` PC927, `MissionResume()` PC935. **Yalnız mümkün yollar CFG** için PC914 ve PC927, PC935'i domine ediyor. Yani aynı handler'ın bu MissionResume noktasına gidebilen her çizgisel/dallı yol iki UI enable callsite'inden de geçer (ama dış global state, Lua runtime/event loop koşulları henüz yürütülmedi).
- İlk gerçek koşul `EQ` PC73; devamında kamera/kesit/animasyon & voice çağrıları var. PC914/927, başlangıçta PC50'yle eşzamanlı yürütüldüğü anlamına gelmiyor. G135'nin statik erişilebilirlik algoritması 937/937 komuta varsayımsal ulaşım buldu; bu gerçek çalıştırılmış olan komut sayısı değil.
- **[G135 orijinal Lua görev CFG GitHub Actions BAŞARILI](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39025885945)**; artifact ID 12098607028. Kaynak script `research/b24_unified/g135_real_first_mission_Lua_control_flow/g135_original_2010_Mission000_Lua51_control_flow_graph_source.py`. Hiçbir Lua script Vita'da henüz çalıştırılmadı.

## Asıl sonraki işler ve dürüst doğrulama sınırı

1. Mission000 Lua 5.1 çalıştırılabilir bir `Mission` runtime, özgün `NPC/Deco/CameraPreset` entity class owner ID'leri, `SetState/Show/Hide/Enable/Disable/SetCamera/Wait/MissionPause/Resume` native callback implementasyonu gerekiyor. G135 kaynak kod grafiği bunu yapmıyor. Birinci haritada MarkV'in uçup uçamayacağı native suit capability/mission gate hâlâ *bilinmiyor*.
2. G133'te kontrol 2/6 özgün UI belleği ofsetini öğrendik, ekranda hangi widget/weapon/gesture olduğu ve gerçek touchHLE source runtime inceleme henüz çözülemedi.
3. G134 tünelleme bugını giderdi, ama "katı olmalı" varsayılan G108 opak görsel yüzeylerinin gerçek iOS authored collider parametreleri bilinmediği için yanlış katılar veya atlanan kapı/nesneler çıkabilir. Gerçek Vita'da yeni build test edilmedi.
4. **NO VPK** kullanıcı tekrar açıkça talep etmedikçe. Son gerçek birleşik link `G134` CI, offline host smoke `G135`. Kullanıcı "bitir" isteğini kapatmak için gereken gerçek Mission script VM ve physics material ownership tamamlanmış değildir.
