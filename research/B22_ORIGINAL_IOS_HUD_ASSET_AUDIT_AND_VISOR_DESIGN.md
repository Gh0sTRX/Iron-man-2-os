# Iron Man 2 iOS → PS Vita — B22 HUD kaynak denetimi ve iki vizör teması
**Tarih:** 2026-10-13. **Durum:** kaynak araştırması + bilgisayar üzerinde test edilmiş HUD çekirdeği, gerçek Vita B17 testini bekliyor. Yeni VPK yok.

## Tasarım kuralı: iki ayrı katman, üç gösterim modu
**Katman A — orijinal Gameloft işlevleri:** Zırh ve HP, mini harita, Unibeam dolum, görev/etkileşim ipuçları, hasar ve atmosfer maskeleri, achievement popup, ana menü, zırh/upgrade ve minigame ekranları. 2010 iOS HUD yerleşimi ile karşılaştırılacak. **Kaynak görselleri hâlâ kurtarılmış değil.**
**Katman B — kullanıcı isteğine göre Vita vizörü:** Üçüncü şahıs oynanışını kapatmayan köşe çizgileri, hedef kilidi, tehdit uyarısı, enerji, mühimmat, özel saldırı hazır durumu. **Iron Man** cyan/beyaz/reaktör odaklı, **War Machine** gri/amber/askerî taktik. Her iki tema aynı oyun verisini kullanır; model/eylem değişikliğine göre sadece görünüm değişir.

Modlar: (1) Original Layout — yalnız A; (2) Hybrid — A + hafif B; (3) Immersive — A + genişletilmiş ama oynanışı engellemeyen B. İki katmanın ayrılması performans, kontrol, aynı HUD bilgisinin tekrar çizilmemesi ve kaynak sadakati için önemlidir.

## Özgün 2010 Gameloft iOS kodundan yeni doğrudan kanıt
Kaynak özel repo: research/B15_Original_All_Mechanics_Audit.zip içerisindeki B15_NATIVE_10760_SYMBOLS.csv, orijinal iOS Mach-O ikilisinden çıkarılmış 10.760 demangle C++ sembolü. Bunlar **orijinal atlas dosyasının kendisi veya fonksiyon gövdesi değildir**.

| Doğrulanan sembol | UI özelliği |
|---|---|
| GamePlayUI::DrawMCArmorAndHP() | Özgün zırh/can gösterimi |
| GamePlayUI::DrawMinimap() | Mini harita |
| MainCharacter::DrawUnibeamProgress(Sprite*) | Unibeam dolum göstergesi |
| GamePlayUI::DrawFullScreenInjuryMask() | Hasar ekran efekti |
| GamePlayUI::DrawFullScreenAtmosphereMask() | Ortama bağlı ekran kaplaması (su altına özgü olduğu kesin değil) |
| GamePlayUI::DrawLensFlare() | Lens flare |
| GamePlayUI::ShowHint(), DrawTutorial(), SetMsgText(), RenderMsgText() | Görev/rehber/durum mesajları |
| GamePlayUI::DrawAchievementUnlock() | Başarım bildirimi |
| GamePlayUI::RenderCutscene(), DrawBlackScreen() | Sahneler arası/cinematic HUD katmanı |
| MissionMgr::FindMinimapObjects(), MissionConditionKill/Gate/Collect/Protect/ToPosition::AddEntityForMinimap() | Harita görev işaretleri |
| MenuManager::LoadSWFFile(char const*,int), MenuManager::OnFSCommand() | SWF menü yükleyici + menü olay köprüsü |
| GSFlashMenu::ReturnToGame(), ReturnToMainMenu(), SetTargetMenu() | Oyun ve menü geçişi |
| MenuIronMan, MenuCircle, MenuCircleSmall, OptionMenu, UpgradeMenu, UpgradeSkillMenu | Ayrı menü/zırh/yükseltme bileşenleri |
| Font::Init(int, ASprite&, ...), FontMgr::DrawString(), Sprite::PaintModule(), Button::InitGfx() | Sprite/font/button çizim altyapısı |

Bunlar özgün sistemlerin varlığını kanıtlıyor; gerçek görsel, renk, koordinat, ses, SWF isimleri ve UI atlası **henüz bulunmuş değil**.

## Gerçek dosya/açık arşiv envanteri
ZIP dizinleri ayrıca denetlendi:
- **B15 VPK:** 43 giriş = 36 .im2v, 5 .im2t, eboot + SFO; **ayrı menü/HUD SWF/PNG/atlas yok.**
- **B16 Expanded VPK:** 69 giriş = 59 .im2v, 5 .im2t, 3 .im2m, eboot + SFO; **ayrı menü/HUD varlığı yok.**
- **B17 VPK:** aynı 69 girişli içerik sınıfları; **ayrı menü/HUD varlığı yok.**
- Özel repo B11_C1L1_Source_Parser.zip, B7_Skinning_Tools.zip, B15_Original_All_Mechanics_Audit.zip ve B6_Animation_Decoder_Runtime.zip dizinleri tarandı: çevre BDAE, zırh/animasyon araçları, kod sembolleri var, fakat kaynağı doğrulanmış özgün UI SWF/atlası yok.
- Kullanıcının gerçek 248.6 MB ve 275.6 MB özgün IPA dosyaları erişilebilir depoda yok. **Orijinal HUD asset sayısı ve gerçek formatı bu nedenle bilinmiyor.**
- Kaynak oyundaki HUD'un yokluğu değil, **bizim private snapshot'ımızın eksikliği** söz konusu.

## Doğrulanmış platform farkı
2010 tarihli iPad 148Apps incelemesi, oyuncunun kask içindeki interaktif HUD'u kullanamamasını oyunun eksik yanı olarak değerlendirmişti: https://www.148apps.com/iron-man-2-ipad/iron-man-2-ipad-review/ . Bu nedenle yeni tam vizör modu **Vita için bilinçli görsel geliştirmedir**, özgün iOS render'ı diye etiketlenmemelidir. 2010 Gameloft gerçek trailer: https://www.youtube.com/watch?v=mU4aao60sUQ . Video düzeni ve kaynak asset dokuları ayrıca karşılaştırılacaktır.

## B22 host C test sonucu — birebir doğrulanan commit içeriği
Kaynak: research/b22_hud/b22_visor.h, b22_visor.c, test_b22_visor.c.
- 480×272 RGB framebuffer; klasik katman, cyan Iron Man ve askerî amber War Machine modları, Original/Hybrid/Immersive, pause/main/upgrade/results ekranlarının çizim iskeletleri, hedef kilidi ve HUD barları.
- **Ubuntu/Linux host GCC C11 ile başarıyla derlendi**: -Wall -Wextra -Werror -pedantic -O1 -g -fsanitize=address,undefined. ASAN_OPTIONS=detect_leaks=1 çalıştırıldı ve PASS çıktı.
- Mod/test: her iki zırhta classic aynı, vizör rengi farklı, 5 UI ekranı, ekran taşmalarının kesilmesi, NaN/Inf girişleri, 200 tekrarlanan varyasyon, guard sentinel kontrolü.
- GitHub blob SHA içerikleri **test edilen birebir C dosyalarıyla eşit**: header 6cd8206f20a60124631873c765971c3d63b82be3, renderer ffc380a76ad0993df1d4ea9334433ff29bc98c8f, tests 19fceb0b7ca74837a42e304785d555c25bb0b2b3.
- **Sınırlar:** Bu kaynaklar henüz B17 renderer oyun döngüsüne, gerçek Vita GPU'ya, orijinal font ikonlarına veya gerçek pause/SFX motoruna bağlanmamıştır; görsel elementler soyut çizimlerdir. Target HP/ammo/mission metni oyun içi arayüzün tamamlanması için ayrıca uygulanmalı.

## Sıradaki kaynak çıkarma adımları
1. IPA geldikten sonra read-only medya + UI scanner ile Payload/IronMan2.app içindeki gerçek SWF/font/sprite/texture dosyaları, arşivler ve imzaları envanterle.
2. MenuManager::LoadSWFFile yolunu gerçek SWF referansına eşleştir. SWF'nin Vita'da native oynatılacağı **varsayılmamalı**; gerekirse sprite/menü öğelerini kaynaklardan yeniden oluştur.
3. Font::Init(ASprite&) ve Sprite::PaintModule kullanımlarını özgün atlas rect'leriyle eşleştir; iOS menü ve oyun içi HUD'un ortak mı ayrı mı asset tuttuğunu kanıtla.
4. B17 test raporu gelince kaynak HUD işlevlerini B19 gameplay state ve B21 R-fire/L-lock/pause çekirdeğine tek kontrollü integrasyonda bağla. HUD'u 480×272 cihazda okunabilirlik ve performans bakımından test et.
5. Tam vizör ekranında oyun merkezini kapatma, üçüncü şahıs Iron Man/WM modellerini gizleme, özgün oyunda olmayan savaş yeteneklerini HUD var diye uydurma.

**Kritik ayrım:** Orijinal HUD'un program fonksiyonlarını bulduk; özgün UI asset byte'larını kurtardık demiyoruz. B22 çift tema prototipi çalışan host kodudur, henüz kurulan Vita oyunu değildir.
