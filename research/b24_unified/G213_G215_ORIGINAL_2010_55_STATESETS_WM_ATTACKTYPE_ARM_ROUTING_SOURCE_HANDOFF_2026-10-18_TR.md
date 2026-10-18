# G213–G215 — Iron Man 2 iOS (2010) özgün 55 StateSet, War Machine özgün saldırı numaraları ve gerçek ARM hedefleri

**Tarih:** 18 Ekim 2026 · **Repo:** `Gh0sTRX/Iron-man-2-os` · **Dal:** `feature/b24-unified-gameplay` · **Yeni Vita ELF/VPK YOK.**

## Temel sonuç ve kanıt düzeyi

Bu turda gerçek 2010 user-owned IPA'nın `Payload/IronMan2.app/states` (361393 byte) native C++ okuyucusu ve özgün Lua5.1 imzalarından yola çıkarak **55 gerçek `StateSet` adının ve kaynak dosya içindeki birbirinden ayrık sınırlarının tamamı** çıkarıldı. G207'nin 379 özgün `AttackType` u32 kaydı ve G212'nin 365 ham `Attack/attack` olay adayı, 55 özgün küme aralığına güvenilir biçimde konumlandı. Ayrıca G214/G215, Iron Man ile War Machine'in özgün `AttackType` numara setlerinin **farklı** olduğunu ama 26 girişli gerçek native ARM `DoAttack` yönlendirme tablosunda **aynı dallara** gittiğini kanıtladı.

Bunlar **doğrulanmış kaynağın nerede ve nasıl yönlendiğine dair somut ilerlemelerdir**. Aşağıdaki açık sınırlamalar nedeniyle oyun içi füze/Uni-Beam animasyonu, damage event, Vita controller veya gerçek 3B gameplay düzelmiş değildir.

## G213A — Tam ikili yükleme şemasının gerçek C++ ARM talimatları

[**G213A PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39131387192). Orijinal Mach-O içindeki şu özgün C++ constructor kodunun gerçek opcodları incelendi:

- `StateDatabase::StateDatabase(char const*)` 0x9E1A8: dosyadan `u16 StateSet count` okumak ve özgün `StateSetData` constructor'ı çağırmak.
- `StateSetData::StateSetData(BufferStream&)` 0x9D85C: `ReadString` ile özgün grup adını okuma; `u32` Lua byte-length; Lua bytecode; id/name alias girdileri; `u16` StateData count; `StateData::StateData` constructor'ı.
- `StateData::StateData(BufferStream&, StateSetData*)` 0x9C528: state adı ve `u16` property count; `ReadString` key + `u32` value (`AttackType` gerçek u32'leri); ek hareket geçişi kayıtları, animasyon izleri ve diğer alanlar.
- `StateTrack::StateTrack(BufferStream&)` 0xA167C: orijinal 12-bayt olay kayıtları.

İlk iki `StateSet` nesnesi `Apache`, `bigmachine`. File ilk `u16` gerçekten 55; Lua51 imzaları gerçekten 55.

**G213B önemli sınır:** Tam `StateData` nested deserializer'ı doğru şekilde ilk **24 özgün StateSet'i** tarayabiliyor, **IronMan** kümesinin ilk `Idle` kaydındaki karmaşık geçiş/kanal varyantında duruyor. G213B CI **başarılı değil**: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39132700988. Burada kalan ilk isimsiz transition / `Falling` ve `DummyE_Chest` byte akışını yanlış yorumlamamak için runtime sınıfı veya silahın doğru isabet penceresi *kanıtlandı* demiyoruz. G213B scripti kaynağı yutmak/tahmini byte atlamak yerine fail-closed durur.

## G213C — 55/55 özgün küme adı ve 379/379 `AttackType` kaynak grubu

[**G213C PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39132808939). Native `StateSetData` header alanları `u16(len), name, u32(lua_len), <Lua51>` gerçek özgün C++ constructor'a göre okundu. 55 Lua programının **tam gerçek byte uzunluğu** Lua51 parser ile her kümede ayrıca doğrulandı. Source-group aralıkları birbirini örtmüyor, paketin tüm 361393 baytını son grubun EOF sınırına kadar kapsıyor.

| Gerçek kaynak `StateSet` | 2010 kaynak offseti | `AttackType` u32 sayısı | Ham `Attack/attack` kayıt adayı |
| --- | ---: | ---: | ---: |
| `IronMan` | 65057 | **56** | **40** |
| `IronMan_suitcase` | 125542 | **56** | **40** |
| `stealth` | 202780 | **56** | **40** |
| `Warmachine` | 287518 | **56** | **40** |
| `im_ai` | 57071 | 15 | 15 |
| `wm_ai` | 353120 | 15 | 15 |
| `Drone_Floating` | 25598 | 15 | 43 |
| Diğer özgün 48 kümeye dağılan kayıtlar | Kaynak JSON'da | Kalan | Kalan |

G213C **tüm 55 özgün isim** ve `379` ham değer ile `365` G212 adayını bir özgün küme aralığına bağladı. Bu, ilgili `AttackType` değerinin **hangi grup aralığında bulunduğunu kanıtlar**, fakat henüz tekil `StateData` state adı ile `StateTrack` geçişinin birebir aynı record içinde olduğunu kanıtlamaz.

## G214 — Iron Man/Mark V/Stealth vs War Machine gerçek özgün AttackType farkı

[**G214 PASS ve statik PNG artifact**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39133010389). Her oyuncu kümesinde özgün 56 `AttackType` değerinin birebir kaynaktan okunan dağılımı:

| Kaynak `StateSet` | `0` | `1` | `2` | `4` | `18` | `25` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `IronMan` | 24 | 15 | 11 | 6 | — | — |
| `IronMan_suitcase` | 24 | 15 | 11 | 6 | — | — |
| `stealth` | 24 | 15 | 11 | 6 | — | — |
| `Warmachine` | 24 | — | — | 6 | 15 | 11 |

- Her 56 **kaynak AttackType sıralaması** Mark VI/IronMan = Suitcase/Mark V = Stealth birebir aynı; War Machine'de **26 ordinalde farklı**.
- Orijinal `Attack/attack` isimli 40 ham event adayının numeric/signature listesi IronMan ile Suitcase/Stealth arasında her durumda aynı DEĞİL. Bu, orijinal hareket animasyonlarının aynı/başka olduğuna **tek başına** kanıt değildir.
- **Önemli:** `Warmachine` içinde özgün `AttackType 18,25` geçmesi, orijinal 10 adet `Warmachine_Aim_M_Ground` kaynağının otomatik `M=18/25` olduğu anlamına gelmiyor. `WeaponDB` mühimmat / missile event / socket eşlemeleri halen çözülmeli.

## G215 — War Machine ID farkı, native ARM switch'te *eşdeğer giriş dalına* çıkıyor!

[**G215 PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39133228342). **İki bağımsız gerçek kaynak** karşılaştırıldı: G214 4 özgün StateSet içinde ham `AttackType` u32 listeleri ve G196B orijinal 2010 `MainCharacter::DoAttack` native **26 entry ARM switch**:

| Özgün IronMan `AttackType` | Özgün War Machine `AttackType` | Aynı native ARM `B` hedefi | Orijinal iki kümede tekrar sayısı |
| ---: | ---: | --- | ---: |
| **1** | **18** | **0xF6930** | 15'er |
| **2** | **25** | **0xF6648** | 11'er |

Yani IronMan'in 56 `AttackType` değeriyle War Machine'in 56 değeri **26 konumda farklı** olsa da **her iki kümenin 56 source entry'si de aynı native `DoAttack` branch destination dizisine gidiyor**. İddia sınırı: aynı branch dest ≠ aynı orijinal silah/hasar/animasyon/hitbox, çünkü dal içi ekipman ve state durumu değişebilir. O nedenle Vita'daki War Machine `18→1` veya `25→2` şekilde kalıcı yeniden adlandırılmayacak; kaynak enum ayrımı korunacak.

## G216 için sonraki net adımlar

1. G213B'de kalan gerçek `StateData::StateData` boş isimli transition, `Falling` ve `DummyE_Chest` mixed source record varyantını gerçek ARM pointer / BufferStream virtual `Read` sırasından çözüp **55 StateSet, 194+ IronMan state record ve tüm StateTrack nested data için 361393/361393 EOF strict parser** kanıtla.
2. Her **gerçek single StateData adı** → AttackType u32 → StateTrack event zamanları → özgün `.anim` kaynak filename ilişkisinin tam ispatı. G212'deki 365 ham event adayı henüz 'gerçek verified event' sayılmıyor.
3. Çözülmüş G215 aynı branch hedeflerinin dal içi `WeaponMgr`, `WeaponDB`, `AttackEntity` ve `Gun01–04`/missile repulsor beam → gerçek WM/IronMan `M` etkinliklerini nasıl ayırdığı. G173 orijinal Uni-Beam 12 anim, G195 hareketli gerçek Chest/Foot rig etkisi hedef.
4. Vita cihazının önceki temel sorunları **AÇIK**: hareketin yerinde sayması, araç/çevre ölçeği, gerçek gece sky/ambient/shadows, WM tüm özel silahlar/animasyonlar, özgün melee hit frame, QTE/cutscene/misyon engine. Kaynak statik host araştırması Vita'nın fiziksel cihazda düzeldiği kanıtı değildir.

**G213A/G213C/G214/G215 kaynak testleri başarılı; G213B tam nested parser halen doğrulama aşamasında başarısız. Yeni Vita ELF/VPK veya görseli uydurulmadı, etkileşimli HTML yapılmadı.**
