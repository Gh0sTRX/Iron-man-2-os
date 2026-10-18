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
