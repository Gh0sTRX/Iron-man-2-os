# G88 — Orijinal 2010 ARM/Lua combat kanıtı + tekrarlı hasar önlemi (VPK YOK)

Tarih: 2026-10-16. Dal: `feature/b24-unified-gameplay`.
Orijinal tek karakter fiziği B14, tek gerçek G8 animasyon sahibi, G83/G87 yer-uçuş geçişleri, G85 Mark V 248 dosya ve G68/G75 haritası korunur.

## 1. Gerçek, yeni G82 combat bug düzeltmesi

Önceki `B24G82Combat` sadece en son `last_contact_id + last_target_id` çiftiyle tekrar hasarı engelliyordu. Tek ve aynı source-observed event 700 için hedef **A → B → A** dizisi gelince A'nın ikinci kez vurulmasını engelleyemiyordu. Bu gerçek mevcut C kaynak akışı sorunudur; **2010 orijinal oyunda bu bug vardı anlamına gelmez**.

- `g82_original_combat/b24_g82_original_combat_coordinator.{c,h}`: bir combo aşaması için gözlenen, doğrulanmış 32 farklı `(event ID, target ID)` çifti tutulur. Eski A kaydı B hit'inden sonra kaybolmaz.
- Bütün 32 giriş dolunca açık kapasiteden eski kayıt çıkarıp A'yı tekrar vurmak yerine **fail closed** `NO_HIT` döner.
- 266/300/500 ms gerçek kaynak G8 combo fazlarının değişiminde seen ledger sıfırlanır; her orijinal faz ayrı tutulur.
- Kaynak hit frame, kaynak AttackEntity hasar sayısı ve kaynak Actor::CanAttack kanıtları hâlâ **üçü birden** gerçek event için zorunlu; herhangi biri yoksa hasar yok. Unit testte 1.0f ve enabled bayrakları **tamamen sahte TEST FİXTÜRÜDÜR**, orijinal 2010 verisi diye kullanılmaz.
- G82 eski testleri, G83 yönlü hareket/aim ve yeni `test_g88_interleaved_original_event_dedup.c` C11 `-Wall -Wextra -Werror -pedantic` testleri geçti.

Bu bounded guard boyutu **bizim güvenlik sınırımızdır**, Gameloft'un orijinal collision listesi olarak sunulamaz.

## 2. Doğrudan kullanıcının 2010 orijinal IPA'sında yapılan gerçek native araştırma

`g88_original_combat_source/g88_original_native_combo_event_xref_and_mission_permissions.py` orijinal sahibi tarafından sağlanan 248,613,763 baytlık iOS 1.0.0 IPA içindeki şifresiz orijinal Mach-O'dan C++ ARM kodunu **salt okunur** çözümler. Lua5.1 Level1 bytecode kaynak `G75` çözücü yeniden kullanılır. Gerçek lisanslı yürütülebilir dosya veya IPA CI artefaktına yüklenmez.

**Doğrulanmış özgün iOS ARM girişleri ve son komut okumaları:**
- `MainCharacter::GetCurrentMeleeAttackStep() const` **0xEA3B8**, **+0x824** native getter ofsetiyle doğrudan okuma.
- `MainCharacter::StartMeleeAttack(float)` **0xEE04C**, **3 gerçek 0x824 alan erişimi**; 5 bounded native call.
- `MainCharacter::UpdateComboAttackAction(int)` **0xF18E4**, 12 native call.
- `Actor::TestMeleeHit(Actor*)` **0xDFD94**; iki native call, önceden G77 doğrulanmış 0.5 BoundingBox scalar.
- `Actor::Damage(float)` **0xD9194**, kaynak G76/G77 iki bağımsız dayanıklılık alanı doğrulanmış.
- `WeaponDB::GetAttackEntityByIndex(int)` **0xAB3EC**, gerçek +0x30/+0x38 attack table pointer/count.
- Bu 6 ana metodun yanında, gerçek combonun counter/callsite izlerini veren 5 ilişkili C++ yöntem daha bulundu. **Henüz orijinal hit-active pencere veya button-buffer koşulu yeniden yapılandırılmadı.**

**Gerçek 2010 Level1 Lua5.1 `SetAttackTypeEnabled` parametreleri:**
- 11 ayrı görev callback'inde kaynak kayıt **(1.0, false)**.
- `MissionTutorial_missile_OnStart` PC205 üzerinde **(1.0, true)**.
- Toplam **12/12 kaynak native çağrı** yeniden doğrulandı. Tek bu bulgu *attack type index 1*'in repulsor/missile vb. hangi API enum olduğunu, gerçek runtime call sırasını veya hangi tutorial koşulunda çalıştığını kanıtlamaz. Kaynak PC çevresindeki if-opcode, gerçek çalışma zamanı predicate demek değildir; otomatik kilit açma henüz B16/G11'e bağlanmamalı.

GitHub Actions ilk G88 CI denemesinde orijinal sembol tablosunda aynı adrese işaret eden yinelenmiş kayıtlar nedeniyle başarısız oldu; gerçek kaynakta **aynı adresteki aliasları tek sayıp farklı adrese sahip çakışmaları reddeden düzeltme** ile orijinal 2010 IPA araştırma işi ikinci koşuda **SUCCESS**:
- [G88 başarılı gerçek iOS ARM/Lua CI run 38956768062](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38956768062)
- Gerçek metadata kaynak artefaktı [12070148997](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38956768062/artifacts/12070148997), 14 gün saklama; iki JSON, IPA/exe/audio bulunmaz.
- G82 ayrı native ARM/host regresyonu [38956260952](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38956260952) SUCCESS; G83 [38956261041](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38956261041) SUCCESS.

## 3. Tam oyun derlemesi ve VPK kuralı

Aynı yeni G88 workflow diğer bağımsız job'da `G75→G84→G85→G87` tekrar birleştirir; güncellenen gerçek `G82` multi-target safety modülüyle sadece Vita ARM `im2_beta` ELF target'ı linkler. **Oyun paketlemesi, `eboot.bin`, VPK, Vita gerçek donanım testi YOK.** **G88 son GitHub Actions run 38956768062 — HER İKİ İŞ SUCCESS.** Gerçek 2010 orijinal iOS Mach-O ARM/Lua kaynak araştırma işi ve diğer G75/G84/G85/G87/G88 birleşik oyun PS Vita ARM `im2_beta` **tam link** işi başarılı. Yalnız gerçek donanım çalıştırması yapılmadı. `*.vpk` yokluğu doğrulandı. Workflow sadece kaynak güvenilirliğini ölçer.

## 4. Yapılmayanlar ve sonraki öncelik

Henüz özgün 2010 hit-active kareleri, gerçek WeaponDB instance DAMAGE değeri, `StartMeleeAttack` native branch-state çözümü, gerçek Actor::CanAttack/SetAttackTypeEnabled tür ID köprüsü, NPC AI, touchHLE ilk görevin canlı vuruş kayıtları, SFX bağlama ve Vita hardware regresyonu bitmedi. **G83 11/11 VPK yayın kapısı KAPALI**.

Sonraki somut araştırma: real ARM 0x824 alanına yapılan yükle/store referanslarının branch data-flow'u ile kombonun izin/iptal/aktif saldırı sırasını yeniden oluşturmak; gerçek WeaponDB `AttackEntity` instance şeması üzerinden hasar alanına sahici typed path bulmak. Kaynak onayı olmadan hasar, düşman veya aktivasyon kareleri üretme.
