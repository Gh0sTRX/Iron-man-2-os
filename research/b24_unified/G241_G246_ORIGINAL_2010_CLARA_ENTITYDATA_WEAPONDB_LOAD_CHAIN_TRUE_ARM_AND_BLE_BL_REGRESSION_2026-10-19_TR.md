# G241–G246 — Orijinal 2010 CLARA -> EntityData -> WeaponDB: gerçek loader/stream formatı, ARM çağrı doğruluğu, Vita engelleri

**Tarih: 19 Ekim 2026.** Proje: `Gh0sTRX/Iron-man-2-os`, dal `feature/b24-unified-gameplay`. **Bu turda fizik, savaş, animasyon, kamera, çevre görsel motoru ve görev akışı değiştirilmedi. VPK yok.** Gerçek Vita donanım logu yok.

## Kaynağa dayalı sonuç: özgün yükleyici zincirinin fonksiyon haritası

| Gerçek original iOS 2010 C++ | ARM VM | Gözlenen kanıt |
|---|---|---|
| `GS_GamePlay::LoadEntities()` | `0xC2E8C` | `ClaraFile::GetEntitiesCount` ve `GetEntityData` çağırır, +0x14 sınıf ID'si ile dallanır, `WeaponDB::AddNewAttackEntity/Weapon/Accessory` çağırır |
| `ClaraFile::GetEntitiesCount()` | `0xD31A4` | özgün container sayısına erişir |
| `ClaraFile::GetEntityData(int)` | `0xD31B4` | `r1<<2 + r1<<5 = 36 × index` şeklinde özgün dizide kayıt seçer |
| `ClaraFile::Load(BufferStream&)` | `0xD5A94` | `0xD5AF0` kaynak BL ile `EntitiesData::LoadFromFile` çağırır |
| `EntitiesData::LoadFromFile(BufferStream&,int)` | `0xD56C8` | `ReadUnsignedShort` ile count, `count*36+4` ayırır, her kayıt için `EntityData::LoadFromFile` çağırır; dizide `+0x24` adımlarla ilerler |
| `EntityData::LoadFromFile(DataStream&)` | `0xD356C` | özgün kayıt ID/name/class ID/ek verilerini DataStream üzerinden okur; özgün sınıf ID +0x14 member alanına yazılır |

**G241 [CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39225464002).** Exact native ARM:
```asm
0xC2EA8 BL ClaraFile::GetEntitiesCount()
0xC2EAC SUBS fp,r0,#0        ; sayısı
0xC2EB4 MOV sl,#0           ; ilk eleman
0xC2EBC MOV r1,sl           ; iterasyon indeksi
0xC2EC4 BL ClaraFile::GetEntityData(int)
0xC2EC8 LDR r1,[r0,#0x14]  ; gerçek kaynak sınıf ID
0xC2ECC MOV r6,r0           ; gerçek EntityData nesnesi
0xC2ED0 SUB r0,r1,#1
0xC2ED4 CMP r0,#0xDC
0xC2ED8 ADDLS pc,pc,r0,lsl #2
```
Özgün G25 C1L1 kaynak sınıf tablo ID'leri ve genuine ARM jump table birbirine gerçek native kaynak üzerinden bağlandı:

| Sınıf | Gerçek ID | Orijinal jump-table B | Native dal | Native WeaponDB çağrısı |
|---|---|---|---|---|
| WeaponAccessory | 104 | `0xC307C` | `0xC3650` | `AddNewWeaponAccessory` `0xC365C` |
| Weapon | 107 | `0xC3088` | `0xC366C` | `AddNewWeapon` `0xC3678` |
| Attack | 108 | `0xC308C` | `0xC3688` | `AddNewAttackEntity` `0xC3694` |

**G242 [CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39225661749).** Original native `ClaraFile::GetEntityData`:
```asm
0xD31B4 LDR r3,[r0,#4]
0xD31B8 LSL ip,r1,#2
0xD31BC LSL r2,r1,#5
0xD31C0 LDR r0,[r3,#8]
0xD31C4 ADD r1,ip,r2
0xD31C8 ADD r0,r1,r0       ; 36*index + gerçek EntityData array base
0xD31CC BX lr
```

**G243 [CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39225909125).** `ClaraFile::Load` içinde `0xD5ACC BL EntityTemplates::LoadFromFile`, `0xD5AF0 BL EntitiesData::LoadFromFile` kesin; `ClaraFile::Load` kendi başına kayıtların üst üste nesne dizisine yerleştirilmesi mantığını taşımıyor, asıl kayıt oluşturma ikincisinde.

**G244 [CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39226459034).** `EntitiesData::LoadFromFile` özgün `0xD56FC BL DataStream::ReadUnsignedShort`, `0xD5700 LSL #2`, `0xD5704 LSL #5`, `0xD5710 ADD`, `0xD5714 ADD #4`, `0xD5718 BL operator new[]` ile **kayıt sayısı × 36 + 4** alloke eder. `0xD58A0 BL EntityData::LoadFromFile(DataStream&)` gerçek kayıt parser'ını çağırır. **`0xD5A58 ADD sl,sl,#1`, `0xD5A60 ADD r6,r6,#0x24`, `0xD5A64 BGT 0xD5894`** ile sıradaki kaydı diziye işler; farklı alternatif çıkış yolunda da `0xD5A80` ve `0xD5A88` +1/+0x24 kullanılır. Burada veri kaynağı **sequential stream**dir; ancak bu, C1L1 kaynak isimlerini dosya ofseti sırasına göre alıp doğrudan orijinal global WeaponDB index'i ilan etmek için yeterli değildir.

**G245 [CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39226786975).** Tek tek özgün EntityData kaydının gerçek native alanlarındaki komutlar:
- `0xD3588 BL DataStream::ReadInt` ve `0xD358C STR [fp]`: gerçek source ID.
- `0xD3594 BL DataStream::ReadUnsignedByte`, `BNE 0xD3798`: ad/ek veri bayrağı; varsa `0xD37A4 BL DataStream::ReadUTF(char*,int)` ve `0xD37B0 STR [fp,#4]` kaynak name pointer.
- `0xD37B8 BL DataStream::ReadByte` ve `0xD37C0 STR [fp,#8]` kaynak kayıt baytı.
- `0xD35B0 BL DataStream::ReadInt`, `0xD35B4 STR [fp,#0x14]`: gerçek source **class ID +0x14**. Bu, G241 `LoadEntities` switch'inin **aynı native kaynaktan gelen sınıf alanını** kullandığının ayrıca kanıtıdır.
- Dizi/öznitelik sayıları ve diğer yükler ayrıca ayrıştırıldı, ancak verinin tam XML-benzeri typed grammar'ı ve attack hasar değerleri burada hesaplanmadı.

## G246 kritik tarayıcı doğruluk düzeltmesi

**[G246 host ARM CI PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39227235165).** G236/G238/G240/G241/G243/G244/G245 source ARM ayrıştırıcıları, `mnemonic.startswith(("bl","blx"))` ile **`BLE` ve `BLO` gibi koşullu B komutlarını BL sanabilirdi**. Kod gerçek Capstone instruction ID `ARM_INS_BL`/`ARM_INS_BLX` kullanacak şekilde düzeltildi; `BLE`, `BLO`, `BLS`, `BNE` host ARM little-endian testleri ve yedi scanner `py_compile` CI'dan geçti. Eski raporlardaki **doğrudan CALL toplam sayıları** gerçek kaynak tekrar üretilene kadar olası koşullu B yanlış sayımları içerebilir; `0xC365C/C3678/C3694` gibi **opcode'u birebir `BL` olarak ayrıca kanıtlanan çağrılar** geçerliliğini korur. Önceki action artifact'ları yeni koda göre geriye dönük değiştirilmiş sayılamaz.

## Hâlâ çözülmemiş olanlar

Özgün `Attack_type0`/ `Attack_type1` C1L1 named records var; ama **bu native isimlerin `WeaponDB::GetAttackEntityByIndex(0/1)` ile birebir runtime eşlemesi** ve `UniBeam` index 4'ün C1L1 Attack adı henüz kanıtlı değil. Gerçek 2010 CLARA stream record order'ın G25 `native_names()` dosya içi offset sırasıyla birebir bağlanması; level-specific vs global weapon registry; diğer asset/import kaynaklarından kayıtların orijinal eklenme sırası; War Machine omuz füze/gatling tuşu, damage/hit penceresi, G8 animasyon / state selection, boss/AI henüz eksik.

Son başarılı G239 **Vita ARM ELF derlemesi** ve G229 120-frame read-only ground probe vardır ama **fiziksel Vita'da stuck walk kök nedeni bulunmuş değildir**. Karakter/araç gerçek ölçeği, gece ışık/skybox/ay/gölge/alfa, ilk görev QTE1456, ses/cutscene/mission completion ve gerçek donanım QA hâlâ açıktır.

**Bu turda yeni VPK, Vita runtime gameplay değişikliği, özgün orijinal oyun binary exportu veya fiziksel Vita test sonucu YOK.**
