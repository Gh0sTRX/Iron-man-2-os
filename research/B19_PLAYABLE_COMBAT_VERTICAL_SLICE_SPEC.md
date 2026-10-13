# B19 gameplay vertical slice: acceptance contract and integration (no new VPK)

Goal: turn B17's movable original armor + prototype sphere target range into a complete, playable 2-5 minute mission-like combat loop. Preserve all B15-B17 installed apps. B17 on-device report remains pending.

## Minimum accepted gameplay (all must pass)

1. Original Mark VI or War Machine player suit; controllable ground, hover, fly, rush and third-person camera.
2. At least one **original 2010 iOS Drone_Army / Drone_Floating BDAE enemy model**, textured and skinned, with authentic idle, move, attack, hurt and death ANIM motion. No placeholder sphere enemy permitted at acceptance.
3. Real enemy READY -> SEEK -> AIM -> ATTACK -> HURT -> DEAD state, spatial position + collision, enemy projectile vs player, player weapon vs enemy, HP/shield, hit feedback and knockback/dodge. Data-driven balances until original stats recovered, marked as prototype.
4. Small original C1L1 world tile, material and ground/obstacle collision rendered using optimized GPU pipeline. Characters must stand on correct world floor.
5. Original repulsor/jet/attack/hit/death SFX and optionally a short looping music track **only if** actual original IPA source is recovered and codec identified. Typed SFX IDs until then; prototype bleeps are not authentic sounds.
6. Two separate SpawnPoint waves; HUD objectives, clear/fail screen, checkpoint and retry, pause and reset. Game state updates with deterministic fixed tick independent of display FPS.
7. Native Debug+ASan/UBSan tests, stable Vita FPS, no unexpected memory/SDL/GPU regressions. Keep known-good B15 installed.

## Flow

INIT -> READY -> ACTIVE -> SPAWN WAVE 1 -> combat -> WAVE 1 COMPLETE -> SPAWN WAVE 2 -> combat -> VICTORY, or PLAYER_HP_ZERO -> FAIL -> RETRY CHECKPOINT.

Game events (HIT, ENEMY_DIED, WAVE_DONE, PROJECTILE_FIRED, PLAYER_HURT, MISSION_COMPLETE) are queued separately from audio and rendering. Model/animation handles belong to scene adapter; objective/spawn logic has deterministic C core and no SDK dependencies.

## Proven inputs and blockers

Original source C++ symbols NPCSpawnMgr::CreateNPC, SpawnPoint::Spawn / IsWaveKilled / IsAllWavesKilled, ProjectileEntity::UpdateCollisions / DoSplashDamage, WeaponDB::FindWeaponEntityById, IMissionCondition::EvaluateComplete / EvaluateFail, CCheckPointManager::MakeCheckPoint / BackToCheckPoint exist; full implementations/stats/serialized mission references have not been decrypted/decompiled.

189 original Drone prefix ANIMs; 81 Enemy prefix ANIMs; real C1L1 geometry+texture subsets; existing working five armor models and motion. Missing: original enemy BDAE mesh binding, original enemy animations baked and displayed, full original scene material + collision mapping, original sound bank formats and scene-to-BCLARA instance links.

This **is a prototype combat training mission** until source iOS mission data are actually decoded; it is NOT proven identical to original Media Mayhem / level1. No new VPK should be issued before B17 hardware feedback. Avoid generating repeated failing GitHub Actions runs and preserve existing rollout.

## Definition of done

Original enemy visible with authentic motion, player/enemy ranged hits, at least one failure and one victory route, two wave transitions, original world tile collision, basic authentic SFX when available, UI and stable Vita performance verified by user; do not label a sphere-shooting range a playable original Iron Man 2 mission.
