# B7 — Original character skinning restored
Private internal research milestone: original BDAE palette / inverse bind / vertex weights recovered for 2010 Iron Man 2 Mark VI and War Machine. Verified 25/29 bind matrices against the original scene rig. Six original .anim clips skinned to both character meshes and prebaked for a Vita visual test.
Source ZIP: `research/B7_Skinning_Tools.zip`.
Reproducible independent VPK overlay: `skinning_b7/b7_vita_overlay.zip`.
Workflow `.github/workflows/animation-b7.yml` compiles `IronMan2_Anim_B7.vpk` (ID IM2D00004) with VitaSDK from the B5 source and validates all six animation payloads. VPK hardware testing remains mandatory. Prior B4 hardware baseline was 13–15 FPS; B5 real device FPS is still unknown.
The earlier B6 rig diagnostic assumed an incorrect quaternion sign convention. B7 corrects this by matching the 25/29 original inverse-bind matrices to 1e-5.
Read `PROJECT_HANDOFF.md` for context. Do not expose/private-release copyrighted original assets.
