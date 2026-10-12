# B16 — real original 2010 armors / 3D combat sandbox

Built independently from B15; uses 2010 IPA original meshes and 27 new original animation clips with original BDAE skinning, in addition to B15's 36 streams (63 total). Code and gameplay behavior are independent reimplementations, **not a recovered original game engine**.

## User-verified issues B15 -> B16
- Idle hover wrongly held repulsor arms up (Aim_Float_idle). New *authentic* IronMan_Air_Idel arms-down animation retargets for Mark IV/V/VI/Stealth.
- WarMachine Aim_Ground_idle/Float_idle raised a palm; selects lower-arms `Warmachine_Aim_M_Ground_idle` and `Warmachine_Aim_M_Float_idle` (genuine original clips).
- Flight Stage 1 analog 0.16–0.77, Stage 2 >0.77; 0.70/0.77 hysteresis. Normal fast/RUSH unchanged otherwise.
- Repulsor muzzle now from original skinned palm mesh vertex for each armor, with native palette-derived per-vertex arm weight masks; Unibeam from original mesh chest vertex, not screen fixed line.
- New 3D ray-vs-sphere hit tests, simple auto-regenerating 3-target waves, missile target cone and projectile preview, Unibeam press/hold/release energy charge, 3D proximity melee and throw, combat Combo1-3, strong punch, air strike, dodge, solid-world AABB test obstacles. Targets use 3D coords. Projectile missile damage is currently computed at lock time rather than physical collision along the way.
- SELECT now cycles *Repulsor/Unibeam/Missile/Melee/Grab/Dodge*, Square fires; holding Square charges Unibeam. Old SELECT VSync moved to desktop V diagnostic. Analog/head-pivot and user inversion toggles preserved.
- All 27 new skinning clips plus exported vertex masks validated and archived in private `combat_b16/b16-overlay.part00..06`. Joined ZIP SHA256 `e488190ea10b2de53ab624efb64c475e15404c2eeb47e1b959be70cf428b2e33`.
- Native regression tests B7-B16 green, plus two neutral/beam rendered previews from C renderer (not PS Vita screenshots).
- **Not original game fidelity**: attack values/energy/missile mechanics newly authored. No original enemy AI, stage mission script, full QTE system, grab animation for all suits, continuous 3D missile collision or GPU rendering. Original catalog contains 304 named player character clips; *not 304 separate skills*.
- New experimental title ID IM2L00011 (does not overwrite known-good B15 IM2K00010); VPK `IronMan2_Combat_B16.vpk`, official VitaSDK build must pass CI. Real Vita hardware test REQUIRED before runtime claims.
