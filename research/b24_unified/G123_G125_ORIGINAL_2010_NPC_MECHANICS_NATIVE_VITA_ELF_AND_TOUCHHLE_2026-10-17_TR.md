# G123–G125 | Iron Man 2 (2010) özgün NPC ve görev mekaniklerini kaynak düzeyinde portlama

**17 Ekim 2026** — `feature/b24-unified-gameplay`; yeni Vita VPK üretmeme kullanıcı kararı **devam ediyor**.

## G123: Özgün iOS ARM fonksiyonlarının gerçek komut akışı çözüldü

Özgün 248.613.763 bayt IPA içindeki `Payload/IronMan2.app/IronMan2` native ARM Mach-O doğrudan analiz edildi; executable GitHub'a yüklenmedi. Gerçek orijinal fonksiyonlar:

| Orijinal C++ fonksiyon | ARM VM | Kanıtlanan davranış |
| --- | --- | --- |
| `CNPC::isAttackState()` | `0xE1A20` | `this+0x2BC` durum grafiğinden seçilen son node `+0x0C` **4 veya 5** ise true |
| `CNPC::isMelee()` | `0xEA220` | **Temel CNPC sınıfı** doğrudan 0 döndürüyor; türetilen override farklı olabilir |
| `CNPC::SetState(int,int)` | `0xE1694` | `this+0x680` mevcut öncelik `<=` yeni int priority olursa yeni state `this+0x684`, yeni priority `this+0x680` yazılıyor; eşitlikte overwrite mümkün |
| `CNPC::shootFrequencyDone()` | `0xE19E0` | native `0x54D84` saat değerinden `this+0x6DC` son atış zamanını ARM 32-bit modüler çıkarma; kalan değer işaretli olarak `this+0x56C` atış aralığını aşıyorsa true |
| `MissionConditionKill::EvaluateComplete(int)` | `0xCB5B8` | `this+0x50` tamamlanma önbelleği true ise true; özgün `+0x6C` hedef vector `+8` sayısı <=0 ise true ve önbellek 1; liste doluysa orijinal actor virtual call'larına ihtiyaç var |
| `GS_GamePlay::UpdateSkyBox(int)` | `0xC2810` | orijinal renderer global nesne varlığı ve renderer `+0x554==1` koşulu, ardından `GS_GamePlay+0x10` sky düğümünün varlığı; gerisi orijinal virtual sky movement; **genuine shader / sky texture alignment çıkarılmadı** |

Diğer özgün durum operatörü `CNPC::isInState(int,int)` `0xE16C8` kaynak node/list traversal `+0x6BC` ve `0x20000` node flag içeren karmaşık koşullar kullanıyor. Bu daha tam izlenmediği için bilerek sahte genel `isInState` yazılmadı.

[Gerçek G123 ARM opcode CI başarılı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39020154641). Kaynak: `research/b24_unified/g123_native_NPC_real_state/`.

## G124: Özgün C karşılıklarını gerçek Vita oyununa bağladım

- `research/b24_unified/g124_2010_real_NPC_source_predicates/b24_g124_real_original_NPC_source_state.h` ve `.c` içindeki `b24_g124_source_npc_is_attack_state`, `b24_g124_source_npc_set_priority`, `b24_g124_source_npc_fire_cooldown`, `b24_g124_source_npc_base_is_melee`, `b24_g124_source_kill_mission_early_branch`, `b24_g124_source_gameplay_sky_update_gate` native original ARM'nin kanıtlanan birebir küçük koşullarını uygular.
- `UNKNOWN/FALSE/TRUE` üç durumlu sonuç kritik: source runtime field, orijinal type ve virtual actor davranışı eksikse sahte cooldown/hit/mission complete üretmiyor.
- Son atış aralığı C signed integer taşmasıyla UB yaratmadan orijinal ARM modulo 2^32 çıkarma + signed karşılaştırmayı modelliyor.
- Patch `g124_add_native_original_2010_npc_state_to_real_Vita_game_ELF_ONLY.py`, yeni `B24_G124_ORIGINAL_NPC_SOURCE_RULES=ON` source feature bayrağını ana `im2_beta` CMake'e ekliyor; eski G75/B14 fizik sahibi, G111/G82 combat, G108 map collider, G106 gerçek MarkV 248 klip ve G71/G73/G95 kaynak ışık/sky ile birlikte **gerçek ARM ELF olarak linkleniyor**.
- **[G124 tam VitaSDK ARM oyun link + host native source tests BAŞARILI](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39020471484)**.
- **VPK yok**, gerçek Vita ekran testi yapılmadı.

**Önemli:** G124 motorun derlenen kaynak kodunda artık orijinal NPC temel koşulları var; ancak **Level1 içinde gerçek NPC actor oluşturma, CNPC'nin 0x6BC/0x2BC linked list state machine'i, tüm `UpdateState*` dalları, spawn/event, gerçek 26 `Damage` sayı ve hitframe, ölüm/mission ilerleme tam portu henüz yapılmadı**. Dolayısıyla sahnede kendi başına gezen saldırgan düşman yok, G92 ölümsüz tek dummy devam ediyor. `GS_GamePlay::UpdateSkyBox` source gate'ten özgün SkyBox render shader'ın çözüldüğü sonucu çıkarılamaz.

## G112B / G119: gerçek orijinal iOS oyunu touchHLE/GDB

- Resmi touchHLE v0.3.0 Linux kaynak derlemesi, orijinal sahibi IPA `IronMan2` ARMv6, native dyld yükleme ve `gdb-multiarch` gerçek ARM remote port 9001 başlangıcı **doğrulandı**.
- [G119C GDB postmortem](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39019984077): Linux GDB orijinal iOS Mach-O'nun `file` olarak tanıtılmasını desteklemiyordu; bu kaldırıldı; seven gerçek 2010 metoda native breakpoint bağladı. `Cannot execute this command while the target is running` hatası gösteriyor.
- [G112B son analiz](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39017745551): `ALSOFT_DRIVERS=null`, `SDL_AUDIODRIVER=dummy` koşullarında bazen `thread 1 already unlocked` panic. Daha önce açık kaynak ses aygıtı yokken `Could not open OpenAL device` hatası alınmıştı. GDB server açılsa bile **orijinal attack breakpoints hit=0**; sahada oyun combatına ulaşıldı denemez.
- G125 yeni **sanal PulseAudio null sink**, `ALSOFT_DRIVERS=pulse`, `SDL_AUDIODRIVER=pulseaudio` ile orijinal sahibin oyununda gerçek iOS combat-event trace çalıştırma denemesi için CI başlatıldı: `.github/workflows/g125-2010-original-touchhle-PulseAudio-virtual-device-GDB-combat-NO-VPK.yml`. Sonuç başarılı dedikten önce `gdb_original_ios_method_breakpoint_hit_total` ve oyun sahnesine ulaşım delili gerekir. Private IPA her durumda GitHub runner sonunda silinir.

## G121 / G122 özgün NPC kaynak fonksiyon adresleri

G121 gerçek 2010 Mach-O source sembol taramasında 1.467 NPC/AI, 1.596 mission/trigger ve 3.863 render/light anahtar kelime eşleşen native sembol bulundu; bu sayılar gerçek benzersiz oynanış mekanik sayıları **değildir** (C++ STL/data ve duplicate etiket dahil). G122 filtresi 194 gerçek C++ `CNPC`, `AIHover`, `AILand`, `BigMachineNPC`, `MissionConditionKill/Protect`, `SpawnPoint`, `TriggerEntity`, `Material` ve `GS_GamePlay` metod adresi seçti. Tam native FSM port için hedefler `CNPC::UpdateStateAttack 0xE5868`, `CNPC::UpdateStateHurt 0xE7190`, `CNPC::OnDie 0xE1BA8`, `CNPC::OnSpawn 0xE1B4C`, `MissionConditionKill::EvaluateComplete 0xCB5B8`.

Kaynak kanıt [G122 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39017544055).

**Devam hedefi**: G125 ses + GDB'yi gerçek oyunda çalıştırıp iOS `AttackEntity::LoadFromFile::GetParamValue("Damage")` post-call 0xA9468'de +0x60 gerçek sayıları yakala; olmazsa kaynak disassembly ile genuine CNPC 0x6BC/0x2BC state node walker ve 26 CLARA TLV field ↔ class ID inheritance alias çöz; hiçbir belirsiz numeric damage'i kullanma. Gerçek Vita VPK ancak kullanıcı açık izin verirse.
