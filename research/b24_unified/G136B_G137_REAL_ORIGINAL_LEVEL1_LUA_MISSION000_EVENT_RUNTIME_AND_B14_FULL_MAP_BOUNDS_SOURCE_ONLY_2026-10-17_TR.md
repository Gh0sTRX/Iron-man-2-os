# Iron Man 2 iOS (2010) → PS Vita: G136B + G137 source mission engine ve tam harita hareket alanı

**17 Ekim 2026 · `feature/b24-unified-gameplay` · YENİ VPK YOK.** İstek: özgün iOS Level 1 görevi ve Mark V hareket yetkilerini esas al; gerçekten çalışan sistemlere bağla; sahnedeki katı/engelleyici geometri sorunlarını kapat.

## G136B kritik gerçek oyun hatası — B14 kendi içinde hâlâ ilk haritayı KIRIYORMUŞ!

G128'de eklenmiş gerçek kaynak dünya sınırları **G75 collision post-step** içerisinde vardı ama gerçek ana oyuncu integratörü **`B14World::tick`** *önce* x[-324,330],y[-351,254] hardcoded beta viewport clamp uyguluyordu. Bu yüzden daha sonra G75'in gerçek sahne polygonlarına izin verdiği x=500,y=500 gibi orijinal level bölgelerine kullanıcı asla yürüyemiyordu.

- `g136_patch_B14_original_render_source_bounds_NO_VPK.py` gerçek eski kaynak rebuilt `work/assets/G66_city.g66m` içindeki **67.323 özgün 24-byte vertex** tamamını doğrudan açıyor ve XY AABB çıkarıyor: **X[-761.033936,+649.193787], Y[-773.509949,+586.695312]**. Bu veriler tanımlı derlenmiş orijinal model kaynağından; uydurma değil.
- Var olan tek B14 intregatorunda `B24_G136_SOURCE_B14_WORLD_BOUNDS=ON` altında eski x330/y254 clamp yerine gerçek source AABB±0.35 kapsül yarıçapını koyuyor. **G75/G128 sourced 1.910+7.487 duvar adayı ve G134 swept capsule son yetkili olmaya devam ediyor.**
- `test_g136_B14_original_world_not_clipped_early.c` gerçek `b14_world_tick` ile x500,y500 artık hard-clamp olmadığı, orijinal source AABB dışına x2000/y2000 kaydırma sınırlandığı sonucunu doğruluyor.
- **[G136B tam birleşik PSVita ARM `im2_beta` ELF link + host C11 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39026506960)**.
- **DİKKAT:** "G66 source visual AABB" ile orijinal "MissionPlayableArea / fiziği katı olan duvar / suit flight allowed" kesinlikle AYNI kavram değil. G108 visual-derived 7.487 candidate kaynağın orijinal authored collision semantic'i değildir; Vita fizik gerçek cihaz testi henüz yok.

## G137 özgün Mission000 24 native Lua CALL uygulama modülü, artık ana Vita C oyununa LINKLİ

G135 gerçek özgün `level1.bclara` `Mission000_OnStart` **937 bytecode PC**, ilk `EQ` koşul PC73; G137 bu PC73'e kadar düz/koşulsuz gerçekten authored `GETGLOBAL/CALL` kaydını eski kanıtlanmış G27 `71 Lua / 1035 call` JSON artifaktından **C kaynak dosyasına otomatik üretiyor**. Orijinal proprietary Lua/IPA Git repo'da yayımlanmadı.

**24 özgün olay**:

| Lua PC | Native çağrı (orijinal Level1 typed ID) |
|---|---|
| 1 | `MissionPause()` |
| 3 | `PauseMusic()` |
| 6 | `Show(1456)` — orijinal QTE interactive obj |
| 9,12,15,18,21,24,27,30 | `Enable(1808,1813,1818,1823,1828,1833,1838,1843)` |
| 34 | `SetState(1062,"idle")` — gerçek Mark V / MainCharacter |
| 37,40 | `Disable(1163)`, `Enable(1158)` |
| 43 | `Hide(1062)` — protagonist |
| 46 | `HideUI(14)` — **SetInputEnabled(14,false) ile aynı API değil** |
| 50 | `SetInputEnabled(14,false)` — gerçek native `Input::ResetKeys/Touches, Actor::Stop` doğrulandı (G132) |
| 53,56 | `Disable(2494)`, `Disable(2499)` |
| 58 | `BlackScreenOn()` |
| 62 | `PlayMusic(88,true)` |
| 67 | `ShowTut(339,13,0)` — gerçekten **3 parametre**, G137 modelde korundu |
| 70 | `PlayVoice(320)` |
| 72 | `IsTutConfirmed()` — sonucu bir sonraki `EQ` PC73 dallanmasını yönetiyor |

**Kod**: `research/b24_unified/g137_original_Mission000_native_boot/`:
- `g137_emit_original_Mission000_lua_prefix_from_G27.py` gerçek PC+typed args ↦ generated native `b24_g137_mission000_owner_original_generated.c`. 24/24 kesin sayım ve yukarıdaki kaynak callsite ID checkleri var. Branch sonrası PC914 / PC927 UI enable ve PC935 MissionResume kesinlikle önceden replay edilmiyor.
- `b24_g137_source_mission000_intro.[ch]`: session start, source Lua PC sorted strict validator, retryable callback gate, state journal, source-native entity IDs and args, original PC73 EOS barrier. Callback uygulanmazsa `BLOCKED_NATIVE_SCENE_BINDING` ve **aynı özgün Lua PC'de** bekler; hiç sahte AI/mission complete oluşturmaz. `b24_g137_mission000_is_gameplay_released` şimdilik 0; oyuncu zırhı flight permission kesin değil.
- `g137_patch_authentic_Mission000_source_live_to_one_game_NO_VPK.py`: gerçekten var olan `work/src/main.c` içindeki tek `b24_unified_tick` çağrısından sonra **bir kez** `b24_g137_mission000_init` + `dispatch_verified_prefix` native runtime hook bağlar. `B24_G137_MISSION000_REAL_SOURCE_EVENTS=ON` ile opsiyonel CMake derleme; ana G134/G136B + G127 NPC + G111 combat + G85 animation motora link edilir. Yeni physics veya animasyon tick yok.
- **ÇOK ÖNEMLİ BAĞLAMA SINIRI:** Vita ana oyununda bugün sadece `MissionPause`'un *scope/request journal* callback'i tanımlı; mevcut B24 kendi orijinal iOS müzik çalma/ses pause manager'i ve QTE scene object ID1456 native binding'i olmadığı için **oyun G137 akışı `PauseMusic` PC3'te BLOCKED**. PC6 QTE ve PC73 tutorial condition **CANLI UYGULANMIYOR**; host test özel stublarla tüm 24 gerçek original callsite'ın doğru sırayla geçmesini test ediyor, bu gerçek sahnede tamamlandı demek DEĞİL. Gerçek level1 Lua VM, camera preset dispatcher, scene entity visibility, native audio + tutorial QTE engine and original 2/6 UI unlock yok. G137 pointer-injected source game normal free-test viewer'ı kilitlemiyor, çünkü sahte QTE süresi / otomatik MissionResume uydurmuyor.
- `test_g137_real_source_Mission000_boot.c`: gerçek üretilmiş özgün Lua 24 event C metadata üzerinde host test; callback olmadan source blok, PC34'te injected fake handler ile durup yeniden devam, tüm 24 handler bound ortamında PC73'te durur; `MissionResume` otomatik çağrılmaz.
- **[G137 başarılı tam Vita ARM `im2_beta` ELF link ve C11 tests](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39027098293)**. Son kaynak açıklaması düzeltmesinden sonra Google Drive geçici IPA erişim hatası nedeniyle aynı workflow yeniden denendi ve **[G137 en son gerçek birleşik Vita ARM source-only SUCCESS 39027228231](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39027228231)** olarak tekrar tamamlandı.

## Bir sonraki tam doğru adım

G137 ilk event `PauseMusic` PC3 için özgün 2010 ARM `PauseMusic(lua_State*)` gerçek C++ ses/audio dispatch mantığını çöz ve Vita B24 native sound owner'a bağla. Sonra `Show(1456)`, `Enable(1808,...)`, `Hide(1062)`, `HideUI(14)` ve `ShowTut(339,13,0)` için kaynak scene entity ID→renderable/GPU görünürlük ve tutorial/QTE old iOS asset mapping; native return `IsTutConfirmed` PC72 ile orijinal Lua PC73 condition loop'u. **Kullanıcı Mark V uçamayabilir dedi ama flight permission source iOS ARM/mission kesini henüz yok, zırhı uydurma zorunlu ground-only yapma.** Orijinal gameplay event/state gerçek sahnede aktif olana kadar `Mission000` tamamlandı iddia ETME.

**VPK ÜRETME.** Yalnız kaynak host test ve gerçek Vita ARM `im2_beta` ELF. Donanımda bu değişiklikler denenmiş değildir.
