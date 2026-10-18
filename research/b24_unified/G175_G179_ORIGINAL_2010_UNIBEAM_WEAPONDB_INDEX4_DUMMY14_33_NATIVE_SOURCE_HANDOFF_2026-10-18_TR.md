# G175–G179 — Orijinal 2010 iOS Iron Man 2 Uni-Beam gerçek WeaponDB indisi 4 ve dummy parametreleri 14/33

**18 Ekim 2026, `Gh0sTRX/Iron-man-2-os`, dal `feature/b24-unified-gameplay`. Özgün oyun sahibi IPA v1.0.0. Yeni VPK yapılmadı.**

## Gerçek orijinal ARM üzerinde tamamlanan işlemler

1. **G175 native C++ araması:** özel owner iOS IPA 248.613.763 bayt bir GitHub Actions çalıştırıcısına GEÇİCİ indirildi; 7.480.208 bayt özgün ARM Mach-O işlendi; orijinal `65500` sembol, ilgili `671` yöntem adayı, `177` seçili ilgili fonksiyon kodu ve `5161` BL/BLX çağrı talimatı sayıldı. Bütün orijinal executable ve IPA çalışma sonunda silindi. Yalnız isim, opcode metadata ve source çağrı grafı artifact olarak çıktı. [**G175 SUCCESS 39107687965**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39107687965). Kaynak: `g175_native_weapon_motion_graph/g175_original_2010_weapon_animation_native_callgraph.py`.
2. **G175B orijinal Lua izni / silah davranışı:** `SetAttackTypeEnabled(lua_State*)` adresi `0x17B80`. Bunun özgün `lua_tointeger` 0x25D9C, `lua_toboolean` 0x25C80 ve `GS_GamePlay::GetMC` 0xC2518 çağrıları kaynak koddan görülüyor. İlk bölümün özgün Lua'sında `SetAttackTypeEnabled(1,false)` 11 yer, `(1,true)` ise `MissionTutorial_missile_OnStart` 1 yer; **bu AttackType=1 değerinin şüphesiz bir füze/Uni-Beam kaydı veya `Aim_M` klibi olduğunu kanıtlamaz.** Önceki G76 gerçek Lua raporuna dayalı doğrulama. [**G175B SUCCESS 39107949966**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39107949966).
3. **G176 gerçek Uni-Beam 3B bağlantı çağrısı:** `MainCharacter::DoUniBeamAttack` 0xF60AC, `Object3D::GetDummyAbsolutePosition(int,int)` 0x159C4 doğrudan `BL` çağrı noktası `0xF611C`. Native register çevresinde `r1 = r8 + 0x48`, `r2 = r5`, `r0 = sp + 0x1C`, `r3 = 0` ve girişte `r5 = r1`: **DoUniBeamAttack fonksiyonunun ilk int parametresi dummy lookup argümanına gerçekten aktarılıyor.** Kaynak bone/dummy adı ve hangi materyal/efekt socketi olduğu HÂLÂ BİLİNMİYOR. [**G176 SUCCESS 39108136489**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39108136489).
4. **G177 önemli kesin özgün silah indeksi:** `0xF60D0 BL WeaponDB::GetInstance`, `0xF60D4 MOV r1,#4`, `0xF60D8 BL WeaponDB::GetAttackEntityByIndex(int)` (fonksiyon 0xAB3EC) ardışık. Orijinal **Uni-Beam native WeaponDB'nin indeks 4'teki saldırı kaydını istiyor**. Bu `AttackType=1`, kaynak CLARA `Attack id=4` veya 4 hasar demek değildir. [**G177 SUCCESS 39108312594**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39108312594).
5. **G178 orijinal çağıran `MainCharacter::DoAttack(int,int)` 0xF64F8:** 646 gerçek ARM komut çözümlendi, 66 doğrudan çağrı; gerçek Uni-Beam'e BL çağrı noktaları `0xF6638`, `0xF6D8C`, `0xF6E04`. Kaynak öncesi kontrol akışı ve ARM talimat bağlamı özel olmayan JSON metadata'ya aktarıldı. [**G178 SUCCESS 39108481599**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39108481599). İlk workflow yazımında Actions job ID'si sayıyla başladığı için otomasyon YAML reddedildi; `ed7a51b` düzeltmesi sonrası asıl native test başarıyla geçti.
6. **G179 en önemli bağlantı değeri doğrulaması:** `DoAttack` içindeki orijinal `MOV r1,#0xE` (iki ayrı çağrı) ve `MOV r1,#0x21` (üçüncü çağrı) gerçek ARM kodu üzerinden denetlendi. Karşılık gelen `BL DoUniBeamAttack` öncesi `r1` değişmedi; `DoUniBeamAttack` bu ilk int'i `GetDummyAbsolutePosition` çağrısındaki `r2` argümanına aktarıyor. **Gerçek kaynak bağlantı seçim argümanları 14, 14 ve 33**, üç gerçek BL adresi sırasıyla `0xF6638`, `0xF6D8C`, `0xF6E04`. [**G179 SUCCESS 39108638079**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39108638079). Orijinal bone/node ID'si olarak henüz isimlendirilmedi.

## G175–179 doğrulanmış teknik tablo

| Kaynak uygulaması | ARM adresi / parametre | Nitelik |
| --- | --- | --- |
| `MainCharacter::DoUniBeamAttack` | `0xF60AC` | Native original |
| `WeaponDB::GetAttackEntityByIndex(4)` | `0xF60D8 → 0xAB3EC`; `r1=4` | **Orijinal sayısal saldırı indeksi doğrulandı** |
| `Object3D::GetDummyAbsolutePosition` | `0xF611C → 0x159C4` | Doğrudan gerçek native bağlantı sorgusu |
| `MainCharacter::DoAttack` | `0xF64F8` | Çağıran native gerçek işlev |
| `DoAttack → DoUniBeamAttack` | `0xF6638` (arg 14), `0xF6D8C` (arg 14), `0xF6E04` (arg 33) | **Üç gerçek native parametre doğrulandı** |
| `SetAttackTypeEnabled(lua_State*)` | `0x17B80`; Lua tür bool/int | Gerçek native Lua köprüsü, AttackType=1 ile aynı DB index değildir |

## Kullanıcı için gerçek ilerleme ve halen açık kalanlar

- **Elimizde özgün Uni-Beam için sayısal üç bağ var: attack source indeksi `4`, farklı kaynak çağrılarda dummy-seçimi ilk parametresi `14` ve `33`.** Bunlar sıfırdan üretilmiş gameplay değerleri değil; 2010 native ARM talimatlarının gerçek immediate değerleri.
- `14` / `33` değerlerinin hangi orijinal `BDAE` dummy/rig node ve hangi durum (ground/hover/belirli zırh) olduğuna dair **henüz native lookup-body + parent transform bağlamı yok**. Rakamları model vertex sırası/sahte silah soketi diye doğrudan kullanma.
- G173 orijinal 12 beam IM2V pose'unun gerçek kaynak stream açılışını çözmüş, ama `G169` halen Vita portunun kabul edilmiş B16 Unibeam olayına bağlı; orijinal iOS arayüz input/controller trigger veya `Aim_M` silah/animasyon eşleşmesi çözülmüş değildir.
- G174, War Machine'in `Aim_M_Ground` 10 klibini orijinal IM2V stream'de başarıyla açmış olsa da native roket/gatling semantiği yoktur. `ThrowMissile` isimli metot tek başına gerçek füze animasyonu ispatlamaz; gözlemlenen yerel doğrudan çağrılar arasında `CameraMgr`, `GamePlayUI`, `ASprite`, `Button::SetKeyEnabled` var, ancak başka indirekt çağrılar olabilir.
- İlk görev QTE1456, özgün model/world parent scale, ay/skyline/render material, ışık-gölge, hareket/yürüyüşü gerçek Vita'da yeniden görme, NPC AI, 13-state melee ve orijinal Damage/WeaponDB tam sahne data eşlemesi **açık**.
- **G175–179 yalnız orijinal kaynak tersine mühendislik/host native analizidir. Vita executable ve VPK üretilmedi, yeni silah/damage gameplay davranışı eklenmedi**. Önceki G174 Vita ARM ELF zaten PASS, gerçek donanım son versiyon testi bekliyor.

## Sonraki kaynak-kanıtlı çözüm

**G180 önerilen:** gerçek original `Object3D::GetDummyAbsolutePosition(int,int)` 0x159C4 bounded ARM işlevini ve `warmachine.bdae`/`Iron_man_mark6.bdae` dummy indeks ↔ rig/skinned node/scene parent dökümünü eşle; `14` ve `33` gerçekten hangi indeks alanına bağlanıyor belirle. Asıl UniBeam emitter/sound/FX file association ve VPK orijinal node köprüsü çözülmeden onaylı oyuncu verisi yerine tahmin yazılmamalı. Ayrıca orijinal `MainCharacter::DoAttack` üç kod yolunun suit/attack mode predicate'lerini ARM CFG üzerinden çıkart; kaynak kanıtından sonra G83 input router'a bağla. YENİ VPK YOK.
