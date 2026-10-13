
# B19 research — Original iOS all-972 enemy / boss / underwater inventory, source coverage and playable demo

Date: 2026-10-13. Private original Iron Man 2 2010 iOS assets. This file is **research only; no Vita VPK or new GitHub Actions run**. B17 device test pending.

## Direct verified source: archived ORIGINAL IPA metadata

Read-only independently decompressed GitHub archive research/B15_Original_All_Mechanics_Audit.zip, specifically its B15_ALL_972_ANIMATIONS.csv and B15_NATIVE_10760_SYMBOLS.csv; verified 972 animation records. These inventories were originally decoded from user-supplied 2010 iOS 1.0.0 IPA. The full IPA itself is not currently held in private repo.

| Original ANIM file prefix | Files | Findings |
|---|---:|---|
| IronMan | 248 | Iron Man player movement and combat |
| Drone | 189 | Drone_Army, Drone_Navy, Drone_Floating: fire, hit, walk, float, land and death |
| Enemy | 81 | Enemy_spider, Enemy_jump_spider, Enemy_Shark, Enemy_F18, cannon |
| Boss | 67 | Boss_Crimson, Boss_Ultimo, Boss_Submarine, state/attack/motion families |
| Warmachine | 56 | War Machine player |
| Underwater | 43 | 34 player-suit movement/attack/death clips PLUS 9 underwater bomb/cannon/ship object clips |
| Whiplash | 36 | Whiplash special combat |
| firepower | 25 | Firepower special combat |
| all smaller prefixes | 227 | killer_shrike (19), bigmachine (17), Military (16), tank (12), Iron (22), doors, NPCs, cars, UI/environment |
| **Total** | **972** | Complete source inventory; not 972 independent 3D visualizations or gameplay systems |

The previous 304 player clip report covered 248 IronMan + 56 Warmachine but **omitted the separately prefixed 34 Underwater playable-armor motion clips**. At least 338 original potential player-armor motion clips are now identifiable. The nine non-armor underwater clips: underwater_bomb_idle, underwater_cannon_attack/idle, Underwater_ship02_idle/shake/fall, Underwater_ship_idle/shake/fall.

Important authentic Underwater transitions: Underwater_Float_2_Swim (699ms), Underwater_Swim_2_Float (699ms); Underwater_Swim_F/D/L/R/U, Swim_Left_dodge and Right_dodge, Swim_Att_Aim and Att_m, swim hurt/death, float idle. This is convincing evidence of a **separate underwater/swimming locomotion mode**; not simply replacing textures on B17's fly stage 2. Underwater_Movie1 (2000ms) is a filename hint, not proof of a prerecorded video format. Underwater rig/mesh/textures remain to locate/bake.

Drone source candidates: Drone_Army, Drone_Floating, Drone_Navy each contain named attack/shoot, walk/move, float2land, land2float, injured/die, evade/afraid and landing family. First playable combat vertical slice should reuse **one authentic low-complexity original drone rig/mesh** with authentic idle, approach, shoot, hit, death, and projectile hitbox. Do not use B16 sphere target as a completed enemy system.

Boss source candidates: Boss_Crimson_Float_Attack_Beam/Laser_L/Laser_R, Float_Defence, Float_Rush_Back/Front, Attack_Left_Punch/Right_Punch, Boss_Ultimo_attack/eye/weakness/struggle, Boss_Submarine_attack/dead/hurt/idle. Crimson may be linked to C++ DynamoNPC, but this identity is NOT yet proved by a direct object-instance reference. Enemy_spider/jump_spider and Enemy_Shark/F18, plus Killer Shrike (killer_shrike), all demand NPC-to-rig mapping.

## Direct verified original ARM Mach-O C++ method names (NOT decompilation of function bodies)

- SpawnPoint::IsWaveKilled, IsAllWavesKilled, SelectSpawnPosition, Spawn; NPCSpawnMgr::CreateNPC; ActorManager::GetLiveEnemyCnt. This supports the existence of native **spawn wave state machine**, not its precise parameters.
- AIWhiplash::UpdateActionAttack; WhiplashNPC::UpdateWhip, UpdateStateParalysisAssult; AIFirepower::UpdateActionAttack; FirepowerNPC::UpdateStateAttackMelee; AIGroundTank::UpdateActionAttack; AISubmarine; JohnnyNPC_1; UltimoNPC; DynamoNPC; SharkNPC; KillerShrinkNPC; SubmarineNPC; BigMachineNPC; FlyNPC. Class names alone do not establish individual model counts, animation-to-entity mapping or mission placement.
- ProjectileMgr::AddProjectile; ProjectileEntity::UpdateCollisions, DoSplashDamage, StartTrajectoryFly; WeaponDB::FindWeaponEntityById; WeaponMgr::SetCurrentWeapon; WeaponAccessory::EnableTrail. Supports real projectile and weapon-attachment system.
- checkpoint::CCheckPointManager::MakeCheckPoint, BackToCheckPoint, ContinueGame; IMissionCondition::EvaluateComplete/EvaluateFail. Supports mission success/failure and checkpoint.
- vox::DecoderMPC8, vox::DecoderMSWav, vox::DecoderRaw; BackgroundMusicPlayer::LoadMusic. **Engine has these decoder classes; file inventory/actual sound codec remain UNVERIFIED**. An unrelated bundled decoder may not have corresponding samples in the IPA.

## Gameplay/asset additions

Gameloft's 2010 iOS advertising lists Mark IV, Mark VI, Stealth and **Underwater** Iron Man suits, and Iron Man/War Machine, nine levels and 25 Gameloft LIVE achievements, bosses Whiplash, Firepower, Ultimo:
https://gamefaqs.gamespot.com/iphone/601312-iron-man-2-for-ipad/data

There are **not 189 distinct drone NPC types**; 189 are animation clips and directional/state variants. The 2010 IntoMobile review observed relatively few common enemy types:
https://www.intomobile.com/2010/05/07/review-iron-man-2-for-iphone-ipad/

Object/source animation prefix clues: C4L1_door2_close/open, C2L2_door_collapse, Container_open/close, Gatecontrol_hurt/idle, control_collect, Time_bomb, vehicles. They can become gameplay world interactions only after original references and triggers resolve. Chapter/scene labels in animation names cannot alone prove which of 10 BCLARA configs instantiate them.

All 10 BCLARA files include Mission/Objective/SpawnPoint/MCondition_KillEnemy/OnStart/OnComplete/OnFail/NextMission/FightBoss dictionary keywords, as read from original_level_index.csv in research/Original_Level_BCLARA_Audit.zip. These are **shared schema markers**, not evidence that all ten levels host boss battles. Real instance/field graphs remain unresolved. Level1.bclara = 339733 bytes and Level10.bclara = 203599 bytes.

## Byte-coverage and reverse engineering progress — defensible accounting

- Source iOS IPA 1.0.0 ZIP: **248613763 bytes**. Source iOS IPA 1.0.3 ZIP: **275580565 bytes**. Neither full original IPA ZIP central directory entry/size/hash manifest is currently accessible from GitHub; cannot give a rigorous **decoded X% of all IPA bytes**.
- **Anim archive: 972/972 structurally decoded** (100% within this *specific* asset format); 1.0.3 989/989. This does not equal finished animations or all game assets.
- **Player animation filenames:** 304 older catalog + **34 confirmed Underwater-suit-prefixed clips** = at least 338 player-motion candidates; 634 other enemy/scene/vehicle animation records. Some names can have dual usages, and the full 338 visual previews were never exported.
- **Missions:** 10/10 BCLARA records independently indexed; **0/10 complete real mission object graphs** parsed. Press reported 9 playable missions; tenth config role unproven.
- **C1L1 environment:** 22919 visible triangles/370 submeshes extracted; 190 texture references, **39/39 referenced original first-scene texture names located**, but true scene instances, full material binding and gameplay collision incomplete. 39/39 is *NOT* 39/39 entire game textures.
- **Executable:** **10760 native C++ symbol names** found, not recovered original C++ function bodies; no whole-engine port. Original IPA mostly parsed via ZIP archive and per-file binary serialization. Do not call unencrypted archive index decoding a cryptographic decryption achievement.
- **Audio/voice/cutscene:** native managers/camera/cutscene function signatures found, actual sound/media bank inventory unmeasured, no codecs proven on real audio bytes.
- **Working Vita:** 5 suit models + B17 59 baked motion assets; B17 real-device quality test pending; no full 2010 original campaign objective playable. Binary packing byte totals and runtime completeness are different axes.

**Conclusion:** single impressive-sounding overall percentage is unsupported. To compute rigorous byte coverage, regain originals and produce IPA ZIP entries with compressed/uncompressed byte totals and normalized content classifications, then per-pack parse coverage and per-system playable implementation fractions. Need separate input ZIP byte coverage, decoded asset coverage, and playable-game coverage.

## First real combat demo — proposed acceptance test, NOT already implemented

In isolated prototype after B17 device test and GPU/audio resource access:
1. Authentic controllable Mark VI/War Machine, camera, walk/run/hover/staged flight.
2. **At least one authentic Drone_Army or Drone_Floating BDAE model/rig + original idle/move/shoot/hurt/death animation**, not 2D/3D spheres.
3. **Real cover/ground collision**, modest authentic C1L1 world tile/material, stable on Vita.
4. Original-derived repulsor/Unibeam emitter mapping + visible projectile/splash, enemy AI seek/aim/fire, HP/shield, hit feedback, SFX, HUD.
5. **Two deterministic SpawnPoint waves**, objective progress, actual win/fail, checkpoint/retry, restart from fail and results screen. Combat flow 2-5 min; rate and time values may be prototype until original BCLARA / executable behavior is recovered.
6. Device acceptance only after B17 report, actual FPS/CPU/UP/COPY/PRES profiling, independent native state tests and unique VPK Title ID. This is a new-gameplay vertical slice, NOT a claim of faithfully ported original Media Mayhem mission. Full mission requires original serialized instances and scripts.

No test VPK generated here. Keep research private to preserve copyrighted original assets.
