# B23 — ORIGINAL THRUSTER / VFX SOCKET FORENSICS (read-only, 2026-10-13)

**Source:** genuinely decoded original 2010 Gameloft iOS v1.0.0 `Iron_man_mark6.bdae` and `warmachine.bdae` rig data inside private `research/B6_Rig_Hierarchy_Prototype.zip`: `MarkVI_original_rig.json` (96 nodes), `WarMachine_original_rig.json` (112 nodes). ZIP GitHub blob SHA `5922b9148519dbd12d80934bb732fbee4c035bfc`. Extracted/parsed directly, no random guessed mesh coordinates. **No VPK, original particle atlas or rendering output in this report.**

## Source-backed attachment nodes

Both models have exactly one `Dummy_Back-node`, parent `Bip01_Spine1-node`, with same **bone-parent-local** position `[0.230852, -0.318889, -0.091814]` (raw BDAE coordinate space, NOT PS Vita Y-up world coordinates).

| Node | Mark VI absolute BDAE record offset (decimal / hex) | War Machine offset | Parent | Parent-local xyz in original source BDAE |
|---|---:|---:|---|---|
| `Dummy_Back-node` | 55184 / 0xD790 | 87380 / 0x15554 | `Bip01_Spine1-node` | `[0.230852,-0.318889,-0.091814]` |
| `DummyE_Foot_L-node` | 59432 / 0xE828 | 92708 / 0x16A24 | `Bip01_L_Foot-node` | `[0.222078,0.008492,-0.000196]` |
| `DummyE_Foot_R-node` | 60440 / 0xEC18 | 93572 / 0x16D84 | `Bip01_R_Foot-node` | `[0.222078,0.008492,0.000196]` |
| `DummyE_Hand_L-node` | 56552 / 0xDCE8 | 89252 / 0x15CA4 | `Bip01_L_Hand-node` | `[0.114930,0.008046,-0.010038]` |
| `DummyE_Hand_R-node` | 58208 / 0xE360 | 90980 / 0x16364 | `Bip01_R_Hand-node` | `[0.114927,0.008025,0.010027]` |
| `DummyE_SlowFlyDust-node` | 54824 / 0xD628 | 86876 / 0x1535C | `Bip01_Spine-node` | `[0.102968,0.277460,0]` |

Additional real joint children: `Dummy_Hand_L/R` likely general palm/weapon attachments; `Dummy_Trail01/02/03/04` beneath hands are **trail candidates**; `Dummy_Foot_L` on both models, plus `DummyE_Midfoot`. War Machine has additional `Dummy_Gun_L/R`, `DummyE_Gun_L/R`, `DummyE_Shoot_L/R` and back mounted `Gun01...Gun04` structure. Do not conflate weapon emitters with flight propulsion.

**Original 2-back-nozzle status:** 1 original spine-back dummy found per rig, NOT two separate `Dummy_Back_L`/`Dummy_Back_R` nodes. Exact left/right nozzle locations and relation between `Dummy_Back` and either original FX configuration or skin surface **not yet decoded**. A central back FX anchor is plausible but **not verified as the actual RUSH thruster source**. We must not assign guessed ±0.2 offsets and claim recovered original coordinates.

## Original executable evidence for an actual effect pipeline

Read-only decompression of private `research/B15_Original_All_Mechanics_Audit.zip` / 10,760 original ARM Mach-O symbol rows directly confirms:
- `MainCharacter::UpdateTrailEffect()`
- `ParticleMgr::AddParticle(..., Emmiter*, ...)`, `ParticleMgr::RemoveParticles(Emmiter*)`, `ParticleMgr::RenderParticlesUsingLines(...)`, `ParticleMgr::Update(int)`
- `TrailEntity::LoadFromFile(EntityData*)`, `TrailEntity::Init(Object3D*)`, `TrailEntity::AddSegment(...)`, `TrailEntity::Render()`
- `ParticleData::LoadFromFile(EntityData*)`
- `ScriptEmmiter::DisplayEffect()`
- `StatesMgr::CleanEmitters(bool)`, `WeaponAccessory::EnableTrail(bool)`

These are VERIFIED real demangled symbol names, **NOT recovered function bodies or call graph**. They demonstrate effect/trail/particle classes in the original executable but DO NOT prove that `Dummy_Back` triggers RUSH, or specify FX atlas file names, exhaust flame geometry/color, emitter rates or right/left offsets.

Public period-specific iOS controls/review corroboration: https://www.videogamer.com/reviews/20100507070001-iron-man-2-review/ (hover thruster UI and flight mode) and https://www.pocketgamer.com/iron-man-2/review-1481/ (flight/hover by jets). These do not verify any internal socket or paired back jet values.

## Critical quaternion/coordinate correction

`MarkVI_hover_t800_worldpose.json` and `WarMachine_fly_t800_worldpose.json` in the older **B6** prototype were generated BEFORE the B7 verified quaternion conjugation correction. DO NOT treat these older XYZ poses as final/accurate engine-world coordinates. Original node **parent/local XYZ and parent graph** from `MarkVI_original_rig.json`/`WarMachine_original_rig.json` are raw source and valid. For real per-frame nozzle positions, resolve live animated hierarchy using the B7 quaternion convention and apply B22.2 model root transform, then verify projected positions on original textured armor mesh.

## Implementation plan (under user-approved B22.4–B22.6)

1. `Stage1`: only original `DummyE_Foot_L/R` candidates (after rig orientation and material emitter verification).
2. `Stage2`: those two plus `DummyE_Hand_L/R` candidates; zero back emitters explicitly asserted even if back node exists.
3. `Stage3 RUSH`: same four plus *two explicitly mapped nozzle outputs* **only once** nozzle symmetry is validated against original armor body/FX scene. `Dummy_Back-node` can provide parent-frame location but not automatically invent real L/R source positions. Temporary procedural two-point layout, if user chooses it later, MUST be labeled new VFX design, not source restoration.
4. Find the full original 248,613,763-byte iOS 1.0.0 IPA or 275,580,565-byte 1.0.3 IPA through a user-supplied private accessible source. Scan `Payload/IronMan2.app` archives for `ParticleData`, `TrailEntity`, `ScriptEmmiter` definitions, texture atlas and effect/config resource references. Reconstruct true `Dummy_Back` asset/name linkage and effect atlas, then validate in desktop renderer/real device. Connected Drive query for `IronMan2`, `Iron Man 2`, `Iron_man_mark6`, `textures` yielded no accessible results in this turn; current private GitHub research archives do not carry verified original FX texture atlas.
5. Zero experimental Vita B17 replacements now. B17 hardware report still pending under standing agreement; preserve B15. The six-socket host module currently requires `valid` per socket and should only activate source-proven attachments after rig-data bindings are constructed.

**Finding level:** model effect attach-point names = VERIFIED ORIGINAL; exact back center = VERIFIED ORIGINAL raw bone local; separate two back vents = NOT VERIFIED; original original particle graphics = NOT RECOVERED; effect code symbols = VERIFIED NAMES ONLY; stage selection = NEW USER-APPROVED Vita DESIGN.
