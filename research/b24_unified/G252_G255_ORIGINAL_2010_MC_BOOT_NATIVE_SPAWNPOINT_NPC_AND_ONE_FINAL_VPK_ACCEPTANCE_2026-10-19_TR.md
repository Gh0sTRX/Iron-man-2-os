# G252–G255 — 2010 native oyuncu başlangıç zinciri / düşman SpawnPoint ayrımı ve TEK VPK kalite kapısı

**19 Ekim 2026 · `feature/b24-unified-gameplay` · KESİN: yeni VPK YOK, gerçek Vita donanım testi yapılmadı.** Kullanıcı talimatı: oyuncu movement, özgün combat/flight/moveset/animasyon state mapping, orijinal MC spawn/çarpışma/ölçek, HUD/ışık/skybox, Mission000 QTE/audio/AI bütünlenmeden VPK yapma; sonuçta **tek bütünleşik test VPK**.

## G252: Gerçek orijinal sınıf 71 SpawnPoint, player startup değil NPC/wave sınıfı çağrıları

**[G252 genuine original 2010 Mach-O + C1L1 Lua CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39238133152)**, ilk CI sembol listesinin nsyms/filtered entry sayısı karışıklığı nedeniyle FAIL olmuştu; ikinci başarılı kaynaktan doğru.

- `GS_GamePlay::LoadEntities()` gerçek 2010 ARM switch class71 gerçek kaynak native jump-table `0xC2FF8 B 0xC3538`.
- `0xC3558 BL SpawnPoint::SpawnPoint(GS_GamePlay*, LuaScript*, MainCharacter*)` **orijinal native constructor** `0xBE74C`.
- G252 gerçekten **18 `SpawnPoint::` C++ named source symbol** buldu. Bizzat `GetPosition 0xBD2CC`, `IsWaveKilled 0xBD2F8`, `Init 0xBD40C`, `IsAllWavesKilled 0xBD978`, `KillMySpawnEnemy 0xBDC44`, `LoadFromFile 0xBDD40`, `Spawn(Entity*,bool) 0xBEBD4`, `Update 0xBF030`, `SelectSpawnPosition 0xBF304`.
- Özgün 2010 ilk bölüm 71 Lua callback'teki typed `SpawnPoint` ID kullanımının **16 `Enable` + 8 `KillSpawnpointEnemy`** olduğu (24 bağlantı) kaynakla doğrulandı. `Mission000_OnStart` bu 16 SpawnPoint'e doğrudan referans vermez.
- **Sonuç**: bu düğümler düşman üreme/dalga kontrolü için kullanılıyor. Bir native oyun motoru bunlardan birini ayrıca player pozisyon kaynağı olarak da kullanıyor olabilir; **kesin hiç player amaçlı kullanılmaz** demek doğru değildir. 2010 kaynak `SpawnPoint` düğüm pozisyonlarını Vita'da oyuncu ayak konumu gibi uygulama.

## G253: MainCharacter oyuncu oluşturma gerçek orijinal fonksiyonları

**[G253 gerçek 2010 owner Mach-O C++ method/call CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39238427873)**.

- Aynı original `GS_GamePlay::LoadEntities()` içinde özgün `0xC36FC BL MainCharacter::MainCharacter()` `0xEC108`. Bu, `SpawnPoint` class71 değil, **asıl `MainCharacter` sınıfını kuran doğru native orijinal oyun engine yoludur**.
- `MainCharacter::LoadFromFile(EntityData*, StateDatabase*)` `0xEC2CC`, `MainCharacter::Init()` `0xEEC64`; gerçek önemli iOS Source owner methods.
- `Entity3D::LoadFromFile` `0x12C78`; `Actor::Init` `0xDBBE0`; `Actor::LoadFromFile` `0xDA93C`.
- Özgün source `MainCharacter::UpdateMoveNavigation 0xF818C`, `UpdateFloatNavigation 0xF7174`, `UpdateFlyNavigation 0xF89AC`, `UpdateInput 0xF3398` ve `OnStateChange 0xF7730` artık gerçek C++ name/provenance tablosunda; yöntemlerin tam anlamı/parametreleri/animasyon input mapping'i henüz çıkarılmadı.
- Ayrı orijinal `Entity3D::OnSpawn(SpawnPoint*,Entity*)` içinde `SpawnPoint::GetPosition()` ve `SelectSpawnPosition()` kullanan NPC/wave yoluna kanıt var. MainCharacter boot'taki kesin dünya xyz'yle bir tutulmadı.

## G254: Özgün MC EntityData→PositionData, StateMgr + WeaponMgr init

**[G254 gerçek original 2010 iOS full native source CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39238652757)**.

- `GS_GamePlay::LoadEntities()` `0xC36FC BL MainCharacter ctor`; source ardından `0xC3728` **vtable +0x68** üzerinden orijinal gerçek `EntityData` pointer ile oyuncu yükleme çağrısı; bu çağrıyı doğrudan `MainCharacter::LoadFromFile` yerine koymak doğru değil, vtable slot eşlemesi ayrıca doğrulanacak.
- `MainCharacter::LoadFromFile` `0xEC2EC BL Actor::LoadFromFile(0xDA93C)`; `Actor::LoadFromFile → Entity3D::LoadFromFile(0x12C78)`; `Entity3D::LoadFromFile 0x12C98 BL PositionData::PositionData(0xC8200)`. Runtime karakter konum kaynak zinciri böyle daraltıldı.
- `MainCharacter::Init 0xEEC78 BL Actor::Init(0xDBBE0)` ve `0xEEC84 BL Actor::InitWeaponData(0xDA694)`. `Actor::Init 0xDBCBC BL WCollision::Init(Actor*,PositionData*)`. Özgün `MainCharacter::Init` aynı zamanlarda pek çok `StatesMgr::GetStateId` / `GetState` çağrısı yapıyor; G8 animasyonun gerçek iOS native state driver'ına bağlandığı alan belirlendi.
- **KESİN eksik**: `Entity3D::LoadFromFile` içindeki orijinal parent/root/relative 3B sahne dönüşümlerinin tamamını gerçek dünya koordinatı olarak çıkarmak, Mission000 oyuncu boot Z, portun doğru başlangıç XY/Z'si; `MC` source local transform `(-1.319,-6.747,25.054)` doğrudan gameplay ayak koordinatı gibi kullanılamaz.
- G249 source `MC` XY farklı Z katmanlarında gerçek G66C, duvar715 yürüyüşü tamamen kilitleyebilir; G251 source noktalardan 3 elevated node yerde 0/8 uçuş 8/8. **Bu kaynak semptomu fiziksel Vita hata nedeninin kesin kanıtı değildir**. Gerçek `G229_WALK_WINDOW` logu gerekecek.

## G255: Kullanıcının istediği bitince sadece BİR test VPK kuralı

**[G255 otomatik fail-closed release CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39238988565)**.

`research/b24_unified/g83_final_vpk_gate/READINESS_STATUS.json` 11 eski standardın üzerine 12. orijinal `Mission000/QTE/audio/cutscene/completion` gerçek bitiş şartı eklendi. `g255_fail_closed_one_vpk_only_after_original_vita_gameplay_qa.py` 12 gate schema, kaynak kanıt URI'leri ve fiziksel Vita gerektiren kapılar için gerçek test ayrıntıları olmadan onaylamıyor. `--require-ready` hazır değilken **exit status 3**, GitHub CI tarafından assert edildi; herhangi bir VPK paketleme komutu çalıştırılmadı.

**Mevcut veri: 12 gerçekten tamamlanması gereken release kalite kabul kapısından yalnızca `972/972 animation source data indexed` alanı verified**, diğer 11 alan verified değil. **Bu, bütün motorun yalnız %8 ilerlediği anlamına gelmez**; kaynak reverse-engineering, anim decode, host collision ve ARM ELF gibi ara aşamalar çalışıyor, ama cihaz/özgün oynanış kabulü hâlâ açık.

Yüksek öncelikli gerçek işleri şimdi: (1) original `MainCharacter` root position parent+local+world iOS bytecode; (2) `G229` gerçek Vita'da yer hareket logu / reproducer; (3) gerçek iOS combat AttackType/WeaponDB runtime array/arm manager, hit/frame/damage; (4) özgün G8 tüm 338 player clip rig compatibility, WM uçuş/yürüyüş ve event command; (5) C1L1 scaling/car, sky/lighting/shadows/alpha; (6) gerçek Mission000 1456 intro QTE/cutscene/audio/NPC wave ve gameplay ending.

Birinin standartları karşılaması için testler, hedef sistemde çalışan gözlemi ve gerçek kaynak verisi gerekir. Böylece **tek VPK** ortaya çıktığında bütünleşik ve anlamlı olacak. VPK'yi erken üretmek/körleme teleport/düşman hasarı uydurmak yok.
