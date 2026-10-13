# B20 native iOS minigame / NPC / codec evidence — 2010 Gameloft Iron Man 2

Status: source-research only. Date: 2026-10-13. Source `research/B15_Original_All_Mechanics_Audit.zip`, `B15_NATIVE_10760_SYMBOLS.csv`. Compressed 1,272,122-byte original metadata CSV was independently inflated and read from the PRIVATE GitHub repo. C++ demangled export names are genuine from previously analyzed original iOS Mach-O, but **we do not have original C++ bodies, branch conditions or gameplay parameters**.

## NEW: at least two named minigame subclasses

```text
GS_Minigame::InitMinigame()
GS_Minigame::LoadMinigameData(int)
GS_Minigame::SetMGState(int)
GS_Minigame::UpdateMinigame(int)
GS_Minigame::RenderMinigame()
GS_Minigame::UpdateTutorial(int)
GS_GamePlay::s_pMinigame

Minigame_Twist::checkBoard()
Minigame_Twist::SetCursor(int, int)
Minigame_Twist::LoadMinigameData(int)
Minigame_Twist::InitMinigame()
Minigame_Twist::UpdateMinigame(int)
Minigame_Twist::RenderMinigame()

Minigame_GateClue::InitMinigame()
Minigame_GateClue::LoadMinigameData(int)
Minigame_GateClue::UpdateIntro(int)
Minigame_GateClue::DrawIntro()
Minigame_GateClue::UpdateMinigame(int)
Minigame_GateClue::RenderMinigame()
```

**Significance:** This is considerably stronger than knowing `GS_Minigame` exists; the original runtime has **at least two class-named different minigames**. The `Minigame_Twist::checkBoard` and `SetCursor` names are strong candidates for the original slide-tile bomb puzzle described in the genuine iOS May 7 2010 IntoMobile review, but **the mapping remains unproven until original instantiated minigame IDs, scripts or C++ function call sites are decoded**. `GateClue` may be a code/gate puzzle but that interpretation is a hypothesis only; do not invent rules.

Original iOS period review independently states that bomb-defusal requires sliding tiles to match an Iron Man arc reactor image within a move limit and includes small bomb tiles. This does not prove which class implements it:
https://www.intomobile.com/2010/05/07/review-iron-man-2-for-iphone-ipad/

B25+ real first mission must preserve puzzle objectives when applicable, rather than interpreting everything as only kill enemy.

## NEW: original AI state database source APIs

```text
StateDatabase::StateDatabase(char const*)
StateDatabase::GetStateSetData(char const*)
StateDatabase::GetStateSetData(unsigned int)
NPCSpawnMgr::CreateNPC(int)
SpawnPoint::LoadFromFile(EntityData*)
SpawnPoint::IsWaveKilled(int,bool)
SpawnPoint::IsAllWavesKilled(bool)
```

**Significance:** Original enemy AI is not merely a timer and a proximity sphere. It exposes named/ID state sets and per-NPC state transitions. The first authentic Drone requires the `StateDatabase` data lookup (or a verified restricted approximation) and recovered model/rig/skin (not in the existing published private game project source bundles). Without original IPA / extracted models, only independent proof-of-logic combat is possible today.

Additional boss function examples verified: `WhiplashNPC::UpdateWhip`, `WhiplashNPC::UpdateStateParalysisAssult`, `FirepowerNPC::UpdateStateAttackMelee`, `DynamoNPC::ChooseAttack`, `MainCharacter::UpdateUltimoBossState`. Original boss animations in B19 source inventory include Crimson, Ultimo and Submarine. `Boss_Crimson` vs `DynamoNPC` exact correspondence still not confirmed.

## NEW: native audio decoder candidates expanded

Symbols include `AdpcmDecoder::cAdpcmIndexTable`, `AdpcmDecoder::cAdpcmStepSizeTable`, `vox::DecoderMPC8`, `vox::DecoderMSWav`, and `vox::DecoderRaw`.

This is evidence of packaged audio decoding support in the application binary. It **does not establish the actual codec of any soundtrack, dialogue or effect asset**. The audio asset archive might be wrapped/concatenated and need own table offsets. When original IPA is reconnected, `research/b18/ipa_media_inventory.py` should magic-scan and verify external audio banks (including non-obvious extensions) before implementing a Vita mixer.

## NEW: UI runtime hint

The symbol list also contains `gameswf::` (hundreds of symbols) and `GSFlashMenu::SaveMcDataToFile(UpgradeSystem&)`. This strongly supports the inclusion of a Flash/SWF-capable UI subsystem, **not proof that all original cutscenes are SWF/FMVs**. The 2010 iOS binary also exposes `GamePlayUI::StartCutscene/UpdateCutscene/RenderCutscene` and spline camera paths, separately. Audit menu vs story cutscene assets independently.

## Original assets still missing for new actual Vita demo

- Original Drone_Army / Drone_Floating skinned BDAE source (repo's B11 original game model ZIP contains only 15 C1L1 environmental BDAEs, plus a Mark VI GLB; B7 tools ZIP has scripts/previews but no original Drone BDAE).
- Full original IPA `anims` clip bytes, audio packs, .bclara mission instances and original state database. Metadata CSV ≠ the original content.
- Native C B19 two-wave game simulation exists under research/b19/host_gameplay, but **visual enemy authentic model & behavior still unavailable**.
- 248.6 MB and 275.6 MB compressed IPAs both known by historic filesize; complete byte coverage percent unknown until actual ZIP manifests and nested file structure are audited. ZIP decompression is not equivalent to DRM decryption.

No VPK was built, no GitHub workflow was run, and B17 real hardware test remains pending.
