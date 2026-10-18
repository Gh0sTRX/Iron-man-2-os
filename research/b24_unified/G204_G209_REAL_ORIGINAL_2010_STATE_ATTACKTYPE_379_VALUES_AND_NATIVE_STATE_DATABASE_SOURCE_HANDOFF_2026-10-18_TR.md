# G204–G209 — Iron Man 2 iOS 2010: 379 özgün AttackType değerinin gerçek kaynak dosyası, native StateData okuma sistemi

**18 Ekim 2026 · Depo `Gh0sTRX/Iron-man-2-os` / `feature/b24-unified-gameplay` · YENİ VPK YOK.**

## Kullanıcı sorusu: "ARM selectorun hepsini çözünce oyunun girdi ayarlarının hepsini çözmüş mü oluyoruz?"

**Hayır.** Özgün `MainCharacter::DoAttack` ARM jump table'da **26 seçim girişi** (0–25) bulunması bütün oyunun girişlerini çözmek değildir. Bunlar 2010 oyun motorunun saldırı/durum tipi yönlendirmesinin bir bölümü. Ayrıca dokunmatik ekranda gerçek gesture/touch event sisteminin `AttackType` state kaydına nasıl dönüştüğü, locomotion (walk/hover/stage2/rush), kamera/nişan, aktif silahın `WeaponDB` ID'si, göreve özel `SetInputEnabled` ve silah izinleri, oynatılan animasyonun zamanı ve gerçek hasar olayı ayrı kaynak aşamaları. 26 entry = 26 kontrolcü tuşu, 26 silah veya 26 ayrı animasyon **değil**. Bu alanları G83/G169 canlı port inputuna tahminen bağlama.

## G204 yanlış negatif değil, farklı kaynak alanlarının ayrımı

**[G204 orijinal Lua51 55 program kontrolü PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39127307068)**: `Payload/IronMan2.app/states` içindeki 55 kısa Lua 5.1 programını ve sabitlerini parse ettik; **55 programda `AttackType` isimli LUA sabiti yoktu**. G204 sonucu *yalnızca Lua programlarına* aitti. Bu bilgi tüm `states` dosyasında `AttackType` yok anlamına gelmez. Sonraki aşamalarda düzeltildi.

## G205 orijinal IPA 865 dosyasının gerçek ham kaynak taraması

**[G205 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39127472586)** 865 orijinal üye üzerinde birebir `AttackType` kaynak metnini buldu:

| Gerçek orijinal IPA üyeleri | Kaynak byte eşleşmesi |
| --- | ---: |
| `Payload/IronMan2.app/IronMan2` (native ARM executable) | 12 |
| `Payload/IronMan2.app/clev` (CLARA sahne paketi ve level callback) | 22 |
| `Payload/IronMan2.app/states` (361393 byte) | **379** |
| **TOPLAM** | **413** |

Eşleşme sayısı **farklı saldırı sayısı değildir**. `clev` içindeki 22 eşleşme farklı seviye kopyaları, Lua misyon ve authored state kayıtları içerebilir; aynı file offset ve original sınıf binding ayrı incelenmeli.

## G206 gerçek non-Lua state alanları — 379/379

**[G206 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39127786047)** tüm `states` blob'unu 55 orijinal Lua chunk'ın gerçek `NativeLua` reader ile hesaplanan bitiş offsetleriyle karşılaştırdı: **379 `AttackType` eşleşmesinin tamamı kısa Lua5.1 bytecode stub'larının DIŞINDA**. Kaynak binary state alanları içinde gerçek başlıklar/öznitelikler `New_anim_set`, `Attack_front`, `Attack_beam`, `Attack_M_Float_move`, `Aim_Move_Left/Right`, `Attack_close_L`, `Attack_Melee`, `DummyE_Hand_L`, `DummyE_Foot_L` gibi özgün metinleri taşıyor. Bunlar orijinal gerçek authored data; yeni interpolated input/animasyon değil.

**G206 sağladığı önemli şema gözlemi:** `AttackType` literalinden hemen önce little-endian `0A 00` yani 10 bayt ad uzunluğu; hemen sonra 4 baytlık sayısal alan. Bu alanın tam kayıt tipi/StateData deserialization sınıf bağı için G207–209 kullanıldı.

## G207 tüm 379 orijinal AttackType arka arkaya u32 değeri — ilk kapsamlı sayı kanıtı

**[G207 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39128015289)**, her 379 kayıtta `u16(10), ASCII("AttackType"), u32LE(value)` verisini **birebir kaynak offsetlerinden okudu**:

```text
0: 111   1: 52   2: 34   3: 4   4: 24   6: 44
7: 1     8: 3    9: 5    10: 6   12: 6   13: 2
14: 2    15: 1   17: 1   18: 43  19: 14  20: 5
21: 5    23: 1   24: 4   25: 11
```

**Toplam 379**; **22 farklı ham sayı**; hepsi **0–25** içindedir, özgün G196/G197 native 26 girişli `DoAttack` switch'in aralığı ile tutarlı. Ancak G207 script `StateData`'nın bu serialized dosyayı yüklediği native C++ zincirini henüz tek başına ispatlamıyor. `u32` sayıları **dokunmatik ekran tuş kodları DEĞİL**.

Sadece aynı kaynak kayıt yakınında görülen özgün hareket adı **ve** u32 değeri örnekleri (ortam/active zırh/animasyon otomatik kanıt değil):

| Orijinal veri yanındaki ad | `AttackType` ham u32 |
| --- | ---: |
| `Attack_front` | 6 (kaynak bu adı birden fazla blokta kullanabiliyor; diğer bloklarda 18 olabilir) |
| `Attack_front_bomb` | 3 |
| `Attack_beam` | 21 |
| `Attack_Left_laser` | 21 |
| `Attack_Right_laser` | 21 |
| `Attack_Left_Punch` | 0 |
| `Attack_Melee` | 0 |
| `Attack_Float_Front` | 18 |
| `Float_Rush_Back_attack` | 13 |

`Attack_beam` adlı state'in `21` değerli olması tek başına bunun Iron Man Mark VI'nin gerçek `UniBeam` `WeaponDB index4` veya G169 six Beam clip ile aynı olduğunu kanıtlamaz. `Attack_M_Float_move` yakınındaki değer **2** ve gerçek `Warmachine_Aim_M_Ground` suffix'iyle otomatik eş anlamlı değildir.

**Kaynak veriden PNG:** G207'daki gerçek 379 ham sayı frekansından üretildi, etkileşimli HTML değil: `/mnt/data/IronMan2_G207_379_Gercek_AttackType_Dagilimi.png` (konuşma çıktısı; GitHub'a kaynak oyun binarysini kopyalama yok).

## G208 gerçek 2010 StateData::GetParam native C++ — anahtar/değer return izi

**[G208 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39128200179)** 40 özgün State* C++ method adı, 13 ilgili implementation decode etti. `StateData::GetParam(char const*,int)` gerçek **0x9C340** native ARM gövdesinde `this+0x24` giriş sayısı, `this+0x1C` 8-baytlık giriş dizisi ve tekrar eden **`LSL index,#3`**, string `__strcmp` benzeri `0x47111C` literal call, eşleşen kayıt `0x9C4E4 LDR R6,[R6,#4]` üzerinden **pair +4 integer value** okuyor. Orijinal ARM bu sözleşmeyle G207 `u16 len + u32` serialized değeri tutarlı. `StateData::GetParam("AttackType",-1)` gerçek G203 register trace ile doğrulanmıştı.

## G209 özgün Game engine StateData ikili deserializer bulundu

**[G209 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39128458308)** orijinal 49 StateDatabase/StateSetData/State* native CPP yöntemi ve native CALL source korundu. Özellikle:

- **`StateData::StateData(BufferStream&, StateSetData*)` 0x9C528**, orijinal 876 opcode; **çok sayıda** `BufferStream::ReadString()` native call: `0x9C5F0,0x9C84C,0x9CBB0,0x9CD2C,0x9D24C`. Bu dosyayı typed veri kayıtlarına parse eden gerçek kaynak constructor adayıdır.
- **`StateSetData::StateSetData(BufferStream&)` 0x9D85C**, 595 opcode, orijinal `BufferStream::ReadString()` @ 0x9D8D0 ve orijinal `StateData` constructor'a bağlı data nesne modeli.
- `StateDatabase::GetStateSetData(char const*)` 0x9D6F0, `StatesMgr::GetStateId` ve `StatesMgr::GetStateAnimId` bu database'den gerçek kaynak state isimlerini arıyor.
- `StateTrack::StateTrack(BufferStream&)` @ `0xA196C`, `StateData` constructor içinde `0x9CFE4` orijinal çağrı (asıl authored animation/attack event alanlarını incelemek için kritik).

G209 bu sınıflar arası çağrıları ve asli C++ isimleri **gerçek kaynak olarak gösterir**, ama sıkıştırılmamış `states` dosyasının ilk byte'ından `StateDatabase` reader ve tam property → anim/fx dispatch zinciri henüz tamamlanmış değildir. Oyun koduna anahtar değer tahminiyle 379 state aktarmadık.

## Devam hedefi G210 ve büyük açık Vita görevleri

**G210 doğru hedef:** G209'daki `StateData::StateData(BufferStream&, StateSetData*)` özgün ARM constructor'ının hangi `BufferStream::ReadString` ardından `u16 keylen/u32 value` tükettiğini ve `StateData +0x1C/+0x24` memory layoutuna yazdığını kaynak bazında kesinleştir. Sonra her 55 state setinin özgün adlarını ve `AttackType` ayarlarının gerçek kaynak `StateTrack` olayları/animasyonları ile eşleşmesini yap. Böylece G83/G169 combat selector'a **orijinal source-backed** data bridge yapılabilir.

**Unutulmayacak user-device açıkları:** Vita'da karakter yürürken yerinden oynamama, world scale/car reference, çevresel ışık ve shader/gölge/sky/ay, War Machine orijinal aiming/rocket/gatling olayları, özgün melee combo hit pencereleri, C1L1 first QTE/cutscene/mission flow. `G204–209` **host/orijinal kaynak CI işleridir**; yeni Vita ELF/VPK üretilmedi. Bu 379 veri **henüz main gameplay loop ile entegre edilmedi**.
