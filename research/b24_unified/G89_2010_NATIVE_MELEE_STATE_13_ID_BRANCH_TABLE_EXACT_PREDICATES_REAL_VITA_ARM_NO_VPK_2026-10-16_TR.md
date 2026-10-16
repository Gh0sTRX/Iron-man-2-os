# G89 — Orijinal 2010 iOS yakın dövüş 0x824 / 0x828 durum alanları ve gerçek ARM koşulları

**16 Ekim 2026; aktif dal:** `feature/b24-unified-gameplay` · Gerçek orijinal `IronMan2_1.0.0_ios_2.2.1.ipa` kaynak taraması ve güvenli C11 referans. **Yeni VPK kesinlikle YOK.**

## 1. G88'den daha ileri gerçek native ARM kanıtı

G88'de `GetCurrentMeleeAttackStep() const` `+0x824` kaynağı biliniyordu ancak tek başına 3 combat animasyonunun native saldırı koşullarını açıklamıyordu.

Yeni G89 ilk kaynak taraması `MainCharacter::StartMeleeAttack(float)` ARM **0xEE04C** fonksiyonunda:
- `+0x824` **2 write / 1 read**;
- bir kaynak yolunda `mov r0,#2; str r0,[r4,#0x824]`;
- farklı kaynak yolunda `mov lr,#1; str lr,[r4,#0x824]`, `add ip,lr,lr; str ip,[r4,#0x828]`;
- `+0x824` değerinin `cmp r3,#0xC` ardından indeksli 4-byte lookup ile sınırlanması. Bu **0..12 indeksli native durum referansı**, 13 adet oynanabilir kombo/saldırı kanıtı **değildir**.

G89B gerçek native `MainCharacter::UpdateMeleeAttackState()` ARM **0xF1DE4** fonksiyonunda aynı `+0x824` alanına tam **12 write / 4 read** saptadı. İşlev native `cmp r0,#0xC; addls pc,pc,r0,lsl #2` türü ARM indeksli dallanma kullanıyor; kodda +0x828 slotundan +0x824 slotuna aktarım izleri de gerçek. Yalnızca disassembly/field xref, tam çalışır C++ state machine değil.

## 2. Orijinal 2010 oyunundan birebir doğrulanmış üç koşul

Gerçek native C++ symbol/ARM komutları ve kaynak C11 referans:

| Orijinal fonksiyon | ARM adresi | Orijinal +0x824 kontrolü | Port için yalnızca doğrulanan durum |
|---|---|---|---|
| `IsInMeleeAttackSlideState() const` | `0xFE09C` | `cmp value,#1; moveq` | Tam olarak `state==1` |
| `IsInMeleeAttackState()` | `0xEA3C0` | `sub value,#2; cmp #10; movls` | **2..12** (unsigned aralık) |
| `IsInMeleeAttackEndState()` | `0xEA3D8` | `sub value,#9; cmp #3; movls` | **9..12** (unsigned aralık) |
| `ResetMeleeAttackState()` | `0xEA518` | `mov #0; str +0x824; str +0x828` | İki kaynak slotu da **0** |

Bu kurallar gerçek orijinal ARM belleği üzerinde bulunan statik predicate'lerdir; 2..12 durumları ayrı ayrı `Ground_Combo_1/2/3` oynatan kesin geçiş mantığı demek değildir. +0x828 ayrı bir state slotudur; nihai orijinal typed isim/işlev eşlemesi henüz kanıtlanmadı.

**Gerçek yeni C11 kaynak modülü:**
- `g89_original_combo_native_flow/b24_g89_real_2010_melee_state_predicates.[ch]`
- `g89_original_combo_native_flow/test_g89_real_2010_melee_state_predicates.c`

Bu C modülü yalnızca doğrulanmış kaynak predicate'leri ve reset davranışını referans verir; G82/G8'i bypass etmez, mevcut B14 fiziğini veya G83 animasyon oynatıcısını değiştirmez. Test `0..31`, büyük UINT32 sınırları ve iki slotun resetini bağımsız doğrular. Predicateler kullanıcıya ait iOS binary'ye dayanır, **yerel yeni yapay saldırı hareketi değildir.**

## 3. Gerçek test ve saklanan kanıt

- Gerçek kullanıcı IPA 248,613,763 bayt / Mach-O ARM 32-bit, iş analizi yalnız geçici GitHub Actions runner'da. Kaynak IPA veya iOS executable repo/artefakta yüklenmedi.
- G89 `g89_decode_original_combo_arm_field_flow.py` özgün 6 native method adresini, 0x824 read/write ve branch/call komşuluklarını kaydeder.
- G89B `g89b_original_melee_state_transition_provenance.py` 16 update-field erişimi ve 3 predicate+reset ARM sequence'lerini **birebir assert** eder. Uyumsuz orijinal binary sürümünde bilinmeyen mapping'i kabul etmez.
- GitHub Actions [**38958176427**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38958176427) kaynak ARM ve C11/PS Vita ARM **OBJECT ONLY** QA. Bu aşamada oyun VPK'sı yok; mevcut G88 birleşik oyun Vita ARM `im2_beta` link testi [38956768062](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38956768062) zaten başarılıydı.
- Kaynak metadata ZIP'i yalnız opcode/register/offset JSON, oyuncuya ait tam IPA/exe/ses dosyaları değil.

## 4. Kalan işler: VPK için 11 nesnel kabul kapısı

`g83_final_vpk_gate/READINESS_STATUS.json` içinde **1 / 11 doğrulanmış**: özgün 972/972 animasyon kaydının indekslenmesi; teknik kaynak kanıtı G76 özgün IPA CI [38926792920](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38926792920).

**10 kapı hâlâ açık ve henüz tamamlanmış sayılmıyor:**
1. 338 oyuncu adlı özgün klibin doğru rig'lerle birleşik oynanması; Mark V 248 kaynak klibin tamamı G85 host'ta çözülmüş olsa da gerçek Vita'da tüm 248 durum test edilmedi.
2. Mark V tüm orijinal hareket ailesinin gerçek oyun cihaz doğrulaması.
3. Yürüyüş/hover/flight/rush/yön/iniş, kapsül/camera gerçek PS Vita bütünleşik donanım testi.
4. Orijinal bütün combo-power/counter/throw/grab input ve native state geçiş koşulları; G89 artık kısmi gerçek enum sınıflandırıcı, fakat tam controller değil.
5. Repulsor/missile/unibeam gerçek isabet kareleri ve orijinal hasar olayları.
6. 26 kaynak Attack / WeaponDB her silah için özgün typed numeric values.
7. Drone/NPC hit/hurt/death/AI ve orijinal Media Mayhem misyon dalga/mission eventleri.
8. G68 haritanın özgün fizik, ışık, kamera, sky/ay, görünmez duvar ve zemin testlerinde düzeltmeler.
9. Orijinal touchHLE oyun döngüsü ve gerçek input/combat davranışı yakalama; önceki G62 mutex engeli henüz aşılmadı.
10. Bütün yukarıdaki öğeler *entegre edildikten sonra* nihai birleşik ana Vita oyununun kaynak/ARM/host/Vita cihaz testleri.

**ÖNEMLİ:** `1/11` genel oyun tamamlama yüzdesi değildir; katı sürüm kapısı kanıtlarından kaçının tamamlandığını gösterir. G73 gerçek PS Vita eski çalışır beta korunur. G85/86, G87/88/89 kaynakla gelişmiştir ancak yeni cihaz kurulumu yapılmadı.

## 5. G90 önceliği

1. `UpdateMeleeAttackState` orijinal 13 durum ID aralığındaki branch/bit flag/dynamic callback graph'ını G89B kaynak ofsetleri ve orijinal `+0x828/+0x82C/+0x830` alanları üzerinden çöz. Sırf isimden input zamanlaması uydurma.
2. Real `AttackEntity::LoadFromFile` değerlerin doğrudan native schema instance kaynağından typed `Damage` sayısına bağlanıp bağlanamayacağını bul, unknown ise hasarı fail-closed tut.
3. Gerçek `Actor::TestMeleeHit` combat hit-active frame ayrı source kanıtı ve `SetAttackTypeEnabled` arg1 gerçek enum eşlemesini çöz.
4. Bütün bunlar ve kalan on sürüm kapısı olmadan **VPK çıkarmama** kuralını koru.
