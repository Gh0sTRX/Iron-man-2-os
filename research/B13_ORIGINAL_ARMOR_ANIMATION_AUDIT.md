# B13 — Original Armor Animation Audit / PS Vita Hardware Report (2026-10-12)

## User-verified hardware: B9 and B10
- B9 user confirmed five armors work on real PS Vita, with no visible model corruption and several authentic skinned animations working. Typically about 23–25 FPS.
- War Machine's cross-retargeted `IronMan_Fly2Ground.anim` looks like abruptly stopping in the air, **not** a plausible full landing.
- Mark V's `IronMan_Air_Move_F.anim` looks like slow aerial advance, **not** maximum-speed flight.
- Current walk clips often use `IronMan_Aim_Ground_move_F` (aimed, raised-arm repulsor stance), not relaxed normal walk.
- B10 photo A/B experiment: War Machine, VSync OFF and ON both ~20 FPS. OFF CPU~22ms UP~29ms COPY~0ms PRES~0ms; ON CPU~20ms UP~29ms COPY~0ms PRES~0ms. **Present VSync wait is not the main observed cost**; texture upload call wall-time dominates SDL phase (could include GPU sync stall; mechanism not established). Do not claim VSync OFF improved FPS.

## Original IPA verified: full named-character clip inventory
- The original iOS 1.0.0 `anims` archive was decoded again with the independent B6 binary parser. **304 genuine named armor character clips**: **248 IronMan**, **56 Warmachine**. Verified native source names, channel counts, keyframe duration, SHA256 per raw clip and partial model scene-name matches.
- The new reproducible study includes every one in `research/B13_Original_Armor_Animation_Audit.zip` (full CSV, prioritized 122 clips CSV, algorithm, complete Turkish report); original file data need not be redistributed publicly.
- Correct Iron Man candidates: `IronMan_Walk_F.anim` (1200ms) for normal walk, **not** B9's aimed `IronMan_Aim_Ground_move_F.anim` (866ms), `IronMan_run.anim` (533ms) for running, `Ironman_Fly_F.anim` for forward high flight (1600ms), `Ironman_Fly_F_RUSH.anim` and RUSH01–RUSH12 for phased faster-flight pose; `Ironman_Fly_Start.anim` (333ms), `Ironman_Fly_End.anim` (400ms), `IronMan_Fly2Ground.anim` (633ms), `IronMan_Air_land.anim` (800ms) are **different candidate transitions**, not synonyms for landing.
- **13 Fly_F_RUSH family assets are bytewise distinct**. Comparing starting local quaternions of **27 common Bip01 joints**, RUSH01 -> RUSH12 shows smooth, progressive root-mean-square angular divergence from `Fly_F`: 1.03, 2.29, 4.22, 6.56, 8.48, 10.46, 12.46, 14.47, 16.50, 18.53, 20.56, 22.60 degrees. Base `Fly_F_RUSH` ~=22.60 deg. Strong evidence of authored intermediate poses, but **does not prove original runtime state transitions or physical velocity**.
- `IronMan_Walk_F` vs `IronMan_Aim_Ground_move_F` has ~40.25° RMS starting local pose difference over same 27 joints; not just a filename distinction.
- War Machine has own `Warmachine_Aim_Ground_move_F` (866ms), `Warmachine_Aim_Float_move_F` (1600ms) and `Warmachine_Aim_Fly_M` (1600ms); **no separate named `Warmachine_Walk_F` or `Warmachine_Fly2Ground`** among 56 prefixed records. Retarget other clips only after verifying animation geometry/weapon rig.
- Further original candidates: `IronMan_Aim_Ground_Beam1/2/3`, `IronMan_Aim_Float_Beam1/2/3`, `Ironman_Fly_Left_dodge`, `Ironman_Fly_Right_dodge`, `IronMan_Jump_land`, `IronMan_Air_land_s_start/_fall/_end`. None are currently verified in Vita VPK.

## B13 next engineering target — not built yet
Keep existing B9/B10 installed as known-working builds. Build a controlled independent **animation comparison/selection prototype** only once samples are visually checked:
1. Separate **relaxed walk/run vs aim walk** with state-based selection, avoid stuck raised-hand pose.
2. Distinguish hover translation, normal flight, staged rush and flight end/landing; clip labels and world velocity are different data.
3. Frame-quality check for `RUSH` incremental poses before gameplay transitions.
4. War Machine landing must be authored/tested from matching source or verified retarget blend.
5. Backlog: GPU/SDL_UpdateTexture stall, B12 C1L1 material assignments; keep private copyrighted assets in repository.

For rigorous source data, inspect `research/B13_Original_Armor_Animation_Audit.zip` and its `B13_ANIMATION_MAP_TR.md`; experiment script `pose_compare.py`, `rush_variants.py` and `ALL_304_ARMOR_CLIPS.csv`.

**DO NOT** describe B13 as hardware-tested VPK or an original game complete port.