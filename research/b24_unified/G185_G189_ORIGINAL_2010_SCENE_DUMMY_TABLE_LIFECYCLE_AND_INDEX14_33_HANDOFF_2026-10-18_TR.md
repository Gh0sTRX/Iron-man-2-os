# G185–G189 — 2010 orijinal iOS Iron Man 2 Uni-Beam dummy group 14/33: `SceneImpl::s_dummiesTable` gerçek başlangıç ve kayıt yönetimi

**18 Ekim 2026 · `feature/b24-unified-gameplay` · kaynak-only çalışma · VPK yok.**

## Önceki sağlam kanıtlar (G175–G184)

Özgün C++ `MainCharacter::DoUniBeamAttack` fonksiyonu native `WeaponDB::GetAttackEntityByIndex(4)` çağırıyor. Orijinal `MainCharacter::DoAttack(int,int)` üç ayrı gerçek `BL DoUniBeamAttack` çağrısında `14`, `14`, `33` ilk integer parametreleri kullanıyor. `Object3D::GetDummyAbsolutePosition` içinden `SceneImpl::GetDummy(int,unsigned int)` (VM `0x61724`) çağrılıyor. Gerçek `SceneImpl::GetDummy` `scene+0x278` tablosundan **grup 14/33 → grubun eleman 0'ı** seçiyor; bu ID'ler **kesin BDAE bone listesi sırası değildir**.

## G185 — özgün grup kaydına ilişkin gerçek ARM akışı

[GitHub Actions G185 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39114341693). `SceneImpl::CollectDummies` ARM `0x63108–0x63714` aralığından **388** özgün assembly talimatı ve **71** bellek store işlemi, 7 gerçek direct-call kaydedildi. `0x63664..0x6367C` bölümü eleman listesine ekleme ve eleman sayısını arttırma işlemleri; `0x6370C` kaynak pointer yerleştirme, `0x63714` gerçek `+0x278` sahne üyesi okuma. Tam kod sırası ve kaynak register akışı JSON kanıtında. Orijinal sembol tablosundan **`SceneImpl::s_dummiesTable` = `0x4EDCA0`** doğrulandı.

## G186 — önemli önceki hatanın düzeltilmesi

[GitHub Actions G186 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39114550231). İlk G184/G185 kodunda Mach-O `__common` bölümünün nominal *dosya offset 0* değerinden okunan `972, 5127504, 2` rakamları yanlışlıkla potansiyel statik içerik gibi raporlanmıştı. Orijinal Mach-O section_32 flag gerçek `0x1` → **`S_ZEROFILL`**; bölüm `__DATA/__common`, sanal `0x4ED800`, 25.600 bayt ve **dosyaya bağlı initialized veri değil**. Bu üç sayı kaynak tablonun gerçek runtime değerleri **DEĞİLDİR**.

G184/G185 betiklerine `__common/__bss` file-read blokajı eklendi ve önceki ham sayılar düzeltilerek ***unavailable*** kabul edildi. G187 kaynak literal taramasına da `[pc,rX]` register-indexed ifadesini PC-immediate gibi yorumlamayı engelleyen katı kontrol eklendi.

## G187 — gerçek C++ global ctor

[GitHub Actions G187 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39114797612). Gerçek sembol **`global constructors keyed to SceneImpl::s_dummiesTable` VM `0x3C60`**, gerçek branş `0x3B80`. 47 ARM talimat ve iki `BL 0x4705F4` görüldü. İki static object initializer/dtor-registration bölgesi var; bunlar orijinal dummy adlarını otomatik açığa çıkarmıyor.

## G188 — özgün boş tablo oluşturuluyor, API fonksiyonları bulundu

[GitHub Actions G188 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39115025388). Native `0x3BF4` ARM PIC literal'dan `0x3BFC ADD r1,pc,r3` ile tam `0x4EDCA0` gerçek tablo adresi alınıyor. `0x3C0C/0x3C10/0x3C14` talimatları gerçek `r5=0` değerini tablo header'ındaki üç 32-bit alana yazıyor. Böylece `s_dummiesTable` **boş veri yapısıyla başlıyor**.

Orijinal named `SceneImpl/SceneMgr` **48** yöntemi tarandı; dört yöntem bu tablo için gerçek PIC xref içeriyor:
- `SceneImpl::DummiesTableDestroy()` **`0x61AAC`**
- `SceneImpl::CollectDummies(ISceneNode*)` **`0x62EA4`**
- `SceneImpl::DummiesTableAdd(char const*)` **`0x641B4`**
- `SceneImpl::DummiesTableCreate(int)` **`0x64684`**

Bu API'lar kaynak kanıtlı; ancak `DummiesTableAdd`'e gerçek `14` ve `33` isimlerinin hangi sırada geldiği daha bulunmadı.

## G189 — doğrudan ARM çağrı incelemesi (NEGATİF sonuç gizlenmedi)

[GitHub Actions G189 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39115216413). Özgün Mach-O `__text` içerisindeki **ARM immediate BL/BLX** çağrıları bu üç real native giriş adresi için tarandı. **`DummiesTableAdd`, `DummiesTableCreate`, `DummiesTableDestroy`: her biri için doğrudan eşleşme 0.** Bu **API'ların kullanılmadığı** demek değil: indirect register / vtable / thunks, Thumb ve runtime/lua registration yolları bu taramada kanıtlanmış değildir. Bu nedenle 14 ve 33 için bir isim tahmin edilmedi.

## Şu anki doğruluk durumu

| Bileşen | Durum |
| --- | --- |
| Uni-Beam özgün WeaponDB saldırı indeksi 4 | Kanıtlı |
| Uni-Beam scene dummy grup seçimleri 14, 33 ve elem. 0 | Kanıtlı |
| Orijinal `SceneImpl::s_dummiesTable` adresi 0x4EDCA0 | Kanıtlı |
| Orijinal Mach-O `__common` = zero-fill, ham disk sayıları geçersiz | Kanıtlı |
| Gerçek global ctor `0x3B80` tablo header'ını sıfırlıyor | Kanıtlı |
| `DummiesTableCreate/Add/Destroy` native API giriş adresleri | Kanıtlı |
| `14` tam kaynak `Dummy_Chest`/hand/başka node adı | **Henüz kanıt yok** |
| `33` tam kaynak ad ve Mark V/VI koşulu | **Henüz kanıt yok** |
| Fiziksel Vita'da Uni-Beam emitter socket/hit frame/hasar | **Bu turda değiştirilmedi/test edilmedi** |
| VPK | **Üretilmedi** |

## G190 devam planı

Native ARM immediate direct çağrıların dışında `DummiesTableAdd/Create`'a ulaşan **Thumb, tail branch, function-pointer/data relocation** ve oyun kaynak sahne yükleyici callback yollarını tara. Orijinal asset metadata veya çalışabilir touchHLE C1L1 runtime `Object3D::GetDummyName(14,0)` ve `GetDummyName(33,0)` isimlerini üretmedikçe BDAE traversed index 14/33'ü emitter olarak kullanma. Doğrulanmış original rig node/scene parent scale ve animasyon örnekleri eşleştirildikten sonra bile tek G8/G83 olay yolu üzerinden portla. **Yeni VPK yok.**

**Diğer açık kullanıcı maddeleri:** gerçek karakter yürüyüş ve harita ölçeğinin Vita cihazında doğrulanması; orijinal çevre ışıklandırma/skybox/gölgeler; War Machine native silah/eşleşme; özgün 13-state melee hit pencereleri; QTE ve ilk görev; tam düşman AI. Bu kaynak turunun başarıları bunları çözmüş anlamına gelmez.
