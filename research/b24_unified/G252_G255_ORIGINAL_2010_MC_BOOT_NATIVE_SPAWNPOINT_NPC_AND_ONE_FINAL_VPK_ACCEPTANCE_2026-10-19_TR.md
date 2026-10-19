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

## G255: Kullanıcının istediği tek VPK testinin **iki aşamalı** doğru kalite kapısı

**[G255 final düzeltilmiş iki aşamalı CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39239447197).** İlk modelde fiziksel Vita'da oyun çalışmadan önce Vita hardware QA istenmesi bir **test/ilk paketleme kilidi** yaratıyordu; bunu açıkça düzelttik. Kullanıcının niyetine uygun doğru sıra:

1. **Tek test VPK ÖNCESİ kaynak kabulü:** `g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json` 7 bağımsız alt sistemin **kaynak birleşme + gerçek original host C11 testleri + tek Vita ARM ELF derlemesi** tamamlanınca source-ready olacaktır: (a) doğru MC dünya kökü/zemin, (b) yer/hover/flight/rush + collision, (c) bütün player rig/anim/state/inputs, (d) özgün WeaponDB/combat/WM gun/missile/hit/damage, (e) karakter/araç oranı, şehir, sky/lighting/alpha/HUD/camera, (f) özgün Mission000 QTE1456/cutscene/audio/düşman dalgası/görev tamamlanma host zinciri, (g) **aynı commit'te tam Vita ARM ELF + host testleri**.
2. **Sonra sadece bir kaynak-bütünleşik TEST VPK** paketlenip gerçek Vita cihazına kurulacak. VPK ilk kez kurulduktan sonra G229 120 gerçek ground frame telemetry, GPU root/çarpışma, gerçek hareket/flight, animation/combat, HUD/scene/mission gameplay QA yapılacak. **Gerçek cihazda çalışmayan bir sistem çıkarsa bunu tamamlandı saymayıp aynı test VPK üzerinden düzeltme listesine alacağız; sürekli gereksiz paketleme yapmayacağız.**
3. **Cihaz testinden SONRA 12 özgün gameplay/animasyon/camera/mission parity kabul kapısı** `research/b24_unified/g83_final_vpk_gate/READINESS_STATUS.json` üzerinden kanıtlı biçimde kapatılacak. Cihazda test edilmeden bu 12 gate'i VPK önkoşulu yapmak mantıksal hata olur.

G255 `g255_fail_closed_one_vpk_only_after_original_vita_gameplay_qa.py` bu iki ayrı dosyayı okuyor; `--require-ready` **yalnız 7 source-ready gate** kapanınca tek test VPK source preflight onayı verir (hazır değilse exit 3). `--require-device-parity` sonradan 12 gerçek cihaz/orijinal oyun parity şartını gerektirir (hazır değilse exit 4). CI'nın test ettiği geçerli durum: **7 source kapıdan 0 tam**, **12 gerçek Vita kalite kapısından 1 tam (yalnız 972/972 animation source indeks)**. Bunlar **oyun motorunun %0 veya %8 tamamlandığı anlamına gelmez**, çok katı **bitiş kapılarıdır**, ara kaynak sistemi hâlâ çalışıyor.

**Yüksek öncelikli açık asıl işler:** gerçek player MC PositionData + parent/world boot, G229 Vita ground root, özgün WeaponDB runtime kayıt sırası/hit-frame/damage, 338 gerçek compatible clip state owner, arabaya göre karakter ölçeği, gece sky/lighting/alpha, Mission000 özgün giriş QTE1456 ve düşman dalgası. İlk test VPK **şu an oluşturulmadı**, 7/7 kaynak kapıları kapanmadan paketlenmeyecek.
