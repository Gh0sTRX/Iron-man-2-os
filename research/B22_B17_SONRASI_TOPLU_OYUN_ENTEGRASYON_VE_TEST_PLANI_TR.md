> **GÜNCEL DURUM — 13.10.2026 AKŞAM / B17 GERÇEK PS VITA TEST EDİLDİ:** Bu dokümanın B17 cihaz testi bekleniyor ve yeni geliştirmenin koşulu olan paragrafları tarihsel plan kaydıdır; kullanıcı B17'yi gerçekten test etti. Hareketleri başarılı buldu; repulsor/WM animasyonları, analog erken hızlanma, yere değmeden iniş ve çok düşük FPS bildirdi. Öncelik GPU gerçek render hattı + doğru animasyon durum makinesi. Gerçek B17 raporu ve ilk host C11 GPU/kontrol laboratuvarı: `research/b18_gpu_probe/README.md`; kanonik son durum `PROJECT_HANDOFF.md`. Eski B15 ve B17 korunuyor, yeni VPK henüz yok.

# Iron Man 2 (Gameloft iOS 2010) → PS Vita | B17 Bekleme Dönemi / Toplu Entegrasyon ve Test Planı
**Tarih:** 13.10.2026 · **Durum:** PLAN + KAYNAK DOĞRULAMA, Vita cihaz testi yok, yeni VPK yok. Bu belge PRIVATE repoda saklanır.

## Mutabakat / ürün stratejisi
Kullanıcı evde değil ve Vita yanında değil. **B17 `IronMan2_Arena_B17.vpk` henüz gerçek Vita'da test edilmedi.** B17'ye dokunma, B15 iyi bilinen rollback sürümünü koru, yeni ayrı dağıtılabilir VPK veya gereksiz GitHub Actions otomasyonu başlatma. **Bu arada tüm oyun modüllerini paralel hazırlayıp test kanıtlarını, eksik kaynakları ve beklentileri topla.** Kullanıcı B17 gözlemlerini gönderdikten sonra bir sonraki anlamlı **tek konsolide sürüm** tasarlanacak. Yapılacaklar listesi tek bir animasyon (örn. yürüme) etrafında daralmayacak.

Oyun için gerçek hedef, bir zırh izleyicisi değil: **orijinal karakter + orijinal düşman + gerçek çevre + kontrol/HUD + iki dalga savaş + saldırı/karşı saldırı + HP/kalkan/ölüm + kazanma/kaybetme + checkpoint/retry + doğrulanmış orijinal ses**. Bu küçük eğitim çatışması tamamlanmadan asıl `Media Mayhem` restorasyonu ilan edilemez.

## Çalışma defteri: modül, gerçekte mevcut kanıt, bekleyen iş, onay koşulu

| Sistem | Şu an eldeki gerçek kaynak | Eksik / önceden hazırlanacak | Gerçek test onayı |
|---|---|---|---|
| Zırh/rig | 5 orijinal im2t; B15 cihazda başarılı. 1.0.0'da 972 anim, 1.0.3'te 989. | Underwater BDAE + bind rig + tekstür kaynağı, ana model atlas materyal kontrolleri, karakter bazlı kaynak-araç eşlemesi | Tüm zırhların idle/ground/hover/sprint/fly/land pozları doğru, hiçbirinde yanlış rig yok |
| Underwater animasyon | B15 orijinal CSV'de 43 Underwater adı; **34 zırh klibi 38 kanal + 9 sahne objesi** | B21 manifest betiğindeki ship büyük/küçük harf sınıflama hatası düzeltildi (`7d852a2`). Gerçek model ve ham kaynak klipler lazım | Gerçek Underwater zırhında özgün Swim_F/D/L/R/U, Float_2_Swim, Swim_2_Float ve hasar; 9 çevre klibi ayrık |
| Oynanış input | B17 mevcut kontrolleri; B21 saf C11 input state modülü ve testleri | R hold ateş, L basılı hedef kilidi, joystick kamera, yürürken analog hız, yatay/dikey yön, D-Pad silah+irtifa, Square gerçek melee, Cross etkileşim ve pause yönlendirmesi tek entegrasyonda yapılmalı | Tuş çatışması / tıklama sürüklenmesi yok, menüde ateş yok, stable lock/drop/reacquire ve kamera snap yok |
| HUD / pause | B21 480x272 çizim prototipi, can/kalkan/enerji, kilit çerçevesi, duraklatma paneli; host suite PASS | Gerçek B19 gameplay state, metin/ikonlar, görev adı, hedef HP, silah enerji/ammo, açılış/duraklatma; ses bus ve ayar kaydı henüz yok | Vita ekranına oturan okunaklı HUD; pause oyunu gerçekten dondurur, müzik/SFX/invert settings kalıcıdır |
| Savaş fizik/mühimmat | B19 native iki dalga HP/damage/fire/win/fail ve B19 independent swept-segment/sphere host tests | İki kaynak henüz birleşmedi; projectile ownership/velocity/world collision, anim zamanlı vuruş, splash, Unibeam chest ve Gun01-04 attachment | Mermiler yüksek FPS / düşük FPS tutarlı, HP değişir, dolum ve hasar gerçeğe benzer, kalkan görselleşir |
| Düşman / AI | 189 Drone, 81 Enemy, 67 Boss animasyon adı ve orijinal `StateDatabase`, `NPCSpawnMgr`, `SpawnPoint` sembolleri | Orijinal Drone_Army/Floating BDAE rig/texture ham kaynağı private snapshot'ta yok; özgün AI state verisi ve spawn ID eşleşmesi lazım | Gerçek dokulu/skinned düşman animasyonu, yaklaş/ateş/al hasar/öl; iki dalga ve retry |
| Dünya/GPU | B11 C1L1 22.919 görünür üçgen ve 39 referans dokusu; B17 renkli test zemini | Vita CPU raster+SDL upload darboğazı; GPU scene renderer, malzeme alpha/depth, sahne transformları ve statik collision | Cihazda sahne+2-3 düşman testinde ölçülen kararlı FPS; hedef bant sadece testle belirlenir |
| Ses/Müzik | Orijinal `SoundManager`, `vox::DecoderMPC8/MSWav/Raw`, `AdpcmDecoder` sınıf adları | IPA ses bankası ve sample referansları henüz toplanmadı; codec ve lisanslı parça sayısı bilinmiyor | Silah/jet/hit/düşman SFX doğru eventlere bağlanır; menüde aç/kapat gerçek motoru susturur |
| Görev/progresyon | 10 `level*.bclara` ve `MissionMgr`/checkpoint API; iOS kaynaklarında 9 oynanabilir bölüm | Original mission graph, actor spawn/objective/equipment, level10 rolü; XP ve özel minigame `Twist`/`GateClue` | İlk özel eğitim görevinde iki dalga kazanma/kaybetme, sonraki aşamada iOS görevinin gerçek başlangıç ve tamamlanma koşulları |
| Cinematic/voice | `GamePlayUI::StartCutscene`, `GS_GamePlay::SkipCinematic`, `CameraPath::BuildSpline` | İçerik FMV mi, in-engine mi, hybrid mi; voice ID ve subtitling bilinmiyor | Kaynaktaki gerçek intro/outro + skip + diyalog sesleri senkron, checkpoint tutarlı |
| Silah / karakter yeteneği | 2010 iOS kaynaklarında repulsor/Unibeam/füze/melee; WM silah Gun01-04 düğüm adları; B16 prototip | Görev/zırh bazlı weapon ID/unlock tablosu; özgün çıkış soketi ve VFX | Iron Man göğüsten Unibeam, avuçtan repulsor; WM gerçek fixture; kullanılmayan yetenekler zorla her karaktere yüklenmez |

### B17 ilk geri bildirim geldiğinde kullanıcıdan istenecekler (tek oturum, yaklaşık 5–10 dakika)
Bu liste yalnızca **B17'de şu anda var olan özellikleri** sınar; B21 prototipindeki yeni HUD/lock/pause'u kullanıcıya yanlışlıkla B17'de aratma.
1. İlk açılış ve 5 zırhın birbirine geçişi; boş ekran/crash var mı?
2. Mark VI yerde idle ve analog hassasiyet/yürüyüş/koşma; War Machine yürürken kol ve gövde pozu.
3. Mark VI ve War Machine uçuşta Stage1/2 ve boost/RUSH duruşu, yavaş-hover kararlılığı; özellikle War Machine Stage3'in geçici prosedürel eğimi.
4. Repulsor avuçtan mı, Unibeam yaklaşık göğüsten mi, missile yaklaşık omuzdan mı; kaydedilmesi mümkünse tek ekran/video.
5. Renkli zeminin gerçekten ayakların altında durması, hareket sırasında arka plan gibi kaymaması, karakterle derinlik ilişkisi.
6. FPS ve profile metrikleri (CPU/UP/COPY/PRES) mümkünse 15–30 saniye; donma/ısınma/beklenmeyen kapanış.
7. Kontrol haritası B17'de **eski**: Sağ/sol omuz irtifa, Kare ateş; Start çıkar. B21 R ateş/L lock henüz VPK'ya eklenmiş değil.

Kullanıcının tek cümlelik özet gözlemi + en az bir ekran görüntüsü bile ilk değerlendirmeye yeterli. Tüm aşamaları aynı anda raporlaması şart değil. Yeni sürüm ancak bu veriyle hazırlanacak.

### B17 sonucu geldikten sonra entegrasyon (sıralı, tek büyük özellik odaklı sürüm)
- **Aşama A — Stabil temel:** B17 sorunlarını sınıflandır/kaynak yazılı bir test haline dönüştür, rollback B15'i koru. CPU/GPU render yolu seçimini sahne/düşman büyümeden kesinleştir.
- **Aşama B — Kontrol/UI:** B21 R fire/L target, Start pause/options, HUD + gerçek B19 HP/energy, fiziksel kontrol çakışma testleri; duraklatma gerçek `dt` ve ses bus'ı askıya alır.
- **Aşama C — Savaş entegrasyonu:** B19 projectile sweep ile B19 görev çekirdeğini birleştir, gerçek düşman model/anim, state, spawn; dünya hit-test, audio event, objective HUD.
- **Aşama D — Özgün içerik:** Underwater outfit yalnız orijinal rig source bulunduğunda; melee comboları orijinal .anim->IM2V, sabit/cinematic içerik ve özgün görev bclara.
- **Aşama E — Host QA + tek Vita candidata:** C Debug/ASan/UBSan, ZIP/sha, TitleID, anim rig manifest, VPK doğrulama. CI kırmızı iterasyonlarını yerel lint/testle azalt ve yalnızca doğrulanabilir tek değişimle Actions tetikle.
- **Aşama F — Kullanıcı Vita deneyi:** doğrudan sohbetten tek tıkla VPK ile birlikte test listesi, tek screenshot/FPS raporu, sorunların sıralı çözümü. Çalışmayan kalite bileşenlerini doğru şekilde prototype diye işaretle.

### Kaynak erişim sınırı ve veri kaybına karşı kayıt
- GitHub özel depoda şu anda B15 972 anim meta/10.760 C++ ad, B6/B7 skinning scriptleri, B11 C1L1 çevre BDAE ve örnek MarkVI rig/motion verileri mevcut.
- Orijinal *tam* IPA dosyaları (`IronMan2_1.0.0_ios_2.2.1.ipa` 248.6 MB, `Iron Man 2 iOS 3.0.ipa` 275.6 MB) erişilebilir kullanıcı dosyası olarak bu çalışma oturumunda bulunmuyor. İçinden çıkarılmış tüm ham Underwater ve Drone model/audio/mission dosyaları bulunmadan gerçek yüzde hesabı veya tam oyun içerik derlemesi yapılamaz.
- Kod doğru hazırlansa da **demo “oynanabilir” kabulü** ancak Vita'da gerçek düşman + dünya + hasar + HUD + win/fail + sound birleşimi kullanıcıca onaylandığında verilmelidir.
- İlerleme sayımı katmanlıdır: ZIP arşivi tanıma ≠ ikili format decode ≠ mesh/anim görüntüleme ≠ Vita oyunda çalıştırma ≠ özgün görev sadakati. Tek bütünsel “%XX tersine mühendislik bitti” tahmini hesaplanmıyor.
