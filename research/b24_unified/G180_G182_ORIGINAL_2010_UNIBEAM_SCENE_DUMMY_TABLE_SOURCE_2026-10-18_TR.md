# G180–G182 — 2010 özgün Uni-Beam dummy kayıt tablosu: ARM kanıt zinciri

**Tarih:** 18 Ekim 2026. **Dal:** `feature/b24-unified-gameplay`. Kullanıcının talimatı: **VPK üretme**. Kaynak-only, özgün iOS 2010 kullanıcı IPA; geçmiş G179 değerleri teyitli.

## G180 tam orijinal source

2010 iOS `Object3D::GetDummyAbsolutePosition(int,int)` gerçek ARM VM `0x159C4`, 20 talimat. Dışarıdan Uni-Beam ile gelen integer dummy grubu `14` veya `33`, ikinci parametre `0` taşınıyor. Koda göre:

```asm
0x159c4 push {r4, r7, lr}
0x159cc ldr r1, [r1, #8]
0x159d4 ldr r0, [r1, #0x90]
0x159d8 mov r1, r2
0x159dc mov r2, r3
0x159e0 bl #0x61724
0x159e4 cmp r0, #0
0x159ec ldrne r1, [r0, #4]
0x15a00 ldrne r3, [r1]
0x15a08 ldrne pc, [r3, #0xc4]
```

Gerçek `BL 0x61724` çağrısının kaydı C++ `SceneImpl::GetDummy(int,unsigned int)`. Native lookup `nullptr` verirse özgün fonksiyon sıfır vektör döndürüyor. Dönen dummy nesnesi varsa 0xC4 vtable slotuna göre transform hesaplaması yapılıyor; virtual fonksiyonun somut C++ override kimliği **henüz çözülmedi**.

Kullanıcı sahipliğindeki BDAE `models` paketinde **`Iron_man_mark6.bdae` 96 rig node**, **`LC_MC_SuitCase.bdae` 96**, **`warmachine.bdae` 112**, **`LC_MC_WarMachine.bdae` 112** node yeniden incelendi. Orijinal `Dummy_Chest`, `DummyE_Chest`, `Dummy_Hand_L/R`, War Machine `Dummy_Gun_L/R`, `DummyE_Shoot_L/R`, `Dummy_Green_Gun` gibi adlar var. **B13 parse_rig listesinde 14/33. node = native SceneImpl indeks 14/33 ispatı yoktur.** [G180 CI PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39111725014).

## G181 en önemli kanıt

Orijinal `SceneImpl::GetDummy(int, unsigned int)` **0x61724**, **tam 12 talimat**; özgün ARM:

```asm
0x61724 ldr r3, [r0, #0x278]
0x61728 ldr r3, [r3, r1, lsl #2]
0x6172c cmp r3, #0
0x61730 bne #0x6173c
0x61734 mov r0, #0
0x61738 bx lr
0x6173c ldr r1, [r3, #8]
0x61740 cmp r1, r2
0x61744 bls #0x61734
0x61748 ldr r0, [r3]
0x6174c ldr r0, [r0, r2, lsl #2]
0x61750 bx lr
```

**Kanıtlanan:** sahne nesnesinin `+0x278` alanındaki dummy grup tablosundan `r1` grup anahtarıyla pointer okunuyor; `r2` (Uni-Beam'de **0**) o grubun eleman indeksidir; eleman sayısı `[group+8]`, eleman pointer listesi `[group]`. Grup yoksa ya da indeks sınır dışıysa null dönüyor. `14` ve `33` sayıları **kesin native scene registry grup indeksleri**; ama **hangi authored BDAE dummy name olduğu henüz eşlenmedi**.

İlk G181 çalışmasının kaynak C++ `BL` site listesinde ARM **`BLS` koşullu dönüş branch'i** yanlışlıkla BL fonksiyon çağrısı sayılıyordu. `1640ac2` kaynak düzeltmesi ve CI katı opcode kontrolüyle bu giderildi. **Bu 12 talimatlı `SceneImpl::GetDummy` gövdesinin hiçbir C++ `BL`/ `BLX` çağrısı yok**. [G181 kesin kod düzeyi CI PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39112024164).

## G182 özgün tabloyu kim dolduruyor?

`g182_native_scene_dummy_registry/g182_original_2010_scene_dummy_registry_writers_arm.py`, `SceneImpl::`, `Object3D::`, dummy/modele bağlı orijinal native yöntemlerde `+0x278` alanının gerçek read/write kodlarını tarıyor. Çalışma [G182 CI](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39112143754). Bu raporun yazıldığı anda CI sonucu henüz sonlanmamışsa PASS varsayılmaz; sonuç okuyup raporu güncelle.

## Değişmeyen/çözülemeyen şartlar

- G179 orijinal saldırı data indeksi `WeaponDB::GetAttackEntityByIndex(4)`; bu ***AssetID=4***, gerçek hasar değeri veya `AttackType=1` anlamına gelmez.
- Orijinal `MainCharacter::DoAttack` içindeki 3 Uni-Beam çağrısının **`14,14,33`** sayılarını `GetDummy(14,0)` veya `GetDummy(33,0)` üzerinden sahne tablosuna yönlendirdiği şimdi kaynak seviyesinde kanıtlı.
- `G83 Aim_M` War Machine native silah girdi eşlemesi, `G169/G173` Beam kaynağının **gerçek orijinal iOS silah giriş karşılığı**, G8 IM2V içindeki efekt trigger zamanı, kaynak harita sky/lights, kablo/rig parent dünyası, gerçek Vita yürüyüşü ve ilk görev QTE halen çözülmedi.
- **Bu aşama yalnızca özgün ARM native kaynak + BDAE analizi; Vita ELF/oyun kodu/VPK yeni üretilmedi.** G174 önceki Vita ARM ELF PASS kaydı ayrı. Yanlış native indeks → kemiğe geçiş yapmayacağız.

## Devam hedefi

Özgün `SceneImpl` constructor/scene-loader resource metadata'dan `+0x278` grup slotlarını oluşturan işlev ve `14/33` numaralarına bağlanan özgün authored dummy isimleri çıkart. Bunun ardından ilgili zırhın `BRES/BDAE` parent transformunu ve orijinal `G8` hareket örneklerini aynı koordinat sisteminde doğrula; **silah patlama/hasar oynanışını tahmin etme**. Yeni VPK hazırlama.

## G182 CI — SceneImpl kaynak tablo doldurma adayları

[G182 CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39112143754). `g182_original_2010_scene_dummy_registry_writers_arm.py`, özgün Mach-O içindeki geniş sembol taramasında `2683` isme uyan kaynak fonksiyon, `1987` çözümlenmiş bounded yöntem ve `56` ham `+0x278` bellek erişimi ortaya çıkardı. Bu 56'nın bir kısmı `pc/sp` veya Irrlicht CSceneManager gibi **başka C++ sınıflarına** ait; 56'sının tümü `SceneImpl` alanı değildir. Doğrudan ilgili native kaynaklar:

- `SceneImpl::CollectDummies(irr::scene::ISceneNode*)` **0x62EA4**, `+0x278` alanına source erişimi `0x63230` ve `0x63714`.
- `SceneImpl::SceneImpl(SceneMgr*, ISceneNode*)` **0x65374**, `0x655BC` konumunda constructor içinde `str r0, [r4,#0x278]`.
- `SceneImpl::UpdateDummies` **0x61DA0**, `ResetDummies` **0x61F1C**, `Initialize` **0x67150** yöntemlerinde aynı member offset kaynak erişimleri.
- `SceneImpl::GetDummyCount` **0x6177C**, orijinal bucket bilgisine erişiyor.

**Henüz kayıt grubunun 14 veya 33. anahtarının hangi named authored node'a bağlandığı kanıtlanmadı.**

## G183 CI — Orijinal isim sorgulayıcısı ve collector kod yolu

[G183 CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39112344705). `Object3D::GetDummyName(int,int)` özgün native ARM **0x15894** fonksiyonu tam `22` talimat ve doğrudan `0x158A4 BL SceneImpl::GetDummy` çağrısı yapıyor. Dummy bulunan durumda vtable `+0x2C` yöntemini çağırıyor, bulunmazsa PIC kaynak fallback string kullanıyor; **run-time gerçek 14/33 isimleri okunmadı**.

`SceneImpl::CollectDummies` (**0x62EA4**) **546** source native ARM talimatı, **18** gerçek doğrudan C++ fonksiyon çağrısı içeriyor, `0x62F60` konumunda kendi kendini rekürsif çağırıyor, sahne düğümü isimlerini `stristr` **0x73E84** ile birden çok kez karşılaştırıyor. GetDummy tablosu `+0x278` alanına referans veriyor. Ayrıca `GetUserPropAsFloat` **0x744C4** çağrısı özgün node özel verisiyle bir bağlantının olabileceğini gösteriyor; hangi property olduğunu kanıtlamadan değer uydurma.

## G184 CI — Gerçek PIC isim desen tablosu incelemesi, henüz eşleşme değil

[G184 CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39112549318). `SceneImpl::CollectDummies` içinde `0x62F8C` ve `0x62FA0` PIC literal'ları kaynakla doğrulandı. İkisi de matematiksel olarak **`0x4EDCA0`** statik adrese çözülüyor. Kaynak image belleğinin ilk 12 baytında `972, 5127504, 2` integer değerleri görüldü. `972` değeri geçerli bir kaynak `char*` dizisi işaretçisi olarak doğrulanmadığından, çalışırken initialize edilen işaretçiler/indirection olasılığı var. **Bu değerlerden grup 14 veya 33 adı çıkmış gibi davranmıyoruz.** `stristr` için kaynak tablo indeksli `[ip, r6, LSL#2]` okuması var fakat bunun native SceneImpl `+0x278` tablosuyla bir-bir aynı enum/sıra olup olmadığı için tam registration data-flow henüz açılmadı.

## G185 devri — ilk hedef

`SceneImpl::CollectDummies` `0x63108`–`0x63714` registration kodunda `r6` indeksinin `scene+0x278` bucket slotuna hangi C++ branch yoluyla yazıldığını tamamla; PIC descriptor runtime init/relocation düzeltmelerini araştır. Alternatif olarak özgün 2010 iOS oyunu touchHLE'de gerçekten C1L1 sahnesine giriyorsa **sadece gözlemlenmiş** `Object3D::GetDummyName(14,0)` ve `GetDummyName(33,0)` source runtime sonucu kaydet. Emulator sahneye ulaşmadan socket ismi ispatlanmış sayılamaz. Daha sonra authored rig dummy matrix ile skin stream coordinate convention çapraz doğrulaması ve *ancak* gerçek native semantic kanıtıyla Vita tek animatöre bağlama. **Yeni VPK hazırlama**.
