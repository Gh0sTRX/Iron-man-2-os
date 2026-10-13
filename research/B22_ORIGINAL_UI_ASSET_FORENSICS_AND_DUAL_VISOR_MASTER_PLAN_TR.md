# Iron Man 2 (Gameloft iOS 2010) — Orijinal HUD Kanıtları, Gerçek Asset Durumu ve İki Ayrı Vizör Tasarımı
**13 Ekim 2026 · Özel depo · B17 cihaz testi hâlâ yapılmadı. Yeni VPK oluşturulmadı.**

## Gerçek sonuç: orijinal HUD kodunu bulduk, orijinal HUD görsellerini HENÜZ çıkarmadık
2010 orijinal ARM Mach-O'dan daha önce çıkarılmış **`research/B15_Original_All_Mechanics_Audit.zip / B15_NATIVE_10760_SYMBOLS.csv`** arşivinin 10.760 C++ sembolü bağımsız olarak yeniden açıldı ve arayüz sınıfları ayrıntılı tarandı.

### Gameplay UI — doğrudan kanıtlanan fonksiyonlar
| Gerçek özgün sembol | Kanıtladığı altyapı | Kaynak dosya henüz nerede? |
|---|---|---|
| `GamePlayUI::DrawMCArmorAndHP()` | Ana karakter zırh/HP gösterimi | İlgili bitmap/atlas **bulunmadı** |
| `GamePlayUI::DrawMinimap()` | Mini harita render yolu | Minimap ikonu/harita kaplaması **bulunmadı** |
| `GamePlayUI::SetMsgText(char*,int)`, `RenderMsgText(int,int)` | Oyun mesajları/yazı UI | Özgün font/sprite **bulunmadı** |
| `GamePlayUI::ShowHint(int,int)`, `DrawTutorial()` | Öğretici ve ipucu | Kaynak sprite **bulunmadı** |
| `GamePlayUI::DrawFullScreenInjuryMask()` | Hasar vignette/mask | Özgün kaplama **bulunmadı** |
| `GamePlayUI::DrawFullScreenAtmosphereMask()` | Ortama bağlı ekran maskesi | Özgün kaplama **bulunmadı** |
| `GamePlayUI::DrawAchievementUnlock()` | Başarım bildirimi | Gerçek grafik paketi **bulunmadı** |
| `GamePlayUI::DrawLensFlare()`, `SetBlackScreen`, `FadeIn` | Görsel efekt/UI geçişi | Efekt atlası **bulunmadı** |
| `MainCharacter::DrawUnibeamProgress(Sprite*)` | Unibeam charge UI'sı | Özgün Sprite ID/UV eşleşmesi **bulunmadı** |
| `GamePlayUI::StartCutscene/UpdateCutscene/RenderCutscene` | Sahneler arası arayüz yönetimi | Gerçek cutscene varlığı **bulunmadı** |
| `MissionMgr::FindMinimapObjects`, `IMissionCondition::AddEntityForMinimap` | Görev hedefleriyle ilişkili minimap veri altyapısı | Gerçek harita marker tipleri **bilinmiyor** |

### Menü / Flash / font sistemi — daha güçlü bulgular
- `MenuManager::LoadSWFFile(char const*,int)`: **SWF dosyası yükleme fonksiyonu mevcut**. Bu, sadece `gameswf` adını görmekten daha güçlü delildir. Ancak gerçek `.swf` arşiv girdisinin adı/formatı/konumu halen doğrulanmadı.
- `GSFlashMenu::SetTargetMenu(MenuBase*)`, `ReturnToGame(bool)`, `ReturnToMainMenu()`, `UnlockLevel()`, `SaveMcDataToFile(UpgradeSystem&)`.
- `MenuIronMan`, `MenuCircle`, `MenuCircleSmall`, `OptionMenu`, `UpgradeMenu`, `UpgradeSkillMenu`; özgün menü sınıflarının hepsi Show/Hide/Update girişlerini kapsıyor.
- `Sprite::PaintModule / PaintModule2`, `Font::Init(int,ASprite&,char*,...)`, `FontMgr::DrawString`. Bu çizim sistemleri **UI sprite atlası / font benzeri kaynaklara işaret ediyor**, ancak gerçek atlas dosya adı veya piksel dökümü yok.
- `gameswf::` aileleri kod içinde bulunuyor; sırf bu yüzden bütün ara sahnelerin Flash/SWF olduğunu söylemek yanlış.

### 2010 orijinal iPhone/iPad oynanış ekranlarında fiilen görülen
- **Mavi/cyan, eğimli üst-sol bar** ve görev başlığı, **alt-sol dairesel radar/joystick**, **sağ-alt yuvarlak saldırı/enerji düğmesi**.
- Firepower dövüşü iPad ekranında `Defeat Firepower` görev başlığı, üst sol HP/bar, alt sol dairesel kontrol, **düşman üzerinde parlak yeşil hedef halkası** var. Görsel kaynağı: https://media.pocketgamer.com/artwork/na-nih/iron-man-2-ipad_1.jpg ; makale: https://www.pocketgamer.com/iron-man-2-ipad/
- Orijinal iOS ekran görüntülerinde ek koruyucu border/filmdeki gibi tam kafa-içi retikül yok. 2010 tarihli iPad incelemesi “kaskın içinden Iron Man HUD kullanabilmeyi dilerdik” diye eleştiriyordu; bu da **vizör katmanımızın yeni bir Vita özelliği olduğunu** teyit eder. https://www.148apps.com/iron-man-2-ipad/iron-man-2-ipad-review/
- İkinci 2010 örnek: https://www.geeky-gadgets.com/iron-man-2-iphone-and-ipad-game-screenshots-21-04-2010/ (gerçek iOS oynanış ekranı; cyan bar / dairesel kontrol).

## Fiziksel dosya denetimi: bugüne kadar ne gerçekten elimizde?
- Aynı oturumda gerçek yerel `IronMan2_Mechanics_B15.vpk`, `IronMan2_Combat_B16_Expanded.vpk` ve `IronMan2_Arena_B17.vpk` ZIP merkez kayıtları açıldı. **B15 43 girdi, B16E ve B17 69 girdi**. B17: 5 `.im2t` model, 59 `.im2v` hareket, 3 `.im2m` maske, `eboot.bin`, `sce_sys/param.sfo`. **Hiçbir VPK'da bağımsız özgün SWF, PNG, TGA, PVR veya menü/HUD atlası yok.**
- Özel repo `research/B11_C1L1_Source_Parser.zip` (22 dosya), `research/B7_Skinning_Tools.zip` (11), `research/B15_Original_All_Mechanics_Audit.zip` (12), B6/B13 kaynak ZIP'leri tarandı: B11 örnek Mark VI GLB ve özgün *çevre* BDAE, B7/11 araştırma önizlemeleri mevcut. Bu paketlerde doğrulanmış ayrı 2010 HUD asset kaynağı yok. Bu, **orijinal IPA'da bulunmadığı** anlamına GELMEZ.
- Orijinal **248,613,763 B** ve **275,580,565 B** `.ipa` dosyalarının tamamı erişilebilir depoda değil. Dolayısıyla orijinal menü sprite atlaslarının toplam sayısı, SWF gerçek adları, görsellerin gerçek pikselleri, zırh ayrımlı HUD skin varlığı **şu an bilinmiyor**.
- Fiziksel arşivden elde edilmiş **orijinal HUD asset sayısı: doğrulanmış 0**. Orijinal UI'yi **oyun kaynak kodu fonksiyonları + 2010 ekran referansı düzeyinde** biliyoruz.

## Üç kipli / iki zırh temalı ama İKİ KATMANLI çözüm

**Katman 1: ORİJİNAL SADAKAT ÇEKİRDEĞİ** (her suit için aynı mantık): 2010 iOS screenshot referanslı konumlar; sol üst orijinal HP/armor UI, görev başlığı; sol alt minimap; sağ alt savaş widget/silah durumu; orijinal Unibeam progress, QTE, cutscene, hurt mask ve menüler **yalnız gerçek veri doğrulanınca** mümkünse aynen eşleştirilir. Var olan grafik kodu `research/b22_hud/b22_visor.c` yalnız çerçeve/renkleri **referans olarak** çizer; görsel olarak bire bir orijinal asset **değildir**.

**Katman 2: VITA VİZÖR KAPLAMASI** (suit'e özel, aç/kapat):
- **Iron Man**: mavi/cyan optik çizgiler, ince altın reaktör/enerji vurguları, az yer kaplayan sağ/sol telemetri; yeşil hedef kilidinden kaynak 2010 UI'yi korur, visor layer kilit rengi altın.
- **War Machine**: soğuk metalik/gri-yeşil + amber silah önceliği, daha düz/askerî panel, ammo ve roket/omuz hardpoint konumu. Mevcut oyun **WM'ye özgü tüm silahların sprite verisini doğrulamış değil**. War Machine ayrı original HUD'da farklıydı diye iddia etme.
- **Modlar:** `Original` = sade 2010 konum referanslı; `Hybrid` = birkaç ince vizör çizgisi ve sayaç; `Immersive` = vizör kenar izleri ve savaş telemetrisi. Hepsi aynı oyun istatistiklerini kullanır. İki suit için menü renkleri farklı ama menü ilerlemesi ve upgrade yetkisi kaynak oyunun kurallarına bağlı.
- HUD **3. kişi kamerayı 1. kişi görüşüne çevirmek zorunda değildir**. Vizör overlay tematik arayüzdür; oyun perspektifi B15/B17 gibi arkadan kalır.
- 480×272 Vita ekranında görüşün ortası, oyuncu silueti ve düşman görünümü kapatılmamalı. Hasar/enerji alarm renkleri anlamlı kalmalı. Her suit HUD'unda alarm aynı mantıksal tipte, renk eşlemesi okunaklı olmalı.
- Menü, pause/options, upgrade ve sonuç ekranları için aynı çekirdek durum tipleri var; **henüz orijinal SWF raster yükleme, gerçek font, menü ikonları, save/load ve audio mute entegrasyonu YOK**.

## Hazırlanmış bilgisayarda test edilmiş C11 çekirdek
Özel repo `research/b22_hud/`:
- `b22_visor.[ch]`: RGB 0x00RRGGBB CPU overlay, source-layout fallback, Iron Man/WM paletleri, üç HUD modu, lock-on kenarlıkları, damage warning, mission/pause/main-menu/upgrade/results panel iskeleti.
- `test_b22_visor.c`: Linux GCC `-std=c11 -Wall -Wextra -Werror -pedantic -O1 -g -fsanitize=address,undefined` ile **başarılı**. Orijinal yerleşimin iki suit için aynı veriyi çizmesi, suit renklerinin ayrılması, 3 kip, merkez görüş alanı, boundary guard, NaN/INF input, pause/menu ekranları ve 200 deterministik sınırlama testi. **VitaSDK ve gerçek FPS test edilmedi**. Orijinal texture ya da arayüz çözümü olarak sunulmaz.
- `original_ui_asset_probe.py` ve `test_original_ui_asset_probe.py`: gerçek IPA geldiğinde entry path/extension ve `FWS/CWS/ZWS` SWF magic header'larını, blob içine gömülü olabilecek header adaylarını, offsets ile kayıt altına alır. **Ürettiği şey asset manifest CSV/JSON, orijinal grafik değil.** Yalnız sentetik IPA testleri **2/2 başarılı**; gerçek IPA üzerinde henüz çalıştırılmadı. Yanlış pozitif imkânını raporlar.

## Gerçek orijinal grafikleri kurtarma sırası
1. Kullanıcının private kaynak IPA dosyalarını erişilebilir hale getir; **önce tüm ZIP dosya adları/magic/size/SHA**, `UI_ASSET_CANDIDATES.csv` üret ve bariz `.swf/.gfx/.pvr/.tga/.png` dosyaları tanı.
2. Gerçek `MenuManager::LoadSWFFile` kaynak arşiv ve dosya referansını bul; aynı `Sprite::PaintModule` atlas indeksleri, `Font/ASprite` font katmanı; sürüm 1.0.0/1.0.3 farklarını doğrula. SWF dosya isimlerini tahmin ederek kodlama.
3. Video/2010 ekranlarıyla elementlerin **orijinal ekran koordinatları** karşılaştır, bar renkleri ve pozisyonları video frame bazında ölç. Pixel-perfect orijinal mod başarı kapısını uygula; bu aşamadan önce 'Original' sadece layout approximation.
4. Iron Man / War Machine oyun içi gerçekten ayrı orijinal HUD grafik skinine sahip mi? Kaynak dosya/ID veya screenshot kanıtlanana kadar bunu bilinmeyen olarak tut. Suit'e özel vizör **bizim seçtiğimiz Vita uzantısıdır**.
5. B17 gerçek cihaz QA'dan sonra B21 input & B19 HP/energy/mission state'ini bu HUD'a bağla. GPU/sahne profili, metin fontu, SWF kullanımı için Vita raster alternatifi ve alfa blending performansını ayrı ölç. Sonra tek anlamlı yeni VPK.

**Sonuç:** `Orijinal gameplay UI veri düzenini doğruladık; orijinal HUD görsel asset dosyalarını henüz çıkarmadık.` Bu ayrım korunmalı.
