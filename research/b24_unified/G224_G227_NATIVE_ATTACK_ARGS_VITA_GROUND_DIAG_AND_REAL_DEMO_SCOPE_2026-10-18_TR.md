
# G224–G227 — Özgün saldırı parametreleri, Vita yürüyüş teşhisi ve bugünkü gerçek demo kapsamı

**18 Ekim 2026. Kaynak: Gh0sTRX/Iron-man-2-os, feature/b24-unified-gameplay. VPK YOK.**

## Orijinal 2010 iOS saldırı verisi

[G224 gerçek ARM source PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39145102276) — orijinal MainCharacter::DoAttack(int,int) 0xF64F8: native r1 AttackType değeri r5'e, native r2 StateTrack olay kaydının üçüncü u32 değeri r8'e aktarılıyor; gerçek 26-kollu saldırı jump tablosunu AttackType r5 seçiyor.

[G225 özgün r8 passthrough PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39145356582) — native default saldırı yolunda 0xF659C MOV r1,r5 ve 0xF65A0 MOV r2,r8, 0xF65A4 BL original Actor::DoAttack(int,int) 0xDA5B8. Gerçek 2010 kaynak çağrı zinciri artık StateData.AttackType → StateTrack.GetEvent → event[index].third → MainCharacter::DoAttack → özgün native case/fallback. Ancak ikinci sayının 0/1/2/3 değerinin hangi silah, kombo, hasar, projectile veya damage moduna ait olduğu hâlâ kanıtlanmadı. Orijinal iOS touch/gesture inputlarının tamamı çözülmedi.

## G226–G227 Vita'da yerinde yürüme

[G226 gerçek son C1L1 kaynak derleme ve analiz PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39145998224): son birleşik Vita main içinde sol analog move_x/y okunuyor, TEK b14_world_tick CPU hareket yapıyor, özgün G66C çarpışma b24_g75_capsule_reconcile dünyadaki XY'yi düzenliyor, camera.player_x/y/z doğrudan world.x/y/z alıyor, b24_gpu_runtime_draw bunu frame_pose'a, b24_gpu_suit_matrix bunu gerçek GPU model matrisinin 12/13/14 çevirisine aktarıyor. Kamera oyuncuyu izlediğinden karakterin ekranda aynı yerde kalması dünya hareketi yok demek değildir. Ancak fiziksel cihazda kullanıcı gerçekten yürüme sırasında ilerleme görmedi; neden hâlâ kanıtlanmadı.

[G227 yeni host + tam gerçek Vita ARM ELF success](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39160392556). Kaynak G227 kodu: `research/b24_unified/g227_vita_walk_world_collision_gpu_qa/`. Gerçek oyun main'e opt-in `B24_G227_WALK_ROOT_DIAGNOSTIC=ON` ile her 120 başarılı frame'de `G227_WALK_ROOT` SDL log yazılıyor. Veriler: analog XY, B14 önceki XY, B14 sonrası XY, native kaynak collision sonrası XY, gerçekte GPU'da kullanılan armor world XY, kamera target XY, gerçek G8 clip yüklenmiş mi? Tam 8 QA sınıfı ile analog deadzone / B14 sıfır hareket / çarpışmanın geri alması / dünya hareketi+takip kamera / dünya hareketi+kamera gecikmesi / uçuş / invalid / paused ayrılıyor. Bu ölçümler yokken sebebi bildiğimiz iddiası YOK. G227 B14, G8, B16, zırh, fiziki collision ve GPU'yu DEĞİŞTİRMİYOR. VPK YOK ve gerçek Vita QA henüz yapılmadı.

## Bugün demo derlense gerçekte kullanıcı ne deneyebilir?

| Özellik | Test prototipi olarak erişim | Orijinal Chapter1 sadakat / engel |
|---|---|---|
| Stark Expo | G66/G68 orijinal harita ve gerçek source çarpışma, gezinti testi | Harita/nesne ölçeği, yüklemeler ve cihazdaki sahne doğrulaması eksik |
| 5 zırh | Mark VI, IV, War Machine, Stealth ve Mark V modellerine geçiş | Hepsi için aynı özgün 2010 hareket/animasyon kapsamı yok |
| Yerde hareket | G83/G8 kaynak yürüyüş, koşu; B14 fizik, G171 çarpışma düzeltmesi | Kullanıcının yerinde sayma bugı çözülmüş değil; G227 yeni log teşhisi |
| Hover / Stage2 / Rush | Stage bazlı prototip uçuş + özgün kaynak IM2V animasyon denemesi | Mark V ilk Expo uçuş sınırlaması dahil özgün Lua izinleri tam değil |
| Kamera ve HUD | Omuz kamera, merkezde crosshair, uçuşta merkezleme, HUD/pause prototipleri | Önceki pause UI ve aim hizalama donanım QA açık |
| Repulsor ve Uni-Beam | B16 prototip ateşleme, G169/G173 gerçek Beam 1/2/3 animasyonları | Özgün DoAttack, VFX, missile, hasar ve cooldown bütünlüğü yok |
| Yakın dövüş | Özgün üç kombo kaynak animasyonları ve test combat akışı | Tam hit window, düşman reaction ve gerçek özgün iOS hasar zinciri yok |
| War Machine | Orijinal WM 1292 vertex model + 10 kaynak M-ground hareket klibi | Omuz roket/gatling, otomatik tarama, M silah semantiği kanıtlanmadı |
| Test hedefi | G10/G11 statik dummy host QA ve prototip bileşenleri | Gerçek Expo haritasında tümüyle işleyen NPC ve enemy AI hazır sayılmaz |
| Görev / QTE | G137–G153 orijinal Mission000 Lua, tutorial ve QTE kaynak iskeleti | PC3/PC6 UI ve QTE eksikleri nedeniyle Chapter1 baştan sona bitirilemez |
| Ses | Bazı özgün ses PCM/SFX oynatma kaynak sistemi | Bütün VO/müzik/weapon/cutscene timing orijinal düzeyde değil |
| Görsellik | Gerçek source mesh ve GPU/VitaGL shader/texture/sky pass mevcut | Siyah skybox, ay konumu, gölgeler, alfa ve karakter–araba ölçüsü donanımda düzelmiş sayılmadı |

**Net:** Bugün mevcut kaynakla doğru isimlendirme `Stark Expo teknik oynanış prototipi` olur. Orijinal oyunun ilk bölümünün tam, hatasız demosu olmaz. Yeni VPK yapılmadı; son gerçek birleşik `im2_beta` ARM ELF başarıyla derlendi ama kullanıcının gerçek cihazında yeniden test edilmedi.

## G228 araştırma önceliği

G227'den gerçek cihaz hareket logu alındığında analog/B14/collision/kamera yollarını nedensel olarak ayrıştır. Ondan sonra özgün kaynak temelli düzeltme yap; GPU root bağlantısı kodda mevcut olduğundan sahte ölçek/hız hacki uygulama. Ayrı akışta 2010 DoAttack event üçüncü u32 0/1/2/3 native case semantiği ve özgün WeaponDB çözümüne devam. Chapter1 gerçek görev/cutscene/ışık/hitbox bitmeden son VPK yok.
