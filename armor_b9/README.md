# B9 Five original armors + animation completion
Hardware B8 was **successfully verified by the user on a real PS Vita**: original Mark VI and War Machine animation works, ground/flight switches, on-screen instantaneous ~18-23 FPS for these models, ~27 FPS Stealth. The user reported missing Mark VI forward flight, War Machine landing, and missing animations for Mark IV/Stealth, plus absence of Mark V from the viewer.

## Source audit
Both original user-owned Iron Man 2 iOS IPA versions carry `suitcase.bdae`, `LC_MC_SuitCase.bdae`, `MC_SuitCase.tga` and a reflection texture. The SuitCase model's 629 vertices, 902 triangles, 25 bones, and PVRTC texture have been extracted and visually inspected; it is the characteristic red/silver Mark V suitcase suit. The original inverse bind transforms agree with the recovered 96-node rest skeleton within ~1.4e-5. The `models/suitcase.im2t` file is derived from the user's original 2010 iOS asset, not an AI model.

`mark4.im2t` and `stealth.im2t` have byte-identical positions and UVs to `mark6.im2t` (802 vertices) so the original Mark VI motion streams can safely be shared by vertex order while retaining their own textures.

## Changes
- Select five armors: Mark VI, Mark IV, War Machine, Stealth, Mark V (SuitCase).
- Mark IV/Stealth: original Mark VI hover, walk, landing, forward-flight poses retargeted by identical vertex layout.
- Mark VI: fast horizontal forward-flight **retargeted from the original WarMachine_Aim_Fly_M** animation. This is original IPA motion, not a native IronMan clip.
- War Machine: original IronMan_Fly2Ground landing keyframes retargeted to War Machine bones and vertices (no original War Machine landing named clip found).
- Mark V: its **own** skinned motion-baked data from original IronMan hover/walk/landing/float-forward clips; its 629 vertices and red/silver texture remain original.
- Original B8 target shooting/range and controls unchanged.
- Unique VPK `IronMan2_Armor_B9.vpk`, ID `IM2F00006`; prior B8 `IM2E00005` is not overwritten.

All five passed native C animated-pose/rest-pose restoration tests, base B7 and B8 tests passed. Animated frames were visually sampled with the native C renderer. Actual Vita B9 FPS and control behavior are **not** verified until user installs; no performance guarantee.

Source overlay `armor_b9/b9_overlay.zip` plus existing immutable project build layers. Keep this GitHub repository PRIVATE because it carries original licensed game assets.
