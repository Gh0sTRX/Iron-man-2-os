# G138 / G139 — Iron Man 2 2010 iOS özgün ses yöneticisine giriş ve Vita SceAudio PC3

**17 Ekim 2026** · `Gh0sTRX/Iron-man-2-os` · `feature/b24-unified-gameplay` · **VPK YOK**.

Kullanıcı Level1'i özgün görev + ses + QTE + kamera + combat çalışır hâlde ilerletmek, her denemede VPK üretmemek istiyor. Bu çalışmada **native Vita BGM ses çıkışı bağlandı**; özgün 2010 ARM ses metotlarının iç fonksiyon akışı ise Drive kota sınırı yüzünden henüz doğrulanamadı.

## Önceki orijinal 2010 ses kaynak kanıtı

- Kullanıcının özgün 2010 iOS Mach-O sembollerinde `SoundManager::PauseAllMusic`, `ResumeAllMusic`, `PlayMusic(int,bool,float)`, `PlaySFX`, `PlayRandomSFX`, `SoundPlayer::LoadSound` vb. **gerçek fonksiyon isimleri** tespit edildi. Adlar 2010 native source behavior/full offsets kanıtlamaz; tam kaynak ARM fonksiyonu G138 ile hedeflendi.
- Özgün `Mission000_OnStart` gerçek Lua: **PC1 `MissionPause()`, PC3 `PauseMusic()`, PC6 `Show(1456)` QTE**, PC62 `PlayMusic(88,true)`, PC67 `ShowTut(339,13,0)`, PC70 `PlayVoice(320)`, PC72 `IsTutConfirmed()`, sonraki PC73 özgün EQ kontrolü. PC914 UI2, PC927 UI6, PC935 MissionResume **tamamen koşullu ve henüz execute edilmedi**.
- IPA içerisinde daha önce **160 `sfx_*.www` gerçek RIFF/WAVE** bulundu, oyun genelinde önceki taramada **803 RIFF/WAVE kapsayıcı** (647 IMA-ADPCM + 156 PCM) kayıt raporlandı. Bu, özgün müzik `88` veya konuşma `320` ile ses dosyaları arasında ad/index eşleme veya Vita'da ses çalındığını **KANITLAMIYOR**.

## G138 yeni özgün 2010 ses native çözümlemesi — DENENDİ AMA ERİŞİM ENGELİ

- Gerçek kullanıcı IPA'sından özgün `PauseMusic(lua_State*)`, `PlayMusic(lua_State*)`, `SoundManager::PauseAllMusic()` ARM çağrılarını, şarkı/ses envanteri RIFF metadata dosya adlarını tarayacak script **kaynağa eklendi**: `research/b24_unified/g138_original_audio_owner/g138_owner_2010_actual_native_PauseMusic_lua_SoundManager_Arm_audio_asset_inventory.py`.
- Workflow `.github/workflows/g138-authentic-2010-iOS-Lua-PauseMusic-SoundManager-ARM-audio-bank-NO-VPK.yml`, [G138 run 39027945638 FAILED](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39027945638) çünkü Google Drive `gdown` her iki 248.613.763 bayt dosyada **Too many users have viewed or downloaded this file recently** kota hatası verdi. **Kodun özgün ARM ses metotlarının semantiğini çözümlediği iddia edilmemeli**. Özgün assetler GitHub'a commit edilmedi; ses dosyası veya IPA yayımlanmadı.

## G139 Vita üzerinde GERÇEK ses çıkış kontrolü — doğrulanmış

- `research/b24_unified/g139_vita_native_audio_music/b24_g139_original_mission_music_bridge.[ch]`:
  - gerçek Vita `sceAudioOutOpenPort(SCE_AUDIO_OUT_PORT_TYPE_BGM,512,48000,STEREO)` arayüzü,
  - `sceAudioOutSetVolume(port,L|R,{0,0})` ile output mute; `{32768,32768}` restore,
  - `sceAudioOutReleasePort` ile port teardown.
  - output init başarısızsa `PauseMusic` gerçekte başarılı sayılmaz. `SetVolume` hata döndürürse de **orijinal Mission000 PC3 olayını ilerletmez**. Başarılıysa PC3 ACK edilir ve tam kaynak sonraki `Show(1456)` PC6 engelinde durulur.
  - Native host fake callback testleri **genuine original source 24 Lua CALL** üretilmiş C olaylarından PC1→PC3→PC6 olay sırasını, port open fail, volume fail, tekrar deneme, mute/unmute doğrular.
  - **Bu bir Vita PCM BGM çıkış/volume state iskeletidir.** Özgün iOS SoundManager tam pause semantics/source mix engine, gerçek müzik stream buffer, source music ID88, PlayVoice320 gerçek wav eşleşmesi, IMA-ADPCM decode ve kullanıcı konsolunda **duyulur ses** HENÜZ YOK. Boş BGM portundaki volume set, orijinal soundtrack'in durdurulduğu iddiası değildir.
- `g139_patch_original_Mission000_PauseMusic_with_real_Vita_SceAudio_NO_VPK.py` gerçekten mevcut G137 birleşik `work/src/main.c` içindeki eski `g137_real_scene_MissionPause_only` dispatcher'ını ses-portu callback'iyle değiştirir; ilk oyun tick'inde ses portunu açmayı dener; `B24_G139_REAL_VITA_AUDIO_OUT=ON` altında `SceAudio_stub` link bayrağı ekler. İkinci B14 physics/motion owner yaratılmaz, kaynak karakter ilk stage=2/rush uçuşu uydurulmaz.
- Tam G139 oyun Vita ELF workflow [G139 39028191817 FAIL (environment)](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39028191817) eski oyun restore sırasında aynı özel Google Drive 250 MB IPA download quota hatası verdi; **G139 tam birleşik game ELF build başarılı denemez**.
- **G139H bağımsız tam native kod testi (owner büyük IPA'ya ihtiyaç duymadan eski güvenilir G27 JSON artifact'inden): [SUCCESS 39028305485](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39028305485)**:
  - özgün 24 Lua event C bytecode-verified metadata'dan üretildi,
  - Linux C11 `-Werror` host audio backend success/failure QTE blockers **PASS**,
  - gerçek `vitasdk/vitasdk:2026.08` içinde `arm-vita-eabi-gcc` ile `B24_G139_REAL_VITA_AUDIO_OUT=1` native ARM **object COMPILED**, Vita `sceAudioOutOpenPort` ve `sceAudioOutSetVolume` unresolved dynamic symbols `arm-vita-eabi-nm` ile doğrulandı. **Bu tam oyun linki veya PS Vita test değil**, modül-native ARM object. VPK ve ses dosyası yayımlanmadı.
- VitaSDK'nin gerçek API bilgisi: https://docs.vitasdk.org/group__SceAudioUser.html.

## Gerçek oynanabilir ilk bölüm için önde kalan işler

1. G138 özgün `PauseMusic(lua_State*)` → `SoundManager` metot bağlarını gerçek iOS ARM disassembly'den doğrula; user IPA rate limit kalkmadan kesin olamaz.
2. Kullanıcı özgün .www/RIFF WAVE kaynakları ile müzik 88 ve voice320 ID'lerini typed audio bank index'ine eşle, PCM16/IMA ADPCM çöz, Vita'da asenkron/worker thread ile WAV verisi stream et. Şu an yalnız native BGM port/volume çalıştırabilecek kaynak var.
3. `Show(InteractiveObj_QTE 1456)` için orijinal scene node class/mesh UI anim data ve tıklama event'inin Vita HUD ile özgün `IsTutConfirmed` PC72 kontrolünü çalıştır. Bu olmadan özgün `Mission000` PC73 sonrası gerçek olaylar ve kontrol2/6 ve MissionResume kaynak doğruluğuyla yürütülemez.
4. Kamera geçişleri, anim/audio sync, true mission node FSM, gerçek enemy spawner/combat/weapon damage, sky/material authored behavior, true native solid flags.
5. G139 tam Vita `im2_beta` link, gerçek Vita hardware audio port test **YAPILMADI**; no fake 30FPS claims, **NO VPK**.

## Kod / CI

- G139 Host native source dispatch + Vita ARM audio module verified [SUCCESS run39028305485](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39028305485).
- G137 full previous `im2_beta` main engine ARM ELF-only [SUCCESS run39027228231](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39027228231).
- G138 and full merged G139 blocked by owner Google Drive download quota (see above). Don't conflate environmental failure with source C code failure, but do not imply full integration verified.
