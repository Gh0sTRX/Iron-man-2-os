# G305 — Özgün iOS AttackType/DoAttack ARM karşılaştırması + yanlış G218 saldırı sayacının düzeltilmesi (NO VPK)

**21 Ekim 2026 · `feature/b24-unified-gameplay`**

## Denetimde bulunan hata
Daha önce G213B'den kurtarılan özgün 2010 `StateData` / `StateTrack` bilgileri G218 ile gerçekten başarıyla yüklenmiş G8 IM2V pozu üzerinden okunuyordu. Ancak eski `native_raw_attack_event_rows_observed`, tek bir `attack`/ `Attack` SOURCE kaydını **render edilen her karede +1** sayıyordu. Tek animasyon 60 kare görünürse 60 native saldırı olmuş gibi yanlış bir telemetri izlenimi yaratıyordu. Üstelik `AttackType` kaynak u32 değeri G197'de çözdüğümüz gerçek native 26 kollu ARM tabloyla canlı read-only gözlemci üzerinde karşılaştırılmıyordu.

## Kaynağa dayanan onarım
- Gerçek G8 oynatıcısının açabildiği pozu değiştirme. `G218` orijinal `attack/Attack` SOURCE olayının gözlem sayısını **yeni açılmış klip/suit geçişinde** artırır, aynı klibin sonraki 60 render karesinde artırmaz. Dosya yüklenemez/animasyon pasifse son klip sahipliği sıfırlanır; yeniden yüklenirse yeni kaynak gözlemi yapılır. Bu, *olayın Vita'da tetiklendiği* demek değildir.
- G197'nin 2010 `MainCharacter::DoAttack` adreslerden doğrulanmış `26` ARM jump-table kaydı G218 içinden yalnızca **STATIC SOURCE CANDIDATE** okunur. G218'in G8 → StateData bağlantısı orijinal native runtime tarafından doğrulanmamış **isim benzerliği eşlemesidir**. Bu nedenle `source_native_DoAttack_runtime_event_proven=0` ve `source_WeaponDB_runtime_index_or_weapon_identity_proven=0` zorunlu.
- Mark VI `AttackType=2` ile WM `AttackType=25` native jump-table hedefi `0xF6648` ortak; Mark VI `1` ile WM `18` `0xF6930` ortak. Bu **aynı saldırı datası/füze/omuz gatling/tuş** kanıtı değildir. Aynı statik hedef bazı ortak guardlara geçebilir; gerçek WeaponDB sıra ve native giriş kaynağı hâlâ açık.
- G218 installer, gerçek statik G197 kaynak başlığını Vita `work/b24/b24_unified` içine fail-closed kopyalar. Projeye tek yeni C++ event, hasar, animasyon, fizik, VPK eklemez.
- Mevcut G218 gerçek G217 artifact'iyle C11 host 194×4 record testleri genişletildi: WM/MK VI ayırımı, birleşen gerçek branch adresleri, tekrar eden 60 kare + gerçek tek dosya sahibinde **tek ham olay gözlemi**, invalid dosya/StateMgr/WeaponDB fail-closed. Tam G171 Vita ARM ELF-only kaynak birleştirme testi de çalışır.

## Orijinal B/G geçmişi ile açık sınırlar
Kaynak G197 jump-table ve G217 AttackType **authentic**; B14/G75 hareket hızları, G11 stage2/Rush ateş kısıtları ve WM G165 Rush source posture bizim homebrew davranışıdır. İlk bölümün özgün Lua `SetAttackTypeEnabled` değerlerinin etkisi native StateMgr runtime ile eşleştirilmeden bunları “2010 motor kuralı” diye sunamayız. C1L1 orijinal Attack / Weapon kayıtlarının dosya adı/ofset sırası `WeaponDB[0/1/4]` kesin sıra değildir (G241–G247). G305 canlı silah semantiğini icat etmez, gösterilebilir kanıtın taşıyabileceği sınırı yükseltir.

**VPK YOK.** G255 7/7 kapılar kapalı. Bu kodun host C11 ve Vita ARM ELF kaynak testlerinin başarılı sonuçları, fiziksel PS Vita 60 FPS, gerçek in-game silah isabeti, yürüyüş, Expo ay/gölge/ışık ya da native Mission000 ilerlemesi kanıtı değildir.

## Doğrulanmış kaynak/derleme testleri, 21 Ekim 2026

- Kaynak düzeltme commit [`826a3dd`](https://github.com/Gh0sTRX/Iron-man-2-os/commit/826a3dda98a8d7029f416e5b82bab9a4a44831cb), dar G218 host include-path düzeltmesi [`747e45d`](https://github.com/Gh0sTRX/Iron-man-2-os/commit/747e45da27560484e5b7817469c1b2cdb4dc8321).
- **[G218+G305 CI — SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39582453239)**: orijinal G217 4×194 `StateData`, statik G197 `DoAttack` ARM 26 kolu, WM `25↔Mark VI 2` ve WM `18↔Mark VI 1` aynı statik branch, 60 render karelik tek G8 klip için tek ham StateTrack kayıt gözlemi, kaynak dışı ve missing fail-closed doğrulandı.
- **[G171 tam oyun Vita ARM ELF-only — SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39582416284)** (aynı G305 source commit `826a3dd`): G218 gerçek Vita main entegrasyonunun G197 kaynak tablosunu doğru şekilde taşıması, diğer G171 kaynak/world/combat/animator/lighting adayları ve son birleşik VitaSDK `im2_beta` link testi geçti. VPK üretilmedi.
- Bu sonuçlar **native iOS WeaponDB index → WM missile/gatling veya gerçek hit zamanı mapping çözüldü** demiyor; statik dal hedefi, özgün gözlenen runtime olay değil. Fiziksel PS Vita/grafik/60FPS/yürüyüş/fotoğraf kanıtı yok. G255 source 7/7 gate hâlâ false.
