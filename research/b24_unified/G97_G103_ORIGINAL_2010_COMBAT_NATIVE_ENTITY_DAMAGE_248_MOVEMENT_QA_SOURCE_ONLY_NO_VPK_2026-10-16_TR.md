# G97–G103 — Özgün 2010 iOS combat kaynak kanıtı, Mark V 248/248 galeri, eksiklerin dürüst durumu

**Tarih 16 Ekim 2026 · dal `feature/b24-unified-gameplay` · yeni VPK YASAK.** Kullanıcının "kalan büyük eksikleri kapat" talebine istinaden gerçek GitHub'da kaynak kodu/CI çalıştırıldı; tamamlanamayan özgün 2010 değerler, görev AI ve Vita donanım testleri varmış gibi sunulmaz.

## G97–G97B — 2010 native saldırı/temas motoru gerçek kaynak zinciri

Orijinal kullanıcı IPA'sı (248.613.763 bayt) CI runner'da geçici açıldı. ARM Mach-O gerçek fonksiyon adresleri ve opcode grafiği:

- `AttackEntity::LoadFromFile(EntityData*)` 0xA934C; ilk analizde **105 özgün ARM komutu/14 int-bool param read**.
- İki farklı `AttackEntity::DoAttack` overload 0xA960C / 0xA9544; ikinci overload doğrudan `ProjectileMgr::AddProjectile` çağırıyor.
- `AttackEntity::DoProjectileAttack` 0xA9298 → özgün `ProjectileMgr::AddProjectile`.
- `ProjectileEntity::UpdateCollisions` 0xB6518 → `ActorManager::FindActorsInRange`, `Entity3D::FindActorsInRangeLight`, `ProjectileEntity::HitImpactActor`.
- `ProjectileEntity::HitImpactActor` 0xB44B0 → çoklu `ActorManager::ValidateActor`, `Actor::CanAttack`; tüm hit branch'lerinin semantiği henüz tam çözülmedi.
- `ProjectileEntity::DoSplashDamage` 0xB4BF0 → actor search + `Actor::CanAttack`.
- `CNPC::OnHit(Actor*,int,float)` 0xE7340; özgün hit/hurt tepki sisteminin önemli kaynağı, fakat Vita'ya NPC AI olarak bağlanmış değil.
- `Actor::Damage(float)` 0xD9194: önceki G76/G77 iki-resource native düzeltmesi mevcut.
- `MainCharacter::UpdateMeleeAttackState()` 0xF1DE4: özgün G89/G90 13 durum ID / 8 branch hedefi önceki kaynak kanıtı.

[Gerçek G97 native ARM CI 38970880539](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38970880539); [G97B metadata çağrı grafiği CI 38970880506](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38970880506).

## G98 — Gerçek, artık tipli 14 AttackEntity veri alanı

Birinci çözümleyici native ARM compiler'ın `ldr register,[pc,delta]; add r1,pc,register` position-independent cstring yapısını tanımadığı için 0/14 isim bulmuştu. **G98B** doğru ARM PC-relative signed delta'yı çözdü: **14/14 gerçek özgün alan adı**.

Orijinal `EntityData::GetParamValue(char const*, int*/bool*)` çağrıları içinde:
- `AttackType` **int**
- `Trail` **int**
- `UseBillboardForTail` **bool**
- `TailEmmiterId_Billboard` **int**
- `UseBillboardForDetonation1` **bool**
- `DetonationEmmiterId1_Billboard` **int**
- `DetonationEmmiterLife1` **int** (kod iki farklı native read'de aynı kaynak adı kullanıyor, typo olduğunu varsayma)
- `UseBillboardForDetonation2` **bool**
- `DetonationEmmiterId2_Billboard` **int**
- `Damage` **int**, özgün `add r2,r4,#0x60` → **AttackEntity gerçek instance field +0x60**;
- `TailEmmiterId` **int**
- `DetonationEmmiterId2` **int**
- `DetonationEmmiterId1` **int**.

**Bu kaynak verisi oyunla ilgili önemli bir somut atılım ama henüz 26 farklı saldırının sayısal hasarları DEĞİL.** Değerler, `EntityData` property'nin doğru BCLARA sınıf/kalıtım kaydına eşlenmesini gerektirir.

[2010 gerçek G98/G100/G101/G102 native ARM ve BCLARA CI 38970880530](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38970880530).

## G100–G102 — 26 gerçek Attack kaydının bütün native alan sınırları parse edildi

Orijinal `level1.bclara` dosyası; 26 `Attack`, 13 `Weapon`, class 108 `Attack` typed scene instance kaynağı. Gerçek instance gövdesinin sayılmış ve boyutlu serializer dizisi ayrıştırıldı:

- Her 26 Attack için **54 adet sınırı doğrulanmış, u16 uzunluk önekli kayıt**; 26/26 parse başarılı.
- `Attack` class 108 kendi yerel iki native property'sini bildiriyor: `AttackType` (native tag8) ve `Position` (tag109). İlk iki serializer kaydı bunlarla tutarlı (4 bayt AttackType ve 92 bayt Position).
- Özgün `Damage` declarer'i yalnız doğrudan `Attack` class108 değil; CLARA class98 `BoxCollisionData`, class110 `Object` ve class213 `Position` şemalarında `Damage` property type tag2 var. G102 kayıtları bu gerçek class sahibi bağlarını koruyor.
- Class110 `Object` şeması **23 yerel property** içeriyor (`Damage`, `Splash`, `SplashRadius`, `UniformSplashDamage`, `ImpactTimer` vb.).
- **HENÜZ çözülmeyen köprü:** Attack id108 instance'ının 54 serializer slotu ile class110 Object damage tag'i arasında özgün `EntityData` kalıtım/özellik dispatch bağlantısının kanıtlanması. Bu yüzden slottaki rastgele int'e `Damage` denip 26 sahte hasar sayısı yazılmadı.

Kaynakları tekrar çalıştırmak için:
`research/b24_unified/g97_source_attack_hit/g97_original_2010_attack_hit_damage_native_xrefs.py`,
`g97b_original_attack_method_edges_and_fields.py`,
`g98_actual_native_AttackEntity_typed_property_string_refs.py`,
`g100_native_original_level1_damage_field_serialized_probe.py`,
`g101_original_2010_26_attack_verified_size_prefixed_stream_probe.py`.

## G103 — Gerçek özgün Actor::CanAttack kısmi koşulları

G97'nin özgün ARM **`Actor::CanAttack(Actor*)` 0xD9278** fonksiyonu şunları doğruladı:

- saldırgan nesnesi `+0x2B8` int actor category slotunu; hedef de `+0x2B8` slotunu okuyor;
- saldırgan kategori **0**: hedef kategori 2 → false; hedef kategori 3 → true; hedef kategori 4 → hedefin özgün virtual method +0x17C sonucuna bağlı (BİLİNMİYOR); diğer kategoriler → true;
- saldırgan kategorisi 0 değil ve 1 değil → false;
- saldırgan kategori 1 → kaynak `+0x158` allow-list pointer / `+0x160` liste uzunluğu ve virtual fallback; exact input nesneleri yoksa BİLİNMİYOR.

Kısmi gerçek koşullar `research/b24_unified/g103_partial_original_actor_attack_permission/b24_g103_verified_original_actor_attack_classification.[ch]` içine **fail-closed UNKNOWN tri-state** ile taşındı; örnek sınıflama bir gerçek iOS karakterin category numarasını *bilmediğimiz* için otomatik düşmana gerçek hasar açmaz. Unit `test_b24_g103_verified_original_actor_attack_classification.c`. Vita ARM object C derlemesi `.github/workflows/g103-original-2010-actor-canattack-native-source-vita-arm-object-NO-VPK.yml` içinde doğrulanır.

## G99 — 248/248 özgün Mark V hareket önizleme galerisi TAMAMLANDI

Mevcut başarılı G96 Stark Expo WebGL2 + 2010 asıl BRES/PVR 296 mesh/24 atlas + orijinal `MC_SuitCase.tga` UV + 629 gerçek Mark V skinned vertex sahnesine G85'in **248/248 orijinal animasyon IM2V akışı** eklendi. 248 gerçek kaynak animasyonu toplam **5.268 adet 20 Hz frame / 39.767.824 bayt source IM2V pose**; G99 HTML kullanıcı arayıp seçip oynatabiliyor. Aynı G83 kaynak rota/bölüm geçişi ve G91 dummy korunuyor.

[**Başarılı G99 tam 248 animasyon 3B kaynak tarayıcı testi 38970071693**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38970071693) · [**İndirilebilir tüm 248 animasyon galerisi, özgün kaplama/harita, ekran görüntüsü ve QA artifact 12075314691**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38970071693/artifacts/12075314691).

Chrome WebGL2 gerçek açılışta tüm 248 animasyon verisi, hareket playback `ground_combo_2`, 629 vertex ve 902 source Mark V üçgen, orijinal PVR kaplama ve sıfır GL error doğrulandı.

**Açık ayrım:** 248/248 fiziksel animasyon kaynağı *browser host'ta seçilebilir* ama **248/248 animasyonun gerçek Vita oyun-state/tuş/yetki geçişi çözülmüş değil**. Tüm zırhlar ve 338 player aile klibiyle donanım gerçek oynanabilirlik testi eksik.

## Devam eden büyük eksikler ve RELEASE durumu

`research/b24_unified/g83_final_vpk_gate/READINESS_STATUS.json` içinde **1/11 katı yayın kanıtı kapısı** doğrulanmış durumdadır. Bu bir yüzde oyun tamamlama ifadesi değildir.

1. `MainCharacter::UpdateMeleeAttackState` 13 state entry, native Action callback/cancel/combos ve G83 real input / G8 player anim full eşlemesi.
2. Gerçek iOS orijinal melee hit-active kareleri, `Damage` property ve 26 class108 Attack / 13 Weapon serialized typed integer değerlerinin **doğrudan eşlenmesi**; NPC can değerlerinin orijinal tipli alanlarına bağlanması.
3. Native gerçek `ProjectileEntity`/repulsor/missile/Unibeam collision/splash/hit timing/weapon audio, target hurt/death ve full drone AI & Lua Media Mayhem event dalgaları.
4. Gerçek Vita G95 sunlight/city shader, kamera/flight/swept collision/hitbox görsel ve FPS donanım testleri; gerçek 2010 iOS touchHLE mekanik input/camera parity (eski mutex-bloğu hâlâ çözülmedi).
5. Bütün 248 Mark V ve diğer armor/338 player kliplerinin fiziksel PS Vita C loader ve G83 route QA'sı.

Önceki G95 gerçek **Vita ARM `im2_beta` full ELF source link SUCCESS**: [38967068698](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38967068698); G99 source WebGL2 original 248 viewer SUCCESS. **Yeni VPK/eboot yok, gerçek Vita cihaz sürümü kurulup test edilmedi.** Tam oyun bitti iddiası yapılamaz.

**Sıradaki en yüksek değerli teknik adım:** native `EntityData::GetParamValue` sınıf kalıtım/param lookup + CLARA gerçek class110 Object inheritance'ının Attack class108 54 alanına bağını çıkar; sayısal `Damage` kaynak integer'ları şema eşleşmesini kesin doğrulamadan ana gameplay damage açma. Ardından G97 2010 native projectile callgraph'ı B24 G82 gerçek actor hit eventine eşle, düşman rig/hurt anim ve mission Lua AI entegre et. Gerçek PS Vita VPK yalnız kullanıcı açıkça izin verince ve kalan kabul kapıları geçince üretilecek.
