# Iron Man 2 iOS (2010) – 304 oyuncu animasyonunun eksiksiz katalog ve Vita araştırma notları

**Veri kaynağı:** Özel kullanıcı IPA'sının 1.0.0 sürümünden çıkarılmış B15 tam envanteri `research/B15_Original_All_Mechanics_Audit.zip / B15_COMPLETE_304_PLAYER_CLIPS.md`. Depodaki önceki doğrulanmış 304 kaydın tümü bu belgeye ayrı ayrı aktarılmıştır. Katalog 2026-10-13 tarihinde otomatik olarak yeniden sayılıp doğrulandı: **304/304, benzersiz isim 304/304; Iron Man 248, War Machine 56.**

**Önemli sınır:** Bu dosyada bütün 304 orijinal kayıt için **isim, toplam süre, etiket/kanal adı sayısı** incelenmiştir. **304 hareketin tümünün kare kare görsel önizlemesi yapılmamıştır.** B6 çalışması orijinal animasyon arşivindeki 972 kaydın ikili formatını uçtan uca çözdü; B7/B13–B16 yalnızca seçilmiş hareketleri iskelete/mesh'e aktardı. Orijinal IPA'nın tamamı bu GitHub deposunda ayrı bir dosya olarak bulunmadığından, burada yeni 304 hareket videosu veya 304 IM2V dışa aktarımı yapıldığı ileri sürülmez. Bu katalog animasyonların biçimsel adından çıkarılabilecek hipotezlerle orijinal işlevin kanıtını birbirine karıştırmaz.

## Özellikle araştırmaya değer henüz uygulanmamış davranışlar

1. **Gerçek melee/branşlanan kombo sistemi:** `IronMan_Ground_Combo_1/2/3`; `ComboPower1..4_final`; `ComboPower_a/aa/aaa/aab/ab/aba/abb` ve bitiş klipleri. Katalogda doğrudan 22 `Combo` kaydı var. Harfli dalların gerçek kontrol sırası (A/B ne demek?), vurma kareleri, çarpışma/hasar kuralları *bilinmiyor*. B16E yalnızca C kodunda hasar ve sayaç uyguluyor; bu gerçek skinned animasyonları içermiyor.
2. **Nesne kaldırma/taşıma/fırlatma:** `Ground_Raise1/2`, `Raise_Idle`, yönlere `Raise_move_[F/B/L/R]`, `Raise_Throw`, `Raise_Throw2`, `Ground_Put_down`. `Ground_Raise1_1` süresi 0ms olduğundan sıradan oynanabilir animasyon olarak döngüye alınmamalı; duruş/işaretleyici olabilir. Orijinal iOS incelemeleri kaldırma eyleminin oynanışta bulunduğunu doğruluyor (https://unvis.it/www.ign.com/articles/2010/05/10/iron-man-2-ipad-review).
3. **Yerde/açık havada karşı saldırı ve yakın saldırı:** `IronMan_Air_CounterAtt`, `IronMan_PushAway_Air/Ground`, `IronMan_Ground_Att_s1_Start/s1/s1_End/s2`, `IronMan_Fly_Att_ready/m/end`. Yanlışlıkla Beam üst-kol pozu olarak kullanılmamalı.
4. **Uçuş hareketleri gerçek geçişli:** `Ironman_Fly_FtoL`, `FtoR`, `LtoF`, `RtoF`; ileri/geri/sol/sağ uçuş; `Fly_Left_dodge`/`Right_dodge`; `Fly2Run`/ `Fly2Ground`; ayrı `Air_land_s_start/fall/end` ve zıplama animasyonları. Sadece dört RUSH alt pozu ile doğru yön geçişleri garanti edilmiyor.
5. **Nişan alma biçimleri:** Tek/iki el `_2H`, sol-el `_L/_LH`, `Aim_M`, hem yerde hem havada hareket ederken atış `*_move_*_Att`. '_M' sözcüğünün kesin 'missile' veya başka bir silah olduğunu yalnızca adından söyleyemeyiz.
6. **Iron Man olmayan açık alternatif oyuncu kaynağı:** 56 Warmachine klibi, kendi `Aim_Fly_M`, `Fly_Att_ready/s`, yönlü uçuş/yer hareketi ve `Aim_M_Float_move_*` içeriyor. `Warmachine_Walk_F` veya `RUSH` adında özgün dosya yok; isim yokluğu oynanış yeteneği yokluğu anlamına gelmez.
7. **War Machine orijinal silah kemikleri:** B6 denetimine göre `Warmachine_Aim_Fly_M.anim` etiketlerinde `Gun01`–`Gun04` geçiyor ve 41/41 animasyon etiketinin orijinal `warmachine.bdae` içeriğinde ada göre karşılığı bulunmuş. Bunlar silah çıkış/bağlantı noktası çözümü için öncelikli adaylar; hangi kemik hangi silahta kullanılmış henüz bilinmiyor. B17'de omuz vertex'i heuristiği *orijinal soket* değildir.
8. **Özel görev ve çevre/QTE:** `QTE_tank01/02`, `jump_bomb1..4`, `Obstacle_man_1..4`, `utah_machine_man1..4`, `hold_boss`, `fall_on_boss`, `Ground_Put_down`, `TreeMan_Raise_1..4`. Bunları sıradan dövüşe eklemeyin; sahne olayları ve `.bclara` eşleşmesi olmadan kullanım bağlamı bilinmiyor.
9. **Hasar/ölüm ve düşme:** Iron Man'in `Ground_Hurt1/2/3`, `Air_Hurt`, `Fly_Hurt/Hurt2`, `Ground_Death`, `Air_death`, `Falling_Hurt_Land` gibi özgün tepkileri var. Hasar ve knockback demo çevrimini tamamlamak için aday.
10. **0ms kayıtlar:** Sıfır süreli animasyonların sabit poz, placeholder veya özel olay olup olmadığı kare/kanal denetimiyle çözülmeden oynatıcıya süreyle mod alınarak verilmemeli.

### 2010 iOS kaynaklarından ayrıntı (başka platform oyunlarıyla karıştırmayalım)

- Gameloft iOS oyununun dönem incelemesinde **9 bölüm**, başlangıçta Iron Man ve ileride War Machine seçimi, her iki karakter için **yakın dövüş, repulsor, füze, hover/uçuş** açıkça anlatılıyor: https://www.intomobile.com/2010/05/07/review-iron-man-2-for-iphone-ipad/
- IGN'in iPad incelemesinde **nesne kaldırma, uçuş, dövüş, hackleme ve upgrade**, Unibeam için atış düğmesini yukarı kaydırma anlatılıyor: https://unvis.it/www.ign.com/articles/2010/05/10/iron-man-2-ipad-review
- Bu bulgular bütün özelliklerin oyunun *her zırhında/her görevinde* mevcut olduğunu **kanıtlamaz**. Yalnızca PS3/Xbox 360 sürümüne ait silah kısıtlamalarını iOS portuna taşımayın.

## Tüm 304 kayıt — grup sayımı

| Karakter / animasyon ailesi | Kayıt |
|---|---:|
| Iron Man / Bekleme / nişan alma | 13 |
| Iron Man / Boss / görev / QTE (aday) | 29 |
| Iron Man / Diğer (isimden belirsiz) | 1 |
| Iron Man / Hasar / ölüm / düşme | 17 |
| Iron Man / Hover / havalanma / zıplama | 52 |
| Iron Man / Hızlı uçuş / kaçınma | 31 |
| Iron Man / Işın / el bombası / kaldırma-fırlatma | 25 |
| Iron Man / Yakın dövüş / saldırı | 30 |
| Iron Man / Yakın dövüş – combo | 22 |
| Iron Man / Yerde hareket / koşu | 28 |
| War Machine / Bekleme / nişan alma | 6 |
| War Machine / Hover / havalanma / zıplama | 22 |
| War Machine / Hızlı uçuş / kaçınma | 2 |
| War Machine / Yakın dövüş / saldırı | 10 |
| War Machine / Yerde hareket / koşu | 16 |
| **TOPLAM** | **304** |

## 304/304 bireysel kayıt, süre ve kanal adı sayısı

**Etiket/kanal adı sayısı, kesin olarak "hareket eden kemik sayısı" değildir.** Etiketlerde model/bağlam girdileri bulunabilir. Tarihsel orijinal adlardaki yazım farkları (`Idel`, `Warmachine_Aattack`, büyük-küçük harf) aynen korunmuştur.

### Iron Man / Bekleme / nişan alma — 13 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `IronMan_Aim_Ground_idle.anim` | 933 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Aim_Ground_idle_2H.anim` | 800 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_idle_Att.anim` | 333 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Aim_Ground_idle_Att_2H.anim` | 800 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_idle_Att_L.anim` | 333 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Ground_idle_L.anim` | 933 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Aim_M_Ground_idle.anim` | 933 | 38 | Orta: silah/nişan |
| `Ironman_Aim_M_Ground_idle_Att.anim` | 400 | 38 | Orta: silah/nişan |
| `IronMan_Ground_Idel.anim` | 1399 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Ground_Idel_1.anim` | 2000 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Ground_Idel_2.anim` | 2333 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Idel_Att_ready.anim` | 933 | 29 | Temel/hareket veya belirsiz |
| `IronMan_main_pose.anim` | 0 | 38 | Temel/hareket veya belirsiz |

### Iron Man / Boss / görev / QTE (aday) — 29 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `Ironman_attack_boss.anim` | 366 | 38 | Olay/bölüme özel |
| `Ironman_fall_on_boss.anim` | 2000 | 53 | Orta: hasar/fizik |
| `Ironman_hold_boss.anim` | 1333 | 38 | Olay/bölüme özel |
| `Ironman_jump_bomb1.anim` | 533 | 38 | Olay/bölüme özel |
| `Ironman_jump_bomb2.anim` | 400 | 38 | Olay/bölüme özel |
| `Ironman_jump_bomb3.anim` | 400 | 38 | Olay/bölüme özel |
| `Ironman_jump_bomb31.anim` | 400 | 38 | Olay/bölüme özel |
| `Ironman_jump_bomb4.anim` | 1033 | 38 | Olay/bölüme özel |
| `IronMan_Obstacle_man_1.anim` | 500 | 38 | Olay/bölüme özel |
| `IronMan_Obstacle_man_2.anim` | 400 | 38 | Olay/bölüme özel |
| `IronMan_Obstacle_man_3.anim` | 400 | 38 | Olay/bölüme özel |
| `IronMan_Obstacle_man_4.anim` | 699 | 38 | Olay/bölüme özel |
| `Ironman_QTE_tank01.anim` | 800 | 38 | Olay/bölüme özel |
| `Ironman_QTE_tank02.anim` | 366 | 38 | Olay/bölüme özel |
| `Ironman_runaway_fail.anim` | 0 | 38 | Temel/hareket veya belirsiz |
| `Ironman_runaway_success.anim` | 1100 | 38 | Temel/hareket veya belirsiz |
| `Ironman_struggle_boss.anim` | 1833 | 38 | Olay/bölüme özel |
| `IronMan_tex_man_1.anim` | 500 | 38 | Olay/bölüme özel |
| `IronMan_tex_man_2.anim` | 400 | 38 | Olay/bölüme özel |
| `IronMan_tex_man_3.anim` | 400 | 38 | Olay/bölüme özel |
| `IronMan_tex_man_4.anim` | 600 | 38 | Olay/bölüme özel |
| `IronMan_TreeMan_Raise_1.anim` | 666 | 29 | Yüksek: nesne etkileşimi |
| `IronMan_TreeMan_Raise_2.anim` | 400 | 29 | Yüksek: nesne etkileşimi |
| `IronMan_TreeMan_Raise_3.anim` | 400 | 29 | Yüksek: nesne etkileşimi |
| `IronMan_TreeMan_Raise_4.anim` | 1066 | 29 | Yüksek: nesne etkileşimi |
| `IronMan_utah_machine_man1.anim` | 566 | 47 | Olay/bölüme özel |
| `IronMan_utah_machine_man2.anim` | 400 | 47 | Olay/bölüme özel |
| `IronMan_utah_machine_man3.anim` | 800 | 47 | Olay/bölüme özel |
| `IronMan_utah_machine_man4.anim` | 400 | 47 | Olay/bölüme özel |

### Iron Man / Diğer (isimden belirsiz) — 1 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `IronMan_Ground_Put_down.anim` | 1799 | 46 | Yüksek: nesne etkileşimi |

### Iron Man / Hasar / ölüm / düşme — 17 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `IronMan_Air_death.anim` | 2000 | 38 | Orta: hasar/fizik |
| `IronMan_Air_fall.anim` | 1600 | 38 | Orta: hasar/fizik |
| `IronMan_Air_Hurt.anim` | 600 | 38 | Orta: hasar/fizik |
| `IronMan_Air_land_s_fall.anim` | 400 | 38 | Yüksek: uçuş/geçiş |
| `IronMan_Falling_Hurt.anim` | 266 | 38 | Orta: hasar/fizik |
| `IronMan_Falling_Hurt_idle.anim` | 266 | 38 | Orta: hasar/fizik |
| `IronMan_Falling_Hurt_Land.anim` | 1066 | 38 | Orta: hasar/fizik |
| `Ironman_Fly_Hurt.anim` | 800 | 38 | Orta: hasar/fizik |
| `Ironman_Fly_Hurt2.anim` | 800 | 38 | Orta: hasar/fizik |
| `IronMan_Ground_Death.anim` | 3000 | 38 | Orta: hasar/fizik |
| `IronMan_Ground_Hurt1.anim` | 466 | 38 | Orta: hasar/fizik |
| `IronMan_Ground_Hurt2.anim` | 466 | 38 | Orta: hasar/fizik |
| `IronMan_Ground_Hurt3.anim` | 899 | 38 | Orta: hasar/fizik |
| `IronMan_Ground_Hurt_run.anim` | 866 | 38 | Orta: hasar/fizik |
| `IronMan_Ground_Hurt_walk.anim` | 1200 | 38 | Orta: hasar/fizik |
| `IronMan_Jump_fall.anim` | 166 | 38 | Orta: hasar/fizik |
| `Ironman_Move_jump_fall.anim` | 166 | 38 | Orta: hasar/fizik |

### Iron Man / Hover / havalanma / zıplama — 52 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `IronMan_Aim_Float_idle.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_idle_2H.anim` | 800 | 38 | Orta: silah/nişan |
| `IronMan_Aim_Float_idle_Att.anim` | 800 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_idle_Att_2H.anim` | 800 | 29 | Orta: silah/nişan |
| `IronMan_Aim_Float_idle_Att_L.anim` | 800 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_idle_Att_R.anim` | 800 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_idle_L.anim` | 800 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_move_B.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_move_B_Att.anim` | 800 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_move_F.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_move_F_Att.anim` | 800 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_move_L.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_move_L_Att.anim` | 800 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_move_R.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Float_move_R_Att.anim` | 800 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_M_Float_idle.anim` | 1600 | 38 | Orta: silah/nişan |
| `IronMan_Aim_M_Float_idle_Att.anim` | 1600 | 38 | Orta: silah/nişan |
| `IronMan_Aim_M_Float_move_B.anim` | 1600 | 38 | Orta: silah/nişan |
| `IronMan_Aim_M_Float_move_B_Att.anim` | 800 | 38 | Orta: silah/nişan |
| `IronMan_Aim_M_Float_move_F.anim` | 1600 | 38 | Orta: silah/nişan |
| `IronMan_Aim_M_Float_move_F_Att.anim` | 800 | 38 | Orta: silah/nişan |
| `IronMan_Aim_M_Float_move_L.anim` | 1600 | 38 | Orta: silah/nişan |
| `IronMan_Aim_M_Float_move_L_Att.anim` | 800 | 38 | Orta: silah/nişan |
| `IronMan_Aim_M_Float_move_R.anim` | 1600 | 38 | Orta: silah/nişan |
| `IronMan_Aim_M_Float_move_R_Att.anim` | 800 | 38 | Orta: silah/nişan |
| `IronMan_Air_Idel.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Air_Idel_1.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Air_Idel_2.anim` | 2733 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Air_land.anim` | 800 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Air_land_s.anim` | 1399 | 38 | Yüksek: uçuş/geçiş |
| `IronMan_Air_land_s_end.anim` | 1100 | 38 | Yüksek: uçuş/geçiş |
| `IronMan_Air_land_s_start.anim` | 300 | 38 | Yüksek: uçuş/geçiş |
| `IronMan_Air_Move_B.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Air_Move_F.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Air_Move_L.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Air_Move_R.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Air_up.anim` | 1200 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Float_Att_ready.anim` | 400 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Float_move_Att_ready_back.anim` | 300 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Ground_Float.anim` | 899 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Jump.anim` | 1166 | 29 | Temel/hareket veya belirsiz |
| `Ironman_Jump2.anim` | 1166 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Jump_Act1.anim` | 699 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Jump_Act1_run.anim` | 699 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Jump_Act3.anim` | 1000 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Jump_Act3_run.anim` | 800 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Jump_float.anim` | 833 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Jump_land.anim` | 400 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Jump_start.anim` | 666 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Move_Float.anim` | 800 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Move_jump_land.anim` | 300 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Move_jump_start.anim` | 666 | 38 | Temel/hareket veya belirsiz |

### Iron Man / Hızlı uçuş / kaçınma — 31 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `IronMan_Fly2Ground.anim` | 633 | 38 | Yüksek: uçuş/geçiş |
| `IronMan_Fly2Run.anim` | 966 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_B.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Fly_End.anim` | 400 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Fly_FtoL.anim` | 800 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_FtoR.anim` | 800 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH01.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH02.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH03.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH04.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH05.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH06.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH07.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH08.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH09.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH10.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH11.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_F_RUSH12.anim` | 1600 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_L.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Fly_Left_dodge.anim` | 699 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_LtoF.anim` | 800 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_M_Att_end.anim` | 200 | 29 | Temel/hareket veya belirsiz |
| `Ironman_Fly_M_Att_ready.anim` | 200 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Fly_M_Att_s.anim` | 1600 | 38 | Yüksek: yakın dövüş |
| `Ironman_Fly_R.anim` | 1600 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Fly_Right_dodge.anim` | 699 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_RtoF.anim` | 800 | 38 | Yüksek: uçuş/geçiş |
| `Ironman_Fly_Start.anim` | 333 | 38 | Yüksek: uçuş/geçiş |
| `IronMan_Rush.anim` | 600 | 38 | Yüksek: uçuş/geçiş |

### Iron Man / Işın / el bombası / kaldırma-fırlatma — 25 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `IronMan_Aim_Float_Beam1.anim` | 600 | 29 | Orta: silah/nişan |
| `IronMan_Aim_Float_Beam2.anim` | 400 | 38 | Orta: silah/nişan |
| `IronMan_Aim_Float_Beam3.anim` | 1266 | 38 | Orta: silah/nişan |
| `IronMan_Aim_Ground_Beam1.anim` | 400 | 38 | Orta: silah/nişan |
| `IronMan_Aim_Ground_Beam2.anim` | 400 | 38 | Orta: silah/nişan |
| `IronMan_Aim_Ground_Beam3.anim` | 1000 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_grenade_idle.anim` | 1399 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_grenade_move_B.anim` | 866 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_grenade_move_B_Att.anim` | 866 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_grenade_move_F.anim` | 800 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_grenade_move_F_Att.anim` | 800 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_grenade_move_L.anim` | 800 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_grenade_move_L_Att.anim` | 800 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_grenade_move_R.anim` | 800 | 38 | Orta: silah/nişan |
| `Ironman_Aim_Ground_grenade_move_R_Att.anim` | 800 | 38 | Orta: silah/nişan |
| `IronMan_Ground_Raise1.anim` | 699 | 44 | Yüksek: nesne etkileşimi |
| `IronMan_Ground_Raise1_1.anim` | 0 | 44 | Yüksek: nesne etkileşimi |
| `IronMan_Ground_Raise2.anim` | 1633 | 44 | Yüksek: nesne etkileşimi |
| `IronMan_Ground_Raise_Idle.anim` | 800 | 29 | Yüksek: nesne etkileşimi |
| `IronMan_Ground_Raise_move_B.anim` | 699 | 39 | Yüksek: nesne etkileşimi |
| `IronMan_Ground_Raise_move_F.anim` | 699 | 39 | Yüksek: nesne etkileşimi |
| `IronMan_Ground_Raise_move_L.anim` | 699 | 39 | Yüksek: nesne etkileşimi |
| `IronMan_Ground_Raise_move_R.anim` | 699 | 39 | Yüksek: nesne etkileşimi |
| `IronMan_Ground_Raise_Throw.anim` | 366 | 30 | Yüksek: nesne etkileşimi |
| `IronMan_Ground_Raise_Throw2.anim` | 433 | 38 | Yüksek: nesne etkileşimi |

### Iron Man / Yakın dövüş / saldırı — 30 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `IronMan_Aim_M_Float_Attack.anim` | 600 | 38 | Orta: silah/nişan |
| `IronMan_Air_Att_s.anim` | 1600 | 29 | Yüksek: yakın dövüş |
| `IronMan_Air_CounterAtt.anim` | 899 | 38 | Yüksek: yakın dövüş |
| `IronMan_Air_Hurt_attack1.anim` | 600 | 38 | Orta: hasar/fizik |
| `IronMan_Air_Hurt_attack2.anim` | 600 | 38 | Orta: hasar/fizik |
| `IronMan_Air_Hurt_attack3.anim` | 800 | 38 | Orta: hasar/fizik |
| `Ironman_Attack_ground_grenade.anim` | 800 | 38 | Orta: silah/nişan |
| `IronMan_Attack_Ground_idle.anim` | 266 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Attack_Ground_move_B.anim` | 1200 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Attack_Ground_move_F.anim` | 1200 | 29 | Temel/hareket veya belirsiz |
| `Ironman_Attack_M_ground.anim` | 600 | 38 | Yüksek: yakın dövüş |
| `Ironman_Fly_Att_end.anim` | 200 | 29 | Temel/hareket veya belirsiz |
| `Ironman_Fly_Att_m.anim` | 1600 | 38 | Yüksek: yakın dövüş |
| `Ironman_Fly_Att_ready.anim` | 200 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Fly_Att_s.anim` | 1600 | 38 | Yüksek: yakın dövüş |
| `IronMan_Ground_Att_end.anim` | 300 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Ground_Att_idel.anim` | 1333 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Ground_Att_idel_B.anim` | 1200 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Ground_Att_idel_F.anim` | 1200 | 40 | Temel/hareket veya belirsiz |
| `IronMan_Ground_Att_idel_L.anim` | 1200 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Ground_Att_idel_R.anim` | 1200 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Ground_Att_s1.anim` | 266 | 33 | Yüksek: yakın dövüş |
| `IronMan_Ground_Att_s1_End.anim` | 300 | 29 | Yüksek: yakın dövüş |
| `IronMan_Ground_Att_s1_Start.anim` | 233 | 29 | Yüksek: yakın dövüş |
| `IronMan_Ground_Att_s2.anim` | 899 | 29 | Yüksek: yakın dövüş |
| `IronMan_Ground_Att_s_r.anim` | 866 | 29 | Yüksek: yakın dövüş |
| `IronMan_Ground_Att_s_w.anim` | 1200 | 29 | Yüksek: yakın dövüş |
| `Ironman_Palsy.anim` | 1066 | 38 | Temel/hareket veya belirsiz |
| `IronMan_PushAway_Air.anim` | 1333 | 38 | Yüksek: yakın dövüş |
| `IronMan_PushAway_Ground.anim` | 1333 | 38 | Yüksek: yakın dövüş |

### Iron Man / Yakın dövüş – combo — 22 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `IronMan_Ground_ComboPower1.anim` | 600 | 40 | Yüksek: yakın dövüş |
| `IronMan_Ground_ComboPower1_end.anim` | 400 | 40 | Yüksek: yakın dövüş |
| `IronMan_Ground_ComboPower2.anim` | 666 | 40 | Yüksek: yakın dövüş |
| `IronMan_Ground_ComboPower2_end.anim` | 666 | 40 | Yüksek: yakın dövüş |
| `IronMan_Ground_ComboPower3.anim` | 800 | 40 | Yüksek: yakın dövüş |
| `IronMan_Ground_ComboPower3_end.anim` | 533 | 40 | Yüksek: yakın dövüş |
| `IronMan_Ground_ComboPower4_final.anim` | 1333 | 40 | Yüksek: yakın dövüş |
| `Ironman_Ground_ComboPower_a.anim` | 666 | 42 | Yüksek: yakın dövüş |
| `Ironman_Ground_ComboPower_aa.anim` | 833 | 42 | Yüksek: yakın dövüş |
| `Ironman_Ground_ComboPower_aaa.anim` | 1766 | 42 | Yüksek: yakın dövüş |
| `Ironman_Ground_ComboPower_aab.anim` | 1566 | 43 | Yüksek: yakın dövüş |
| `Ironman_Ground_ComboPower_aa_end.anim` | 600 | 42 | Yüksek: yakın dövüş |
| `Ironman_Ground_ComboPower_ab.anim` | 1033 | 43 | Yüksek: yakın dövüş |
| `Ironman_Ground_ComboPower_aba.anim` | 1700 | 43 | Yüksek: yakın dövüş |
| `Ironman_Ground_ComboPower_abb.anim` | 2700 | 43 | Yüksek: yakın dövüş |
| `Ironman_Ground_ComboPower_ab_end.anim` | 1166 | 43 | Yüksek: yakın dövüş |
| `Ironman_Ground_ComboPower_a_end.anim` | 500 | 42 | Yüksek: yakın dövüş |
| `IronMan_Ground_Combo_1.anim` | 266 | 40 | Yüksek: yakın dövüş |
| `IronMan_Ground_Combo_1_end.anim` | 233 | 40 | Yüksek: yakın dövüş |
| `IronMan_Ground_Combo_2.anim` | 300 | 40 | Yüksek: yakın dövüş |
| `IronMan_Ground_Combo_2_end.anim` | 300 | 40 | Yüksek: yakın dövüş |
| `IronMan_Ground_Combo_3.anim` | 500 | 40 | Yüksek: yakın dövüş |

### Iron Man / Yerde hareket / koşu — 28 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `Ironman_Aim_Ground_move_B.anim` | 866 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Aim_Ground_move_B_Att.anim` | 866 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Ground_move_F.anim` | 866 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Aim_Ground_move_F_Att.anim` | 866 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Ground_move_L.anim` | 866 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Aim_Ground_move_L_Att.anim` | 866 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Aim_Ground_move_R.anim` | 866 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Aim_Ground_move_R_Att.anim` | 866 | 38 | Temel/hareket veya belirsiz |
| `Ironman_Aim_M_Ground_move_B.anim` | 1399 | 38 | Orta: silah/nişan |
| `Ironman_Aim_M_Ground_move_B_Att.anim` | 1399 | 38 | Orta: silah/nişan |
| `Ironman_Aim_M_Ground_move_F.anim` | 866 | 38 | Orta: silah/nişan |
| `Ironman_Aim_M_Ground_move_F_Att.anim` | 866 | 38 | Orta: silah/nişan |
| `Ironman_Aim_M_Ground_move_L.anim` | 866 | 38 | Orta: silah/nişan |
| `Ironman_Aim_M_Ground_move_L_Att.anim` | 866 | 38 | Orta: silah/nişan |
| `Ironman_Aim_M_Ground_move_R.anim` | 866 | 38 | Orta: silah/nişan |
| `Ironman_Aim_M_Ground_move_R_Att.anim` | 866 | 38 | Orta: silah/nişan |
| `IronMan_run.anim` | 533 | 45 | Temel/hareket veya belirsiz |
| `IronMan_runflash1.anim` | 66 | 38 | Temel/hareket veya belirsiz |
| `IronMan_runflash2.anim` | 200 | 38 | Temel/hareket veya belirsiz |
| `IronMan_runflash3.anim` | 533 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Run_Att_end.anim` | 5066 | 29 | Temel/hareket veya belirsiz |
| `Ironman_Run_Att_ready.anim` | 5066 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Walk_Att_end.anim` | 5733 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Walk_Att_ready.anim` | 5733 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Walk_B.anim` | 1200 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Walk_F.anim` | 1200 | 38 | Temel/hareket veya belirsiz |
| `IronMan_Walk_L.anim` | 1200 | 29 | Temel/hareket veya belirsiz |
| `IronMan_Walk_R.anim` | 1200 | 29 | Temel/hareket veya belirsiz |

### War Machine / Bekleme / nişan alma — 6 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `Warmachine_Aim_Ground_idle.anim` | 933 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Ground_idle_2H.anim` | 800 | 41 | Orta: silah/nişan |
| `Warmachine_Aim_Ground_idle_Att.anim` | 933 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Ground_idle_LH.anim` | 933 | 41 | Orta: silah/nişan |
| `Warmachine_Aim_M_Ground_idle.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Ground_idle_Att.anim` | 1600 | 42 | Orta: silah/nişan |

### War Machine / Hover / havalanma / zıplama — 22 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `Warmachine_Aim_Float_idle.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Float_idle_2H.anim` | 800 | 41 | Orta: silah/nişan |
| `Warmachine_Aim_Float_idle_Att.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Float_idle_L.anim` | 800 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Float_move_B.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Float_move_B_Att.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Float_move_F.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Float_move_F_Att.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Float_move_L.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Float_move_L_Att.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Float_move_R.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Float_move_R_Att.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_M_Float_idle.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Float_idle_Att.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Float_move_B.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Float_move_B_Att.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Float_move_F.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Float_move_F_Att.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Float_move_L.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Float_move_L_Att.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Float_move_R.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Float_move_R_Att.anim` | 1600 | 42 | Orta: silah/nişan |

### War Machine / Hızlı uçuş / kaçınma — 2 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `Warmachine_Aim_Fly_M.anim` | 1600 | 42 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Fly_M_Att.anim` | 1600 | 42 | Temel/hareket veya belirsiz |

### War Machine / Yakın dövüş / saldırı — 10 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `Warmachine_Aattack_Float_idle_LH.anim` | 800 | 41 | Orta: silah/nişan |
| `Warmachine_Aattack_Ground_move_B.anim` | 866 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Attack_Float_idle_2H.anim` | 800 | 41 | Orta: silah/nişan |
| `Warmachine_Attack_Float_move_B.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Attack_Float_move_R.anim` | 1600 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Attack_Ground_idle_2H.anim` | 800 | 41 | Orta: silah/nişan |
| `Warmachine_Attack_Ground_idle_LH.anim` | 933 | 41 | Orta: silah/nişan |
| `Warmachine_Attack_Ground_move_R.anim` | 866 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Fly_Att_ready.anim` | 200 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Fly_Att_s.anim` | 1600 | 41 | Yüksek: yakın dövüş |

### War Machine / Yerde hareket / koşu — 16 kayıt

| Orijinal animasyon | Süre (ms) | Kanal adı | İnceleme odağı |
|---|---:|---:|---|
| `Warmachine_Aim_Ground_move_B.anim` | 866 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Ground_move_B_Att.anim` | 1399 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Ground_move_F.anim` | 866 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Ground_move_F_Att.anim` | 866 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Ground_move_L.anim` | 866 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Ground_move_L_Att.anim` | 866 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Ground_move_R.anim` | 866 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_Ground_move_R_Att.anim` | 866 | 41 | Temel/hareket veya belirsiz |
| `Warmachine_Aim_M_Ground_move_B.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Ground_move_B_Att.anim` | 1399 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Ground_move_F.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Ground_move_F_Att.anim` | 866 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Ground_move_L.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Ground_move_L_Att.anim` | 866 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Ground_move_R.anim` | 1600 | 42 | Orta: silah/nişan |
| `Warmachine_Aim_M_Ground_move_R_Att.anim` | 866 | 42 | Orta: silah/nişan |

## Kullanım ve uygulama önceliği

**Önce** gerçek `Combo_1/2/3` + `Ground_Att_s1` ve `Raise/Throw` kliplerini orijinal BDAE iskeletine bakarak IM2V biçimine dönüştür; evrelerin süresini ve 3D temas anlarını analiz et. **Aynı anda** War Machine `Gun01..04` kemiklerini dünya uzayı transformlarıyla karşılaştır, soket tahminlerini gerçek node'larla değiştir. **Sonra** `IronMan_Walk_F` ile `Fly_F/F_RUSH` animasyonlarını War Machine iskeletine güvenli retarget et; mevcut B17 prosedürel öne eğmeyi gerçek animasyon diye adlandırma. **Daha sonra** QTE/boss/nesne kaldırma olaylarını orijinal level script ve spawn çözümlemesiyle ilişkilendir. Kullanıcının B17 gerçek PS Vita testi gelene kadar yeni VPK üretme.

**Ham arşivlerin gizliliği:** Kaynak kullanıcı IPA'sı ve çıkarılmış animasyon keyframe verileri özel depoda tutulmalı; internete yeniden dağıtılmamalıdır.
