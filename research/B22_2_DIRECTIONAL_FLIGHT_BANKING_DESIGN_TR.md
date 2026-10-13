# B22.2 — Directional Flight, Banking and Animation Blending (TASARIM / HOST-PLAN)

Tarih: 2026-10-13. Iron Man 2 iOS → Vita. **Bu belge tasarım önerisi, çalışan Vita özelliği değildir.** B17 gerçek PS Vita testi bekliyor. B15/B17 sürümleri, B19–B22 kodları değiştirilmedi. Yeni CI/VPK yok. Yalnızca özel repoda kayıt.

## İstenen deneyim
Sadece irtifa yükselt/alçalt yerine ileri giderken gerçek 3B tırmanış/dalış; hafif sola/sağa yönlendirmede zırhın yavaşça yana yatması (bank/roll); Stage 2 hafif viraj, Stage 3 hızlanıp daha güçlü ama kontrollü bank; giriş bırakıldığında düzgün doğal toparlanma. Karakter gövde animasyonu, dünya koordinatlarındaki hız, kamera, elden fırlayan silah çıkış soketleri birlikte tutarlı olmalı. Kullanıcı özgün iOS videolarından bu hissi örnek verdi; tam özgün uçuş fiziği henüz decompile edilmedi.

## Elimizdeki doğrulanmış orijinal veriler
- `Ironman_Fly_F` 1600 ms; `Ironman_Fly_F_RUSH` 1600ms ve özgün ayrı RUSH01...12 ara pozları; değişen joint starting poses doğrulanmış ancak özgün runtime sırası/fizik değeri kanıtlanmadı.
- `Ironman_Fly_Left_dodge`, `Ironman_Fly_Right_dodge` doğrulanmış ayrı **kaçınma** klipleri. Sürekli dönüş için birebir bank animasyonu sayılmamalı.
- `IronMan_Air_Move_F` yavaş ileri hareket; `Warmachine_Aim_Fly_M` War Machine özgün uçuşu. WM için özgün dedike RUSH henüz kanıtlanmadı.
- B15 doğal kontrollere ve 3 stage'e ilişkin kullanıcı gerçek Vita geri bildirimi var. B17 ayrı VPK henüz cihaz testi görmedi.
- 59 baked IM2V hareketli vertex stream (B17); tam çalışma anında skinning yok. **Model root orientation matrix** ile mevcut pozların tamamını eğmek mümkün; özel arm/leg additive deformation ise yeni skinning/blend implementasyonu ve test ister.
- Geçmiş B10 gerçek Vita profili CPU ~20–22 ms, SDL_UpdateTexture UP ~29 ms; açı animasyonu performans kazancıymış gibi iddia edilmez.

## Önerilen kontrol: Camera-directed Arcade Flight (varsayılan)
Temel çakışma: B21 tasarımında Vita **R=ateş**, **L=füze kilidi**, D-pad yukarı/aşağı = ince irtifa, **sağ analog kamera** ve sol analog hareket. L/R aynı anda eski irtifa tuşları olamaz.

- Stage 1 (slow hover): sol analog yatay düzlemde ileri/geri/yan hareket, vücut neredeyse dik; sağ analog özgür kamera orbit. Eski temel hissi korur. D-pad up/down hassas irtifa.
- Stage 2 (forward flight): sol analog ileri yönünde hareket/itki; sağ analogun kamera pitch'i hareket vektörüne kontrollü olarak dikey bileşen ekler: kamera yukarı bakıyorsa ileri gitmek aynı zamanda tırmandırır, aşağı bakıyorsa dalış. Sol analog X'in uçuş heading'ini dönüşe yönlendirmesi ve **yaw-rate/steering kaynaklı roll**. Kamera ve uçuş yönü ayrıştırılır, kullanıcı başını aniden savurmadan seyir eder.
- Stage 3 (Triangle boost): aynı analog mantığı fakat yüksek hızda daha ağır steering damping, daha yüksek (sınırlandırılmış) bank pozu ve güvenli kamera takip gecikmesi. Stage2->3 `Fly_F`/`RUSH01..12`/RUSH geçişi gözle ayrı doğrulanmalı.
- Alternatif sonradan eklenebilir: `Direct Nose` uçuş kontrol şeması (ilerleme hızının korunduğu seyirde sol Y doğrudan pitch, sol X yaw/bank). **Mevcut B15 sol Y'nin ileri hareket/stage eşikleriyle çakışacağından ayrı seyir-hızı state'i ve kalıcı opsiyon olmadan varsayılan olarak değiştirme.**
- Pause options uçuş pitch inversion, bank sensitivity, camera follow strength. B21 ayarları ile birleştir; şimdilik tasarım.

## Teknik ayrım / önerilen durum
1. **Gerçek hareket:** `velocity` 3B, `desired_dir` (kamera pitch'inden/hareket heading'inden), ivme, hız sınırı, süzülme/friction; `position += velocity * dt`. R/L ateş/lock ile çakışmaz. Ground/hover vs stage2/3 farklı kurallar.
2. **Görsel root orientation:** `body_yaw` = travel heading'in yumuşatılmış açısı, `pitch` = dikey hız/hedef pitch ile görsel burun açısı, `roll` = dönüş hızı/steering X. Roll *uçuş eğilimi*; tek başına world velocity update yerine geçmez. Pilot başlangıç sınırları örn. Stage2 +/-15–20° roll, +/-20–30° pitch; Stage3 +/-25–30° roll; **özgün oyunun kesin değerleri değil**, Vita gözlemiyle ayarlanacak.
3. **Baked animation:** aynı `.im2v` sampled vertex'ler üzerine önce zırh root transform, sonra world translation; ilk prototip yeni anim yüklemeden yapılabilir. Sürekli bank için dodge clip'i loop yapma. Gerçek kol/bacak reaksiyonunda orijinal anim joint quaternion pose lerini maskeyle blend ederek bake 3-5 pose bank/pitch örneği; farklı suit binding ve vertex counts/memory test gerektirir.
4. **Dönüş düzgünlüğü:** `dt` clamped/smoothed, yaw shortest-arc veya quaternion slerp, roll spring-damper, target-bias minimum jerk. Neutral analogla aniden upright snap yok.
5. **Kamera:** rig-head takip pivotu; global horizon aslen sabit, camera bank'ın küçük bir kısmını (isteğe bağlı max ~3°) izler, tam roll kadar eğilmez. Dönerken önüne bakabilme, görüş/lock HUD hedef projeksiyonu ve 480x272 reticle koordinatı stabil kalır.
6. **Silahlar:** el/omuz/göğüs attachment world positions **current root orientation** uygulanarak hesaplanır. B22.1 missile lock seçilmiş hedefi world-space izler; kamera/body dönüşünde no-snap. Ground/world collision ayrı physics gate, tırmanış ceiling ve altitude limitations BCLARA data bulunduğunda.
7. **Performans:** GPU geçişiyle doğrulanmadan 30/60fps taahhüt yok. Root transform makul maliyetli fakat B10 SDL_UpdateTexture darboğazı duruyor. Vita B17 ve yeni flight karşılaştırmasında CPU/UP/COPY/PRES/FPS ölç.

## Minimum acceptance test — yeni VPK ancak B17 QA sonrası
- Stage1 eski hover/walk/camera hissini bozma; analog bırakma → drift kontrollü ve zırh nötr.
- Stage2 ileri + kamera yukarı tırmanış (Y gerçekten yükselir), aşağı dalış; yumuşak left/right bank, yatışı bıraktığında kademeli toparlar; world position/hud tutarlı.
- Stage3 hız artırır, bank ve pitch sınırları bozulmaz; RUSH source poses kamera ve beden matrisleriyle çakışmaz.
- Mark VI/Mark V/WM geçişinde retarget problemsiz; WM native RUSH yoksa aynı klibi uydurma diye etiketleme.
- Füze lock L ve ateş R işlevi kameralı manevrayla aynı anda çalışır; pause dondurma, hasar ve yerden çarpışma güvenli.
- Desktop deterministic tests (heading/pitch/yaw, frame dt, quaternion, normalization) + Vita screenshot/video, FPS ve profil metrikleri. Başarı **cihazda kanıtlandığında** işaretlenir.

## Önemli dürüstlük sınırı
Bu öneri mevcut orijinal animasyon dosyalarını kullanabilir fakat **özgün 2010 iOS flight engine kodunun birebir portu değildir**. Orijinal engine direction/roll/pitch/controller parametreleri henüz kanıtlanmadı. Şu anda kod değil, bilimsel test planı hazırladık; B15/B17/B22.1'de değişiklik yok.
