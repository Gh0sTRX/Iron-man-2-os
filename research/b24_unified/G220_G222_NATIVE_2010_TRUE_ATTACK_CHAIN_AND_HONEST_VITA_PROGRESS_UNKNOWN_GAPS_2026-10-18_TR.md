# G220–G222 — 2010 iOS Iron Man 2 özgün saldırı zinciri TAM yerli ARM doğrulama + PS Vita dürüst ilerleme/eksik listesi

**Tarih:** 18 Ekim 2026. **Kaynak:** kullanıcı orijinal iOS Iron Man 2 2010 1.0.0 IPA, C++ symbol table 32-bit ARM Mach-O, 55 original `StateSet` / 1487 `StateData` / 3658 `StateTrack`, Vita `Gh0sTRX/Iron-man-2-os` / `feature/b24-unified-gameplay`. **VPK YOK.**

## Gerçek başarı seviyesinin sınırı

Orijinal `states` ikili verisinin 361393 / 361393 baytını G213B tam doğrulukla çözdük (**55 set, 1487 state, 379 AttackType ve 3658 track**). Bu, **bütün oyunun/IPAnın %100 çözüldüğü** anlamına gelmez. G217 4 oyuncu StateSet × 194 = **776 özgün durum** ve `attack/Attack/trail` marker metadata'sını read-only C11'e aktardı. G218 bunu **gerçek Vita `src/main.c`** üzerinde yalnızca G8'in gerçekten yüklediği IM2V clip seçimine, tek B14 physics + G83 route + G169 beam + G8 animator düzenini BOZMADAN bağladı; [gerçek Vita ARM `im2_beta` ELF-only PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39137626303), [host PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39137626298). **Bu fiziksel Vita'da test demek değil.**

## G220 — tüm özgün 2010 ARM text ve doğrudan StateTrack event tüketicileri

[**G220 CI PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39140750863): 14164 özgün 2010 ARM method (1,081,168 ARM instruction) symbol-boundary tarandı ve **`StateTrack::GetEvent(int,int)` native 0xA14F0** için **beş kesin doğrudan BL çağrı** bulundu:

| Caller original CPP | Tam özgün çağrı adresi | Geri dönen index'in amacı hakkında güvenli yorum |
|---|---|---|
| `StatesMgr::IsInvulnerableState(State*,int,int)` | `0x9FA60` | Kaynakça invulnerable state değerlendirme |
| `StatesMgr::IsInvulnerableOrNonInterruptibleState(State*,int,int)` | `0x9FD5C` | Native source invulnerable/noninterruptible sorgusu |
| `StatesMgr::IsInXXXState(State*,int,int,char*,int)` | `0x9FFF8` | Kaynak state olay indeksini gerçek `entry[index].third u32` değere çevirebiliyor |
| `Actor::UpdateStateAttack(int,State*)` | **`0xDB684`** | Native olay seçimi ve aktör saldırı dispatch yolu |
| `WhiplashNPC::UpdateStateAttack(int,CNPC::NPCStateNode&,void*)` | `0x13D8C0` | Whiplash NPC saldırı state olay yolu |

İlk sadece symbol-biçimli all-ARM tarama başarısız oldu; yöntem ARM method sınırlarına göre düzeltildi, **başarılı CI gerçek symbol method corpus** ile 5 çağrıyı doğruladı. Bunlar doğrudan çağrılar; dolaylı/vtable/diğer inlined state tüketicilerinin tamamının bilindiği iddiası yok.

## G221 — AttackType ile gerçek original event payload C++ sanal çağrıya iletiliyor

[**G221 CI PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39141125765). G213B gerçek `StateData`, G219 orijinal `Actor::UpdateStateAttack` ARM opcodes ve G220 gerçek çağrı kaynaklarını birleştiren 21 komut-korunan native zincir:

1. `0xDB65C BL StateData::GetParam("AttackType",-1)`; kaynak ARM `0xDB660 CMP R0,#1`, `0xDB664 CMPNE R0,#18`, `0xDB668 MOV SL,R0`. Native AttackType özgün sayı olarak korunur.
2. `0xDB684 BL StateTrack::GetEvent` (0xA14F0); parametre önceki ve şimdiki gerçek state zamanlarından hazırlanır, dönüş **örtüşen olayın index'i** veya -1.
3. `0xDB690–0xDB6A4` gerçek `12×index` adres hesaplar, `0xDB6A4 LDRGE R2,[R0,#8]` **seçilen event'in üçüncü u32 alanını** `R2` register'ına yükler. Olay bulunmazsa `R2=-1`.
4. `0xDB6C8 MOV R1,SL` AttackType birinci C++ int argümanı; `0xDB6D0 MOV R0,R5` Actor `this`; `0xDB6D4/0xDB6D8` özgün `LDR PC,[R3,#0x110]` vtable dynamic call. Böylece kaynak `Actor::UpdateStateAttack` native `(AttackType,event third)` çağrı girişini hazırlar.
5. G221 exact owner authored data: IronMan/MarkV/WarMachine/Stealth özgün grupların **her birinde 56 gerçek AttackType-associated `attack/Attack` event numeric trio**. Third u32 source değerleri yalnızca **0/1/2/3**, lakin **hangi silah/hasar tipi oldukları henüz bilinmiyor**. Dağılım: IronMan `1:43,0:10,2:2,3:1`; MarkV `1:47,0:6,2:2,3:1`; WarMachine `1:44,0:9,2:2,3:1`; Stealth `1:47,0:6,2:2,3:1`. Bu, tüm oynanış anlarının 56 event olduğunu göstermez; authored source satır sayısıdır.

## G222 — original C++ vtable hedefi artık adıyla KESİN

[**G222 CI PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39141403533). Gerçek source `vtable for MainCharacter` ARM native `__const` **VM 0x4BD85C**, Itanium address point `vtable symbol +8`, runtime `vptr+0x110` = vtable symbol `+0x118`. Gerçek kod pointer `0xF64F8` — **`MainCharacter::DoAttack(int,int)`**! Bu, tahmin değil native bytes + C++ symbol alias kanıtı.

Aynı gerçek slot:
- Base `Actor` vtable `0x4BD474`: `Actor::DoAttack(int,int)` `0xDA5B8`.
- `WhiplashNPC` vtable `0x4C030C`: `WhiplashNPC::DoAttack(int,int)` `0x13C0D4`.
- `CNPC` vtable aynı `Actor::DoAttack` pointer'ı içeriyor.

**Artık güçlü kaynak zinciri kesin: `StateData.AttackType → StateTrack::GetEvent(previous,current) → event[index].third_u32 → MainCharacter::DoAttack(AttackType,eventVal)`.** Ancak *hangi `AttackType`/eventVal hangi silah, mermi, damage, recoil, animasyon ve isabet mekanizmasına gider* tam çözümlenmedi. G215 source IM id 1/2 ile WM 18/25 aynı native ARM switch hedeflerine gider fakat runtime state/weapon branch farklı, silahların aynı olduğu iddia edilemez. G177 original UniBeam `WeaponDB::GetAttackEntityByIndex(4)` ayrı kanıtlı; Stage2, Rush missile/rocket firing ile karıştırılmamalı.

## Kullanıcının bilmemizi istediği DÜRÜST ilerleme ve hâlâ yapamadığımız işler

| Sistem | Kaynaktan ne kesin? | Vita'da gerçekten ne yapıldı? | **Hâlâ çözemediğim / bilmediğim** |
|---|---|---|---|
| iOS 2010 `states` binary | **%100: 361393/361393 bayt; 55 set, 1487 states, 3658 tracks** | 776 suit state salt okunur G217/G218'e kaynak model olarak girdi | Oyun/IPAnın geri kalanının genel kurtarma yüzdesi **bilinmiyor** |
| Orijinal saldırı engine source | G220–G222 ile **AttackType+event payload→`MainCharacter::DoAttack` kanıtlandı** | Henüz C++ 2010 silah/hasar mantığı Vita B16'ya taşınmadı | Third u32 `0/1/2/3` hangi efekt/weapon/hit? Tam unknown |
| G83/G8/IM2V kaynak animasyon | B18/G8 original IM2V hareketler, MarkV original 248, WM M-ground 10, UniBeam MarkV/VI 12 clips mevcut | G83 tek G8 source animator; G218 G8 gerçekten yüklenmiş clip'i source state ile okuyabiliyor; Vita ARM ELF derlendi | Native iOS StateMgr state ↔ IM2V clip birebir **runtime çağrı ilişkisi** kanıtlanmadı; bazı WarMachine animasyonlar hâlâ eksik |
| Yerde yürüme/root motion | Gerçek `Move_Walk`=2, `Move_Run`=3 state kayıtları | B14 fizik, G171 host kaynak çarpışma düzeltmeleri mevcut | Kullanıcı cihazında karakter yürüme animasyonu oynuyor ama yerinde sayıyor; **root/world transform aktarımı çözülmedi**; yeni fiziksel test yok |
| Ölçek/model/harita | Original IM2T mesh ve Expo sahne data/map kaynakları bulundu; native G66C collision var | G168 ve G171 kaynak model/original collision denemeleri | Karakter araba yanında aşırı küçük; kaynak bind/world birimleri ve gerçek 1:1 ölçek **kanıtlanmadı** |
| World collision | Original source G66C, road source G159/G160, G171 sahte sculpture collider geri çekme | Birleşik ARM code ve host yürüyüş testi | Gerçek Vita tüm duvar/yol/merdiven/platform/karakter collider hardware regresyonu **yapılmadı** |
| Kamera/HUD | G83 G84 omuz kamerası, HUD overlay, nişan girişi kaynak rotası | Single main kamera ve G164 hero framing kaynak kodu | Gerçek iOS input rejimi, aim offset ve Stage2/Rush hard-device testi, pause tam QA **yapılmadı** |
| Çevre görselliği | Özgün sky mesh/PVRTC ve source atlas/texture assets, bazı α düzenleri kurtarıldı | GPU/VitaGL, G73 source sky, G164 sky framing ve G75 geçici ışık flagleri | Kullanıcı daha önce siyah skybox, yanlış ay, ışık/gölge yok, PNG kenar/alpha bildirdi: **Vita'da düzelmiş olduğu kanıtlanmadı** |
| Melee combo | `Attack_Ground_COMBO1/2/3` gerçek state/markers; G8 original three combo clips | G8 animasyon owner ve B82/G111 geçici combat rules var | Gerçek iOS hit window, collision hitbox, hedef reaction/damage, bütün melee chain varyasyonları **tam bilinmiyor** |
| Repulsor/Beam/rocket/WM | `AttackType` values/ARM targets; original UniBeam `WeaponDB index4`, source Beam1/2/3 and WM M-ground bank | B16 accepted shots, G169/G173 source Beam and G172 native WM M clips; one G8 animator | `M` suffix **füze olduğu kanıtlanmadı**, WM shoulder gatling/rocket/lock-on ve orijinal UniBeam damage/timing **tam değil** |
| Touch/ARM selector tüm kontrol | 26 switch targets source ARM kanıtlı, Input Lua `SetAttackTypeEnabled` özgün çağrı | Prototype Vita tuşları ve G84/B16 port controller | **26 AttackType ID'yi çözmek 2010 touch/gesture, analog/aim, weapon swap, hover/flight/rush, pause ve tutorial input'un tamamını çözmez**. Native input sampling ve original TouchHLE birebir kayıtları eksik |
| Chapter1 Mission/QTE | G137 original Mission000 Lua, G146 QTE çağrı zinciri, G147–153 gate data | Source-only game mission/cutscene/QTE prototipleri var | **C1L1 başlangıç QTE, Objective trigger, gerçek enemy AI, fail/retry, cutscene senkronu ve bitirme koşulu tam uçtan uca Vita'da çalıştırılmadı** |
| Ses | iOS original PCM/SFX data ve G144/G145 source audio kodu üzerinde çalışıldı | Host ve Vita ELF kaynak sisteme bağlı bazı parçalar | **Tüm sahne müzikleri, VO, repulsor/rocket/UniBeam ve cutscene seslerinin birebir 2010 dispatch'i kanıtlanmadı** |
| PS Vita oynanabilir demo | C kaynak modülleri ve VitaSDK birleşik `im2_beta` ARM ELF derlenebiliyor | Son birleşik ELF [G218 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39137626303) | **Son sürümün gerçek Vita üzerinde tam Chapter1 oynanış testi YOK; son end-to-end VPK YOK** |

## Nasıl dürüstçe ölçüyoruz?

**`states` tek dosyasını çözme %100.** Tüm kaynak IPA ya da ilk bölüm çalışır remake port oranı %100 değildir; tüm görev, renderer ve iOS engine assets üzerinde kanıtlı genel denominator yok, dolayısıyla **projeye gerçek bir yüzde uydurmak bilimsel olmaz**.

Üç ayrı ölçüm mantığı:
1. **Kaynak mimari araştırması: ileri aşama.** State file, native ARM event dispatch, selected source IM2V and vtables gerçek kanıtlı.
2. **Vita üzerinde statik entegrasyon: kısmi ve çalışır ARM ELF.** B14 GPU G8 source animation + G218 passive data bağlandı, B16 prototype firing var.
3. **Orijinale sadık oynanabilir Chapter1/Expo: bitmedi; donanım QA eksik.** Yürürken yerinde sayma, küçük ölçek, görsellik, full combat, gerçek mission kritik blokaj.

**Öncelik sırası:** (a) G222 sonrası native `DoAttack(AttackType,eventVal)` vtable 2010 kod dalı ve `StateTrack` value enumerations kaynakla çöz; (b) fiziksel Vita root movement ve source world scale kesin çöz; (c) WM AimM/input/shoulder weapon and combat collision; (d) sky/lighting/alpha/genuine model map finishing; (e) QTE mission complete and single final VPK. **VPK şimdilik kullanıcı isteğiyle yapılmıyor**; orijinal hak sahipliği korunan IPA GitHub'a konmuyor.
