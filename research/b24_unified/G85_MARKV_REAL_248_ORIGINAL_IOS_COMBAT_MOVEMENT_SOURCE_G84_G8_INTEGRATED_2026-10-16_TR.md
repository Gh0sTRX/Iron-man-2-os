# G85 — All 248 original IronMan clips rebuilt for original Mark V and integrated in REAL G84 main (NO VPK)

2026-10-16, owner project. **Verified CI build reports:**
- [G85 true 2010 IPA 248 clip baker](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38949763439) — SUCCESS.
- [G85 real B24 G75/G68/G84/G8 motion player Mark V integration](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38951302478) — SUCCESS.

## Concrete results

Original 2010 user-owned Gameloft IPA `anims` holds 248 IronMan .anim clips. Earlier Mark V G68 isolated candidate had only **7 clips** and 629 genuine source weighted vertices. G85 reconstructs **all 248/248 original bone channel motions for actual original `suitcase.bdae` Mark V weighted skin** using B13 source inverse bind, with original 2010 track channel data. The max rest-pose inverse-bind error is **1.35812637923e-5**, under 2e-4. Frame poses baked at 20Hz as streamed G8-native `.im2v` with exact final duration. 248 total generated raw streaming data **37.93 MiB**, no full-RAM preload; each G8 stream opens two 629v xyz buffers (~15 KB) and the G8 pose/blend buffers. Three original source clips were duration 0, correctly stored as single-frame IM2V.

G85 248 original source streams filename pattern `suitcase_ironman_*.im2v`. Existing G9/G83 native original source actor labels are doubled `ironman_ironman_*.im2v`; G85 maps `ironman_ironman_*` → `suitcase_ironman_*` by stripping only the first `ironman_` tag. This mapping was a real initial CI finding; previous false "missing" records were merely a naming prefix mismatch, resolved in final successful CI.

**Actual game source patch:** `research/b24_unified/g85_markv_full_moveset/g85_patch_G84_single_main_for_real_MarkV_629_source_NO_VPK.py`, runs **after** G75 real B24/G68 source assembly and G84 G83 main loop route. Adds `B24_G85_NATIVE_MARKV_629` compile option default **OFF** so G73 or G84 old gameplay remains unchanged until explicitly enabled in a future executable test. Source asset `models/suitcase.im2t` at actual suit index **4**, header verified **629 vertices**, same authentic Mark V geometry source. Mark VI remains original 802v; War Machine remains 1292v.

**Game integration, enabled source compile:** G83 original 2010 ground walk/run/hover/directional fly/rush/aim transitions now also recognized as true Mark V author B13 rebaked rig; G8 remains the **one true original source IM2V animation player** for 802/1292/629 respective suits. Existing G8 three-combo melee and B16 accepted repulsor trigger now reach real Mark V original source animation clips (source repulsor stems follow the same genuine naming and 2010 original file). Original arm-mask retained as fallback, never invent a second weapon event. B14 single world tick, G68 city + G75 camera/collision remain in their existing code; no second physics owner. G82 source combat math available but not arbitrarily used to invent damage on first-level missing real enemies. No VPK generated.

**Actual source tests completed:**
- 248/248 original files and exactly 629v `IM2V` 20Hz header files were staged with actual G75/G84 `work/animations`.
- Every chosen IronMan G83 motion source resolves to the correct G85 Mark V 629v filename.
- Independent host C test `test_g85_all_248_markv_true_G8_im2v_stream.c` links against **real existing G8 `b24_original_im2v_stream.c`** and opens, samples start/midpoint/end and finite-checks **all 248 genuine motion streams**, reporting 3 zero-duration source clips; success.
- Actual B24 G75/G84/G85 main source host syntax checks and **PS Vita ARM native cross compiler** checks with `B24_G84_ORIGINAL_MOVESET_ROUTER=1` and `B24_G85_NATIVE_MARKV_629=1` passed.
- Last successful CI emitted only authenticated derived .im2v and **source integration metadata**, NO VPK, no Vita game executable, and no hardware validation.

## Remaining blockers / release gate remains BLOCKED

Full gameplay behavior and all original moveset/combat not yet completed: original iOS/touchHLE attack hit windows and button buffering, exact 2010 weapon per-attack damage numeric values, NPC rigs/AI/script missions, audio mapping, WarMachine exhaust/rig and all original suit-specific stages, original source animation full body contact/transition gameplay edges. Source clips decoded and runnable by G8 DO NOT by themselves mean real iPhone gameplay semantics have been accurately reconstructed. G75 city collisions/floor/camera and lighting PS Vita QA remain outstanding. `B24_G85_NATIVE_MARKV_629` DEFAULT OFF for safety. **User explicitly requires ALL real moveset and combat before first next VPK — NEVER generate or publish VPK during G85/G86.**

## Repro

1. Run `g85_bake_all_248_original_IronMan_onto_suitcase_629_im2v.py` on original owner IPA with authentic B13 and B11 dependency bundle to produce 248 stream files, or reuse successful GitHub Action 38949763439 artifact.
2. Reassemble genuine G75/G68/G84 B24 source as previous documented verified flow.
3. Run `g85_patch_G84_single_main_for_real_MarkV_629_source_NO_VPK.py`, stage `suitcase_ironman_*.im2v` into `work/animations`.
4. Host test all 248 using existing original source G8 stream playback test.
5. Vita ARM source compile with flags only, no app/VPK. Latest successful GitHub Action 38951302478 proves all five steps.
