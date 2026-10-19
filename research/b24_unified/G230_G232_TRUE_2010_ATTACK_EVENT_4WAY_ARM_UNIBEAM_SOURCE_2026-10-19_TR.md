# G230–G232 — Iron Man 2 (2010) gerçek saldırı olay alt seçim tablosu ve Uni-Beam kontrol akışı

**19 Ekim 2026 · `Gh0sTRX/Iron-man-2-os` / `feature/b24-unified-gameplay` · Orijinal iOS ARM native veri · VPK YOK.**

## Önceki kesin kanıtlar

G213B özgün `states` dosyasını 361.393 bayta kadar çözdü; 55 StateSet, 1.487 StateData, 3.658 StateTrack ve 379 AttackType parametresini doğruladı. G221 gerçek `Actor::UpdateStateAttack` üzerinden `StateTrack::GetEvent` indeksini ve `event[index*12+8]` üçüncü u32 değerini `r2` ile çağrıya aktardı. G222 gerçek iOS `MainCharacter::DoAttack(int,int)` vtable kimliğini doğruladı. G224/G225 DoAttack başlangıcında `AttackType r1→r5`, özgün üçüncü event `r2→r8`, 26 kollu üst saldırı tablosu ve temel `Actor::DoAttack` geri dönüş argümanını doğruladı.

## G230: Gerçek ikinci 4-yollu ARM tablo **kaynak kanıtı**

**[G230 GitHub CI PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39211999462)**. G196'nın özgün, 646 komutluk iOS 2010 ARM dökümü ile G221 StateTrack dosyasını GitHub Actions artifact'larından yeniden yükledik; yalnız metinsel tahminden veya yeni programlanmış saldırı kodundan sonuç çıkarılmadı.

- `0xF6518: MOV r8,r2`: orijinal olay kaydının üçüncü u32 argümanı saklanıyor.
- `0xF6524–0xF6528`: AttackType `r5` için **üst 26 kollu** seçim; kaynak id 1 ve 18 aynı `0xF6930` hedefini paylaşır.
- `0xF6A30: CMP r8,#3`; `0xF6A34: ADDLS pc,pc,r8,lsl #2`: **ayrı 0–3 dört kollu kaynak seçim**.
- ARM PC+8 hesabıyla tablonun gerçek dört `B` kaydı: `event 0→0xF6C60`, `1→0xF6CE0`, `2→0xF6D58`, `3→0xF6D98`.
- Yerel `0xF6930..0xF6A34` bölümünde **r8'e doğrudan overwrite bulunmadı**. Bu yalnız yerel kaynak kanıtıdır; eksiksiz path-sensitive/indirect interprocedural veri akışı ve tüm oyun zamanı seçim koşulları kanıtlanmış değildir.

Orijinal G221 `AttackType` ile ilişkili 56 olay satırındaki üçüncü u32 dağılımı:

| Zırh kaynak StateSet | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| IronMan | 10 | 43 | 2 | 1 |
| IronMan_suitcase | 6 | 47 | 2 | 1 |
| Warmachine | 9 | 44 | 2 | 1 |
| stealth | 6 | 47 | 2 | 1 |

Bu kayıtların tamamı ana saldırı yolunun her çalışmasında bu dört kolu tetikler anlamına **gelmez**.

## G231: Özgün Uni-Beam çağrı yolları

**[G231 gerçek kaynak ARM kontrol akışı PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39212240872)**. Gerçek dört dallanma kökünden, yalnız native direkt `B` / koşullu `Bxx` + düz akış + çağrı dönüşü kabulü ile statik erişilebilirlik grafiği kuruldu. Koşul doğruluğu, dolaylı vtable çağrısı ve runtime state **kanıtlanmış değildir**.

| Olay üçüncü u32 | Orijinal branch başlangıcı | Statik ulaşılabilir kaynak `DoUniBeamAttack` |
|---|---|---|
| 0 | `0xF6C60` | Bu sınırlı grafikte yok |
| 1 | `0xF6CE0` | Bu sınırlı grafikte yok |
| 2 | `0xF6D58` | `0xF6D8C: BL 0xF60AC`; kaynak dummy **14 Dummy_Chest** |
| 3 | `0xF6D98` | `0xF6E04: BL 0xF60AC`; kaynak dummy **33 Dummy_Foot_L** |

Original iOS API `MainCharacter::DoUniBeamAttack` at `0xF60AC`. **Bu tablo 2'nin mutlaka göğüs Uni-Beam, 3'ün mutlaka ayak atışı çalıştırdığı anlamına gelmez**; kontrol akışı statik olarak ulaşılabilirken game state koşulları gerçek runtime'da çağrıyı engelleyebilir. Native dummy index = bağlanmış efektin bütün kaynak PNG/shader/karakter runtime sistemi demek değildir.

## G232: 0/1 ve diğer kollardaki gerçek doğrudan BL site/callee envanteri

**[G232 genişletilmiş G231 CI PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39212414010)**.

- `event 0` kökünden statik erişilebilir özgün kaynak BL: `0xF6C48→0x7FD3C`, `0xF6C58→0x7B36C`, `0xF6C68→0xB1F14`, `0xF6C74→0xAB324`, `0xF6C7C→0xAB3EC`, `0xF6CA4→0xC1078`, `0xF6CB0→0xC2528`.
- `event 1`: `0xF6CE8→0xB1D2C`, `0xF6CF0→0xAB324`, `0xF6CF8→0xAB3EC`.
- `event 2`: `0xF6D8C→0xF60AC` ve önceki kollara dönüş yolu olarak `0xF6C48→0x7FD3C`, `0xF6C58→0x7B36C`.
- `event 3`: `0xF6E04→0xF60AC` ve aynı iki ortak çağrı.

`0xF6C48` ve `0xF6C58` event 0 kökünden daha **düşük adreslerde** olsa da gerçek kaynak unconditional/conditional branch üzerinden ulaşılabilir kabul edildi; logun bu kayıtları isimlendirmesi doğrudan **doğrusal bir sonraki talimat** olduğu anlamına gelmez. Diğer BL hedeflerinin C++ fonksiyon isimleri bu taramada **eşlenmedi**. 0/1 için "füze", "gatling", "repulsor" söylemek henüz kanıtsız.

## Güvenilirlik / sonraki iş

G230, G231 ve G232 gerçek eski GitHub Actions artifaktlarında bulunan orijinal 2010 ARM opcode metadata ve StateTrack kayıtlarından yeni sonuçlar üretti. Üçü de **GitHub CI başarıyla geçti**; VitaSDK ARM derlemesi veya fiziksel Vita testi **yapılmadı**. Oyun kodunda mevcut `DoAttack`, G83/G8 animasyon ve B14 hareket sistemi değiştirilmedi; yeni VPK, sahte hit window, silah butonu veya roket durumu eklenmedi.

Sonraki mantıklı adım: `0xB1F14`, `0xB1D2C`, `0xAB324`, `0xAB3EC`, `0xC1078`, `0xC2528` gibi doğrudan BL hedeflerini özgün Mach-O sembolleriyle doğrulamak, ardından branch predicate ve War Machine runtime silah modu veri akışını çözmek. Ayrıca G229 Vita yürüyüş telemetri sistemi host CI başarıda olsa da **gerçek cihazda yerinde saymanın nedeni hâlâ çözülmedi**. Özgün C1L1 karakter/araç ölçeği, sky/ışık/PNG alfa, melee hasar pencereleri ve Mission000 QTE/intro da açık.
