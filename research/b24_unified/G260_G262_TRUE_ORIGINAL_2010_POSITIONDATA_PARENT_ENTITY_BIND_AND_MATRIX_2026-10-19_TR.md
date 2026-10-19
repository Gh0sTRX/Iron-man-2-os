# G260–G262 — Gerçek orijinal 2010 Iron Man 2 oyuncu konum sisteminin PositionData/Bind_To_Entity/Matris yolu

**19 Ekim 2026 · branch `feature/b24-unified-gameplay` · tek-VPK kuralı devam · oyun fiziğine/anim/combat/aydınlatmaya hiçbir uydurma değişiklik yapılmadı.**

## Neden bu araştırma?

Kullanıcı cihaz testinde yerde yürüme animasyonu oynadığı hâlde Iron Man'in dünya koordinatının değişmediğini; flight'ta yer değiştirebildiğini bildirdi. G248–G249 gerçek C1L1 city geometri ile bu tip 0/8 ground hareket + 3/8 flight kabul semptomunu, özellikle farklı Z katmanlarında, host source üzerinde yeniden üretti. G252 gerçek `SpawnPoint` sınıfının düşman dalga mantığı taşıdığını kanıtladı; 16 yerin doğrudan oyuncu start noktası olduğu iddia edilmedi. G253–G258 `MainCharacter` load → `Entity3D::LoadFromFile` → özgün C-string `"Position"`/`"Model"` typed components zincirine indi.

### G260 — Özgün `PositionData` C++ owner method ve ARM kaynakları

[**G260 başarılı orijinal iOS native CI**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39262527719).

Özgün iOS native Mach-O **65.500** sembolün C++ çözümlemesinden **6 özgün `PositionData::` metodu** çıktı:

| Orijinal 2010 C++ fonksiyonu | Native iOS adresi | Kaynak anlamı |
|---|---|---|
| `PositionData::SetPath(CameraPath*, int)` | `0xC7EE8` | Kamera yoluyla hareket/görev interpolasyon yolu |
| `PositionData::Init()` | `0xC7F10` | `+0x2C` bağlanılan ID'si `EntityMgr::FindEntityById(int)` ile aranır; pointer `+0x34` alanına yazılır |
| `PositionData::RefreshPosition(int)` | `0xC7F4C` | `+0x38` bağlantı modu branch; poz/bağlantı güncelleme |
| `PositionData::LoadFromFile(EntityData*)` | `0xC815C` | 6 orijinal typed CLARA özelliği okur |
| `PositionData::PositionData()` | `0xC8200` | Oluşturucu; pos/quat/scale default alanlarını kurar |
| `PositionData::GetMatrix(irr::core::CMatrix4<float>*)` | `0xC826C` | Konum/rotasyon/ölçek içeren matris dönüşümünü hesaplar; poz XYZ alanlarını `matrix +0x30,+0x34,+0x38` adreslerine yazar |

Gerçek 2010 ARM `GetMatrix` başlangıç: `0xC827C LDR lr,[r0,#4]` → `0xC8284 STR lr,[r1,#0x30]`; `0xC8288 LDR ip,[r0,#8]` → `0xC8290 STR ip,[r1,#0x34]`; `0xC8294 LDR r6,[r0,#0xC]` → `0xC829C STR r6,[r1,#0x38]`.

### G261 — 6 gerçek özgün native parametre adı PC-relative ARM literal kaynaklı

[**G261 başarılı orijinal iOS CI**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39262916694). Gerçek orijinal `PositionData::LoadFromFile` `0xC815C` içindeki C string'ler Mach-O read-only metin adreslerinden PC+8 ve altı 32-bit signed delta ile çözüldü:

| Kaynak C-string parametresi | Tip | `PositionData` ofseti | Gerçek ARM çağrı noktası |
|---|---|---|---|
| `Position` | Vector3 | `+0x04` | `0xC817C BL EntityData::GetParamValue(vector3*)` |
| `Rotation` | Quaternion | `+0x10` | `0xC8190 BL EntityData::GetParamValue(quaternion*)` |
| `Scale` | Vector3 | `+0x20` | `0xC81A4 BL EntityData::GetParamValue(vector3*)` |
| `AttachType` | int | `+0x38` | `0xC81B8 BL EntityData::GetParamValue(int*)` |
| `Bind_To_Entity` | int | `+0x2C` | `0xC81CC BL EntityData::GetParamValue(int*)` |
| `AttachOffset` | Vector3 | `+0x3C` | `0xC81E0 BL EntityData::GetParamValue(vector3*)` |

`Position` string original VM `0x49BAF0`, `Rotation 0x4A0E34`, `Scale 0x4A0E14`, `AttachType 0x4A1150`, `Bind_To_Entity 0x4A115C`, `AttachOffset 0x4A116C`. Bu isimler kullanıcı arayüzü için uydurulmadı, gerçek original iOS C++ literal metinleri.

### G262 — Bağ nesnesi çözümü ve yerel konum matrisinin gerçek ARM instruction kanıtı

[**G262 başarılı iki genuine-source artefaktından salt-okunur CI**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39263324181).

- `PositionData::Init` `0xC7F18 LDR r3,[r0,#0x2C]` kaynak `Bind_To_Entity` değerini okur; `0xC7F30 BL EntityMgr::GetInstance` ve `0xC7F38 BL EntityMgr::FindEntityById`; `0xC7F3C STR r0,[r4,#0x34]` gerçekten nesne pointerını saklar.
- `PositionData::RefreshPosition` `0xC7F5C LDR r5,[r0,#0x38]`: bu önceki G261'deki gerçek `AttachType` kaynak alanıdır. Bağ/rotasyon/offset davranışlarını ileride native branch yolları üzerinden çözebiliriz.
- `GetMatrix` pos+4,+8,+C kaynak 3D koordinatını sonuç matrisinin translation +0x30,+0x34,+0x38 alanlarına koyar. **Bu yalnızca konum matrisinde yerel çeviri kanıtıdır; parent/world actor final transform ve fiziksel ayak hizalaması kanıtı DEĞİLDİR.**

## Henüz kapatılmayan gerçek oyuncu başlatma ve yerde yürüyüş hatası

1. Orijinal 2010 `MC` class112 named C1L1 node ID **1062** ve authored direct transform child node ID **1064**, yerel `Position=(-1.319,-6.747,25.054001)` G257 source tarafından kanıtlıdır; bu değerler **oyundaki nihai dünya başlangıç `world.x,y,z` değildir**.
2. `PositionData::LoadFromFile` asıl `MC` kayıt parametrelerinden özgün `Bind_To_Entity`/ `AttachType`/ `AttachOffset` değerlerini getirdiğinde, `RefreshPosition` bağ dönüşümü ve `GetMatrix`/parent birleşimi aynı original native kodla hesaplanmalıdır. Yalnızca bu şekilde gerçek worldZ ve G66C zemin etkileşimi kanıtlanabilir.
3. `G229_WALK_WINDOW` ile gerçek Vita 120-frame `B14_proposed_Z,G75_resolved_Z,GPU_actor_Z` donanım logu hâlâ YOK; G256 kaynak/probe eklendi ve ARM ELF derlendi ama cihaza bu sürüm kurulmadı. Character/car scale ve lighting de henüz bitmedi.
4. Vita tarafında `world.z` yanlış olabilir diye rastgele `2.82955` veya `25.054` atanmıyor; özgün G66C duvar 715 silinmiyor. Bu tur araştırma kodu/host native CI **Vita gameplay root, fizik, sky/light, combat veya mission akışını değiştirmedi**.

## Aynı kullanıcı onaylı yedi iş akışı sırası

1. Özgün oyuncu root/spawn/world Z/ground çarpışması (**şu an bu aşamada**).
2. Movement ground/hover/stage2/rush.
3. Orijinal animation/G8/StateMgr/War Machine rig.
4. WeaponDB özgün saldırı/damage/projectiles/combos.
5. **Harita/ölçek + çevresel ışıklandırma/armor+araç/bina ışığı/gerçek gölge/gece moon ve alfa/HUD** (G259 değişmeyen sıra CI guard).
6. Mission000 original QTE/cutscene/audio/enemy waves/end.
7. Aynı commit full Vita ARM ELF + host QA; 7/7 kaynak hazır olunca yalnız bir test VPK, sonra gerçek Vita QA 12 kapı.

G260–G262 tamamlandı. **VPK üretilmedi.**
