# G140–G142 — Iron Man 2 (iOS 2010 1.0.0) özgün 803 ses, gerçek kaynak kimlikleri, Vita streaming

**17 Ekim 2026 / Gh0sTRX/Iron-man-2-os / feature/b24-unified-gameplay / YENİ VPK YOK.**

## Kullanıcı 1.0.0 Drive IPA erişimi: kota problemi aşıldı

Kullanıcı sürüm 1.0.0 IPA'nın kotayı aşmadan alınabileceğini hatırlattı. Daha önceki GitHub CI / gdown iki dosya ID'si **aynı** `IronMan2_1.0.0_ios_2.2.1.ipa` (248.613.763 bayt), eski download limiti sürüm 1.0.3 nedeniyle değil **gdown üzerinden anonim indirme kotası** nedeniyleydi. Google Drive bağlı oturumunun authenticated raw fetch yöntemiyle 1.0.0 **eksiksiz** alındı. SHA256 `4c338c71cdd2817afb10099b90834c911d3c82e94adc477f24a9f9f4e0479c94`. Özgün IPA/ARM executable **GitHub'a yüklenmedi** ve kullanıcıdan tekrar istenmedi.

2010 IPA'da toplam **803/803 gerçek RIFF WAVE ses** parse edildi: **111 `m_*` müzik, 160 `sfx_*` efekt, 532 `vfx_*` diyalog/seslendirme**. Codec sınıfları: **526 mono 32kHz 4bit IMA ADPCM, 121 stereo 32kHz 4bit IMA ADPCM, 119 mono 22.05kHz PCM16, 32 stereo 22.05kHz PCM16, 5 mono 16kHz PCM16**. 803 kaynak RIFF başlığı uyumlu, 0 rejected.

Birinci seviyede kaynağa göre `vfx_dialogue_level1_*` **47** konuşma, `vfx_briefing_level1_jarvis` **1**, `m_expo_*` **16**, `sfx_ambiance_expo*`/`sfx_expo_*` **5**; ilave seçilmiş gerçek kaynak birinci görev müzik/SFX ve gerçek native audio ID88/voice320/321 sesleriyle kullanıcıya **76 değişmemiş orijinal WAV** için 15.9MB özel ZIP verildi. Özgün `.www` uzantıları aslında RIFF WAVE, sadece uzantı `.wav` olarak düzeltiliyor. Müzik, konuşma ve silah etkileri için **sekiz** WAV dosyası offline FFmpeg ile **48kHz stereo PCM16 LE** olarak doğrulandı. Bu örneklerin hepsi **GERÇEK kaynağın yeniden kodlanmış ses örnekleri**, fabrikasyon veya sentetik ses değil. Bu tek başına gerçek Vita konsolda duyulur ses veya özgün görev içi playback kanıtlamaz.

Yerel doğrulama arşivi:
- `IronMan2_iOS_v1.0.0_G142_Level1_76_Original_WAV.zip` — 76 dosya, özel kullanıcı konuşma artifact'i.
- `G142_2010_ORIGINAL_803_AUDIO_ID_TO_WWW_FILENAME_NATIVE_SOURCE.json` — **803/803** ID ve orijinal IPAdaki dosya adlarının kontrolü. Bu içeriğin orijinal ses binary byte'ları GitHub'a commit edilmedi.
- `G142_full_803_audio_source_manifest.json`, WAV SHA256/RIFF codec tablosu.
- Kaynak repo çıkarma kodu `research/b24_unified/g140_owner_wav_audio/g140_extract_owner_original_2010_V100_audio_and_optional_103_difference_NO_VPK.py`; `--v100 original.ipa --out outdir [--v103 original_v103.ipa]` ile gerçek 1.0.3 IPA erişilebilirse byte-by-byte SHA fark raporu üretir. **1.0.3 ses hash karşılaştırması henüz yapılmadı**; eski animasyon çalışmasında 1.0.0 972 clip, 1.0.3 989 clip (17 yeni iPad/civilian) ve 972 ortak clip byte-identical. Bu animasyon bilgisi, seslerin de tamamen aynı olduğu anlamına gelmez.

## Kritik: gerçek kaynak 803 kayıtlı audio tablo ve ARM Lua mapping SONUNDA ÇÖZÜLDÜ

2010 özgün `Payload/IronMan2.app/IronMan2` **7.480.208 bayt Mach-O** içinde tam **803 × 40 bayt** kayıtlı orijinal ses adları tablosu ikiz şekilde duruyor:
- İlk kopya raw file offset **4663040 / original Mach-O VM 0x473700**, ikinci kopya raw file offset **4695160**; iki byte table **tamamen eş**, her kayıt null terminatörlü ve sabit stride40; 803/803 ad eşsiz ve **IPA'daki ses kayıtlarıyla %100 eşleşti**.
- Orijinal `BackgroundMusicPlayer::LoadMusic` ARM VM **0x155D9C**, `0x155E34 ldr` literal offset +`0x155E50 add pc` ile **gerçek 0x473700 tablo adresine** gidiyor; indeks `r5` üzerinden `8+32=40` stride hesaplanıyor, C++ `SoundPlayer::LoadSound` ile `IronMan2.app/%s.www` kaynak yolu oluşturuluyor. Bu ID eşlemesi yalnız sıralama tahmini değil native pointer referansı + IPA dosya envanteri doğrulamasıdır.
- `PlayMusic(lua_State*)` native **0x18000**, `0x1804C sub r1,r8,#1` -> `SoundManager::PlayMusic(int,bool,float)` **0x1431F0**. Dolayısıyla **ORIGINAL Level1 Lua `PlayMusic(88,true)`** = sıfır tabanlı kaynak ID87 = **`m_pre_cutscene_intro.www`**.
- `PlayVoice(lua_State*)` native **0x18A04** `0x18A4C`/ `0x18A78 sub r1,r5,#1` -> `Game::PlayVoice(int)` **0x976B0** -> `SoundManager::PlaySFX`. Original Level1 `PlayVoice(320)` => index319 => **`vfx_intro_level1_jarvis_1.www`**. Sonraki index320 => `vfx_intro_level1_tony_1.www` ID321, fakat bu 321 ID'nin çağrıldığı kesin bir Mission000 PC source event bu çalışmayla kanıtlanmadı.
- Native `Game::PlayVoice` Game+0xE4 son voice index ile aynıysa IsPlaying kontrolü, farklıysa eski voice StopSFX→yeni PlaySFX yapıyor. Ses atlama/yenileme mekaniği için bu native branch önemlidir.

## Önemli DÜZELTME: `PauseMusic()` global müzik pause / volume mute DEĞİL

Özgün `PauseMusic(lua_State*)` VM **0x17ECC** gerçek 2010 ARM komutları:
`Game::GetInstance` → `Game::StopCrtBGM(2000.f)` (PC literal `0x44FA0000` = exact IEEE-754 **2000.0**), Lua dönüş 0.
`Game::StopCrtBGM(float)` VM **0x97728**, **`ldr r1,[Game,#0xEC]`** mevcut kaynak BGM track index ve `SoundManager::StopMusic(index,fade)` native **0x142188** çağrısı.
`SoundManager::PauseAllMusic()` native **0x14213C** tamamen BAŞKA yöntem: VoxEngine::PauseAllEmitters groups 8 ve 2; `PauseMusic` Lua'sı bunu ÇAĞIRMIYOR. `StopMusic` named handler original VoxEngine emitter handles üzerinden stop eder; exact fade/time birimi 2000.0 parametre native kaynaktan kanıtlandı, ms olması makul fakat fonksiyon semantiğinin özel time scale'i henüz ayrı doğrulanmadı.

**G139 eskiden PC3'ü sadece Vita BGM port sesini 0 yapınca ACK EDİYORDU; BU KAYNAK SADIK DEĞİLDİ.** Şimdi `b24_g139_original_Mission000_audio_dispatch` ses port output helper'ının gerçekten çalışmasına rağmen PC3'ü **bilerek BLOKE EDİYOR**, çünkü orijinal [Game+0xEC] music track ID henüz çalışma sırasında doğrulanmadı/gerçek stop-fade playback bağlanmadı. SceAudio mute halen bağımsız native audio utility olabilir ama hiç bir biçimde authentic PauseMusic eventi sayılmaz.
Yeni `research/b24_unified/g142_original_2010_native_sound_id_semantics/b24_g142_native_sound_source_truth.[ch]` exact ID87/319, stop current indexed track with native literal 2000, full original source event PC3/PC62/PC70 callback gating C mantığı ve kaynak host testleri sunar. **Asıl ilk görev QTE PC6, tutorial ve MissionResume hâlâ aktif değil.**

## PS Vita ses motoru

- G139 gerçek `sceAudioOutOpenPort(BGM,512,48000,stereo)`, `sceAudioOutSetVolume`, native ARM compiled. Artık bu generic device mute = original PauseMusic demiyor.
- G141 **`sceAudioOutOutput`** çağıran **ayrı Vita kernel ses thread'i** ile diskten gerçek original WAV'den offline decode edilmiş 48k stereo S16LE PCM stream; pause/EOF/loop ve 2KiB 512-frame test host+Vita ARM **[G141 SUCCESS 39029573691](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39029573691)**. Bu PCM player source re-usable ve şimdi ID88 / voice320 dosya adları çözüldü. Fakat gerçek orijinal intro ID88 ve voice320 playback'nun görev scripti içindeki zamanlaması, ayrı VOICE output port ve fade emitter playback hâlâ eksik.
- G142 native original sound source C host + Vita ARM doğrulama CI: `.github/workflows/g142-original-2010-native-AudioID88-Voice320-PauseMusicStopCrtBGM-Vita-ARM-NO-VPK.yml`.
- Yeni `.vpk` üretme, kullanıcı her yeniden kurulumdan kaçınıyor; sadece kaynak/PCM decode/ELF backend testleri. 2010 IPA kullanıcıya ait, ASLA kaynaktaki telifli ses kayıtlarını genel depoya yükleme.

## Bundan sonraki source-faithful sıralama

1. G142 audio ID source table üreticisini tam oyunun native `B24` kaynaklarına opsiyonel gir; gerçek ID88 `m_pre_cutscene_intro` ve voice320 `vfx_intro_level1_jarvis_1` PCM assetlerini G141 Vita streamer üzerinden **orijinal sınıflarına göre** müzik/voice/SFX ayrı kanala bağla.
2. Native original Game `+0xEC` current BGM alanını gerçek mission intro kaynak akışıyla doğrula; PC3'te `StopCrtBGM(2000.f)` fading semantics. Kaynak değeri belli olmadan PC3'ü sırf mute yaptık diye geçirme.
3. Original QTE `Show(1456)`, tutorial `ShowTut(339,13,0)`, `IsTutConfirmed()` PC72/branch PC73 ve daha sonra 2/6 UI kontrollü gerçek `MissionResume`. Bunları tamamlamadan ilk gerçek görevün oynanabildiğini söyleme.
4. 1.0.3 IPA authenticated fetch sağlanınca 803 audio dosyasını versiyonlar arası hash karşılaştır.
