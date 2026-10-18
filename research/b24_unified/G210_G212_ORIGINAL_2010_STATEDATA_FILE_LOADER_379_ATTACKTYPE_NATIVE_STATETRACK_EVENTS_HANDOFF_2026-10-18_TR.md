# G210–G212 — Orijinal Iron Man 2 (2010 iOS): gerçek StateDatabase dosya yükleme zinciri ve StateTrack olay pencereleri

**18 Ekim 2026 · `Gh0sTRX/Iron-man-2-os` · `feature/b24-unified-gameplay` · YENİ VPK/ELF YOK.**

## Kullanıcının hedefi
Vita'ya özgün 2010 iOS oyununun hareket, ateş, Uni-Beam, War Machine, melee, HUD ve görev motorunu taşırken native kaynak kanıtı olmayan silah/input/moveset davranışı uydurma. G196–209 kanıtlı 26 `DoAttack` seçici dalı ve 379 orijinal state `AttackType` kayıt değerleri gerçek iOS kaynağından çıkarıldı. **26 AttackType/native selector girdisi tüm dokunmatik kontrol sistemini çözmek değildir:** ekran dokunuşu/gesture, joystick, hedefleme, silah değiştirme, sprint/walk, hover/flight/rush ve Lua input permission ayrı sistemler.

## G210 — Gerçek 2010 native FileStream → BufferStream → StateSetData → StateData

[**G210 CI PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39130254660).

G210 original iOS user IPA'nın gerçek ARM Mach-O sembol/decode'undan **15 kesin native BL** kenarını doğruladı:

- `StateDatabase::StateDatabase(char const*)` (0x9E1A8): gerçek `FileStream::FileStream` (0x9E200), `FileStream::Size` (0x9E208), `FileStream::Read` (0x9E234), `FileStream::Close` (0x9E240), `BufferStream::BufferStream` (0x9E254), `StateSetData::StateSetData(BufferStream&)` (0x9E55C).
- `StateSetData::StateSetData(BufferStream&)` (0x9D85C) gerçek `StateData::StateData(BufferStream&,StateSetData*)` (0x9DF60), gerçek `BufferStream::ReadString()` (0x9D8D0).
- `StateData::StateData(BufferStream&,StateSetData*)` (0x9C528) gerçek `BufferStream::ReadString()` (0x9C5F0, 0x9C84C, 0x9CBB0, 0x9CD2C, 0x9D24C) ve `StateTrack::StateTrack(BufferStream&)` (0x9CFE4) çağrıları.
- `Actor::UpdateStateAttack(int,State*)` (0xDB610) gerçek `StateData::GetParam(char const*,int)` (0xDB65C, hedef 0x9C340) kullanıyor. G203 önceki native kaynak literal anahtarı `"AttackType"` ve default `-1` ispatlamıştı.
- Orijinal `BufferStream` virtual read çağrılarının gerçek ARM VTABLE argümanları G210'da kaynaktan ayrı ayrı: `database: r4`, `state_set: r6`, `state_data: r3`. Tek bir hayali register varsayılmadı.
- **379/379** kaynak `states` dosyası `u16LE(10), "AttackType", u32LE(value)` byte offset ve değeri G207 raporuyla yeniden birebir karşılaştırıldı; hepsi 0–25. Kaynak native `GetParam` 8-byte bellekte key pointer/value offset+4 okuyor.

**Sınır:** Kodun bu fonksiyonları içerdiği kesin; gerçek iOS runtime'ın belirli bir `states` dosyasını hangi aktif actor/armor'a ne zaman yüklediği ve her 379 parametrenin gerçek state nesnesi sınırları henüz cihaz/TouchHLE runtime izinde ispatlanmadı. G210, böyle bir runtime yürütme olmadığından Vita'daki saldırı/movement işleyişini değiştirmiyor.

## G211 — Native StateTrack 12 bayt özgün event zaman yapısı

[**G211 CI PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39130512289).

- `StateTrack::StateTrack(BufferStream&)` özgün ARM gövdesi **0xA167C** (kaynak constructor thunk 0xA196C bu entry'ye branch yapıyor).
- `StateTrack::GetEvent(int,int)` özgün ARM gövdesi **0xA14F0**.
- `StateTrack` constructor `BufferStream::ReadString` (0xA16C8) ile özgün track adı ve virtual read ile `u16` event sayısı yükler; native ARM `LSL count,#4` ardından `SUB count, count, count LSL #2` **12 bayt × count** array allocation/copy hesaplamasını doğruluyor. Üç 32-bit alan özgün.
- `GetEvent` kaynak ARM entry+[0] başlangıç değerini, entry+[4] süresini okuyor, **end=start+duration** hesaplayıp sorgunun iki zaman argümanına göre karşılaştırıyor. Göstermeyen durumda gerçek kaynak `MVN r0,#0` = **-1**. Sonraki kayıt adımı **+12 bayt**.
- Üçüncü 32-bit alan anlamı, değerlerin saniye/ms/tick birimi ve `AttackType` ile `WeaponDB` hasar/yayın/frame ilişkisi henüz kanıtlı değildir. `GetEvent`'in zaman aralığı var diye "şu frame vuruyor" denmez.

## G212 — Orijinal `states` ikili dosyasındaki named Attack/attack track event KAYIT ADAYLARI

[**G212 CI PASS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39130759380).

Orijinal `Payload/IronMan2.app/states` (361393 bayt), native kaynak `StateTrack` constructor'ın `u16 stringlen + name + u16 unknown + u16 count + 12×count` örtüşmesine göre **byte-for-byte** tarandı:

- `Attack` birebir adının 13 ham eşleşmesi, `attack` adının 360 ham eşleşmesi.
- Şema sınırlarıyla örtüşen toplam **365 kaynak aday kaydı**: `Attack` 9 adet, `attack` 356 adet.
- Bu kayıtlarda **611 orijinal 12-byte event veri üçlüsü** aday olarak çıkarıldı. Gerçek authored original byte-offset, ilk `u32` başlangıç, ikinci `u32` süre, üçüncü sınıflandırılmamış `u32` JSON'a kaydedildi.
- Örnekler: kaynak dosya ofset 6295 `Attack` → **start=477 duration=0**, 6425 → **472,0**, 6549 → **471,0 ve 871,0**, 6952 → **490,1300**; kaynak 4943 `attack` → **450,1300**, 5698 → **580,1000**. Bunların birimlerini **ms** olarak isimlendirmek henüz kanıtlı değil ve hiçbirinin gerçekten hitbox/beam fire frame'i olduğu kanıtlanmadı.
- Sırf ASCII `Attack` veya `attack` rastlantısal eşleşmesi olabileceğinden şema ve bounds kontrolü uygulansa bile **365 kaydın tamamının native StateTrack ctor tarafından runtime yüklendiği ayrı kanıt gerektirir**.
- Orijinal 2010 kaynak sayılardan ve bunların konumlarından statik önizleme çizildi: `G212_IronMan2_2010_Kaynak_Attack_Event_Zaman_Araliklari.png` (yalnız bu konuşmada; gerçek iOS/Vita oynanış görseli değil, etkileşimli HTML değil).

## G213 sonraki doğru amaç ve geride kalan Vita oyun problemleri

- `StateDatabase` kaynak `BufferStream` binary parser'ını **55 StateSet** ve her bir `StateData/StateTrack` için tüm alanlarda endian, boyut, event sayısını kullanarak sıfırdan eksiksiz yeniden parse etmek; G212 365 adayın hangilerinin gerçekten StateTrack olduğu ve hangi state/suit/weapon'a ait olduğu bu sayede kesinleşecek.
- Ardından `Actor::UpdateStateAttack`, `WeaponMgr::GetCurrentWeapon`, `MainCharacter::DoAttack` / `DoUniBeamAttack`, G83/G169 gerçek animasyon owner ve event time kaynağı ile **kanıtlı** bağlama. Özellikle G173 Uni-Beam 12 source anim ve G195 Dummy_Chest/Foot gerçek moving joints ile sinyal zinciri.
- **Cihazda açık işler:** karakterin yerinde yürüyüşü (movement controller/root/world transform), özgün araba karşısı ölçek, gece çevre ışığı/gölge/skybox/ay, War Machine gun/rocket + Aim_M gerçek input semantics, özgün melee combos/hit windows, C1L1 QTE/mission flow. Bunların hiçbiri G210–212 CI host raporuyla Vita'da düzeldi ilan edilmez.
- **G210–212 yalnızca orijinal iOS kaynak + GitHub CI testleri. Yeni Vita ELF/VPK üretilmedi.**
