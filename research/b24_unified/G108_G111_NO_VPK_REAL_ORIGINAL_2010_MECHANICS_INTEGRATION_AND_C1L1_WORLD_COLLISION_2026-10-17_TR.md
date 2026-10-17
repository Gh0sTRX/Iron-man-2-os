# Iron Man 2 iOS → PS Vita: G108–G111 gerçek oyun mekaniği ve sahne düzeltmeleri

**Tarih:** 17 Ekim 2026 · dal `feature/b24-unified-gameplay` · **KULLANICININ YENİ KESİN KISITI: HİÇ YENİ VPK YOK.** Kullanıcı G104'ü gerçek Vita'da test edip yürüme/hover animasyonu iyi, stage2/rush repulsor bozuk, harita yüzeylerine giriliyor, transparan yazılar siyah, skybox siyah ve aydınlatma yok dedi; sonrasında yeni VPK kurulumunun zahmetli olduğunu, yeni VPK istemediğini, eksik **asıl iOS oyunu mekaniklerini** kaynak olarak çözüp halletmemizi açıkça söyledi.

## G108 — Görünen orijinal dünya ve fizik collider uçurumu, GERÇEK kaynak entegre edildi

- Eski G68/G75 fizik yalnız **1.910** gerçek 2010 G66C kaynak collider üçgenine bakarken görüntüde **22.441** gerçek 2010 G66M kaynak render üçgeni var.
- G107 doğrulandı: opak ve dik kaynak görüntü üçgenlerinin **7.506** tanesinin yaklaşık merkezinde 0,8 kaynak birim tolerans içinde fizik collider AABB komşusu yok. Bu sayı mutlak eksik fizik duvarı sayısı değil.
- G108 `research/b24_unified/g108_source_geometry_collision/` gerçek `G66_city.g66m` dosyasından **7.147** ek *muhtemel katı görünen* kaynak orijinal dik/opak triangle ayırdı. Yedi orijinal şeffaf atlas (1,6,7,9,15,19,20), düz zemin/yatay yüzey, zaten G66C'de yakın yüzü olan duvar ve aşırı geniş/global elemanlar eklenmedi. **Kaynak render geometrisinden fizik türetmek, özgün iOS Actor/CollisionEntity solidity yetkisiyle eşit değil!** Bu seçenek deneyseldir.
- **İkinci bir physics engine yok.** Var olan tek `b14_world_tick` + `b24_g75_capsule_reconcile` çağrısının `wall_clear` testinde aynı orijinal kaynak dünya ile **7147 ilave kaynak duvarı** sorgulanıyor. Source geometry 12x12 kaynak birim uniform-cell CSR index: **16.790** toplam cell→face işaretçisi, kare başına 22.441 triangle lineer taraması yok.
- Gerçek G68 kaynak C testi 7.147 triangle'ın **7.098'inin kendi gerçek centroid kapsülü için engelleyici olduğunu**, 5.000 indexed query host stresini doğruladı. Gerçek Vita CPU/GPU FPS **henüz cihazda ölçülmedi**, C11 benchmark host süresi cihaz süresi değildir.
- Kaynak patch `g108_enable_original_visible_wall_grid_in_single_G75_main_NO_VPK.py` ile CMake bayrağı **`-DB24_G108_SOURCE_VISUAL_WALLS=ON`**. Bayrak varsayılan OFF, G111 CI source rebuild'de ON.

**[G108 gerçek G68 kaynağı host + tam Vita ARM `im2_beta` ELF-only derleme BAŞARILI 39012995942](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39012995942)**. **Hiçbir `.vpk` üretilmedi.**

## G109–G110 — iOS mekanik kodunun Gerçek C++ çalışma davranışı çıkartıldı

Orijinal kullanıcı iOS 2010 ARM Mach-O:
- `EntityData::GetParamValue(char const*, int*)` özgün native `0xD7548`.
- `EntityData::GetParamValue(char const*, bool*)` özgün native `0xD76BC`.
- `this+0x20` field-name descriptor container; `+0x0C` field count; `+0x10` field-names base, **12 bayt** 2010 ARM stride ve key ptr +4.
- `this+0x1C` typed parameter-data vector; indekse karşılık **8 bayt** field-data record, ilk word veri işaretçisi, ikinci word kaynak serialized payload boyutu.
- ARM `bl 0x47111C`: Mach-O LC_DYSYMTAB `__symbol_stub4` 12 bayt stub ile **GERÇEK iOS libc `_strcasecmp`** dinamik importu, **ismi büyük/küçük harf ayrımı yapmadan** arıyor; ilk eşleşen indeks seçiliyor. Bu tahmin değil.
- ARM `bl 0x470E88`: aynı kaynakta **GERÇEK `_memcpy`** dinamik importu. Kaynak field payload ptr ve runtime boyutu bu kopyalamaya gönderiliyor; **bu, 26 `Damage` sayısı bulundu demek değil.**
- G98 ARM zaten `AttackEntity::LoadFromFile` içinde `"Damage"` **int** accessor ve gerçek native AttackEntity `+0x60` destination field kanıtını kaydetmişti.
- **[G109 orijinal native ARM getter, `Actor::TestMeleeHit`, original 13 state audit 39013413605](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39013413605)**; **[G110 actual iOS dyld `strcasecmp`/`memcpy` import başarı testi 39013413600](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39013413600)**.

## G111 — Asıl oyun G82 combat sistemine native get-property/permission/attack-state eklendi

Yeni `research/b24_unified/g111_original_game_combat_gates/b24_g111_original_source_entitydata_and_combat_permission.[ch]` kaynak-native logic içeriyor:

1. Orijinal `EntityData` şemasından ad doğrulamalı alan bulma, case-insensitive kaynak isimli `Damage` **4-byte int32** değerini `memcpy` ile alma (iOS ARM 32-bit 12/8 descriptor stride bilgisinin portable logical portu, 64-bit host bit-birebir struct representation değil).
2. `Actor::CanAttack` native `0xD9278` kıyasını **G103 gerçek actor +0x2B8 category** verisiyle çalıştırma. Attacker sınıf0 vs target2=DENY, vs3=ALLOW, vs4=UNKNOWN (native vtable), attacker1 allowlist/vtable çözülmediyse UNKNOWN. Aktör sınıf0=Iron Man varsayılmaz.
3. `MainCharacter::IsInMeleeAttackState` özgün native `0xEA3C0` kanıtlı `+0x824` state 2..12 onay; iOS "bu kare hit aktif" anlamı asla çıkarılmaz.
4. **Gerçek mevcut** `research/b24_unified/g82_original_combat/b24_g82_original_combat_coordinator.[ch]` içine `#ifdef B24_G111_NATIVE_SOURCE_GATES` ile bağlandı. Damage uygulanabilmesi için bunların ÜÇÜNÜN özgün source-kanıtlı olarak somut instance kayıtlarından sağlanması **zorunlu**. Eksikse fail-closed; G92 ölümsüz flash dummy'ye asla otomatik orijinal NPC canı veya hasar uydurulmaz.
5. Eski üç kaynak flag ile keyfi `Damage=12` fixture verisi artık G111 aktifse tek başına hasar veremiyor. Sadece tüm `original_*_verified` native delilleri test fixture tarafından açıkça sağlandığında gerçek G82 iki-resource +0x3BC/+0x394 hasar zinciri kullanılabiliyor.

Kaynak patch `g111_apply_authentic_2010_entitydata_actor_melee_to_single_B24_SOURCE_ONLY.py`. Gerçek eski B14 fiziği, G83 gerçek hareket selector, G85 248 orijinal MarkV, G106 özgün fly_att_s, G71 gerçek orijinal RGBA şeffaf pass, G73 gerçek orijinal gök ve G95 test ışığı **aynı `im2_beta` ARM ELF** ile *birlikte* derlendi. **Yeni VPK yok.**

**[G111 2010 iOS orijinal fonksiyon mantığı, G82 gerçek damage gate, G108 harita ve TAM Vita `im2_beta` ARM ELF testlerinin tamamı BAŞARILI, 39013755500](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39013755500)**.

**Önemli ayrım:** G111 testleri gerçek iOS 2010 **metot kurallarını** doğruluyor, 26 `Attack` instance'da henüz bulunamamış gerçek hasar sayıları için testte kullanılan **örnek/sentetik `Damage=12`** orijinal silah gücü değildir. Bu sayıya oyun varmış gibi izin verilmiyor.

## Hangi gerçek büyük eksikler hâlâ var?

- **26 gerçek CLARA class108 `Attack` / 13 `Weapon` instance** gerçek `EntityData` property-name ↔ 54 count-prefixed alan eşlemesi (**özgün `GetParamValue` isim ve memcpy metodu artık kesinleşti ama serialize class-prototype inheritance ilişkisi yok**). Attack `Damage` sayıları olmadan gerçek hasar aktif olamaz.
- **Özgün melee hit-active frame** ve native `UpdateMeleeAttackState` 13-state 8 branch tam iOS input/action dispatch kuralı ve 2010 touch gesture sinyalleri; yalnız source predicate ve G8 combo3 var.
- **NPC düşmanlar, özgün AI/misyon Lua dalgaları, projectile visual+real hit/hurt/death/FX** hâlâ tam oyuna entegre edilmedi; bir G92 dummy tanı aktörü var, gerçek 2010 C1L1 mission NPC değil.
- **G73 sky materyal ↔ texture sampler exact eşleme ve gerçek 2010 GLSL/Fixed function light combiner**, şeffaf billboards'ların gerçek PVR blend mode/draw order, cihazda henüz yeniden gözlenmedi; G71/G95/G106 çözümlemeleri gerçek source materyal kodu değil, iOS asset'i kullanan deneysel GPU yaklaşımı.
- G108 görsel-geometri collider seçimi *öneri*, true 2010 fizik katılık etiketleri ve yüzey-normal semantiği/ayrık araç/obje collision script entegrasyonu gerekir. Sahada yeni collision regressions olabilir.
- **248 gerçek MarkV source klibi pakette mevcut olsa da tüm 248 gameplay transition / original intent switch şartları hâlâ bağlı değil**; eski B13 fallback diğer suitlerde var.
- PS Vita G111 deneysel kaynak kodu **cihaza kurulup denenmedi**. Kullanıcı **yeni VPK istemediği için üretilmeyecek**, kullanıcı açıkça fikrini tekrar değiştirene kadar.

## Sonraki teknik sistem sırası

Öncelik: G111 kaynak-proven `EntityData::GetParamValue` field-names `this+0x20` native descriptor yapısının CLARA 26 Attack instance serializer 54 slot ile exact native class hierarchy çözümü → 26 gerçek numeric Damage. Sonra gerçek `UpdateMeleeAttackState` event timing/action-cancel ve ProjectileEntity/Actor::CanAttack ile genuine enemy/mission source. Bu bitmeden native mobile input/flight animation parity iddia edilmez.

**NO VPK** sert kontrol: G108/G111 CI `--target im2_beta` (yalnız ARM executable ELF), `find work -name '*.vpk'` sıfır. Yeni VPK önerme/üretme.
