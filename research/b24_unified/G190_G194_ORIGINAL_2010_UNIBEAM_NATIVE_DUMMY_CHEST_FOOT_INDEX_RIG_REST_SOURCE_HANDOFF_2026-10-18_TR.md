# G190–G194 — 2010 iOS Iron Man 2 Uni-Beam orijinal isim/soket indekslerinin çözümü

**18 Ekim 2026 · Dal: `feature/b24-unified-gameplay` · PS Vita VPK üretilmedi.**

## GERÇEK KIRILIM — özgün kaynakta 14 = Dummy_Chest, 33 = Dummy_Foot_L

G179 kaynağından zaten kanıtlanmış olan `MainCharacter::DoAttack` → `DoUniBeamAttack` ilk int parametreleri **14, 14, 33** ve Uni-Beam `WeaponDB::GetAttackEntityByIndex(4)` idi. Önceki G189 ARM `BL` full section scan üç dummy constructor API'sında **0** çağrı bulmuştu. Bu sonuç bir *tarama kapsamı hatasıydı*: kodu tek `__text` bölümü gibi disassemble etmek mixed code/literal/data yüzünden devamını kaçırıyordu.

**G190:** Orijinal 2010 C++ sembol sınırlarını temel alan ayrı ARM method decode neticesinde şu kaynakları kesin doğruladı:

- `Game::DoInitInLogo()` **0x97E6C** içinde `DummiesTableCreate(int)` **0x97FD8** çağrısı ve **34** gerçek `SceneImpl::DummiesTableAdd(char const*)` çağrısı (**0x97FE4 ... 0x98170**).
- `Game::~Game()` kaynak destructor kodunda iki `DummiesTableDestroy()` direct `BL` çağrısı.
- **G190 CI SUCCESS:** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39118436434.

**G191:** G190 kaynak başlangıç dizisini doğrudan orijinal Mach-O ARM `LDR reg,[pc,...]` + `ADD r0,pc,reg` ve isim string kaynağı ile çözdü. `0x97FCC MOV r0,#0x22` → `DummiesTableCreate(34)` parametresi gerçek; **34 ismin tamamı gerçek 2010 native literal kaynak**:

| ID, sıfır tabanlı kaynak kayıt sıra numarası | Orijinal 2010 C++ kayıt anahtarı |
| ---: | --- |
| 0 | Position_Dummy |
| 1 | FinalPosition_Dummy |
| 2 | Dummy_Cam |
| 3 | Dummy_L_Cam |
| 4 | Dummy_R_Cam |
| 5 | Dummy_Grab |
| 6 | Movement_Dummy |
| 7 | Barrel_Dummy |
| 8 | Dummy_Trail01 |
| 9 | Dummy_Trail02 |
| 10 | Dummy_ForeArm_R |
| 11 | Dummy_Hand_R |
| 12 | Dummy_Hand_L |
| 13 | Dummy_Back |
| **14** | **Dummy_Chest** |
| 15 | DummyE_ |
| 16 | Dummy_Projectile |
| 17 | Dummy_Qte1 |
| 18 | Dummy_Qte2 |
| 19 | Dummy_Shoulder_L |
| 20 | Dummy_Shoulder_R |
| 21 | Dummy_Canno |
| 22 | Dummy_Gun_L |
| 23 | Dummy_Gun_R |
| 24 | Dummy_Green_Gun |
| 25 | Dummy_FocusCam01 |
| 26 | Dummy_FocusCam02 |
| 27 | Dummy_Car_Escape_center |
| 28 | Dummy_Car_Escape_left |
| 29 | Dummy_Car_Escape_right |
| 30 | Dummy_Action |
| 31 | Dummy_Beaten |
| 32 | Dummy_CounterAtt |
| **33** | **Dummy_Foot_L** |

**G191 SUCCESS** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39118751027 .

**G192:** `DummiesTableAdd` gerçek 2010 ARM gövdesi sıralama korunmasını kanıtlıyor:

- `0x641C4 MOV fp,r0` özgün string argümanını tutar.
- `0x641D0 LDR r8,[r1,#8]` önceki ad sayısı = eski indeks.
- `0x641E8 ADD sl,r8,#1`, `0x641FC STR sl,[r5,#8]` sayacı artırır.
- `0x643D4 LSL r5,r8,#2` önceki indeks ×4.
- `0x6440C MOV r0,fp`; `0x64410 BL #0x471170` string kopyası işlevi; `0x64414 STR r0,[r6]` yeni string pointer'ını **önceki indeksin** yerine yazar.
- `0x64418 MOV r0,r8` gerçekten kayıt indeksi döndürür.
- Başlangıç `Game::DoInitInLogo()` 34 adet sıra korunmuş Add çağrısı yapar. **G192 CI SUCCESS** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39118909028 .

**G193 kesin 2010 C++ anahtar eşleşmesi:**

- `SceneImpl::CollectDummies` G184 gerçek native `s_dummiesTable` kaynak dizisini sıfırdan `r6` ile dolaşıp `stristr` ile düğüm isim eşleşmesi yapar.
- Kaynak G185 gerçek 2010 ARM `0x63234 LDR r4,[r5,r6,LSL#2]` ve `0x6370C STR r0,[r5,r6,LSL#2]` **AYNI r6 indeksini sahne `+0x278` grubunda** kullanır.
- `SceneImpl::GetDummy` `0x61728 LDR r3,[r3,r1,LSL#2]` 14 veya 33 grup indeksini kullanır, grup varsa `r2=0` ilk elemanı döndürür.
- G179+G191+G192+G184+G185 kaynak JSON metadata'ları ile **orijinal ARM opcode-birebir** G193 doğrulaması **SUCCESS**: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39119194834 .
- Böylece özgün oyun içinde Uni-Beam'e verilen **14 grubu gerçekten `Dummy_Chest`**, **33 grubu gerçekten `Dummy_Foot_L`** native anahtarıdır. `33` değerinin hangi gameplay varyantında seçildiği ayrıca çözülecek; bunu otomatik başka saldırı diye varsayma.

## G194 gerçek dört orijinal zırh BDAE kaynak rest matrisi

**G194 CI SUCCESS:** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39119381593 . Orijinal user-owned `models` paketi ve B13 BRES/BDAE parser'ından gerçek düğümler/parent'lar ve 4×4 **rest rig local-world** matrisler çıkarıldı. Sadece veri/PNG host tanısıdır; Vita'da çalışan yeni Uni-Beam sistemi değil.

| Özgün 2010 BDAE | Rig düğümü | Grup 14 native key `Dummy_Chest` | Grup 33 native key `Dummy_Foot_L` |
| --- | ---: | --- | --- |
| `Iron_man_mark6.bdae` | 96 | `Dummy_Chest-node`, parent `Bip01_Spine1-node` | `Dummy_Foot_L-node`, parent `Bip01_L_Foot-node` |
| `LC_MC_SuitCase.bdae` | 96 | Aynı kaynak adlar | Aynı kaynak adlar |
| `warmachine.bdae` | 112 | Aynı kaynak adlar | Aynı kaynak adlar |
| `LC_MC_WarMachine.bdae` | 112 | Aynı kaynak adlar | Aynı kaynak adlar |

Gerçek Mark VI rig dinlenim pozu yerel world matrisi translasyonu:

- Chest node: **X ≈ -0.000001, Y ≈ -0.563787, Z ≈ 1.543968**.
- Sol ayak node: **X ≈ 0.232995, Y ≈ 0.078091, Z ≈ -0.023842**.
- Mark V: chest yerel Z ≈ 1.539823; foot X ≈ 0.214936, Y ≈ 0.082516, Z ≈ -0.024732.
- Buradaki sayılar **orijinal BDAE rig koordinatlarıdır**, Vita'daki gerçek world-position, animasyonlu skin örnekleri veya FX emitter dünya koordinatları **değildir**. Bu koordinatları doğrudan B14 dünya sistemine eklemek kaynak sadakati olmaz.
- Kaynak rig'in **statik** 3D düğüm PNG'si G194 CI artifact'inde var; etkileşimli HTML yok, gerçek Vita ekran kaydı değil.

## Başarılmış ve halen açık olan gerçek oyun maddeleri

**Bu aşamada gerçekten tamamlanan:** Özgün Uni-Beam `WeaponDB index4`; gerçek çağıran `DoAttack` sayıları `14/33`; oyun `Game::DoInitInLogo` içerisindeki 34 orijinal kayıt; native SceneImpl lookup grubunun gerçek C++ `Dummy_Chest` ve `Dummy_Foot_L` isimleri; Mark VI, SuitCase, War Machine orijinal BDAE'deki ilgili düğümlerin rest matrisleri.

**Yapılmadı ve iddia edilmemeli:** Vita'da gerçek `Dummy_Chest` / `Dummy_Foot_L` üzerinden oynayan Uni-Beam görsel efekti; son animasyonun her karede gerçek node transformu, orijinal native Uni-Beam frame damage/hit timing; orijinal MarkV/VI hangi koşulda index33 kullanıyor; WM rocket/gatling source binding; ilk C1L1 QTE/cutscene; karakterin gerçek cihazda yerinde yürüme problemi, orijinal actor/vehicle world scale; çevresel ışık/gölge/ay/skyline. **G190–194 kaynak/host CI işleridir; yeni Vita ELF/VPK yapılmadı.**

**G195 bir sonraki doğru iş:** G193 kaynak anahtarlarının G194 gerçek isimli parent rig matrisiyle ilişkisinden hareketle, G8/G83 2010 IM2V animasyon karelerindeki `Bip01_Spine1` ve `Bip01_L_Foot` track dönüşümlerini **orijinal authored animation** olarak örnekle, animasyonlu dummy world transformu (rest × skin/node TRS) ve gerçek `G169` Beam1/2/3 faz olaylarını eşleştir. Aktif oyun VFX'in dünyaya taşınması ancak animasyon + parent dönüşümü doğrulanınca; no invented emitter offset. Yeni VPK yok.
