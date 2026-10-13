# B18 — Orijinal Iron Man 2 iOS (2010) Ses, Cutscene ve Görev Kodu: Yerel Sembol Kanıtları

**Araştırma tarihi:** 13.10.2026. **Kaynak:** `research/B15_Original_All_Mechanics_Audit.zip` içindeki `B15_NATIVE_10760_SYMBOLS.csv` ve `B15_MAIN_CHARACTER_METHODS.md`. ZIP, GitHub'dan read-only indirilmeden base64 + DEFLATE ayrıştırılarak orijinal demangle C++ listesi sorgulandı. Özgün kullanıcı IPA'sının 2010 ARM Mach-O ikilisinden önceki aşamada çıkarılmış **10.760 unique native symbol** bulunmaktadır. **Bunlar C++ fonksiyon isimleri; fonksiyon gövdeleri, ses dosyaları veya oynatılabilir cutscene'ler değildir.**

## 1. Ses sistemi artık yalnızca 2010 incelemeleri üzerinden varsayılmıyor

Aşağıdaki orijinal C++ demangled kayıtları doğrudan var:
- `SoundManager::InitAllSound()`, `SoundManager::Init()`, `SoundManager::Update(unsigned int)`, `SoundManager::Suspend()`, `SoundManager::Resume()`, `SoundManager::Reset()`.
- `SoundManager::PlaySFX(int, bool, float, bool)`, `SoundManager::PlayRandomSFX(int const*, int, bool, float)`, `SoundManager::PlayRandomSFX(bool, float, int, ...)`, `SoundManager::StopSFX(int, float)`, `SoundManager::StopAllSFX(float)`.
- `SoundManager::PlayMusic(int, bool, float)`, `SoundManager::StopMusic(int, float)`, `SoundManager::StopAllMusic(float)`, `SoundManager::PauseAllMusic()`, `SoundManager::ResumeAllMusic()`, `SoundManager::DisableMusic(bool)`.
- `SoundManager::PauseAllSFX()`, `SoundManager::ResumeAllSFX()`, `SoundManager::SetSFXVolume(float)`, `SoundManager::SetMusicVolume(float)`, `SoundManager::IsPlaying(int)`.
- `SoundPlayer::LoadSound(char*, int, int, vox::VoxSouceLoadingFlags)` ve `SoundPlayer::ResetDataHandle(int)`.
- `MainCharacter::PlayAttackSound(int, int)`.

**Güvenle çıkarım:** Orijinal oyun SFX ve müzik için iki ayrı yönetilen kanal/grup kullanıyor; load, play, stop, pause, resume, volume, saldırı sfx, rastgele sfx ve mümkün fade argümanları bulunuyor. **Belirsiz:** integer ID değerleri, gerçek .sfx/.wav/.ogg türleri, soundtrack sayısı, sesler tekil kayıtlarda mı yoksa ses bankasında mı, karakter diyaloglarında kimin konuştuğu, true 3D audio veya mixer uygulaması, codec. `vox::VoxSouceLoadingFlags` yalnızca bir tür adı; veri dosyasının uzantısının `.vox` olduğunu **kanıtlamaz**.

## 2. Sinematik çalıştırma + kontrol işlevleri doğrulandı

Orijinal ikili üzerindeki semboller:
- `GamePlayUI::StartCutscene(int)`
- `GamePlayUI::UpdateCutscene(int)`
- `GamePlayUI::RenderCutscene()`
- `GamePlayUI::EndCutscene(int)`
- `GS_GamePlay::EnterCinematic()`
- `GS_GamePlay::SkipCinematic()`
- `CameraPath::BuildSpline()`, `CameraPath::StartLinearInterpolation(int)`, `CameraPath::GetInterpolatedPosInSplineByTime(...)`, `CameraPath::GetInterpolatedPosInSplineBySpeed(...)`.
- `CameraSource::GetCameraPath()`, `CameraPathEntity::BuildCameraPath(...)`, `CameraWayPointMgr::UpdateCameraPathEntity()`.

**Güvenle çıkarım:** Motorun bir gameplay cutscene/cinematic durum yönetimi var ve kamera yolları spline/interpolation destekliyor; geçiş, render/update ve skip API'leri var. **Belirsiz:** cutscene önceden kodlanmış video mu, in-engine sahne mi, yoksa karma mı; hangi ses diyalog ve kamera yollarıyla eşleşiyor; her görevde kaç sekans var. `RenderCutscene` ismi kendi başına video codec veya motor içi animasyonun kesin kanıtı değildir. Asset manifesti ve cinematics call-site incelemesi zorunlu.

## 3. Görev yapısı, checkpoint ve kayıt

- `MissionMgr::SetCurrentMission(Mission*, bool)`
- `MissionMgr::OnAllMissionComleted()`, `MissionMgr::StartLevelCountdown(int)`, `MissionMgr::Pause()`, `MissionMgr::Resume()`, `MissionMgr::SaveLoad(checkpoint::IStream*)`.
- `IMissionCondition::EvaluateComplete(int)` ve `IMissionCondition::EvaluateFail(int)`.
- `checkpoint::CMissionCommand::DoCmd()`, `checkpoint::CMissionCommand::UnDoCmd()`, `checkpoint::CMissionCommand::GetId()`.
- `MainCharacter::SaveLoad(checkpoint::IStream*)`.

**Güvenle çıkarım:** Özgün oyun görev geçişi, koşul değerlendirme ve checkpoint/save mekanizmalarına sahip. Bunlar daha önce `clev` arşivinden doğrulanan `Mission`, `Objective`, `NextMission`, `OnStart/OnComplete/OnFail` stringleriyle tutarlı. **Belirsiz:** 10 `level*.bclara` kaydın her biri ayrı oynanabilir bölüm mü, orijinal görev grafının instance offset/ptr çözümü, kayıt dosyasının formatı, amaç sıralaması, spawner linkleri. Dönemin iOS incelemeleri **9 bölüm** bildiriyor; 10 dosya ≠ ispatlanmış 10 bölüm.

## 4. Doğru teknik araştırma sırası — Vita testi olmadan

1. Her iki kullanıcı IPA'sının özgün içeriğine erişip `Payload/IronMan2.app/` altında yalnızca **dosya isimleri, boyut, signature, SHA-256** bazlı medya taraması yap. Depodaki önceki kaynak ZIP'ler tam IPA yerine geçmez; hiçbir ses dosyası sayısı şu an açıklanamaz.
2. Orijinal ses banka/index yapısı tanınırsa yalnızca manifest kayıtlarıyla `sound_id → original pack + offset/length → decoded codec → native usage` bağla. `SoundManager::PlaySFX(int...)` ve `PlayMusic(int...)` ID'lerin sistemde bir rolü olduğu yönünde ipucu, ama ID tablosu henüz çıkarılmış değil.
3. `GamePlayUI::StartCutscene(int)` girişlerinin kayıt ID'lerini/asset referanslarını ve `CameraPathEntity` / `GS_GamePlay` olaylarını kaynak ikili ya da BCLARA üzerinden eşle. Video var diye varsayma.
4. Önce **küçük bağımsız ses prototipi** (tek özgün efekt, loop, pause/mute, volume), sonra voice/dialog ID ve camera timeline event; ardından görev başı/sırasında/sonu sinematik senkron.
5. Kaynak dosyaların tamamı ve lisanslı konuşmalar/müzikler gizli kullanıcı deposunda; orijinal varlıkların kamuya yeniden dağıtımı otomatik meşru değildir.

## 5. B18'in teslim ölçütü

Şu an B18 araştırma aşaması için **gerçek bir erken kilometre taşı**: hem ses hem cutscene hem görev yöneticisi kod tarafında adlarıyla tespit edildi. Fakat **B18 tamamlandı denemez**: gerçek IPA medya kaynak envanteri, codec tanıma ve ilk ses dönüştürme yapılmadı. Bu rapor yeni VPK üretmez ve GitHub Actions çalıştırmaz.

Kaynak kıyasları: `ROADMAP_AFTER_B17_2026-10-13.md`; `research/ORIGINAL_LEVEL_ARCHIVE_AUDIT.md`; `research/B15_Original_All_Mechanics_Audit.zip`. Repo özel kalmalı.
