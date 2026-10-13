# B21 Input/HUD/Underwater — Verified research and test-only modules (2026-10-13)

**Do not install a new Vita VPK yet.** B17 real device QA is pending. This folder is **portable PC-tested C11 code and original animation metadata preparation**, not a new Vita app.

## Exact original iOS mechanics versus the Vita adaptation

Period **Gameloft iOS** sources (not Sega PS3/Xbox360):
- 2010 IGN iPad review says game auto-targets, fire-button slide upwards for chest Unibeam; suffers awkward off-screen target acquisition: https://unvis.it/www.ign.com/articles/2010/05/10/iron-man-2-ipad-review
- 2010 Pocket Gamer iPhone review says repulsors, missiles, Unibeam, melee and automatic aiming only for enemies in the player's view: https://www.pocketgamer.com/iron-man-2/review-1481/
- 2010 Macworld confirms walking/running/hover/flying and nine objectives: https://www.macworld.com/article/205532/ironman2review.html
- Gameloft original app description says Iron Man for agility and War Machine for firepower; underwater suit supported: https://gamefaqs.gamespot.com/iphone/601312-iron-man-2-for-ipad/data

**Game design decision, NOT recovered original Vita controls:**
- **R: hold to fire**; **L: hold stable target-lock on a visible enemy**; auto-aim on fire, limited cone, will be a different *soft acquisition* fallback in actual B22 integration.
- Left analogue ground walk/run automatically by intensity; while flying, Stage 1/2 based on intensity, Triangle grants air rush/boost. Right analogue orbits camera. Never force a harsh camera snap when locking.
- D-Pad Up/Down **vertical hover**, Left/Right **cycle available weapons**. This frees Square for original melee combo (after clip bake), Cross for interaction, Circle for flight toggle. Select reserved for later target switch. Start opens **Pause**, not exits.
- **Control collision warning**: original B17 has L/R ascend/descend, Square shoot, D-pad L/R live inversion toggles, D-pad U/D weapon cycling, Start exits game, and Triangle boost toggle. All must be migrated *together* in the eventual Vita main.c integration, not cherry-picked.
- Underwater **Swim direction** may require dedicated level-specific controls, not treat swimming as ordinary aircraft flight. Do not lock hero capability list without IPA mission/armor ability map.

## Portable code and tests

Files: `b21_control_lab.[ch]`, `test_b21_control_lab.c`:
- Per-frame edge/held semantics for button presses; R held fire, Square single melee, L stable target id, automatic reacquisition upon target death; no camera snap. Validates no button actions during pause, inverse camera settings, music/SFX toggles and HUD numeric normalization.
- The lock search prefers front-facing on-screen candidates and distance within cone. Current prototype uses `visible` data flag, a 3D angle test and numerical distance; world occlusion and lock line-of-sight are NOT implemented. Does not read real source weapon or targeting values.
- Pause menu code allows START to pause/unpause, Cross options, Circle back and D-Pad to select/toggle music/SFX/invert X/invert Y/sensitivity. No actual audio bus calls or persistent save yet.

Files: `b21_hud_canvas.[ch]`, `test_b21_hud_canvas.c`:
- 480x272 CPU bitmap overlay: 3 health/shield/energy bars, minimal center reticle, optional target lock corner brackets and enemy HP, masked pause/options panel.
- Numeric bars are representative prototype state, **not recovered iOS HUD textures**. Text labels have to call the existing Vita renderer's `write_text` adapter; not integrated in B17's frame loop. Not final art/style.
- Underlying C11 source was **compiled and tests passed on local Linux host** with `gcc -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer`. Both input suite (target lock persistence and reacquisition; pause and inversion settings) and raster suite (bars, lock clipping, pause panel, memory guards) were run.
- These files are separate host-only source, not a new automatically built Vita app. A VitaSDK build, device FPS, and input correctness remain untested.

## Underwater bake preparation (NO authentic .im2v generated yet)

Source research/B15_Original_All_Mechanics_Audit.zip B15_ALL_972_ANIMATIONS.csv:
- **43** `underwater_*` source anim names; **34** have the 38-joint-name Underwater player suit rig, **9** are distinct underwater ship/bomb/cannon scene objects. Includes `Underwater_Swim_F/L/R/U/D`, `Underwater_Float_2_Swim` and `Underwater_Swim_2_Float` (699 ms), Aim_Float, Swim_Att, Dodge, Swim_Hurt, Dead and `Underwater_Movie1` (unknown movie in-game usage).
- Companion scanner `underwater_manifest.py` consumes **actual B15 archived CSV**, validates source has exactly 972 entries, 43 underwater prefix clips, 34 suit-clip candidates each with 38 label entries, 9 scene objects, and outputs per-clip original name/duration/bone-label count/raw SHA256/category and candidate flags.
- Prerequisites for real skinned bake: original raw ANIM clip transform bytes + **Underwater suit model BDAE** with actual bind skeleton and skinned-mesh matching rig, corresponding original textures. Existing project repo contains scripts B6/B7 and the inventory CSV but none of these complete Underwater sources currently as usable pair. **DO NOT** retarget animations blindly onto Mark VI and announce that Underwater suit has been restored.
- `0 ms` dead idle tracks are rejected by existing .im2v clip loader (ms<100): treat as bind/static pose until examined. `Underwater_Movie1` is a 2000 ms bone animation name, not evidence of an encoded cutscene movie codec.
- Once original IPA is accessible: run scanner, use B6 original animation decoder + B7 skinning tools to bake rig-specific native `.im2v` and compare source-rest pose, root motion, timeline, FPS 20 and skinned previews. **Only then** add a new sixth Underwater suit and distinct swim physics.

## Intended B22-integration acceptance

No new build until user confirms B17 real-device behavior. Subsequent real Vita gameplay: player HP/shield from B19 game state, lock and soft aim on true enemy 3D model in LOS, genuine Unibeam chest and missile hardpoint, 2-wave combat start/clear/fail, pause/resume with audio state and save, no previous B15/B16 regression. Preserve a debug FPS/pipeline profiler panel via pause instead of permanent button reservation.


## Underwater case regression — fixed 2026-10-13
Original `B15_ALL_972_ANIMATIONS.csv` contains `underwater_bomb/cannon` with lowercase `u`, while ship/cargo has `Underwater_ship*` with uppercase `U`. Earlier metadata script used case-sensitive scene clip lookup and **would incorrectly treat six scene ship clips as 38-joint playable suit clips**. This is now fixed in `underwater_manifest.py` with `name.casefold() in SCENE_CLIPS` (commit 7d852a2).
- Original archived metadata independently verified 43 records: **34 at 38 channels**, other **9 at 4/5/7 channels**. Two 0-ms suit pose records, `Underwater_Dead_Float_idle` and `Underwater_Dead_Swim_idle`, are excluded from timed-bake candidates.
- `python3 test_underwater_manifest.py` supplies a **synthetic 972-clip CSV** with realistic upper/lower case scene entries. Checks 34/9 split, 38-channel suit, static poses, missing data, invalid non-underwater names. 3/3 regression tests passed with an equivalent local copy of the parser's classification/build logic; actual full original IPA baking remains blocked.
- This is a corrected **metadata classification**, not an exported `.im2v`, not a sixth installed Vita suit, and not a claim that we recovered Underwater BDAE geometry.
