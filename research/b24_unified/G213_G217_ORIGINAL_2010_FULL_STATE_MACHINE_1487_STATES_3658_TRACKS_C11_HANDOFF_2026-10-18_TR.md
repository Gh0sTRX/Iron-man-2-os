# G213–G217 — iOS Iron Man 2 (2010) özgün 55 StateSet / 1487 StateData / 3658 StateTrack tam kaynak kurtarma

**18 Ekim 2026 · `Gh0sTRX/Iron-man-2-os` · `feature/b24-unified-gameplay` · VPK YOK.**

## Kesin kaynak kurtarma

[G213B başarılı tüm kaynak testi](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39135273483): Kullanıcının orijinal iOS 2010 `Payload/IronMan2.app/states` ikili dosyası **361393 / 361393 bayt, ilk byte'tan EOF'a, sıfır rastgele skip** ile orijinal `StateDatabase → StateSetData → StateData → StateTrack` native 2010 ARM kurucu düzenine göre tamamen ayrıştırıldı. **55 gerçek StateSet, 1487 gerçek StateData, 379 orijinal AttackType, 3658 StateTrack**. 379 AttackType değeri/orijinal byte offset eski G207 listesiyle 379/379 birebir. G212 ilk kaba taramadaki 365 `Attack/attack` track adayı **365/365** olarak doğrulandı; gerçek tam parser **4 yeni** kayıt buldu: toplam **369 gerçek named attack track**, 0 G212 false positive.

G213B orijinal ARM 0x9CBAC/0x9CCB8/0x9CD2C geçiş kümesindeki ilk isimsiz kaydı, son trailing name alanını ve koşullu string okumasını çözerek IronMan::Idle data kaymasından kurtuldu. İlk parser testinde `source_original_state_name` yanlışlıkla `Default` son bayrak alanıyla eziliyordu; son successful CI'da bu değişken hatası giderildi, 1487 gerçek state adı korunuyor. `0:Idle`, `1:Jump`, `2:Move_Walk`, `3:Move_Run`, `13:Float_Move`, `14:Fly` kesin orijinal adlardır.

**Orijinal zırh veri kümeleri:** `IronMan`, `IronMan_suitcase`, `Warmachine`, `stealth` her biri **194 StateData, 612 gerçek StateTrack, 56 AttackType state**. Tam G213B kaynak JSON GitHub Actions artifact içinde. Bu bulgu Vita cihazında hareket düzeltilmiş olduğu anlamına gelmez.

## Gerçek orijinal saldırı/ARM kaynak köprüsü

[G214 başarılı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39133010389) — 56 authored AttackType değerleri IronMan/Suitcase/Stealth = `0:24, 1:15, 2:11, 4:6`; Warmachine = `0:24, 18:15, 25:11, 4:6`. WM 26 pozisyonda farklı orijinal u32 kayıt numarası kullanır. Bu değerleri birbirine kopyalayıp Vita için sahte silah inputu üretme.

[G215 başarılı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39133228342) gerçek native `MainCharacter::DoAttack` jump table kaynağı ile eşlendi: IronMan `AttackType 1` ve WM `18` **aynı ARM hedef 0xF6930**, IronMan `2` ve WM `25` **aynı ARM hedef 0xF6648**. Tüm 56 kayıt ARM branch hedef sırası aynı, silah/animasyon/hasar çıktısı aynı olduğu kanıtlanmadı.

[G216 başarılı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39134560344) 38 gerçek orijinal ARM komutu: ortak branch `0xF6930` özgün runtime actor register `[r4+0x5e4]` değerleri 0/1/2 durumuna göre ayrılıyor, seçici `r5` belirli kaynak koşullarda `0x10/0x16` oluyor. Özgün `WeaponMgr::GetCurrentWeapon` ve diğer ortak branch `0xF6648` içinde gerçek virtual method +0x128 mevcut. Bu enum değerlerinin user touch, füze, repulsor, Beam veya `_M` silah kimliğine eşitliği **henüz ispatlanmadı**.

## G217 — Vita portta ileride kullanılabilecek gerçek 2010 READ-ONLY C11 kaynak tablosu

[G217 host C11 derleme/test + PNG başarılı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39135629451). Kaynak üreteci: `research/b24_unified/g217_real_2010_native_states_to_port_data/g217_make_authentic_original_2010_suit_motion_attack_event_source_header.py`. Tam gerçek G213B JSON'dan **4 × 194 = 776 original state**, native ID, tam state adı, AttackType (varsa), type, loop, next_state ve toplam track sayısını `b24_g217_AUTHENTIC_original_2010_iOS_source_states_ONLY_NO_VPK.h` başlığına ve JSON'a yazdı. Kaynak dört suit içinde gerçek `attack`, `Attack`, `trail` işaretlerine ilişkin **224 authored event satırı** C11 header'a alındı. Sunulan statik PNG oyun ekranı değil, orijinal event başlangıç değerleri grafiği.

| Orijinal native StateData index | Gerçek state adı | IronMan/MarkV AttackType | WM AttackType |
|---:|---|---:|---:|
| 0 / 2 / 3 | Idle / Move_Walk / Move_Run | — | — |
| 13 / 14 | Float_Move / Fly | — | — |
| 24 | Attack_Float_idle | 1 | 18 |
| 40 / 42 / 44 | Attack_Ground_COMBO1 / COMBO2 / COMBO3 | 0 | 0 |
| 65 / 66 | Attack_M_Float_idle / Attack_M_Ground_idle | 2 | 25 |
| 84 / 85 / 86 | Attack_Ground_Beam_prepare / Beam / Beam_out | 4 | 4 |
| 88 / 89 / 90 | Attack_Float_Beam_prepare / Beam_out / Beam | 4 | 4 |

**Gerçek kaynak `attack` StateTrack ham başlangıç değerleri** — IronMan: `COMBO1 = 300`, `COMBO2 = 200`, `COMBO3 = 500`, `Attack_M_Ground_idle = 260`, `Attack_M_Float_idle = 250`, `Attack_Ground_Beam_out = 413`, `Attack_Float_Beam_out = 507`. Orijinal Track [0] başlangıç [4] duration ve [8] sınıflandırılmamış int değerlerini içeriyor. **Bunlar henüz ms, hasar çarpma veya projectile/sound spawn anı olarak doğrulanmadı.** Kaynak genelleyip oyuna girdi uydurulmadı.

**Özellikle C1L1 Mark V uçuş kısıtı:** `IronMan_suitcase` StateData içinde `Fly` bulunması, ilk Expo görevinde özgün Lua izin/görev motorunun uçuşu açtığını kanıtlamaz. Eski gerçek cihaz gözlemi root movement yok, uçuş hareket var; kaynağı çözmek Vita input ve fizik bugı ortadan kaldırmaz.

## G218 hedef ve kalan kullanıcı cihaz problemleri

Tamamlanmamış: özgün `StateTrack` üçüncü u32 semantiğinin, gerçek WeaponDB/AttackEntity attack/damage, `MainCharacter::DoUniBeamAttack`, `MainCharacter::UpdateMeleeAttackState` ve oyun touch event/state geçiş çağrılarının doğrulanması. Sonra gerçek G217 data modelini G83/G169 tek özgün IM2V animation owner'a **source-backed** bağla. Dört suits orijinal M/Beam/Combo oynatma ve uçuş saldırı izinleri ayrı test gerektirir.

Vita üzerinde **henüz düzelmiş sayılmayacak**: yürürken world/root yerinde sayma, araba yanında küçük kalan karakter/harita ölçeği, özgün çevresel ışık gerçek gölge/skybox/ay, War Machine'in omuz silahları, fiziksel melee hitbox/hasar, C1L1 intro QTE/cutscene ve tam mission flow. **G213–G217 original source + host C11 derlemesi, yeni Vita ELF veya VPK yok.**