# G269–G275 — Özgün 2010 Iron Man 2 ilk bölümünde gerçek MoveEntityToEntity hedefi ve PositionDummy Num/Position1 çözümü

**19 Ekim 2026 · `Gh0sTRX/Iron-man-2-os` / `feature/b24-unified-gameplay` · ÖZGÜN kaynak testleri tamamlandı, yeni VPK yok, gerçek fiziksel PS Vita testi yapılmadı.**

## Kullanıcı isteği ve değişmeyen sıra

Öncelik hâlâ (1) özgün `MC` oyuncu konum/root/zemin yürüme kilidi, (2) ground/hover/flight/rush, (3) G8 özgün tüm IM/WM animasyon state/input, (4) silah/WeaponDB/hasar/combo, **(5) Expo harita/karakter-araç oranı, dört Sun, ambient, gökyüzü/ay, armor+araç/bina ışıklandırması, gölge ve transparan alfa/HUD/kamera**, (6) gerçek Mission000 QTE/audio/NPC-wave/end, (7) tek kaynak durumunda host C11/VitaSDK ARM ELF; ardından **bir bütünleşik test VPK**, sonra gerçek Vita QA. Hiçbiri sırf source disassembly yapıldı diye oynanabilir işaretlenmedi. Aşağıdaki özgün görev açılışı hareketi hâlâ birinci aşamadaki gerçek MC dünya kökü/yürüme verisini anlamaya hizmet ediyor; Mission000 oynatılmadı.

## Başlangıç: G263–G268 ile varılan kaynak doğrular

2010 orijinal C1L1 class112 `MC` id **1062**, `Position` child **1064**, authored local XYZ `(-1.319,-6.747,25.054001)`. Gerçek `PositionData` alanları **AttachType=0, Bind_To_Entity=-1, AttachOffset=(0,0,0)**; MC başka bir sahne entity'sine authored bound DEĞİL. `PD_MC` ID1195 ise AttachType1 ile MC'ye bağlanır. `Mission000_OnStart` gerçek Lua5.1 kaynak **PC170**: `MoveEntityToEntity(1062,1892,3000)`; 1892 typed `PositionDummy` **`PD_IM_jump_goal`**. 3000 native üçüncü integer argüman gerçek hareket fonksiyonuna geçiyor, cihazda süre birimi/akış yürütmesi ölçülmedi. PC170 özgün PC73 koşulunun sonrasındadır; her açılışta koşulsuz yürütülür demeyin.

## G269: üç nesne Position kaydı gerçekten var, hepsi bağsız

**[G269 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39270034638).**

| Original child source ID | Orijinal 2010 CLARA XYZ | AttachType | Bind | AttachOffset |
|---|---|---:|---:|---|
| 1893 | (-0.493,-28.062,3.705) | 0 | -1 | (0,0,0) |
| 1894 | (0,0,0) | 0 | -1 | (0,0,0) |
| 1895 | (-1.928,-13.790,25.830) | 0 | -1 | (0,0,0) |

Bu üçü özgün gerçek `0x005C` native typed 12/16/12 poz/quat/scale kayıtları; cihazda üçünün ortalama konum olduğu iddia edilmedi. Eski `PositionDummy::` literal C++ araması kaynak sembollerde sonuç vermedi; gerçekte sınıfın adı **`PositionDummyEntity::`**, G270/G271 ile düzeltildi.

## G270: üçlü paket bütün PositionDummy nesnelerinin standart düzeni

**[G270 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39270380114).** Özgün C1L1 `PositionDummy` class schema **class ID36**. Bu sınıftaki **137/137** entity'nin **3 source child TRS bileşeni** var. Orijinal `GS_GamePlay::LoadEntities` ARM class36 jump `0xC2F6C→0xC3454`: `0xC3460 BL PositionDummyEntity::PositionDummyEntity() (0xD2E84)`. Kaynak `EntityData::GetParamComponent("...", Component*) (0xD7BB4)` parametre adını native loop ile karşılaştırıp seçilen bileşeni yükler; sırf üç kayıt var diye üçünü de oyun yürütür demek yanlış.

## G271: gerçek Lua hareket ve PositionDummy C++ sınıfı

**[G271 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39270715487).** Gerçek orijinal iOS Mach-O'da **20 `PositionDummyEntity` C++ symbol**; başlıcaları:

- `PositionDummyEntity::LoadFromFile(EntityData*)` **0xD2ED8**
- `PositionDummyEntity::GetPosition()` **0xD306C**
- `PositionDummyEntity::GetAbsolutePosition()` **0xD2B94**
- `MoveEntityToEntity(lua_State*)` **0x19BA0**; gerçek `lua_tointeger` üç argümanı okur, `EntityMgr::FindEntityById` ile MC ve hedefi arar, C++ vtable `GetPosition` çağrısı, 3000 argümanı float'a çevirip `0x19C84 BL Entity3D::MoveFromTo(vector3&,vector3&,float,float,float) (0x14650)` çağrısı vardır; süre pozitif değilse farklı reset/teleport benzeri yol mevcut ancak gerçek yürütme/mod iddiaları için ayrıca test gerekir.

## G272: gerçek `Num`, `Position1,2,3` ve ortalama formülü

**[G272 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39271120298).** Özgün `LoadFromFile` ARM PC-relative literal C-string'ler:
`Num` **0x4A15E8**, `Position1` **0x4A15EC**, `Position2` **0x4A15F8**, `Position3` **0x4A1604**. Native class object member ptr Position1 `+0xE4`, Position2 `+0xE8`, Position3 `+0xEC`, `Num` sonucu sayı `+0xF0`. `GetPosition` / `GetAbsolutePosition`:
- Mode1: `Position1` x,y,z.
- Mode2: `(Position1+Position2)*0.5` — özgün float **0x3F000000**.
- Mode3: `(Position1+Position2+Position3)*0.3333333432674408` — özgün float **0x3EAAAAAB**.

Bu gerçek iOS native assembly ve sabitleridir, tahmini interpolasyon formülü değil.

## G273–G274: özgün ilk bölüm root `Num=0` → gerçek iOS mode1

**[G273 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39271460153)** ve **[G274 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39272328775)**.

- **137/137** orijinal class36 `PositionDummy` veri kökünün adı+class pointer sonrası **12 byte** TLV bölümü var: önce 4 byte kaynak referans, **u16(4),u16(4),int32(0)**. Gerçek sınıf36 `Num` tek bir integer native parametresi; bütün 137 root'da **Num=0**. Bunun anlamı her oyun nesnesinin 3 children'ı olsa da native `LoadFromFile` sadece bir bileşen yükler.
- `PositionDummyEntity::LoadFromFile 0xD2EFC` `GetParamValue("Num",int*)`, sonra `0xD2F04 ADD r0,r5,#1` ve `0xD2F08 STR ...+0xF0`, `0xD2F30 GetParamComponent("Position1")`. `GetPosition 0xD3080 CMP mode,#1`, `BEQ 0xD309C`, original `+0xE4 Position1` x/y/z alanı döner.
- **PD_IM_jump_goal gerçek Num=0**: 2/3 bileşenin ortalaması kesinlikle özgün bu dosyanın authored ilk normal yükleme yolu DEĞİL. Runtime source MC initial world boot ayrıca ispatlanmadı.
- Özgün CLARA class36 şema sözlük offset **2230**; alt alan adlarının kaynak offset sırası **Num 2251, Position1 2259, Position2 2377, Position3 2495**. Bu, ilk serialized child1893'ün Position1 ile bağlantısı için kuvvetli source-ordinal kanıtıdır; RAM EntityData class-loader child idx mapping tam çalıştırılmadığı için bu kesin runtime world position diye lanse edilmedi.

## G275: source candidate read-only C11 referansı, VPK'ya yazılmadı

**[G275 gerçek orijinal source metadata ve C11 host QA SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39272740265).**

Üç farklı bağımsız gerçek iOS kaynak izini bağladık:
- Native `Mission000_OnStart PC170 MoveEntityToEntity(1062,1892,3000)`
- `PD_IM_jump_goal` kaynak `Num=0 → Position1` yükleyici yolu
- Class36 `Position1` property sırası + ilk serialized Position child **1893** authored local XYZ **(-0.493,-28.062,3.705)**.

Bunlardan read-only `b24_g275_original_2010_scripted_movement_goal_source.h` ve JSON üretildi, host `cc -std=c11 -Wall -Wextra -Werror -pedantic` ile özgün değerler doğrulandı. **Source-level hedef adayı** budur; **ilk intro PC170 koşullu execution, gerçek entity RAM index eşlemesi, parent/world matrix, ayak-ground Z ve Vita yürüme bug'ı hâlâ kanıtlanmadı**. Aynı zamanda **oyuna scripted movement eklenmedi, fizik/harita/ışık/anim/combat değişmedi, fiziksel Vita testi ve VPK oluşturulmadı**.

## Sonraki odak

1. **Asıl ilk önceliğimiz** gerçek `MainCharacter` boot dünya root ve G75 C1L1 collision uyumu; source `MC` authored Z25.054 ve scripted local jump-goal Z3.705 tek başına player floor ölçüsü değildir.
2. Orijinal MoveEntityToEntity akışı için `PositionDummyEntity::GetPosition` component RAM index/EntityData loader mapping'ini tamamen doğrula; gerekirse real G66C grounded source host collision testinde hedefi ayrıca incele.
3. Herhangi bir sinematik hareket/bağ nesnesi problemine çözüm bulunsa bile analog ground stick→B14→G75→GPU root; G229 120-frame gerçek Vita günlük testi VPK kurulana dek açık.
4. Kullanıcı onaylı iş sırası (movement→animations→combat→**map+lighting**→mission+audio→ELF→tek VPK) asla değiştirilmez. Görsel üretimi/HTML/VPK bu turda istenmedi ve yapılmadı.
