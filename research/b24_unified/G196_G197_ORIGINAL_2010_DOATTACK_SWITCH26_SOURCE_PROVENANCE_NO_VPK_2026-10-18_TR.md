# G196–G197: Orijinal 2010 iOS Iron Man 2 saldırı yönlendirme tablosunun 26 girişi (kaynak kanıtı)

**18 Ekim 2026 · `Gh0sTRX/Iron-man-2-os` / `feature/b24-unified-gameplay` · VPK YOK.**

## G196 özgün `MainCharacter::DoAttack(int,int)` ARM kodu

Gerçek kullanıcıya ait 2010 iOS 1.0.0 Mach-O içindeki C++ sembolü: **`MainCharacter::DoAttack(int,int)` `0xF64F8`**. 646 gerçek ARM opcode, 84 doğrudan/koşullu branch kaydı ve özgün 2010 `DoUniBeamAttack` için 3 gerçek `BL` çağrısı:

| Native BL | Kaynak r1 grubu | G193 kaynak kanıtlı özgün isim |
| --- | ---: | --- |
| `0xF6638` | 14 | `Dummy_Chest` |
| `0xF6D8C` | 14 | `Dummy_Chest` |
| `0xF6E04` | 33 | `Dummy_Foot_L` |

G196 gerçek özgün assembly kaynak çıkışında `0xF6524 CMP r5,#0x19` ve `0xF6528 ADDLS pc,pc,r5,lsl #2` bulundu. ARM'de PC komut adresi+8 olduğundan **giriş 0 `0xF6530`**, giriş 25 ise `0xF6594`; `0xF652C` ise aralık dışı girdinin common default branch'idir. Böylece özgün fonksiyonun **26 adet 0–25 saldırı seçici girişinin** gerçekten mevcut olduğu kanıtlandı.

**Önemli:** G196'nın temel CFG araç çıktısında dolaylı/vtable atlamaları güvenilir modelleyemediği için bazı çağrılara hiçbir geri predecessor çıkmıyor; buna dayanarak `33` kolunun oyunda ölü olduğunu söyleme. Ayrıca source static possible-reachability != orijinal controller input veya gerçek silah/oyun durumu koşulu ispatı. 33 kolu özgün komutlarda vektör/floating point değerleri de hesaplıyor; hangi native saldırı varyantı olduğu halen bilinmiyor.

[**G196 tam kaynak/PNG CI SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39124662533).

## G197: Kaynak C11 referansı, 26/26 özgün tablo gerçek ARM karşılaştırması

`research/b24_unified/g197_source2010_attack_dispatch/b24_g197_original_2010_attack_dispatch_reference.h` statik **kaynak referansı**; oyunda yeni silah/animasyon yönlendirme kuralı DEĞİL. C11 host test gerçek 26 özgün jump-table ARM hedefini G196 kanıtına karşı tek tek doğruluyor.

| Kategori | Giriş ID'leri | Kaynak native branch hedefi |
| --- | --- | --- |
| Sıfırdan başlayan özgün giriş | 0 | `0xF6A30` |
| Özel yol | 1 ve 18 | `0xF6930` |
| Özel yol | 2, 12, 25 | `0xF6648` |
| Özel yol | 4 | `0xF65C4` |
| Ortak varsayılan yol | Diğer 19 indeks | `0xF6598` |
| Kapsam dışı indeks | 26 ve üzeri | `0xF6598` |

**Bu ID'ler 7 ayrı silah demek değildir.** Bunlar sadece özgün ARM dallanma noktalarıdır. G197 helper ayrıca *yalnız* üç kanıtlı native `BL` adresini `14/14/33` ve `Dummy_Chest/Dummy_Foot_L` bilgisine bağlıyor. Farklı bir site veya key için fail-closed, bilinmiyor döner. Touch input / `Aim_M` / `WeaponDB` ID / hasar otomatik uydurulmaz.

`test_g197_original_iOS2010_ARM_switch_no_fake_weapon_semantics.c` host GCC `-std=c11 -Wall -Wextra -Werror -pedantic -O2` ile derlenip çalıştırıldı. GitHub Actions orijinal G196 ARM artifact'ini indiriyor, C kodundaki **26 hedefin tamamını ve 3 dummy callsite'ı kaynakla birebir karşılaştırıyor**. G197 PNG `G197_ORIGINAL_2010_DOATTACK_26_ENTRY_NATIVE_ARM_SOURCE_MAP.png`, kaynak ARM'den 26 girişlik statik çizim; gerçek Vita HUD/game frame değil.

[**G197 final CI PASS ve PNG**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39125039478).

## Doğru işlenmesi gereken kalanlar

- G196/G197 **orijinal saldırı *dispatch* yapısını buldu**; ancak gerçek native iOS `DoAttack` parametre 1'in kullanıcı eylemleri, aktif zırh, silah türü, animasyon hareket olayıyla eşleşmesi **henüz kanıtlı değil**.
- G195 gerçek altı Mark VI BEAM animasyonunun B13 ile **hareketli göğüs/sol ayak düğüm matrislerini** çıkardı; bunlar Vita game-world efekt konumu değil.
- G169/G173 kaynak original 3 beam fazını mevcut Vita tek animatör yoluna kaynak akışıyla bağladı; native iOS `DoAttack` runtime event ↔ mevcut B16/G84 silah/animator mapping ve doğru ilk bölüm QTE/ateş çerçevesi **açık**.
- Kullanıcının büyük açık maddeleri — gerçek Vita yürüyüşü / gerçek boyut ölçeği / gece light-skybox-gölge / War Machine tüm native moveset ve rockets / özgün melee damage/hit windows / C1L1 QTE — bu turda düzeltildi iddiası YOK.
- **G196–G197 Vita ELF veya VPK üretilmedi; yeni silah davranışı canlı Vita motoruna eklenmedi.** Yeni kullanıcıya VPK yükletme.
- **G198 önerilen:** orijinal 2010 C++ `DoAttack` giriş ID'lerini iOS gerçek animasyon/unlock/controller event route ile eşleştirmek için `DoAttack` çağıran native methods ve veri tablosu durumunu source xref çıkar; aynı zamanda B14 yürüyüş oyuncu render vs world size testini host düzeyinde sürdür. Native kanıt olmadan 33'ü chest'e bağlama.
