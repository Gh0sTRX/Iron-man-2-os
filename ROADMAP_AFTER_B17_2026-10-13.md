# Iron Man 2 iOS → PS Vita — B17 Sonrası Yol Haritası ve Tamamlama Kriterleri
**Tarih:** 13 Ekim 2026 · **Plan türü:** karar/araştırma belgesi; bu commit YENİ VPK ÜRETMEZ.  
**Temel:** özel kullanıcı kaynakları; `PROJECT_HANDOFF.md`, `research/B18_COMPLETE_304_PLAYER_ANIMATIONS_CATALOG_TR.md`, `research/ORIGINAL_LEVEL_ARCHIVE_AUDIT.md`, `research/B11_ORIGINAL_C1L1_SCENE.md`, `research/B12_ORIGINAL_C1L1_TEXTURE_RECOVERY.md`, B17 CI run **38323319029**.

## Amaç ve dürüst sınır
**İstenen nihai çıktı:** Gameloft'un **2010 iOS sürümünün** oynanabilir PS Vita yeniden oluşturması; özgün zırhlar/animasyonlar, uçuş + doğru karaktere özgü silahlar, düşmanlar/bosslar, görevler, ses ve müzik, özgün diyalog/ara sahneler, menüler, kayıt/yükseltme/progresyon; gerçek cihazda makul kararlılık ve performans. Şu andaki Vita projesi özgün iOS motorunun kaynak-kod portu değildir: özgün varlıklardan beslenen, sıfırdan yazılan bir C/SDL2 oyun prototipidir. **B17 henüz cihazda denenmedi.**

**İdeal senaryo tahmini:** B18–B32 = **15 kontrollü mühendislik kilometre taşı**, her birinin fiziksel VPK olması şart değil. 7–10 tanesi yaklaşık cihaz VPK'sı olabilir, diğerleri veri/araştırma/masaüstü testleri. B32 sonrasında **1–3 RC** ve kalite düzeltmeleri olasıdır. Bu **garanti edilen sayı veya teslim tarihi değildir**. Eksik orijinal mission örneklerini ve motor davranışını çözmek, içeriği yeniden yazmak, ses/cutscene biçimi ve GPU sürücü uyumluluğu kolayca ek aşamalar gerektirebilir. Gerçek oynanabilir ilk özgün misyon hedefi **B25 civarı**, tam hikâye hedefi **B32 sonrası**.

## Kesin mevcut durum (kanıt seviye ayrımı)
| Alt sistem | Doğrulanmış teknik durum | Oyun tam mı? |
|---|---|---|
| Modeller/zırhlar | **5** orijinal doku+mesh, gerçek Vita'da daha eski sürümlerde kullanıldı; Mark VI, IV, V/Suitcase, Stealth, War Machine | Hayır; ek zırh/LOD/material/doğru rig eşlemesi açık |
| Animasyon | 1.0.0 IPA'nın **972** original kayıt formatı çözülmüş; oyuncu karakterlerinin **304** (248 IronMan, 56 WM) ad/süre/kanal envanteri; B17 **59** pre-baked `.im2v` | Hayır; 304'ün tamamı görsel/test edilmiş değil, true melee/throw/transition eksik |
| Karakter kontrolü | B15 iyi hissedilen 3rd-person analog/kamera/hareket; B16 uyumsuz silah animasyonları kullanıcı tarafından gerçek Vita'da görüldü; B17 bağımsız colored arena cihaz testi bekliyor | Hayır; gerçek iOS karakter yetenekleri ve durum geçişleri tamamlanmadı |
| Performans/render | C yazılım **480×272 rasterizasyon**, yazılımla dokulu üçgenler + `SDL_UpdateTexture` ile SDL2 görüntü sunumu. vitaGL linker bağımlılığı, mevcut 3D çizim kodunun glDraw* kullandığı anlamına **gelmez**. B10 real Vita daha önce ~20 FPS, UP ~29 ms ölçüldü; VSync ON/OFF benzerdi. | Hayır; ölçekli map ve düşmanlı sahnelerden önce gerçek GPU 3D A/B şart |
| Orijinal mekan | `C1L1` adlı 10 görünür model kaynağı, **22.919** doğrulanmış üçgen/370 submesh ve ayrıca collision/sky/floor modelleri. 39 özgün texture referansı, 42 PNG dönüşümü; ilk araç GLB'leri dokulu. | Hayır; çoğu shader/material, scene instancing, spawn/collision çözülmedi |
| Görev yapısı | Orijinal `clev` arşivinde **10** `level1..10.bclara` kaydı, schema'da Mission/Objective/NextMission/SpawnPoint/OnStart/OnComplete/OnFail vs. | Hayır; obje/instance ve görev akışı çözülmedi |
| Kampanya sayısı | 2010 Macworld incelemesi, Gameloft orijinal tanıtımı ve Pocket Gamer dönemin ilanı oyunu **9 oynanabilir bölüm/konum** olarak tanımlıyor. `10 .bclara` ≠ `10 oynanabilir bölüm` ispatı. | Onuncu config belirsiz |
| Ses/seslendirme | 2010 iOS review'leri oyundaki **voice acting/diyalog** varlığını doğruluyor. Orijinal tanıtım rock/metal soundtrack ve klasik “Iron Man” kaydını anıyor. | **Ses arşivinin dosya formatı, codec'i, sayısı, kaynakları, voice event mapping HENÜZ DENETLENMEDİ** |
| Sinematik | Hikâye/diyalog olduğu biliniyor; **önceden render edilmiş video, engine içinde canlı cutscene ya da diyalog overlay** ayrımı orijinal IPA üzerinde henüz yapılmadı. | Dosya türü, script/timeline/camera/audio eşleşmeleri bilinmiyor |
| Oyun sistemi | Prototip combat HUD/3D sphere hit, cooldown, wave; orijinal oyunun hedefleme/AI/equipment/program state'i geri kazanılmadı. | Hayır |

**Platform ayrımı:** Kamuya açık PS3/360 Iron Man 2 incelemelerindeki cutscene, voice cast ve silah sistemi **Gameloft iOS oyununun doğrulanmış kanıtı değildir**.

## Teknik grafik kararı (kritik yol)
Mevcut renderer `src/renderer.c`: `render_triangle()` + CPU `uint32_t pixels[480*272]`; `src/main.c`: `SDL_UpdateTexture()`, `SDL_RenderCopy()`, `SDL_RenderPresent()`. Build, SDL2/VitaGL kitaplıklarını link edebilir, ama sahneyi GPU 3D API ile doğrudan çizmez. VitaGL, sceGxm için OpenGL sarmalayıcısıdır (https://github.com/Rinnegatamante/vitaGL); Vita SDL2 backends için platform belgesi (https://wiki.libsdl.org/SDL2/README-vita). **Karar:** B19'da küçük bir orijinal zırh + C1L1 environment slice ile GPU geometry/texturing, alpha, UV, depth, shader, performance A/B. Grafik yolu karara bağlanmadan tüm C1L1 görünür modellerini CPU raster'e aktarma. Target ilk aşamada stabil >=25–30 FPS değerlendirme, kesin başarı garantisi değil. Cihazdaki AN/CPU/UP/COPY/PRES metriklerini izle; ekran sunum kaynaklı bloklamayı shader sorunu sanma.

## Seslerin tamamını kapsayan ilk araştırma (B18, yarın da cihaz olmadan yapılabilir)
1. Tam özgün IPA erişilebildiğinde **salt-okunur** `Payload/IronMan2.app/` kaynak envanteri: üst düzey dosyalar, isimli arşivlerin format/magic/index yapıları, olası audio/video/speech/localization dosyaları; 1.0.0 ve 1.0.3'ü dosya hash ile karşılaştır. **Şu anki GitHub deposu tam IPA'yı saklamıyor; ses biçimi/sayısı hakkında varsayım yapma.**
2. Oyun içi sesleri ayır: (a) menü/HUD sesleri, (b) UI, (c) repulsor, Unibeam, missile, minigun, melee, hit, engine/thruster/air, (d) düşman/hit/death/boss, (e) dünya/ambient, (f) müzik, (g) karakter voice/dialogue, (h) cutscene soundtrack/audio. Her kaynak: IPA dosya yolu, boyut, metadata, codec/container **kanıtla**, kanal örnekleme, süre, loop, referans edilen görev/event, oynatılabilirlik durumu, SHA256.
3. Her bulunan orijinal dosyanın PCM/OGG/MP3/ADPCM vb. olduğunu **header/decoder ile doğrulamadan iddia etme**. Önce ffprobe/araçsız magic signature; gerekiyorsa kendi arşiv indeks parser'ı, sonra yalnızca doğrulanmış codec'leri Vita uyumlu kayıpsız/uygun bir taşıma formatına dönüştür. Kaynak gizliliği ve müzik/seslendirme lisansları korunmalı.
4. PS Vita ses motoru: SDL2 audio veya Vita native `sceAudioOut` tabanlı ses oynatımı, kanallar, öncelik, 3D attenuation, müzik/voice/SFX üç ayrı bus, streaming/bellek, loop ve pause/mute, gecikme/mixer profil testleri. B20 minimum demo iki orijinal efekt + bir müzik döngüsü; bir önceki B15 kurulumuna dokunmadan.
5. Dialog kaynaklarını `speaker_id -> voice asset -> subtitle id -> scene event/time` olarak çıkar. Lip-sync/face animation yalnızca **orijinal kaynak rig/track** bulunursa; bulunmazsa karakterin yüzüne rastgele ağız animasyonu uydurmadan orijinal nişan/konuşma kamera ve altyazı akışını kurtar. Baştan beri seslerin dosya yapısı bilinmediğinden teknik başarı garantisi verme.

## Cutscene seçenekleri ve doğrulama kapısı
- **FMV çıkarsa:** görüntü codec/container tanı, ses senkronizasyonu ve decode maliyeti, Vita'da desteklenen yola dönüşüm veya meşru kişisel kullanım için yerel kaynaktan dönüştürme; başlat/pause/skip, altyazı.
- **Gerçek zamanlı engine sahnesi çıkarsa:** özgün `bclara`/sahne kamera yollarını, karakter transform animasyonlarını, sahne nesnelerini, diyalog/voice event zamanlarını ve geçiş/atlama durumunu çöz. Tek başına orijinal animasyon klibi olması, cutscene timeline çözüldü demek değildir.
- **Hibritse:** bölüm giriş/çıkış, ara radyo konuşmaları, QTE, video ve runtime sahnelerini aynı event timeline ile sırala.
- Kayıt/skip/retry sırasında görevin durumu bozulmamalı; cutscene sonundaki kontrol tekrar oyuncuya dönmeli.

## 15 kilometre taşı (B18–B32), ideal senaryoda
| Aşama | Çıktı / teknik hedef | Bitiş ölçütü ve bağımlılık |
|---|---|---|
| **B18** | **Kaynak envanteri:** tüm ses, diyalog, sinematik adayları + `clev` 10 kaydın ilk instance/isim eşleşmeleri (araştırma, VPK şart değil) | IPA hash/format/magic/manifest, varsayım vs doğrulama ayrılmış; en az ilk görev referansı |
| **B19** | **GPU performans prototipi:** native VitaGL/sceGxm karşılaştırması, gerçek shader/material/texture/depth, orijinal küçük level slice | Cihazda B17'ye göre aynı kamera/sahne A/B, kararlı çalışma ve frame time ölçümü |
| **B20** | **İlk sesli Vita demo:** 2–3 gerçek SFX + 1 döngü müzik, thruster/repulsor tetikleme | Cihazda stereo/mix/loop, pause/volume, kontrolsüz bellek artışı yok |
| **B21** | **Gerçek hareket ve yakın dövüş:** orijinal `Combo_1/2/3`, Air attacks, Throw; War Machine neutral walk/fly/RUSH güvenli retarget | Tam skinned clip, üst-gövde/alt-gövde çakışmasız, gözle ve temel unit testle doğrulanmış |
| **B22** | **Doğru silahlar:** Unibeam göğüs, Repulsor eller, WM Gun01..04 gerçek socket haritası, füze/tracer/çarpışma, karakter-yeteneği sistemi | Silah ve projectile farklı çıkışlar; orijinal IPA'dan doğrulanan özellik matrisi |
| **B23** | **Düşman/boss temel motoru:** özgün düşman rig/animasyon, AI state, hp/damage/projectile, hit reaction, melee & ranged | Tek özgün düşman tipiyle baştan sona çatışma; gerçek düşman animasyonu; sistem testleri |
| **B24** | **Orijinal C1L1 görünür ortamı:** ölçülmüş LOD, materyaller/lightmaps, world spawn/collision ve kameranın çevreyle ilişkisi | Gerçek dünya zemininde hareket/uçuş, collision ve hedef koordinatları tutarlı |
| **B25** | **İlk gerçek görev dikey dilimi:** özgün `OnStart/Objective/OnComplete/OnFail`, AI, reward/checkpoint, level geçişi | **Görev 1 başlangıçtan sonuç ekranına gerçekten oynanabilir**, sessiz olmayan temel sesli sürüm |
| **B26** | **Karakter voice/dialogue + ambient & müzik:** event/voice/subtitle map, tetikleme, speaker/channel priority | En az ilk bölüm diyalogları ve müzikleri ses taşıması/timing doğrulanarak çalışır |
| **B27** | **Cutscene oynatıcı:** FMV/engine/hybrid format kararı; intro/outro, altyazı, skip/pause, kamera | İlk bölümün intro+outro sinematikleri gerçek varlıklarla senkron |
| **B28** | **Oynanabilir bölümler 2–3** | Her bölüm ayrı checkpoint, boss/puzzle, objective ve video/audio kontrolü |
| **B29** | **Oynanabilir bölümler 4–6** | Aynı tamamlama kapısı; sorunlu özel mekanikler ayrı regression test |
| **B30** | **Oynanabilir bölümler 7–9** (orijinal 9-bölüm kanıtı doğrultusunda) | 9/9 orijinal oynanış, ayrıca level10 config'in rolü açıklanmış |
| **B31** | **Tam kampanya sistemi:** ana menü, seçim, armor upgrades/unlocks, kayıt/yükleme, retry, HUD/options/credits | Tam sıfırdan bitirme, ara kayıttan güvenli dönüş, bölümlerin doğru sırayla açılması |
| **B32** | **Tamamlanma için stabilizasyon:** frame pacing, ses/cutscene desync, RAM, uzun süreli test, final doğruluk tablosu | Hepsi Vita'da regression/soak testten geçer; sonra RC1–RC3 çıkabilir |

**Önemli:** B23/B24 ve B26/B27 gerekirse paralel geliştirilir. 15 satır iş büyüklüklerinin eşit olduğu iddiası DEĞİLDİR. Her yeni ses/mission türü, beklenmeyen shader/codec engeli ilave sprint yaratabilir. Kritik hatalar olmadan **tahmini 15 aşama + 1–3 RC**, kritik engeller olursa sayı önceden garanti edilemez.

## Test/paketleme stratejisi ve GitHub bildirim gürültüsü
- Kullanıcı şu anda konsol test edemiyor. **B17 cihaz raporu gelmeden B18 ve sonraki numarayla gereksiz VPK DERLEME.** Kaynak taraması/plan/çoklu native regression GitHub'da research-only, maliyeti düşük tutulmalı.
- Her beta **cihazda bir kazanım** sunmalı. 15 milestone 15 ayrı indirilecek .vpk değildir. Aynı commit içinde soru çöz/derle/güncelle; ardışık kırmızı GitHub Actions pushlarını engellemek için statik/lokal kontrolleri CI öncesi çalıştır.
- Kullanıcının istediği dağıtım: **doğrudan `.vpk` linki**, isim, MB, TITLE_ID, zırh/animasyon sayısı; ayrıca GitHub successful workflow yedeği. Aynı TitleID sadece bilinçli sürüm yükseltmede; B15 rollback ayrı kalmalı.
- Cihaz testi sonrası gerekli minimum B17 ölçümü: Mark VI/WM ground idle+walk+run, FLIGHT stage1/2/3, Unibeam chest socket and missile anchor, floor/collision depth, AN/CPU/UP/COPY/PRES/FPS. Kullanıcının güvenilir B15 kontrolleri korunmalı.
- Test kapıları: reproducing source -> native Debug+ASan+UBSan -> assets/hash/ZIP/SFO title-id -> VitaSDK build -> gerçek Vita scenario -> yeni proje handoff. GitHub Actions yeşil ≠ Vita FPS doğru.

## Tamamlama tanımı (oyun 'bitti' demeden önce)
1. Orijinal iOS sürümünde belgelenen tüm **9 oynanabilir bölüm** boyunca oyuncu başlatır, objective ilerletir, kazanır/kaybeder, retry eder, kayıt alır/geri yükler.
2. Doğru karakter seçimleri, özgün kabiliyet/upgrade kuralları (kanıtı bulunabilen her özellik), oyuncu ve düşman animasyonları, boss/QTE/nesne etkileşimleri çalışır.
3. Bölüm müzikleri, efektler, özgün voice diyalogları ve doğrulanmış ara sahne biçimleri eksiksiz/uygun şekilde senkron çalınır. Yoksa 'tam restoration' değil 'oynanabilir demake' diye adlandır.
4. Cihaz kararlılığı/performansı dürüstçe raporlanır, açılış-dönüş-kapanışta crash/memory leak olmamalı. Hedef kullanılabilir kararlı FPS, veri toplamadan 30 veya 60 garanti edilmez.
5. Orijinal IPA dosyalarını ve lisanslı şarkı/seslendirmeleri gizli tut. Dışarıya dağıtım ile kişisel orijinal IPA'dan yeniden oluşturma arasında telif/lisans farkları vardır.

## Harici 2010 iOS-only kanıt
- Macworld, 21 May 2010: dokuz oyun bölümü, flying/checkpoints/timed/puzzle: https://www.macworld.com/article/205532/ironman2review.html
- Gameloft orijinal iPad tanıtım açıklaması: dokuz bölge, rock/metal soundtrack ve “Iron Man”: https://gamefaqs.gamespot.com/iphone/601312-iron-man-2/data
- Pocket Gamer, Apr 26 2010: nine stages: https://www.pocketgamer.com/iron-man-2/iron-man-2-rockets-onto-iphone-app-store-except-in-the-us-germany-and-austria/
- Guardian 2010 iPhone incelemesi: seslendirmeler: https://www.theguardian.com/technology/gamesblog/2010/jun/02/iron-man-2-iphone-game-review
- TouchArcade 2010 iOS: spoken dialogue/voice acting: https://toucharcade.com/2010/05/04/iron-man-2-arrives-on-us-app-store/
- vitaGL OpenGL wrapper / native GPU: https://github.com/Rinnegatamante/vitaGL


## B18 erken çalışma — özgün kod API'leri bulundu (13 Ekim 2026)
- Tam `B15_NATIVE_10760_SYMBOLS.csv` arşivi **read-only** açılarak 10.760 orijinal Mach-O C++ sembolü üzerinde tarama yapıldı. Kanıt belgesi: `research/B18_AUDIO_CINEMATIC_NATIVE_SYMBOL_AUDIT.md`.
- **Ses:** `SoundManager::PlaySFX/PlayMusic/SetSFXVolume/SetMusicVolume/PlayRandomSFX/Stop/Pause/Resume`, `SoundPlayer::LoadSound`, `MainCharacter::PlayAttackSound` özgün fonksiyonları bulundu. Sound ID tabloları, codec ve ses kaynakları henüz bilinmiyor.
- **Sinematik:** `GamePlayUI::StartCutscene/UpdateCutscene/RenderCutscene/EndCutscene`, `GS_GamePlay::EnterCinematic/SkipCinematic`, `CameraPath::BuildSpline/GetInterpolatedPosInSplineByTime` özgün fonksiyonları bulundu. **Ara sahnenin FMV mi yoksa canlı 3D mi olduğu hâlâ belirsiz.**
- **Görev:** `MissionMgr::SetCurrentMission/SaveLoad/OnAllMissionComleted`, `IMissionCondition::EvaluateComplete/EvaluateFail`, `checkpoint::CMissionCommand::DoCmd/UnDoCmd` sembolleri var. BCLARA gerçek instance değerleri henüz çözülmedi.
- **Yeni test edilmiş okuyucu:** `research/b18/ipa_media_inventory.py` yalnızca kullanıcının kendi orijinal IPA ZIP girişlerinin dosya adını, boyutunu, SHA-256 değerini, 64 bayt imzasını ve video/ses/altyazı adayı sınıfını CSV+JSON olarak listeler; varsa 1.0.0 ve 1.0.3 dosya farklarını verir. Python 3 stdlib, sentetik 4 dosyalı IPA ile çalıştırılıp test edildi. Gerçek oyun sesleri henüz **sayılmadı, çıkarılmadı, dönüştürülmedi**, bu nedenle B18 tamamlanmış sayılamaz.
- Kullanıcının önceki orijinal 248/275 MB IPA dosyaları şu anda GitHub deposunda mevcut değil; bağlı Drive aranmasına rağmen bulunamadı. Tam ses/cutscene sayımı için gerçek dosya veya erişilebilir bağlantı gerekiyor.
- Bu araştırma için yeni VPK, VitaSDK build veya GitHub Actions job başlatılmadı.
