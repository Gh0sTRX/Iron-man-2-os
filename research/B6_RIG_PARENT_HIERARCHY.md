# B6 original BDAE scene hierarchy + authentic joint motion (2026-10-12)

## Verified new milestone
From **Iron Man 2 IPA 1.0.0** original BRES/BDAE version `0,0,0,133`, a **72-byte tree node** structure is now understood:
- `+0x00 u32`: node name string absolute pointer
- `+0x0c f32[3]`: local translation
- `+0x18 f32[4]`: local quaternion
- `+0x28 f32[3]`: local scale
- `+0x34 u32`: child count
- `+0x38 u32`: absolute pointer to packed child array, **72 bytes per child**.

Recursive validation:
- `Iron_man_mark6.bdae`: **96 original tree nodes**, all valid, no cycles/duplicate names.
- `warmachine.bdae`: **112 original tree nodes**, all valid, no cycles/duplicate names.
- `Bip01_L_UpperArm-node` among authentic skeleton hierarchy, with original local pose.
- Original `IronMan_Aim_Float_idle.anim`: 31 of 37 non-path animation labels matched scene nodes.
- Original `Warmachine_Aim_Fly_M.anim`: 38 of 41 non-path animation labels matched scene nodes. Missing labels include scene/environment entries; they may live outside Bip01 root.

The evaluator binds `Bip01_... ` animation track labels to matching `Bip01_...-node` and propagates global transforms through the genuine tree. It generates **moving diagnostic skeleton poses** for:
- `IronMan_AirLand_Original_Rig_B6.gif` (31 frames from real `IronMan_Air_land.anim`)
- `WarMachine_Hover_Original_Rig_B6.gif` (31 frames from real `Warmachine_Aim_Float_idle.anim`)

Important precision: scene-local quaternion convention (xyzw) appears mathematically consistent with the BDAE bind rotations, but exact original runtime visual parity still needs testing. **These are diagnostic bones, NOT animated textured armor**.

## Reproducible code / results

Private bundle: `research/B6_Rig_Hierarchy_Prototype.zip`, containing:
`bdae_rig_b6.py`, `evaluate_pose_b6.py`, `export_skeleton_gif.py`, full original parent graphs and rest transforms (JSON), sample world poses, animations and diagnostic PNGs.

Already existing B6 transform decoder and C11 runtime:
`research/B6_Animation_Decoder_Runtime.zip`

## Next engineering blocker
Recover **vertex-to-bone indices, weights, inverse-bind matrices, and mesh/node association** from original 0.0.0.133 BDAE. Current GLB/Vita rasterizer exports mesh positions/UV but does not encode skeletal weights. Building a VPK now without solving skinning would only show a disconnected diagnostic skeleton or static armor. Keep known-good B4/B5 unchanged.

Also request actual Vita B5 CPU MS / SDL MS / FPS at user's convenience; B4 hardware baseline ~13-15 FPS.

All original game data must remain in this PRIVATE repository; don't redistribute assets publicly.
