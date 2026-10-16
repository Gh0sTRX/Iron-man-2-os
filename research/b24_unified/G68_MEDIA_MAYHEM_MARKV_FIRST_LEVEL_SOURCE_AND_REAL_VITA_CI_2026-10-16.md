# G68 — Mark V suitcase / iOS Media Mayhem first-level playable vertical slice — 2026-10-16

## VERIFIED GitHub facts
- Branch: `feature/b24-unified-gameplay`; do not touch protected previous G67/G65 or stable device baselines.
- Full workflow: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38885906487 (COMPLETED/SUCCESS).
- Native host C mission tests: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38885885502 (SUCCESS).
- G68 artifact ID **12039049497**: `IRONMAN2_B24_G68_MARK_V_MEDIA_MAYHEM_SOURCE_CANDIDATE_VPK`; ZIP archive 6,075,265 bytes. 14-day retention; VERIFY expiry before sending links.
- Inside ZIP: `IronMan2_B24_G68_MarkV_Expo_Combat.vpk`, Vita TITLE_ID `IM2G68001`.
- VitaSDK/vitaGL native executable, eboot, SFO, VPK zip CRC and asset layout verified in run 38885906487.
- This is a **build-only verification**. NO actual Vita hardware test, FPS, input behaviour or graphical outcome confirmed by owner yet.

## Original 2010 sources recovered and genuinely used
- Full original user-owned 1.0.0 iOS IPA retrieved to temporary GitHub runner only, not committed.
- Actual native first-level C1L1 G65 22,441 owner original triangulated faces (32 materials, 31 original textures, 67,323 interleaved packed vertices).
- Actual native G59 collision 1,910 original triangles.
- **Mark V = genuine original `suitcase.bdae`**, its own vertex topology: 1 source primary mesh, **902 actual triangles, 629 source BRES weighted/skinned body vertices**. This is not a recolored Mark VI model.
- Original `MC_SuitCase.tga` 512x512 PVR decoded with prior B9/Underwater calibrated BGRA->RGBA ordering.
- Seven genuine IronMan original 2010 source `.anim` tracks B13 weighted skin baked to Mark V at 20fps: `Ground_Idel`, `Aim_Ground_move_F`, `Aim_Ground_idle_Att`, `Aim_Float_idle`, `Fly_F_RUSH`, `Ground_Combo_1`, `Air_land`. Native VitaGL VBO updated only when 20Hz pose frame changes.
- Real original source inverse-bind check less than 0.0002. Original animation files are not claimed to be connected with the game's original scripted controls/timings.

## What G68 beta actually implements
- Isolated derived G67 3D controller/camera/floor and G59 wall-clipping code; original scene VitaGL rendering.
- Square: repeated repulsor pulse with 0.92 forward-facing cone; L: prototype melee; Cross hover; Triangle/Circle up/down; R flight Rush; left analog move/right analog camera; Up reset mission; Start pause; Select HUD mode toggle currently has limited effect.
- 2 prototype drone waves, 2 + 3 holographic diagnostic hit-target stand-ins, health, AI ranged damage cooldown, hit detection, HP, finished/lost and restart.
- Original 2010 iOS Media Mayhem begins Mark V demonstration at Stark Expo and a robot attack (contemporary review). But this implementation's enemy positions/damage/timers/HP are **G68 prototype**, NOT original level1 CLARA node/world transforms or verified iOS AI and collision LOS.
- HUD is diagnostic bars/reticle/progress ticks, not authentic source window assets.
- Source city and G59 source collision compiled in; PS Vita collision, textures, animation orientation and performance **not validated on device**.

## Crucial missing features before user-requested **FULL playable first mission**
1. Execute faithful original `level1.bclara` Lua 5.1 `Mission000_OnStart` / `Mission_Go_to_attack` mission condition chains and camera intro transitions, scripted trigger/checkpoint/save/win/fail from source rather than demo rules.
2. Render 9 source-proven intro enabled civilian/Deco actors (G42/G43), plus choose genuine original first-stage Drone BRES model/rig/animations with exact spawn instances and source-level enemy AI.
3. Native original audio/VO/musical cues and intro/outro cutscenes, authored camera poses, PVR/alpha/shader fidelity and remaining city mesh/node transform corrections.
4. Actual native Vita hardware tests and realistic FPS; no 30/60 FPS promised. G68 '7 clip' coverage is a small subset of existing G10 248 playable-character authored source candidate clips.
5. Obstacle-aware enemy LOS and collision; current source triangle wall checks affect player movement, not repulsor line-of-sight.

## Source layout / build reproducer
- `research/b24_unified/g68_media_mayhem/g68_pack_source_mark_v.py`
- `research/b24_unified/g68_media_mayhem/g68_suitcase_runtime.h`
- `research/b24_unified/g68_media_mayhem/g68_mission.h`
- `research/b24_unified/g68_media_mayhem/test_g68_mission.c`
- `research/b24_unified/g68_media_mayhem/g68_assemble.py`
- `research/b24_unified/g68_media_mayhem/g68_build_ci.sh`
- `.github/workflows/b24-g68-vita.yml`
- G67 untouched; all generated assets, original IPA and built executable are excluded from Git source and created as CI temporary build products.

## Device QA for owner, if they choose
Install the extracted VPK as `IM2G68001`, leaving B24 G67 `IM2G67001` and known-good tests unchanged.
Check visual Mark V red/silver atlas / proper 3D orientation, camera and floor; arm articulation idle/walk/hover; square fire targets; L melee and kill 5 targets across 2 waves; input Pause only START; restart D-pad UP; FPS screenshot. Record any crash, graphics corruption, floating camera, texture errors or enemies behind walls.
**Do not report full original level complete**. Next iteration should prioritize original Drone_Army/Floating source rig/mesh, exact source original Mission000 events, no repeated VPK until real advances.
