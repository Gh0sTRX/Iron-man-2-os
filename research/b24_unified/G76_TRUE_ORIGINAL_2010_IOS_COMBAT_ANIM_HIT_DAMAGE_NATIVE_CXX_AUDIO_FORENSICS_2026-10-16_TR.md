# G76 — Original Iron Man 2 (2010 iOS IPA) combat, damage, animations, sounds, real native ARM source — 2026-10-16

## Owner's direction
User explicitly wants genuine original IPA combat data decoded now, not a simulation/policy guessed from homebrew B14. Distinguish **actual original 2010 iOS asset/code byte evidence** from unproven game semantics. Do NOT generate a VPK during research. Previous full G75 B24/B14 speed tune is a homebrew source-only change; no original iOS flight constants had been extracted.

## 1. Actual original 2010 animation bank: COMPLETE per-combat raw decoding
**Successful G76 real owner IPA CI:** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38926792920 (subsequent equivalent G76E run 38927056851). Script `research/b24_unified/g76_original_combat/g76_2010_combat_animation_binary_forensics.py`.

- Original 2010 `Payload/IronMan2.app/anims` asset bank verified **972** named .anim entries. **441** source names matched broad combat/attack/reaction keyword scan; **110** source names matched damage/hurt/death/related keyword scan. Keyword-selected buckets include some noncombat named objects; **441 are not 441 finished distinct usable combat actions**.
- For all 441 selected entries: decoded genuine source XYZ per-joint constant/keyframed channel bytes, signed keyframe time, quaternion key channels, source counts, positional key trajectories and full original raw SHA-256. CSV `G76_ORIGINAL_ATTACK_DAMAGE_CLIP_TIMELINES.csv` and JSON `G76_TRUE_2010_COMBAT_HURT_ANIM_SOURCE_CHANNEL_REPORT.json`. Decoding does not itself identify actual attack hitbox frame or world movement. All are original 2010 IPA bytes, not B14.
- Verified examples: `IronMan_Ground_Combo_1.anim` duration **266ms**, **5 animated xyz /24 quaternion**; `Combo_2` **300ms 5/23**; `Combo_3` **500ms 6/23**. `IronMan_Ground_Hurt1` **466ms 8/26**; `Drone_Army_Attack` **1666ms 7/26** and `Drone_Army_Hurt` **600ms 7/24**. Footsteps/Bip01 local XYZ keyframe net move during combo1 about **0.281657 /0.247580**, combo2 **0.188353/0.178491**, combo3 **0.239434/0.345417**; these are LOCAL JOINT translation, not confirmed world root-motion or attack hit timing.

## 2. Authentic iOS native C++ machine code, not guessed gameplay
Actual owner `Payload/IronMan2.app/IronMan2` is a 32-bit ARM Mach-O **7,480,208 bytes**, real symtab reports **65,500 symbols** (not 65,500 independent source methods), encryption info `cryptid=0`, so it can be disassembled. G76 scanned **2,313** matched combat-related C++ names; **1,961** candidate native function entries underwent 96-byte entry disassembly. 80 important native methods were further function-bounded scanned in G76B, 2010 true method entry ISA semantics; 22+ targeted complete bounded methods in G76D/E. All work on user's privately sourced IPA; original executable not uploaded to repository.

**Exact authentic C++ method addresses:**
- `Actor::Damage(Actor*, float)` **0x000D908C**.
- `Actor::Damage(float)` **0x000D9194**.
- `Actor::CanBeHurt(Actor*)` present; its compiled body loads `this+0x394` as a FLOAT and requires it >0 on the damage eligibility path.
- `MainCharacter::Damage(Actor*,float)` **0x000ED63C** -> calls `Actor::Damage(Actor*,float)` after per-attacker direction/impact vector calculations.
- `Actor::TestMeleeHit(Actor*)` **0x000DFD94** -> directly calls `Model::GetBoundingBox()` twice, contains real VFP spatial subtraction/multiplication/compare math. Source authentic volume overlap, not a damage amount formula yet.
- `MainCharacter::StartMeleeAttack(float)` **0x000EE04C** -> StatesMgr `GetState`, WCollision::CheckCanWalk, SoundManager::PlaySFX, StatesMgr::SetState. Source walking clearance and state/sound gates authentic.
- `MainCharacter::GetCurrentMeleeAttackStep() const` **0x000EA3B8** -> two instructions `ldr r0,[r0,#0x824]; bx lr`: **exact confirmed original native combo step field offset +0x824**.
- `MainCharacter::UpdateComboAttackAction(int)` **0x000F18E4** -> source mesh dummy position, `WNavigation::AddForceVector` four times, `Actor::LookAt`, `Model::GetBoundingBox`; means combo needs true 3D locomotion/aim/hit action instead of only changed static pose; exact original timing/step input not decoded.
- `MainCharacter::ThrowMissile(ProjectileEntity*)` **0x000EA850**.
- `MainCharacter::DoUniBeamAttack(int, Actor*, float,float, vector3d const&)` **0x000F60AC** -> `WeaponDB::GetAttackEntityByIndex`, `Object3D::GetDummyAbsolutePosition`, `Emmiter::Clone/SetPosition`, SoundManager. Original chest/attachment anchoring candidate, exact ID to part not proven.
- `ProjectileEntity::DoSplashDamage()` **0x000B4BF0** -> `ActorManager::FindActorsInRange`, `Entity3D::FindActorsInRangeLight`, and multiple source `Actor::CanAttack` checks, real radial candidate pruning.
- `ProjectileEntity::UpdateCollisions()` **0x000B6518** -> original actor range tests and `HitImpactActor, MissTarget, SetState`. Native original branch table, multiple VFP math routines.
- `WeaponDB::FindWeaponEntityById(int)` **0x000AB654**; `WeaponDB::GetAttackEntityByIndex(int)` exists and is directly used by native Unibeam code.

### Damage calculation NEW proof: two separate actor durability values
Exact native ARM instruction-level confirmed from `Actor::Damage(float)`:
- `vldr s15,[r0,#0x3BC]` load first resource as 32-bit float
- `vmov s14,r1` damage argument bits into VFP
- `vldr s16,[r0,#0x394]` load second float
- if first resource positive: `vsubhi.f32 s15,s15,s14`, conditionally `vstrhi s15,[r0,#0x3BC]`
- if first resource is not positive on entry: separate code path subtracts damage from second `vsub.f32 s15,s16,s14`, stores to `[r0,#0x394]`.
- Negative first value is clamped to 0 on first path. This structurally supports primary barrier then secondary HP-like resource; **type field names SHIELD/HEALTH are hypothesized** until serialized actor-class property field mapping independently verifies; note it does not obviously carry overshoot from a depleted first resource into the second within the SAME call.
- `Actor::CanBeHurt` specifically checks second `+0x394` float >0. Thus +0x394 strongly resembles life/HP but requires typed schema confirmation.
- Death/hit callbacks use virtual method dispatch tables, so do not infer exact voice/FX or damage modifiers from static calls alone.

The original `CNPC::InitShield()` is a real C++ method, but its local code writes shield effect pointer at `this+0x748`; **this does not by itself prove +0x3BC's property name**. `CNPC::OnHit(Actor*,int,float)`, `UpdateStateHurt` and `OnDie()` now decoded as actual bounded ARM opcodes for follow-up per-action assembly control flow.

## 3. Original first level script is actual source
Existing G75 owner Lua bytecode audit https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38913735917: 71 real first-level event callbacks and 1,035 static native engine callsites. 12 `SetAttackTypeEnabled` calls, **11× (1,false), 1× (1,true)** on `MissionTutorial_missile_OnStart`. This conclusively shows script-automated attack-type permission transition in missile tutorial; which attack id=1 refers to not proven. Actual backend native C++ combat logic independently confirmed above; don't conflate Lua condition bytecode with stat math.

## 4. Genuine source audio records in original IPA
G76C source-only binary scan: original `states` 2010 game pack contains 55 embedded Lua chunk signatures; original `sfx_` file count **160** with **66** matching broad combat-related filename patterns. Verified first 16 bytes of `sfx_combo_1.www`, `sfx_armor_hit_1.www`, `sfx_crimson_missile.www` etc are **RIFF WAVE fmt**: `52 49 46 46 ... 57 41 56 45 66 6D 74 20`. Their original source .www file naming does NOT indicate exotic format, they are real WAV container bytes. PCM subtype/channels/rate must be formally validated before asserting SDL_LoadWAV/Vita playback.
- Original SFX examples `sfx_combo_1/2/3.www`, `sfx_combo_power_a/aa/aaa/aab/ab/aba/abb.www`, `sfx_armor_hit_1/2.www`, `sfx_crimson_attack_melee.www`, `sfx_crimson_missile.www`. No audio files uploaded or Vita binary produced. Source-only RIFF verifier for user-supplied IPA exists at `g76_original_combat/g76f_extract_real_riff_wave_combat_sfx_NO_VPK.py`, but do not claim its export workflow passed: there is **no uploaded G76F WAV artifact yet**.

## 5. Exact scope and current status
**DONE, source-backed:** 972 original full record indexed; 441 combat-related keyframe time/XYZ/quat records decoded; 110 hurt/death-like records; real 2010 owner ARM Mach-O executable confirmed disassemblable; original damage double durability field offsets +0x3BC / +0x394; exact ComboStep +0x824; real projected explosion ActorManager/CanAttack calls, Unibeam weapon DB and attachment, melee collision and SFX; real sound 160 SFX and verified RIFF WAVE combat samples. GitHub CI success **no new Vita VPK**.
**STILL RESEARCH, DO NOT INVENT:** Field +0x3BC exact typed property name (shield likely); weapon stat numeric tables and original per-weapon damage values; original combo hit frame timestamps / combo input edges; native NPC rig-to-BRES state machine visual Vita integration; exact source SFX playback on Vita; whole original Lua mission execution; G75 ground/lighting/flight already source-tested but new combined Vita untested.
**NEXT:** classify native EntityData weapon table serialization and `Actor` typed property offsets with xrefs; native `CNPC::OnHit` damage modifications and original weapon scalar register data-flow; expose a console-readable symbolic reverse-engineered STATE graph without launching copyrighted game code; map `StartMeleeAttack` and `UpdateComboAttackAction` frame action to skinned original combo one/two/three; validate original WAV fmt sample type before inserting into B24 sound owner.
Repository scripts `research/b24_unified/g76_original_combat/g76_2010_combat_animation_binary_forensics.py`, `g76_2010_native_arm_combat_method_provenance.py`, `g76b_arm_damage_call_graph_and_literals.py`, `g76c_real_2010_lua_combat_states_weapon_sound.py`, `g76d_native_actor_damage_instructions.py`, `g76f_extract_real_riff_wave_combat_sfx_NO_VPK.py`. No executable/VPK uploaded or changed.

## G76 native Actor damage math reference now implemented and ARM tested
- Source paths:
  `research/b24_unified/g76_original_combat/b24_g76_original_native_damage_math.c/.h`,
  `test_b24_g76_native_damage_math.c`.
- GitHub Actions https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38927881762 **SUCCESS** for deterministic host and VitaSDK **ARM object-only** compilation. **NO new VPK**, no repackage, no user device test.
- Recovered original source ARM `Actor::Damage(float)` two-branch arithmetic:
  1) positive primary float at actor +0x3BC: subtract incoming float damage, clamp >=0; do **not** in the same damage event subtract excess from +0x394,
  2) primary already depleted and positive secondary at +0x394: subtract incoming float damage, clamp >=0,
  3) both depleted: no resource reduction.
- Host test original-offset neutral field names demonstrates 30→20 primary, 20→0 primary on 25 hit with secondary 120 untouched, then second 60 and 0. Added API finite/positive bounds for safety are NEW and must not be mistaken for decompiled original ARM conditions. Typed HP/shield mapping, original status transition, hit reactions, native virtual callback dispatch and float attack scaling not yet restored.
