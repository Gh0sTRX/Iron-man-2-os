# Iron Man 2 — animation archive investigation (2026-10-12)

**Real source:** user-provided `IronMan2_1.0.0_ios_2.2.1.ipa` containing `Payload/IronMan2.app/anims` and `models`.

## Newly verified
- The `anims` archive lists **972 individual .anim records**. Their leading length-prefixed name tables were parsed successfully for **972/972** records.
- 248 animation names begin with `IronMan`, and 56 with `Warmachine` (case-insensitive).
- Concrete original clips: `IronMan_Aim_Float_idle.anim`, `IronMan_Air_land.anim`, `IronMan_Aim_Ground_move_F.anim`, `Warmachine_Aim_Fly_M.anim` and `Warmachine_Aim_Float_idle.anim`.
- For `IronMan_Aim_Float_idle.anim` the name table includes **38 strings**, with 31 of 37 non-path strings appearing as text in original `Iron_man_mark6.bdae` and `Iron_man_mark4.bdae`; names include `Bip01_Spine` and `Bip01_L_UpperArm`.
- For `Warmachine_Aim_Fly_M.anim`, **41/41 non-path names** are found in original `warmachine.bdae`, including `Bip01`, arm/leg names, `Gun01`–`Gun04` and `WarMachine`. An additional table string is the developer's historical `.bdae` animation source path.
- This is a **file-name / joint-name correspondence check**, NOT decoded animation keyframes, bone-parent hierarchy, bone transforms or per-vertex skin weights. Do not claim working original animation yet.

## Engineering implications
The new investigation links the animation clips to target model names and shows that the character assets embed the same joint vocabulary. The original game's actual arm/leg articulation remains blocked by animation transform data decoding and proper rig/skin reconstruction.

Short path to satisfying Vita gameplay:
1. Keep **Asset Beta**, **Flight B4** and **Performance B5** as separate rollback builds.
2. User-reported B4 FPS was 13–15; request hardware B5 **FPS, CPU MS, SDL MS** when available. Do not infer B5 hardware gains from desktop benchmarks.
3. Reverse engineer a *single* Iron Man/War Machine idle or hover clip, then `ground->hover->fly` transitions, rather than attempting all 972 at once.
4. Use a controllable small scene with collision/flight + repulsor feedback as the first playable vertical slice, while keeping original Iron Man 2 engine port a longer-term separate goal.
5. Preserve every verified hardware milestone in `PROJECT_HANDOFF.md` in this private repository.

## Attached tools
The user can access `IronMan2_Animasyon_Tarama_2026-10-12.zip` in this chat; it contains `anim_audit.py`, `animation_inventory.csv`, `ANIMATION_AUDIT_README.md`. The audit script requires only Python 3 and the user's IPA. No copyrighted keyframes are embedded in the audit package.
