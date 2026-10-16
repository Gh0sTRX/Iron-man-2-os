# G81–G83 — Orijinal Iron Man 2 2010 IPA tam moveset, gerçek touchHLE oyunu, birleşik combat ve VPK engeli

**Tarih:** 2026-10-16. **Kullanıcı talebi:** 2010 iPhone orijinal oyunun bütün hareketleri, komboları, yakın dövüşü, hasar, silah, düşmanlarla savaş ve stage akışı G73/G75 oyunuyla birleşecek. Eski iyi harita/oyun performansı korunacak. **Tamamlanmadan yeni VPK oluşturulmayacak.**

## I. Bu tur GERÇEK orijinal iOS uygulaması touchHLE ile çalıştırıldı
- Kullanıcının bağlı Drive'ındaki doğru orijinal **IronMan2_1.0.0_ios_2.2.1.ipa**, **248,613,763 bytes**, `com.gameloft.IronMan2` / CFBundleVersion 1.0.0 doğrulandı. Kullanıcının IPA'sı Github deposuna veya dışarıdaki üçüncü taraflara yüklenmedi.
- Eski GitHub G62 CI'nda derlenen orijinal touchHLE v0.3.0 Linux runtime artefact `12015633037` yerel çalışma ortamında açıldı. `touchHLE --help` çalıştı.
- Linux **Xvfb/llvmpipe GLES1-on-GL2** üzerinde gerçek orijinal oyun çalıştırıldı. İlk denemede OpenAL device başlatılamadığı için panic oldu. `ALSOFT_DRIVERS=null` eklendi; özgün 2010 başlık ekranı gerçek çizildi, ~35–40 FPS değerleri görüldü.
- touchHLE'ye penceredeki (640,400) koordinatına **gerçek simüle parmak tıklaması** yapıldı; oyun `New Game / Continue / Options` ana menüsüne geçti. Ardından (680,280) `New Game` seçildi ve gerçek **LEVEL 1 - Media Mayhem / STARK Industries** brifing ekranı **yükleme %40 ve %99** aşamalarında görüntülendi.
- Linux yazılımsal ekran sürücüsü üzerinde sonraki aşamada touchHLE'nin `src/environment/mutex.rs:212` `Attempted to unlock non-error-checking mutex ... already unlocked!` hatası emülatörü durdurdu. **Gerçek 2010 savaş gameplay'i, hit inputları, orijinal kare olayları ve orijinal düşman saldırısı emülatörde henüz gözlemlenmedi.** touchHLE topluluk veritabanında orijinal iOS 1.0.0 beş yıldız destek gözlemi var: https://appdb.touchhle.org/apps/451; fakat bu laboratuvarın Linux/G62 build'i henüz level1'e giremedi.
- Kullanıcının orijinal IPA'sı kaynak olarak korundu; ne yeni Vita uygulaması ne VPK yapıldı.

## II. 972/972 orijinal ANIM ham kaynak kaydı çözüldü — DOĞRUDAN MEVCUT ORİJİNAL IPA
Yerel containerda orijinal `Payload/IronMan2.app/anims` native index, 972 dosyanın byte aralıkları, iskelet adları, tüm XYZ konum ve quaternion rotation frame zamanları yeniden decode edildi.

- Orijinal `anims` blob SHA256: `daf843660a2ddc66e2189683961e020335c88d3edc522bfd03db444acc85113b`.
- Gerçek orijinal kaynak figür dosyası adlarından: **248 IronMan**, **56 WarMachine**, **34 UnderwaterArmor**, **9 UnderwaterObject**, **398 Drone/NPC/Boss**, **227 other scene/vehicle/NPC = 972**. İlk 248+56+34 = **338 oyuncu-zırh animasyon adayı**, 972 bağımsız oynanabilir hareket değil.
- Dönüş/poz, süre, kanal sayısı ve SHA256 kaydı 972/972 listesinde; 338 oyuncu alt listesi ve CSV ayrıca çıkarıldı. Sıfır süreli oyuncu klipleri: **5**, runtime sürekli döngü olarak kullanılmamalı.
- **İKİNCİ BAĞIMSIZ G81 KAYNAK AUDIT EŞLEŞMESİ:** önceki kaynak B18 304/304 kayıt adı ve kanal sayısı ham orijinal IPA ile tam eşleşti. İlk denemede dört `Run_Att_end/ready` ve `Walk_Att_end/ready` süre farkı çıktı; sebep bu animasyonların ilk keyframe zamanı sıfırdan sonra, G81'de duration = max - min hatası olmasıydı. Doğru kaynak total anim süresi = **son mutlak frame tick'i**; düzeltildi, B18 ile **304/304 isim, süre ve kanal sayısı tam eşleşti**.
- B18 `IronMan_Ground_Combo_1/2/3` 266/300/500ms gerçek, `ComboPower_a,aa,aaa,ab...` dalları kaynak isim ve süre kanıtı. **Kombonun oyundaki tuş ve hit-frame grafiği henüz decode değil.**
- GitHub kaynakları: `g81_complete_moveset/g81_original_972_all_moveset_manifest.py` (gerçek IPA binary parser; source duration patched), `g81_existing_304_authenticated_legacy_catalog_host.py` (eski bağımsız 304 doküman), G81 304 host Actions https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38942170230 (SUCCESS). Gerçek 972/972 parse yerel container üzerinde başarıyla çalıştı. **G81 tam 972 için GitHub CI başarı iddiası yok; CI tetikleme engellendi; 972 yerel test sonucu ayrı.**

## III. G82 hakiki kaynaklardan birleşik combat modülünün ilk adımı
Yeni `g82_original_combat/b24_g82_original_combat_coordinator.[ch]`:
- Var olan G8 gerçek orijinal 2010 `Ground_Combo_1/2/3` kliplerinin 266/300/500 ms açma/buffer/sonlandırma zincirini kullanıyor.
- G77 gerçek orijinal `Actor::TestMeleeHit` 0.5× model BBox köşegen broadphase matematik modülünü kullanıyor.
- G76 gerçek orijinal `Actor::Damage(float)` 2 float dayanıklılık alanı ve orijinal +0x3BC/+0x394 branch matematiğini kullanıyor.
- Kaynak **hit-frame** ve **gerçek AttackEntity numeric Damage** doğrulanmadığından koordinatör varsayılan olarak hiçbir sahte hit üretmiyor. Test fixture'ı ile input verildiğinde üçlü kombo + önce birinci sonra ikinci dayanıklılık kaynak matematiği doğrulanıyor; *gerçek gameplay hit-frame teyidi değildir*.
- GitHub CI https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38941589551 (SUCCESS) host + PS Vita ARM **yalnızca kaynak object** derlemesi. G82 henüz gerçek G75/G73 Vita oyun sahnesine fiziksel olarak bağlanmadı; eski çalışan uygulama korunuyor.

## IV. Mark V ve kalan zorunlu işler
- Orijinal Mark V bir **629 ana-weighted-vertex** `suitcase.bdae` rigidir; IronMan 802v XYZ klipleri doğrudan kopyalanmamalı. G68 önceki projede bu Mark V için **7 özgün orijinal 2010 re-skinned stream** hazırlamıştı, tam 248 clip Mark V için GPU/live playable değil.
- `b24_all_player_304_original_bake.py` 304 orijinal IronMan/WarMachine klibini B13 bind-matrix ile gerçek skinlenen IM2V streams şeklinde hazırlamış eski kaynak; G10 ayrı MarkIV/Stealth/MarkV source-rig retarget yönlendirmesi var. Bu branch'te **gerçek tam Mark V moveset 248/248 fiziksel oyun QA geçmedi**.
- Orijinal `AttackEntity::LoadFromFile` ve `ProjectileEntity::LoadFromFile` 45 kaynak property adı; C1L1 26 gerçek `Attack`, 13 `Weapon` nesnesi ve WeaponDB array; per-weapon DAMAGE değerleri native instance property veri alanlarıyla gerçek kaynağa bağlanmadı.
- Orijinal oyun kodundaki `StartMeleeAttack`, `UpdateComboAttackAction`, `StartThrow`, `UpdateJumpKickAttackState`, `ThrowMissile`, `DoUniBeamAttack`, native enemy AI, touchHLE kontrolleri, gerçek G68 düşman render/AI ve Stage1 görev sonlandırma koşulları **tam birleşik gameplay haline gelmedi**.
- G73 güzel görünen 22k+ triangle Expo haritası, G75 kamera/yükseklik/çarpışma ve orijinal lighting kaynak testleri bir sonraki Vita sürümünde korunmalı; kaynak G82 ayrı host proof, yeni VPK yok.

## V. Kesin kullanıcı VPK talimatını yazılı teknik gate haline getirdik
- `g83_final_vpk_gate/g83_source_completeness_before_vpk.py` ve `READINESS_STATUS.json` zorunlu 11 kabul ölçütü.
- `--strict` herhangi doğrulanmamış bir satırda **bilerek başarısız çıkar**. Yenisi `.github/workflows/g83-verify-no-vpk-until-complete.yml` CI guard, **her şey tamam olmadan paketleme yok**.
- 2010 tüm moveset source catalog + doğru Mark V skin + gerçek bütün kombo branch input ve hit-frame/touchHLE replay + gerçek silah kaynak sayıları + enemy AI/hurt/death + Expo collision/light/camera + B24 full source host/Vita ARM testlerinden sonra kullanıcı isteğiyle **tek birleşik yeni TEST VPK** üretilecek. Şimdilik VPK üretilmeyecek.
