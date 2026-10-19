# G236–G237 — Orijinal 2010 WeaponDB kaynak sahipliği, 3 ayrı dizi ve demo önündeki gerçek engeller

**19 Ekim 2026 · `feature/b24-unified-gameplay` · özgün iOS 1.0.0 ARM/Mach-O + C1L1 CLARA · VPK üretilmedi.**

## G236: Orijinal veri kaynağını yeniden doğrulama

[**G236 kaynak CI başarı**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39217798346), [**G237 için tam ARM talimat bağlamı sunan genişletme CI başarı**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39217954495).

Özel GitHub CI içinde kullanıcıya ait **248.613.763 baytlık** 2010 IPA geçici alana indirildi; gerçek **7.480.208 baytlık** Mach-O'daki **65.500 native sembol** kaynakta yeniden okundu. `C1L1 level1.bclara` gerçek native tipli nesnelerinin 26'sı **Attack**, 13'ü **Weapon**. `Attack_type0` adlı kaynak kayıt **native instance ID 329**, `Attack_type1` **native ID 332** olarak doğrulandı. Bunların global `WeaponDB::GetAttackEntityByIndex(0/1)` dizisine birebir eşitliği henüz **doğrulanmış değil**: scene node ID, AttackType state parametresi, global array index ve native method argümanı dört ayrı kavramdır.

Orijinal semboller:

- `WeaponDB::GetAttackEntityByIndex(int)` `0xAB3EC`; `WeaponDB::GetInstance()` `0xAB324`.
- `WeaponDB::AddNewAttackEntity(EntityData*)` `0xAB894`.
- `WeaponDB::AddNewWeaponAccessory(EntityData*)` `0xABBD4`.
- `WeaponDB::AddNewWeapon(EntityData*)` `0xABF14`.
- `WeaponMgr::InitWeaponData(EntityData*,Entity3D*,int)` `0xB27E4`.
- `AttackEntity::LoadFromFile(EntityData*)` `0xA934C`; `WeaponEntity::LoadFromFile(EntityData*)` `0xC14B8`; `WeaponAccessory::LoadFromFile(EntityData*)` `0xC0970`.

G236 özgün `AddNew*` fonksiyonlarının gerçek ARM opcode metadatasını ve `WeaponMgr::InitWeaponData` kaynak fonksiyonunu ayrı JSON'da saklar. Tam IPA veya executable hiçbir GitHub artefaktına eklenmemiştir.

## G237: Kaynakla doğrulanmış üç ayrı native 32-bit container alanı

[**G237 gerçek G236 opcode kaynak CI PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39218307104). `g237_original_native_three_WeaponDB_arrays/` denetçisi, orijinal C++ method adına, native nesne constructor `BL` adresine, eski sayıyı okumaya, `count+1` hesabına, kapasite karşılaştırmasına, pointer alanı erişimlerine ve sayı alanına `STR` yazımına bakıyor.

| Dizi | Native pointer | Native capacity | Native count | Orijinal AddNew | Orijinal constructor BL |
|---|---|---|---|---|---|
| Weapon | `+0x00` | `+0x04` | `+0x08` | `0xABF14` | `0xABF34→0xC1710` |
| WeaponAccessory | `+0x18` | `+0x1C` | `+0x20` | `0xABBD4` | `0xABBF4→0xC0A40` |
| Attack | `+0x30` | `+0x34` | `+0x38` | `0xAB894` | `0xAB8B4→0xA9784` |

Özgün Attack methodundan örnek gerçek opcodes:
```asm
0xAB8CC  LDR r6,[r8,#0x38]  ; mevcut attack count
0xAB8D0  LDR sl,[r8,#0x34]  ; attack capacity
0xAB8D4  ADD r2,r6,#1       ; önerilen yeni count
0xAB8D8  CMP r2,sl          ; capacity kontrolü
0xAB92C  LDR r5,[r8,#0x30]  ; attack pointer array
0xABB9C  STR ip,[r8,#0x38]  ; count yazım örneği
```
Bu **native kaynak container/veri düzeni** doğrulamasıdır; runtime'ın bütün C1L1 kayıtlarını belirli isim sırasıyla eklediği veya WeaponDB[0]'ın `Attack_type0` olduğu ispatı değildir. G77B `GetAttackEntityByIndex` fonksiyonunun `+0x30` pointer / `+0x38` count kullandığına dair bağımsız eski analizle tutarlıdır.

## Demoya kadar kaç teknik kapı kaldı?

Bir *kaynak keşfi tamamlanma yüzdesi* ile *Vita'da oynanabilir demo tamamlanma oranı* aynı değildir. Projede kalan **en az beş bağımsız kabul kapısı** vardır:

1. **Ground hareket fiziksel Vita doğrulaması:** Analog→B14→orijinal çarpışma→GPU world root G229 telemetry; yerde oyuncu hareket etmiyor gözlemi ancak cihaz log/görüntü ile kapanabilir.
2. **Özgün AttackEntity davranışının gerçek entegrasyonu:** Bu turda 2010 0/1/4 indeks erişimleri ve üç container yerleşimi öğrenildi; gerçek orijinal index→kayıt isimleri, weapon/assistant→zırh ve gerçek hit/anim/StateMgr olay tetikleme hâlâ eksik. Dummy düşman hasarı kontrol edilmeli.
3. **Dünya ölçeği ve görsel bütünlük:** Arabaya kıyasla küçük karakter, gece city sky/ay/ışık/gölge/PNG alfa ve collision görünür haritayla eşleşmeli.
4. **Oyuncu arayüzü ve hareket kontrolleri:** HUD omuz kamera kuralları; Ground walk/aim-fire/hover/flight/rush ayrımının gerçek Vita input ve G8 stream ile QA'sı; yanlış pause tetiklemesi tekrar kontrol edilmeli.
5. **İlk bölüm görev akışı:** Orijinal Mission000 intro/QTE1456, ses/cutscene, düşman ve görev bitişinin en az bir giriş→oynanış→başarılı görev test döngüsü.

Bunlardan biri bile fiziksel Vita'da başarısızsa tamamlanmış özgün Chapter1 demosu denemez. Bu yüzden güvenilir bir "%90 bitti" veya kalan saat/tarih hesabı verilmedi. İlk **sınırlı kontrol/çarpışma/combat sandbox demosu** ile **orijinal senaryoya sadık tam ilk bölüm** farklı teslim kapsamlarıdır.

### Sonraki odak

G238, **`WeaponDB::AddNewAttackEntity` native kayıt ekleme sırasını** ve özgün C1L1 EntityData yükleme/registration çağrı zincirini eşleştirmeli. Yalnız native pointer/counter offset'lerini bilmek, `Attack_type0`'ın global attack[0] olduğunu ispatlamaz. Aynı anda G229 hardware gözlemini bekleyen ground kilidi ve görsel ölçek blokajları kapatılmalı.

**Yeni VPK yok, bu aşamada yeni Vita ARM executable derlenmedi, fiziksel Vita oynanış testi yapılmadı.**
