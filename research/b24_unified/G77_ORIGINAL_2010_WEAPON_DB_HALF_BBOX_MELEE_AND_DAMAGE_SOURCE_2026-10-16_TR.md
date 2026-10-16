# G77 — Orijinal Iron Man 2 (2010 iOS) WeaponDB, melee hitbox ve gerçek hasar matematiği

**Tarih:** 2026-10-16. **Ana kural:** Mevcut G73 Vita VPK'sı değiştirilmeyecek, G75 birleştirilmiş kaynak kodu korunacak, yeni VPK üretilmeyecek. Orijinal IPA'nın ARM Mach-O sembolleri ve G76 meta-analizleri kanıttır; bizim B14 C prototipinin silah sayıları özgün veri diye sunulmayacak.

## Gerçek kaynak / kanıt

- Önceki G76 orijinal 2010 IPA ikili araştırmasından kaynak dosyaları: `G76D_ORIGINAL_NATIVE_DAMAGE_HP_COMBO_ARM_INSTRUCTION_TRACE.json`, `G76B_ORIGINAL_2010_NATIVE_DAMAGE_COMBAT_DIRECT_CALL_GRAPH.json`, `G76_TRUE_2010_COMBAT_HURT_ANIM_SOURCE_CHANNEL_REPORT.json`, `G76C_ORIGINAL_2010_STATES_WEAPON_EFFECT_SOUND_SOURCE_METADATA.json` (Actions https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38927056851).
- G77 kaynak-derlenebilir deneyler ve kodlar `research/b24_unified/g77_original_weapon_db/b24_g77_native_weapon_db_index.c/.h`, `b24_g77_melee_source_radius.c/.h`; ayrıca G76 düzeltmesi `g76_original_combat/b24_g76_original_native_damage_math.c/.h`.
- Kaynak gösterimi her bir ARM kodu için gerçek **orijinal** 2010 Mach-O adreslerine dayanır; bu C kopyaları yalnızca izole matematik/erişim çekirdekleridir. Orijinal bitiş/hasar animasyon olaylarının **tam yeniden üretimi değillerdir**.

## 1. WeaponDB orijinal saldırı tanımları

**Fonksiyon:** `WeaponDB::GetAttackEntityByIndex(int)` **ARM adresi 0x000AB3EC**. Gerçek komutlar:

- `ldr r3,[r0,#0x38]` → obje +0x38 giriş sayısı
- `ldr r0,[r0,#0x30]` → obje +0x30 saldırı tanımı işaretçi dizisi
- `ldr r0,[r0,r1,lsl #2]` → dizi[index] 4 bayt işaretçi
- `cmp` / `bge` ve `mov r0,#0` → indeks negatif veya >= sayısı ise NULL.

Kaynak C referansı aynı indeks/sınır davranışını düz 32/64-bit uyumlu API ile veriyor; 32-bit oyun nesnesinin 64-bit PC'de birebir belleğe dökümü olduğunu iddia etmiyoruz. **Host + Vita ARM kaynak derleme testi başarılı:** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38933759699.

`MainCharacter::DoUniBeamAttack` doğrudan `WeaponDB::GetAttackEntityByIndex` çağırıyor. Hangi indeks hangi saldırı, kayıtların veri dosyası, özgün silah hasarları henüz çözülmedi. Yeni kaynak IPA arama denemesi için `g77a_owned_2010_weapon_db_asset_origin.py` ve `g77b_original_arm_WeaponDB_and_Melee_bbox_literal.py` yazıldı ancak **orijinal IPA üzerinde G77 yeni tarama çalıştırılıp başarılı diye işaretlenmedi**.

## 2. Gerçek melee çarpışmasının kaynak sabiti **0,5**

**Fonksiyon:** `Actor::TestMeleeHit(Actor*)` **0x000DFD94**.

- Kod göreli **+0x20**: `vldr s16,[pc,#0x110]`. ARM'de PC-relative literal adres = mevcut ARM komutu +8 +0x110 → fonksiyon göreli **+0x138**.
- G76D ham komut çözümleyicisi bu değeri kod sanarak `svclo #0` gösteriyor; bu **çalıştırılan komut değil**, fonksiyon sonrasındaki literal havuzu veri. ARM `svclo #0` kod sözcüğü `0x3F000000`; IEEE-754 tek duyarlık olarak **0,5**.
- Orijinal `Model::GetBoundingBox` iki ayrı modelde çağrılıyor. Kutu boyutlarının 3 eksen farklarının kareleri toplanıp karekökü alınıyor, her biri 0,5 ile çarpılıyor. Bu iki yarı-köşegen büyüklüğü ve kaynak başka bir dinamik/global tolerans, ikinci 3B ayrım mesafesine karşılaştırılıyor: `vcmpe.f32 s13,s15; movhi r0,#0; movls r0,#1`.
- Orijinal global toleransın sayısal değeri ve sanal metot tarafından getirilen hangi noktaların mesafesi olduğu **henüz tam eşleşmedi**. Bu nedenle C fonksiyonunda orijinal bilinmeyen tolerans ve iki kontrol noktası **parametre**; uydurma sabit yok.
- Kaynak C `b24_g77_melee_source_radius.c` ve testleri gerçek 0,5 sabitini kullanıyor, tam Vita oyunu/animasyon döngüsü henüz bağlı değil.

## 3. Actor::Damage(float) ikili dayanıklılık, önemli G76 düzeltmesi

2010 ARM `Actor::Damage(float)` **0x000D9194**:
- Nesne `+0x3BC` birinci dayanıklılık float, `+0x394` ikinci dayanıklılık float.
- Birincisi pozitifse sadece birinci havuz azaltılır; bu havuz alt limit **0**.
- Birincisi zaten tükenmişse ikinci havuz azaltılır. **Orijinal `vstr s15,[r0,#0x394]` sonunda ikinci havuz alt limit 0'a çekilmiyor, negatif sonuç bellekte kalabilir.** G76 modelinin bunu 0'a kırpması yanlıştı; G77 kodu ve testleri düzeltildi.
- Aynı darbede birincinin negatif taşması ikinci havuza otomatik aktarılmıyor; özgün ölüm/hurt status sanal fonksiyonları hâlâ ayrı.
- +0x3BC “shield”, +0x394 “health” diye isimlendirmek için özgün sınıf/property bağlantısı gerekir; şimdilik `primary_resource`, `secondary_resource`.

Kaynak C test: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38932672217 **SUCCESS** (PC host + Vita ARM nesne derlemesi).

## 4. Özgün ses ve animasyon verisi

- İlk üç Mark VI combo animasyonu özgün `.anim` veri bankasında 266ms, 300ms ve 500ms; doğrudan 2010 ham keyframe kanalları G76'da çözüldü. Bu değerler *hit window* değil.
- 160 özgün `sfx_` dosyası, 66 savaşla ilişkili isim. `sfx_combo_1/2/3.www` başlıkları gerçekten `RIFF/WAVE`, ancak PCM kodek/samplerate ve Vita üzerinde playback **henüz test değil**. `g77c_original_sfx_www_wave_codec_audit.py` raporlayıcı yazıldı, bu G77 aşamasında yeni orijinal IPA taraması çalıştırılmadı.

## Yapıldı / Yapılmadı

**Yapıldı:** Gerçek WeaponDB indeks/sınır mantığı 2010 ARM komutlarından çıkarılıp kaynak C'ye yazıldı, PC ve Vita ARM testlendi. Gerçek 0,5 melee çevre/mesafe sabiti literal havuzundan çözüldü ve kaynak C çarpışma matematiği yazıldı. İkinci hasar havuzunun negatif sonuç davranışı düzeltildi. Özgün 2010 kombo animasyon/ses veri kaynaklarının varlığı önceden G76 ile doğrulandı.

**Henüz yapılmadı:** Orijinal WeaponDB kayıtlarından her repulsor/füze/Unibeam hasar değeri, bitiş/hurt animasyonunun vuruş karesi, gerçek kaynak ilave melee toleransı, özgün tam NPC AI davranışı, orijinal `.www` seslerin Vita üzerinde oynatımı, G77 birleşik oyun üzerinde gerçek PSVita testi.

**VPK yok.** G73 kurulu sürüm ve G75 korunan birleşik prototip kaynakları değişmedi. B24'ün uydurma sayısal hasar değerleri özgün Gameloft verisi diye sunulmadı.
