# Iron Man 2 2010 iOS → PS Vita | G128–G132 gerçek Stark Expo katı yüzeyler / özgün Level 1 görev ve Mark V giriş yetkileri

**17 Ekim 2026**. Dal: `feature/b24-unified-gameplay`. Kullanıcı isteği: eşzamanlı bütün combat/weapon/hitframes peşine düşme; **ilk Level1 / suitcase Mark V'in izin ve görev akışını özgün Lua'dan çöz**, kaynak haritanın katı yüzeylerini düzelt, no new VPK.

## 1. Büyük hata: G108/G75 eski beta koordinat penceresi orijinal geometriyi DIŞARI ATMIŞ

G108'daki eski `G108_X0=-336, NX=56` ve `G108_Y0=-360, NY=52` (12 kaynak birim/cell) yalnız x[-336,336], y[-360,264] içindeki opak dik geometriyi uzamsal indekse ekliyordu. Ana `g75_source_capsule.c` içindeki eski `wall_clear` de merkezde x[-325,331], y[-352,255] sınırını gameplay/mission dışında **sert ve keyfî** kullanıyordu. Bu, source level'ın gerçek oynanabilir hududu kanıtı değil.

**Gerçek G68 `G66_city.g66m` okunarak CI'de BİREBİR ölçülen model AABB:**
- X: **−761.034 … +649.194**, Y: **−773.510 … +586.695**. 
- Eski merkezi clipping yüzünden **374 kaynak opak dik üçgenin centroid'i** eski G108 bbox dışında kalıyordu. Bu sayı original authored-solid collision surface sayısı DEĞİL.
- G128 kaynak `b24_g108_visible_original_wall_grid.c` 12 birimlik orijinal kaynak mesh indexi **256×256 CSR** olarak genişletti; tüm gerçek `G66M` vertexlerinden **runtime exact source bounding rect** hesaplıyor, G75'nin keyfî sabit sınırını artık `b24_g108_grid_source_bounds_allow` ile kaynak sahne envelope'u üzerinden değerlendiriyor. G108 verisi yüklenemezse eski muhafazakâr sınıra döner; gerçek physics B14 tek owner.
- Toplam kaynak *render-geometri türevi, özgün iOS solidity'si doğrulanmamış* opak/dik engel üçgeni **G108=7147 → G128=7487 (net +340)**.
- Gerçek 2010 mesh centroid kapsül QA'da **7472/7487 blocked**, 15 pass; kaynak coğrafyanın kapsama regresyonu ve 5000 indexed query başarı; **donanım gerçek testi YOK**. 374 dışarıda kalan triangle listesi ile +340 yeni aday bire bir eşit tutulmamalı (broadphase, overlap/filtre farkı).
- Kaynak geometrinin her opak dik poligonunun gerçek oyuncu çarpışması olduğu KANITLI DEĞİL. Görev izinleri ve source scene node model/Collider flag eşlemesi hâlâ asli yapılacak iş.
- **[G128 full true VitaSDK `im2_beta` ARM ELF-only native link + real owner world source C11 QA SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39024369900)**. **Yeni VPK KESİNLİKLE YOK.**

## 2. Orijinal ilk görevin 71 Lua5.1 handler'ı — statik görev kanıtı

G129 önceki 2010 user original full 71 Lua51 chunks G26 + gerçek 1035 CALL G27 source-metadata artefactlerini yeniden çaprazladı, orijinal IPA'yı yeniden indirmeden. **[G129 SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39024283631)**, [JSON artifact 12097892208](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39024283631/artifacts/12097892208).

- Toplam 71 orijinal Lua callback; 45 tane sınıfı `Mission`. Level1 gerçek görev/callback **adları**: `Mission000`, `Mission_Go_to_attack`, `Mission_clear_enemies`, `Mission_Go_to_citizen_[0..3]`, `Mission_first_enemy`, `Mission_attack`, `Mission_save_citizen`, `Mission_Go_toto_missile`, `MissionTutorial_missile`, `MissionGoto_building[000..003]`, `Mission_Attack_enemy`, bomba devre dışı etme ve son düşman temizleme. Bu liste özgün author script handler'larını kanıtlar, bunların native `OnStart/OnComplete` olaylarının sahnede hangi sırayla ve koşulla gerçekten çalıştığı **henüz yürütülmedi/kanıtlanmadı**.
- `Mission000_OnStart` orijinal Lua bytecode PC1 `MissionPause()`, PC6 `Show(InteractiveObj_QTE ID1456)`, PC9–30 8 özgün `Deco_man` enabled, PC34 `SetState(MainCharacter ID1062,"idle")`, PC37 `Disable(Deco005 1163)`, PC40 `Enable(Deco004 1158)`, PC43 `Hide(MC1062)`, PC50 `SetInputEnabled(14,false)`, PC53/56 iki fence disable, PC70 `PlayVoice(320)`; ilk koşullu branch PC73.
- İlerleyen aynı callback statik PC914 `SetInputEnabled(2,true)`, PC927 `SetInputEnabled(6,true)`, PC935 `MissionResume()`. **Branch-conditional opcode'ların runtime path'i hâlâ çözülmedi**. Bunların ilk açılışta mutlaka/doğrusal olarak çalıştığı iddia edilemez.
- `SetCamera(1864,0)` ve `SetCamera(1868,7000)` ilk handler'da gerçek source; iki kamera da PC73 öncesi olmak zorunda DEĞİL. İlk source boyut/değerleri yetkisini API semantiği olmadan 7000ms kesin süre diye çevirmiyoruz.
- Level1 Lua statik kaynakları doğrudan `SetFlightEnabled`, `SetCanFly`, `DisableFlight` gibi adlandırılmış global API komutu içermiyor; **bu, first-Level Mark V'in gerçekten uçamayacağının NEGATİF KANITI DEĞİL**. Actor class native capability veya mission input control tarafından engellenmiş olabilir.

## 3. Orijinal ARM komutu artık `SetInputEnabled(14,false)`'in özel bir kontrol türü olduğunu kanıtlıyor

**[G130 gerçek 2010 input/movement method ARM SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39024647915)** [source metadata artifact 12097708669](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39024647915/artifacts/12097708669).

**[G131 aynı ISA gerçek input branch SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39024721893)**.

**[G132 Mach-O original C++ callees resolved SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39024837326)**.

2010 iOS real `SetInputEnabled(lua_State*)` **VM 0x18494**:
- `lua_tointeger(state,1)` ile input ID, `lua_toboolean(state,2)` ile enabled değerini okur.
- **0x184CC `cmp r5,#0xE` → input ID14 için özel dal `0x184F4`**. Kod14 sıradan 2|4|8 genel bit maskesi değildir.
- Özel dal `Game::GetInstance` (0x975E8) → **`Input::ResetKeys()` 0xFFE78**, `Input::ResetTouches(true)` 0xFFFF8, `Input::SetEnabled(0, bool)` 0x1001F8, **`GS_GamePlay::GetMC()` 0xC2518**, **`Actor::Stop()` 0xDB504** çağırır. Ardından ortak **`GamePlayUI::SetUIKeyEnabled(id,bool)` 0x1D260** yoluna katılır.
- Normal ID2 ve ID6 çağrısı, `GamePlayUI::SetUIKeyEnabled` 0x1D260 üzerinde ayrı switch branch ile UI girişlerini etkinleştirir. `Input::SetEnabled` iOS gerçek native pointer girişleri için bayrak kelimeleri kullanıyor (ID0 false ise [input+0x0] = 0x7FFFFFFF, true ise 0), ancak bunun fiziksel **flight-only** izin anlamına geldiği kanıtlanmadı. `GamePlayUI::SetUIKeyEnabled` id14 source 0x1D2D8 özel toplu branch; id2/6 switch cases ayrı.
- Çok önemli negatif ayrım: `luaX_setinput` ARM0xCFB30 **Lua dilinin lexer fonksiyonudur**, oyun kumanda `SetInputEnabled` ile aynı şey DEĞİL.
- **Bu iOS kaynaklara göre ilk açılıştaki 14=false orijinalde kontrol reseti / aktör durdurma ve UI gate operasyonudur**; `Mark V uçmuyor` veya `Stage 2 yasak` iddiasına eşit DEĞİLDİR. Kullanıcının fark ettiği "görev kuralları ve suit yetkileri" ayrımı çok doğru; sonraki adım UI key 2/6 native action mapping ile özgün `Mission000` branch-runtime koşullarını çözmek.

## 4. Sonraki doğru entegrasyon: Level1 first, only mission-authorized movement/combat

İlk Level1'de oyunun 248 Mark V fly/rush animasyonunu önceden *veya tüm suitler için* zorlamamalıyız. Yürüme, hover ve uçuş yetkisi şu üç **ayrı source domain** ile belirlenmeli:
1. Gerçek 2010 suit native hareket kabiliyeti (suitcase capability); **per-armor value henüz kesin değil**;
2. O anki Level1 native Mission/Trigger/QTE durumu ve engine input enabled set;
3. Gerçek oyun actor mode/transitions; game combat animations from 2010 source ownership.

Bu domain'lerin tamamı kanıtlanmadan ilk seviyede uçuşu kalıcı disable etmek de, her zaman Stage2/Rush'a izin vermek de **kaynak sadakati değildir**. Geçerli Vita kaynak derlemesi uçuşu hâlâ modern B14/G83 prototip olarak serbest tutar; source-faithful Mission000 interpreter/execution and native UI key binding are NOT yet installed. Bu rapor Level1 gerçek görevi uygulandı demiyor.

## 5. Kalan asli kaynak render/fizik işleri

- `G128` unbounded absolute-grid bug'ı çözdü ama render mesh triangle katı mı değil mi original 2010 physics author tags hâlâ yok. Özellikle geometri batch materyali üzerinden seçim **deneyseldir**.
- Kamera/MC gerçek scene parent transforms, mission intro`SetCamera`, hasar/AI spawn, atomik gate ve MissionResume şartları eksik.
- Görsel: G71 alpha, G73 original sky sources, G95 original Sun position-based diagnostic light son Vita donanımında yeniden görülmedi; iOS native GL shader/blend/state farkları hâlâ tam çözülmedi.
- **Kullanıcı kesin NO VPK**: G128 gerçek VitaSDK ARM `im2_beta` ELF-only ve G129/G130/G131/G132 host CI; `.vpk` sıfır.

İlgili kod: `research/b24_unified/g108_source_geometry_collision/`, `g129_first_mission_source_rules/`, `g130_original_suitcase_flight_permission/`, `g132_original_input14_native/`; workflow `.github/workflows/g128-full-original-StarkExpo-source-bound-collision-one-Vita-B14-ELF-NO-VPK.yml`.
