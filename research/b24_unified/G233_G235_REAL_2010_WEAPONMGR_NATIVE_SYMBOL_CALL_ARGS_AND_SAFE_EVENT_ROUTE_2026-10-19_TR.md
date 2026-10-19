# G233–G235 — Özgün iOS 2010 WeaponMgr C++ kimliği, gerçek sabit parametreler ve kaynak eşleme modülü

**19 Ekim 2026 · özel `Gh0sTRX/Iron-man-2-os` deposu · `feature/b24-unified-gameplay` · VPK YOK.**

## G233 — dokuz ARM hedefi için gerçek C++ Mach-O sembolleri (CI PASS)

[**G233 özgün iOS 1.0.0 kaynak test sonucu**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39216296529): önceki G232 dört kollu doğrudan BL çağrı adresleri, kullanıcıya ait orijinal **248.613.763 baytlık** 2010 IPA'dan özel GitHub CI içinde çıkarılan **7.480.208 baytlık** orijinal Mach-O `LC_SYMTAB` sembolleriyle eşleştirildi. `G76.parse_macho` ve `c++filt` kullanıldı; önceki G196 gerçek ARM opcode dökümüyle bütün dokuz farklı BL hedefi yeniden karşılaştırıldı. Dokuzunun tamamı gerçek C++ fonksiyon **başlangıç adresiyle birebir** eşleşti; yalnız yakın kaynak sembole bağlayarak isim uydurulmadı.

| Özgün BL hedefi | Kaynak 2010 C++ |
|---|---|
| `0x7FD3C` | `CameraMgr::GetInstance()` |
| `0x7B36C` | `CameraCtrl::ShakeCamera(int,float)` |
| `0xB1F14` | `WeaponMgr::GetWeapon(int)` |
| `0xB1D2C` | `WeaponMgr::GetAssistantWeapon(int)` |
| `0xAB324` | `WeaponDB::GetInstance()` |
| `0xAB3EC` | `WeaponDB::GetAttackEntityByIndex(int)` |
| `0xC1078` | `WeaponEntity::DoAttack(Actor*,int,Actor*,WCollision*,State*,AttackEntity*,int)` |
| `0xC2528` | `GS_GamePlay::GetInstance()` |
| `0xF60AC` | `MainCharacter::DoUniBeamAttack(int,Actor*,float,float,irr::core::vector3d<float> const&)` |

Orijinal IPA ve Mach-O dosyası yalnız geçici CI çalışma dizininde okundu, analiz sonunda silindi; depoya veya GitHub artefaktına orijinal tam binary yüklenmedi. Sadece adres, orijinal C++ isimleri, kesin başlangıç doğrulaması ve belirsizlikler raporlandı.

## G234 — `GetWeapon` / `GetAssistantWeapon` için özgün ARM çağrı sabitleri (CI PASS)

[**G234 kaynak-yalnızca analiz SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39216623274). G196 orijinal 646 ARM komutu ve G233 tam orijinal sembollerinden şu **doğrudan bitişik talimatlar** doğrulandı:

| Olay dallanması | Kaynak ARM talimatları | Anlamı |
|---|---|---|
| Olay `0`, kaynak başlangıç `0xF6C60` | `0xF6C60 MOV r1,#0`; `0xF6C64 ADD r0,r4,#0x32C`; `0xF6C68 BL 0xB1F14` | Özgün `WeaponMgr::GetWeapon(0)` |
| Olay `0`, WeaponDB | `0xF6C74 BL 0xAB324`; `0xF6C78 MOV r1,#0`; `0xF6C7C BL 0xAB3EC` | Özgün `WeaponDB::GetAttackEntityByIndex(0)` |
| Olay `1`, kaynak başlangıç `0xF6CE0` | `0xF6CE0 MOV r1,#0`; `0xF6CE4 ADD r0,r4,#0x32C`; `0xF6CE8 BL 0xB1D2C` | Özgün `WeaponMgr::GetAssistantWeapon(0)` |
| Olay `1`, WeaponDB | `0xF6CF0 BL 0xAB324`; `0xF6CF4 MOV r1,#1`; `0xF6CF8 BL 0xAB3EC` | Özgün `WeaponDB::GetAttackEntityByIndex(1)` |

Bu temel bulgu **silah slotu 0 ile saldırı veri tabanı indeksi 0/1'in ayrı kavramlar** olduğunu gösteriyor. Olay 0 yolunda ayrıca özgün `WeaponEntity::DoAttack(...)` adresi `0xF6CA4→0xC1078`; olay 1'de mevcut yardımcı silahın kullanımı başka dolaylı çağrı/guardlarla sürebilir. Kontrol akışının tamamen çalıştığı, hangi zırhın bu dalı kullanacağı, orijinal tuş veya ateşleme cooldown'ı **kanıtlanmış değil**.

G231/G232 kaynağından olay 2 ve 3 için özgün `DoUniBeamAttack` çağrıları: `event2 0xF6D8C→0xF60AC`, gerçek kaynak Dummy_Chest `14`; `event3 0xF6E04→0xF60AC`, kaynak Dummy_Foot_L `33`. **Statik erişilebilirlik çalışma zamanındaki görsel/silah davranışına eşit değildir.**

## G235 — orijinal `AttackType` ve event 0–3 kaynak çakışmasını engelleyen C11 modülü

[**G235 C11 host CI SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39217015949). Dosyalar:

- `research/b24_unified/g235_verified_four_event_attack_route_reference/b24_g235_original_2010_event_source_reference.h`
- `research/b24_unified/g235_verified_four_event_attack_route_reference/test_g235_original_2010_source_only_event_routes.c`

`b24_g235_original_source_event(original_AttackType,third_u32)` yalnız özgün üst ARM dalı `AttackType 0→0xF6A30` veya `1/18→0xF6930` ise dört kaynak yolun aday metadatasını üretir. Gerçek 0..3 kaynak dalları ve silah veri tabanı index 0/1 veya Uni-Beam dummy 14/33 ayrı alanlarda tutulur. Diğer tüm özgün `AttackType` ID'leri, özellikle War Machine'in `AttackType=25` kaynak Aim_M durumu, **UNKNOWN** döner. `actual_2010_runtime_selected_state_PROVEN` ve `original_controller_or_gameplay_effect_proven` bayrakları her zaman **0**; modülde hasar/mermi/füze üretimi, sahne, animasyon, kullanıcı girişi veya GPU değişikliği YOK. G197 özgün üst ARM jump table ile C11 regresyonu geçer.

İlk G235 workflow dosyasında bir YAML `name:` tırnaklaması hatası vardı ve GitHub işi başlamadan reddetti; daha sonraki `8b3479e` düzeltmesiyle yeniden çalışan **39217015949** host testi başarılı tamamlandı. Önceki reddedilen çalışma PS Vita kaynak motorunun derlenemediği anlamına gelmiyordu.

## Teknik sonuç ve açık işler

Bu kaynak başarısı artık temel/iç-yardımcı silah yolunun aynı doğrudan fonksiyon olmadığına ve orijinal 2010 kodun gerçek sayısal parametrelerine kanıt sağlar. Fakat **orijinal `WeaponDB` entry 0/1 nesnesindeki silah türü, Mark V/VI ve War Machine armor eşlemesi, WM omuz füze/gatling vs hangi buton/TouchHLE gesture, stok/cephane/soğuma, gerçek hasar/hit anı, global 2010 StateMgr runtime seçimleri** henüz çözülmedi. Dolayısıyla G235 gerçek oyunda yeni saldırı çalıştırmıyor; bu kaynak modülü **ilerideki güvenli port entegrasyonunun doğrulanmış sözlüğü**.

G229 host yürüyüş telemetrisi başarılı fakat fiziksel Vita'da yürüyüş kilidi hâlâ çözülmedi. Harita karakter/araç ölçeği, gece skybox/ışık-gölge/alfa, C1L1 ilk görev QTE ve cutscene tam değil. VitaSDK `im2_beta` ARM ELF bu G233–235 turunda yeniden derlenmedi; **VPK hazırlanmadı, gerçek PS Vita testi yapılmadı.**
