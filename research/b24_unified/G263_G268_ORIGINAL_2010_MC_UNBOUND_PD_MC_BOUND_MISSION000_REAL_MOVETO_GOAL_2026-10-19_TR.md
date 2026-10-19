# G263–G268 — Iron Man 2 (2010 iOS) MC gerçekten bağlı mı, Mission000 açılışta nereye hareket ediyor?

**19 Ekim 2026 · `Gh0sTRX/Iron-man-2-os` · `feature/b24-unified-gameplay` · VPK YOK.**

## Amaç ve gerçek kabul sınırı

Kullanıcının Vita gözlemi: yerde yürüme animasyonu oynuyor ancak dünya koordinatı hareket etmiyor, uçuşta ise hareket görülebiliyor. Gerçek original C1L1 geometride G249 düşük/orta/üst Z destekleri farklı hareket kabulüne sebep oluyor. **Hikâyenin gerçek açılış oyuncu world/feet XYZ ve Mission000 runtime script state henüz doğrulanmadığı için** orijinal sahne verilerindeki herhangi bir koordinata Vita karakterini zorla taşımıyoruz.

## G263 — MC Position alt kaydı ve orijinal AttachType native yönlendirmesi

**[G263 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39265134305).** `level1.bclara` gerçek `MainCharacter` class112 `MC` **ID1062**, native `Position` bileşen çocuk **ID1064**. Gerçek 2010 `PositionData::RefreshPosition(int)` `0xC7F4C`, `+0x38` `AttachType` değeri `1` ise `0xC7F78 BEQ 0xC8054` branşı, sonra `EntityMgr::GetInstance` `0xC8054`, `EntityMgr::FindEntityById` `0xC805C` çağrısı yapar. `+0x2C` kaynak `Bind_To_Entity` değeridir. Bu native kaynak, animasyonun kendi başına dünyayı hareket ettirdiği anlamına gelmez.

## G264 — Tüm 663 özgün Position bileşeninin 92-bayt kaydı

**[G264 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39265523733).** Gerçek `0x005C` tipli çocuk/ebeveyn header + uzunluk etiketli konum/katsayı bileşeninden önceki 36 bayt kaynak incelendi; **663 orijinal Position alt kaydında yalnız 11 farklı prefix deseni** var; bunların 632'si aynı varsayılan değerleri taşıyor. Native attach-mode1 `0xC8054–0xC80B4` orijinal ARM satırları bağlanılan nesneyi ID ile bulup model rotasyonu ve `AttachOffset` ile işleyebildiğini gösterir. Bu aşamada 36 bayta kaynak adlarını varsayım olarak yapıştırmadık.

## G265 — Büyük sonuç: orijinal MC AttachType / Bind_To_Entity / AttachOffset gerçek typed değerleri

**[G265 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39266087905).** G261'deki gerçek `PositionData::LoadFromFile` altı native property adı/tipi ile `0x005C` typed source payload uzunluklarını birleşik doğruladık:

- `AttachType`: `0x0006 + 0x0004 + int32` tagged kaydı
- `Bind_To_Entity`: `0x0004 + int32` kaydı
- `AttachOffset`: `0x000C + 3×float32` kaydı
- Orijinal 663 Position bileşeninin **651'inde `AttachType=0`, 12'sinde `AttachType=1`**. Bunların 632'sinde `Bind_To_Entity=-1`, 31 kayıt başka entity ID'si tutar.
- Gerçek **`MC` (class MainCharacter ID1062)**: **`AttachType=0`, `Bind_To_Entity=-1`, `AttachOffset=(0,0,0)`**. Yani *sahne kaynak verisinde MC'nin başka bir nesneye bağlanan konum modu yok*; runtime'da Mission000 hareket komutları hâlâ rol oynar.
- Gerçek **`PD_MC` (PositionDummy ID1195)**: **`AttachType=1`, `Bind_To_Entity=1062` (MC), `AttachOffset=(0,0,0)`**. Bu, **PD_MC'nin MC'ye bağlanan görev konum nesnesi** olduğunu doğrudan kaynak değerleriyle doğrular. `PD_Trigger_tutorial_move` kaydı da `Trigger_Tutorial_move` nesnesine `Z=7` ofsetiyle bağlanır.
- Diğer bağlanan objeler arasında 1408 `InteractiveObj_obstucle` gibi gerçek ilk bölüm ID'leri vardır. Bu, decoded layout'un hayalî olmadığını gösterir.

**Sınır:** Bu MC başlangıç gerçek dünya `Z=25.054` ya da ayak tabanı `Z=2.82955` demek değildir; oyuncu native script/mission yüklemesi sonra hareket ettirebilir.

## G266–G267 — Gerçek orijinal Mission000 Lua MC hareket komutu ve hedef ID

**[G266 orijinal native 71 Lua callback CI PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39266489219), [G267 true native hareket hedef argümanı CI PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39266705335).**

Orijinal `Mission000_OnStart` **Lua PC 170** gerçek `MoveEntityToEntity(1062, 1892, 3000)` çağrısı yapar:

- **1062**: `MC` (orijinal MainCharacter).
- **1892**: `PD_IM_jump_goal` (original source PositionDummy; 1892 ID'si G25 class ile gerçek).
- **3000**: orijinal statik üçüncü sayısal argüman, *süre birimi/oyun motoru uygulaması henüz tam kanıtlanmadı*.

Bu orijinal kaynak **ilk bölüm scriptinin MC'ye hareket komutu verdiğini** ispatlar; PC170 bir koşullu branch sonrası olabilir, oyunun her açılışında çalışacağı ve bunun oyun sırasında fiziksel yürüyüş bug'ını kesin açıkladığı kanıtlı değil. `Mission000_OnStart` içinde `PC34 SetState MC`, `PC43 Hide MC`, `PC111 Show MC` gibi gerçek MC kaynak çağrıları da ayrıldı. `PD_MC` özgün native source Position mode1 bind üzerinde MC'yi takip eder; taranan `ENTITY_ARGS` sınırlı global fonksiyon setinde PD_MC'ye ayrı doğrudan Lua çağrısı görünmemiştir. Bu, motorun PD_MC'yi kullanmadığı anlamına gelmez.

## G268 — Hedef PD_IM_jump_goal'un özgün çocuk konum belirsizliği

İlk G268 denemesinde `PD_IM_jump_goal` için **tek** 12/16/12 rigid child beklediğimizden test FAIL oldu; kaynak belirsizliği bastırmak yerine analiz genişletildi. **[G268 düzeltilmiş orijinal 2010 CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39267245206)**. Bu `PositionDummy` original named source **ID1892** altında **üç** ayrı native typed 0x005C position/rotation/scale çocuk kaydı bulunuyor:

| Özgün çocuk ID | Gerçek kaynaktaki XYZ (yerel) | Quaternion | Scale |
|---|---|---|---|
| **1893** | (-0.493, -28.062, 3.705) | identity | 1,1,1 |
| **1894** | (0,0,0) | identity | 1,1,1 |
| **1895** | (-1.928, -13.790, 25.830) | identity | 1,1,1 |

Bu satırların üçü de gerçek özgün CLARA kaynak sayısal veri ama **hangisinin `Entity3D::GetParamComponent("Position")` tarafından seçilip hedef dünya matrisi hâline geldiği henüz kanıtlanmadı**. G24 strict transform tablosunda bu nesneye üç farklı çocuk denk geldiği için tek global XYZ ilan edilmedi. Sonraki G269 önceliği orijinal `EntityData::GetParamComponent` çocuk bağlantı/type seçim algoritması ve `PositionDummy` runtime `GetPosition()`/Mission `MoveEntityToEntity` uygulanması.

## Test VPK planı ve değişmeyen iş sırası

1. **Şu an** gerçek MC boot/mission script dünya kökü, ilk bölüm ground/collision.
2. Ground/hover/flight/rush gerçek hareket.
3. G8 gerçek animasyon/StateMgr tuş ve War Machine rig.
4. Özgün WeaponDB, damage, missile, melee combo/hit.
5. **Harita, karakter-araç ölçeği ve tam çevresel/dinamik ışıklandırma, Sun001–004, gece gökyüzü, ay, gerçek gölge, alfa, HUD/kamera.**
6. Orijinal Mission000 intro QTE/audio/cutscene/NPC waves ve görev bitiş.
7. Tek kaynak sürümünde full Vita ARM ELF + host QA; **sonra sadece bir bütünleşik test VPK** ve bununla fiziksel cihaz QA.

**Bu turda gerçek Vita üzerinde yürüyüş düzeldi iddiası, gerçek cihaz test logu, yeni VPK, fizik/collider silme, ışıklandırma shader'ı veya oynanabilir yeni görev yok**. Araştırma ve GitHub başarılı orijinal kaynak CI'ları vardır.
