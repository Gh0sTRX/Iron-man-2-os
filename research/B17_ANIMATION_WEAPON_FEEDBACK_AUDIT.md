# B17 — ORIGINAL PLAYER ANIMATIONS / WEAPON AND CONTROLLER EVIDENCE (2026-10-13)

## USER-VERIFIED B16E HARDWARE FEEDBACK (authoritative observation)
User personally tested B16E on their modded real PS Vita. Its repulsor tracers visibly originate from hands, but the firing animations look disconnected from actual weapon actions; Unibeam incorrectly uses hands rather than the chest; missiles trigger an odd repulsor arm animation; melee deals prototype damage without visible melee motion. War Machine still raises an arm while walking and has no satisfactory distinct normal/boost flight posture. User wants analog-only walking/running, true world-anchored colorful 3D training ground, War Machine normal and boost retarget from Iron Man where reliable, and game-specific suit/weapon capabilities (not every suit must equip everything). User considers B16E a weak transitional prototype; retain B15 good controller feel as benchmark.

## Facts verified directly in private original IPA inventories
- `research/B15_Original_All_Mechanics_Audit.zip` includes `B15_COMPLETE_304_PLAYER_CLIPS.md` with **248 IronMan + 56 Warmachine = 304** original named character clips, drawn from 972 original iOS 1.0.0 .anim records. The complete list contains more than attacks: idles, transitions, damage, bosses, actions and QTE. This does not imply 304 different usable player actions.
- Normal vs aimed gait: `IronMan_Walk_F.anim` 1200ms vs `IronMan_Aim_Ground_move_F.anim` 866ms. `IronMan_run.anim` 533ms. `Ironman_Fly_F.anim` 1600ms; `Ironman_Fly_F_RUSH.anim` 1600ms plus twelve distinct `RUSH01..12` poses. `IronMan_Air_Idel.anim` 1600ms supports relaxed hover.
- Relevant ORIGINAL melee: `IronMan_Ground_Combo_1.anim` 266ms, `_2` 300ms, `_3` 500ms, `IronMan_Ground_ComboPower1.anim` 600ms, `Ironman_Ground_ComboPower_a/aa/aaa/ab/aba/abb` plus unique end branches, `IronMan_Air_CounterAtt.anim` 899ms, `IronMan_PushAway_Ground.anim` 1333ms. There are 22 records in explicit combo classification, plus other attack clips. The 59 baked IM2V in B16E contain none of these direct melee/combos; they cannot magically render merely because the C combat counter increases.
- War Machine: `Warmachine_Aim_Fly_M.anim` 1600ms, `Warmachine_Aim_Float_move_F.anim` 1600ms, `Warmachine_Aim_Ground_move_F.anim` 866ms, `Warmachine_Aim_M_Ground_move_F.anim` 1600ms, `Warmachine_Fly_Att_s.anim` 1600ms and `Warmachine_Fly_Att_ready.anim` 200ms. No named War Machine-specific `Walk_F`, `Fly_F_RUSH`, or `Fly2Ground` file appears within the 56-prefix original clip inventory. Absence of those exact names does NOT prove that the original game could not walk/rush/land.
- The 59 B16E pre-baked motion datasets include `warmachine_fly.im2v` (from WM authentic source), `warmachine_float_move.im2v`, `warmachine_run_retarget.im2v` (IronMan_run retarget), `warmachine_ground_relaxed.im2v`, `warmachine_air_idle.im2v`, and `mark6/suitcase_rush01/06/12/full.im2v`. They DO NOT contain a War Machine native Rush or original grounded combo.
- All B16E weapon state, damage, lock-on, cooldown, energy and 3D sphere targets are new prototype mechanics. Do not present as decompiled original iOS engine.

## B16E bugs verified from reconstructed `src/main.c`, `src/b14_pose.c`, `src/b16_action.c`, and `src/renderer.c`
1. `main.c` calls `b16_attack_begin` for all successful ranged attacks, including Unibeam and missiles: those modes use repulsor Beam1/2/3 arm tracks as unrelated animations. Melee never starts an animated clip at all.
2. The weapon tracer emitter is set unconditionally to an animated palm vertex (`camera.emitter_vertex`); Unibeam therefore emerges from a hand.
3. `b14_pose.c` selects `B13_FLOAT_MOVE` for War Machine's `B14_FLY`, even though `warmachine_fly.im2v` is already loaded into B7 and could play as the fallback.
4. WM `B14_WALK` lacks an authored neutral B13 walk, so it drops to B7 baseline aimed-walk, raising the arm. `warmachine_run_retarget.im2v` exists as an alternate.
5. B16E `b14_world.c` uses independent `rush` button toggle for ground run, contrary to user's full-stick preference.
6. `world_grid()` initially drew only wireframe ground lines; this is not an actual colored solid floor.

## Evidence from PUBLIC sources — distinguish Gameloft iOS from different console games
- Marvel official Tony Stark profile: chest-centered Unibeam, palm/gauntlet repulsors: https://www.marvel.com/characters/iron-man-tony-stark/in-comics
- 2010 Gameloft iOS original marketing: Iron Man more agile, War Machine heavier firepower, both run/hover/fly; weapons/upgrades after levels: https://gamefaqs.gamespot.com/iphone/601312-iron-man-2-for-ipad/data
- Original 2010 **iPhone** review explicitly describes repulsors, missiles, Unibeam and fists, plus unlockable upgrades: https://www.pocketgamer.com/iron-man-2/review-1481/
- 2010 iOS review mentions both character's melee, repulsors, missiles, hover/fly and later character choice: https://www.intomobile.com/2010/05/07/review-iron-man-2-for-iphone-ipad/
- External PS3/360-specific weapon rules DO NOT prove Gameloft's 2010 iOS per-suit loadout locks. To establish mission/armor restrictions rigorously: decode original iOS mission/upgrade/save scripts, `level*.bclara`, LUA/UI tables, and equipment dependencies; do not invent capability matrix.

## B17 isolated experimental implementation (CI hardware status must be read separately)
Source patch: `research/b17/apply_b17.py`, workflow: `.github/workflows/arena-b17.yml`.
- Keep B15/B16 apps installed separately. B17 uses different VPK title ID `IM2N00013` (intended until VPK SFO verified).
- Ground locomotion auto-walk/auto-run based on analogue magnitude >=0.78; triangular input can still toggle AIR rush (not required for ground run).
- War Machine normal airborne FLIGHT chooses native B7 `warmachine_fly` rather than aim float move. Boost posture uses the available native WM flight plus a **procedural 0.43-radian lean**, NOT yet the requested true IronMan RUSH-to-WM retarget; label it prototype.
- War Machine slow walk uses existing IronMan_run-to-WM retarget rather than raised-arm aimed walk; later need original `IronMan_Walk_F` retarget to WM skeleton and genuine walk gait.
- Beam1/2/3 arm layer is called only for actual repulsor mode; chest Unibeam and shoulder missiles select geometric vertex anchors (heuristic rest-mesh vertices, NOT authentic original weapon sockets). Melee HUD explicitly calls out missing original animation.
- A checkered cyan/steel solid world floor is rasterized as genuine projected triangles with depth before armor; test arena geometry is independently authored and is NOT recovered C1L1 scene.
- Critical: DO NOT claim B17 VPK compiled or tested on PS Vita until GitHub CI verifies. Real FPS unknown, and floor rendering could worsen the documented ~29ms SDL texture upload bottleneck.

## Next highest-value reconstruction
(1) hardware screenshot and B17 stage/combat profiling; (2) adapt existing original BDAE skinning animation-baker tools and original IPA clips for IronMan_Walk_F -> WM neutral walk, Ironman_Fly_F / RUSH -> WM normal and boosted pose, while comparing bind matrices; (3) bake original `IronMan_Ground_Combo_1/2/3` and suitable WM attacks into .im2v and implement explicit melee animation state with 3D hit timing; (4) map true per-suit weapons, native effect/weapon anchor nodes and mission unlocks from game files; (5) original C1L1 small real textured geometry slice after performance measurements. Protect private copyrighted assets.
