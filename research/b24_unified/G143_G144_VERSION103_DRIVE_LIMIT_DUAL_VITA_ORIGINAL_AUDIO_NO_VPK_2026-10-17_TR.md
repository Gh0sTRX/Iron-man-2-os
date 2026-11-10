# G143/G144 — Source 2010 sound ID integration, Vita dual audio, version 1.0.3 status

2026-10-17 | branch feature/b24-unified-gameplay | NO NEW VPK.

## Original 1.0.3 comparison: BLOCKED, never pretend complete

Original owner Google Drive file Iron Man 2 iOS 3.0.ipa, id [private file ID removed], size 275580565 bytes verified from connected Drive metadata. Authenticated Drive raw fetch returns HTTP 413: max 268435456 bytes. Anonymous GitHub Actions gdown cannot retrieve the public file (rate limit/public resolver) [run G143 failed](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39030926936). This is an ACCESS limit, not an asset decoder result. The sound banks across v1.0.0 and 1.0.3 have NOT been byte-compared; do not claim identical. A complete 1.0.3 RIFF/WAVE and SHA-by-filename scanner has been written in research/b24_unified/g143_version103_audio_research/g143_source_original_2010_103_sound_manifest.py; it accepts --v103 and optionally --v100 to produce true version diffs without exporting game bytes.

## Additional source 2010 native facts (v1.0.0 Mach-O)

- Game constructor at 0x99524 sets [Game+0xEC] = -1 in ARM instruction 0x99564. [Game+0xE4] voice and related BGM indices +0xF0,+0xF4,+0xF8,+0xFC are also -1 initially.
- Game::GetCrtBGMIndex 0x9762C returns [Game+0xEC]; setter 0x97654 stores there.
- Game::PlayCrtBGM(int,bool,float) at 0x98218 updates +0xEC via ARM store at 0x9828C after sound-manager playback choice, unlike PlayMusic(lua_State*) which calls SoundManager directly.
- Original PauseMusic(lua_State*) 0x17ECC calls Game::StopCrtBGM(2000.0f) 0x97728, which passes [Game+0xEC] to SoundManager::StopMusic(int,float) 0x142188. 2000.0 is exact source float; wall-clock interpretation still unproven. Do not pretend mute equals original current-music stop.
- Real original 803x40 byte name table matches IPA all 803 sounds. Lua PlayMusic(88,true) resolves native index87 file m_pre_cutscene_intro.www; PlayVoice(320) native index319 file vfx_intro_level1_jarvis_1.www.

## G144 real sound channels

- New source: research/b24_unified/g144_original_level1_real_pcm_channels/b24_g144_source_audio_channels.[ch].
- Music source ID88 → ux0:data/ironman2/audio/m_pre_cutscene_intro.pcm on one real SceAudioOut BGM channel. Jarvis speech ID320 → ux0:data/ironman2/audio/vfx_intro_level1_jarvis_1.pcm on a separate real SceAudioOut MAIN channel. Separate threaded G141 PCM readers; Game B14 tick never blocks on audio sample output.
- G144 original-event stop with fade argument >0 intentionally returns not acknowledged: exact iOS fade-time unit and target current track must first be verified. Mission000 PC3 and original QTE1456 remain NOT playable; G144 implements real original sound sample output backend infrastructure, not full original SoundManager semantics.
- User private original IPA audio converted 48k stereo 16bit little-endian, original tracks ID88 duration 27.428s and ID320 duration 2.126s. Private user ZIP under /mnt/data/IronMan2_G144_Original_Level1_Vita_PCM_ID88_ID320.zip (verified current turn) contains two .pcm assets and manifest. Do not commit game PCM to public GitHub.
- [G144 GitHub Actions SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39031175329): source C11 exact sound-ID-to-path regression passed; real VitaSDK 2026.08 ARM compilation of G144+G141+G139+G142 all passes, sceAudioOutOpenPort/SetVolume/Output and sceKernel thread refs verified. No VPK, no Vita handheld test, NOT full im2_beta link.
- A useful next step is connecting G144 backend to source G137 main game's independent BGM+voice channels and genuine source current-music Game+0xEC, then QTE source ID1456 and PC72 tutorial state. Keep original mission fail-closed until actual events acknowledged.

No user permission to create a new VPK at this moment.
