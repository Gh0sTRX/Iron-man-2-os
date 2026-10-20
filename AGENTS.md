# Iron Man 2 (Gameloft iOS 2010) -> PS Vita — engineering agents

This is the **existing** private Iron Man 2 iOS-to-PS Vita preservation/port project. Work inside this repository, on `feature/b24-unified-gameplay` unless explicitly instructed otherwise. The user currently operates from the ChatGPT mobile app and expects concrete commits/tests, not repetitive status reports.

## Non-negotiable scope

- Port/reconstruct **original** Gameloft Iron Man 2 iOS 1.0.0/1.0.3 gameplay. Original-source data beats plausible guesses. Mark every unverified rule, animation, hit window, collision, spawn, rendering property and native call as **unknown**. Never turn a synthetic host fixture into proof of hardware gameplay.
- Work order stays: **1. true initial world root/ground walking -> 2. hover/Stage2 flight/rush -> 3. G8 player and War Machine original animations -> 4. authentic original weapon/combat/damage -> 5. original Stark Expo city, character/car scale, environment LIGHTING/shadows, sky/moon, texture alpha, HUD/camera -> 6. Mission000/QTE/NPC/cutscene/audio -> 7. same-commit integrated host QA + Vita ARM ELF, then only one authorized VPK.** Lighting is mandatory and must not be dropped or reordered.
- User explicitly asks for **NO NEW VPK** until pre-VPK acceptance gates pass. Do not package, publish, upload or install any VPK, IPA, proprietary game assets or PS Vita firmware. Keep CI artifacts source/diagnostics only. `source/IronMan2_Vita_GitHub_Ready_CI_R2.zip` and previous GitHub Actions build artifacts are historical source inputs, not proof of a finished port.
- No invented story spawn point, arbitrary teleport, widened collision, erased original wall face, guessed rig/moveset, fabricated sun values, fake lighting screenshots or 60-FPS claims. Preview only authentic-rendered GIF/PNG when actually generated; user does not want interactive HTML or AI-generated game screenshots.
- Never leak private Drive URLs, PUP/IPA bytes or secret material into public source or CI artifacts.

## True current state and evidence (2026-10-20)

- Original C1L1 **G66C 1910 triangles** and collision source have host tests; historical **G161** PS Vita gameplay was user-tested with **walk-in-place**, unnatural scale, absent/incorrect sky/lighting and incomplete animation. Later G171/G278/G279/G296 **ARE NOT physically Vita tested**. Source-only G171 120/120 host ground/flight acceptance does not prove Vita controller/renderer behavior.
- G276: **same authored local XY** on different original Z floor layers can be blocked (0/8 directions) or accepted (8/8), so changing Z blindly or deleting G66C wall 715 is forbidden. Authored CLARA local MC/PositionDummy XYZ is not proven runtime story-world spawn.
- G277: source collision reject categories. G278: first 3 successfully rendered game-world boot/GPU/camera samples in Vita main. G279: optional `ux0:data/ironman2_g279_walk.csv` first BOOT and contiguous WALK120 CSV. **G296 now queries the original G66C floor at each real WALK120 endpoint instead of silently reporting stale/zero support.** This measures but **does not fix** walking.
- G279/G296 authoritative source: `research/b24_unified/g279_vita_walk_persistent_trace/`; offline analyzer is `g279_analyze_Vita_walk_trace_TR.py`; original boot and source tests are `research/b24_unified/G279_REAL_VITA_FIRST_RENDERED_WALK_EVIDENCE_CSV_SOURCE_ONLY_2026-10-20_TR.md`, `research/b24_unified/G276_G278_REAL_EXPO_Z_LAYER_WALK_COLLISION_AND_VITA_FIRST_RENDERED_WORLD_BOOT_TR_2026-10-19.md`.
- Source readiness gates are **all currently false** in `research/b24_unified/g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json`; do not relax them to ship.
- Historical G161 was located and loaded as an archive in Vita3K. Vita3K official 3.74 main firmware was installed in ephemeral GitHub CI. **G295** fails in stock GitHub Ubuntu CPU Vulkan with `vk::Instance::enumeratePhysicalDevices: ErrorInitializationFailed`; earlier OpenGL needed 4.4. This is an **emulator host GPU blocker**, not proof that the game boots into playable world. Do not burn cycles rerunning the same default GitHub runner without a new supported graphics hypothesis or GPU-capable machine.
- The complete native PS Vita ELF integration workflow (no VPK) is `.github/workflows/g171-2010-source-sculpture-false-wall-ground-walk-G169-full-ARM-NO-VPK.yml`; reconstructs transient `work/src/main.c` in CI, not a directly committed `src/main.c`. Avoid editing imaginary root source trees.

## Immediately repeatable no-VPK tests

```bash
python3 research/b24_unified/g279_vita_walk_persistent_trace/test_g279_real_source_patch_guards.py
python3 research/b24_unified/g279_vita_walk_persistent_trace/test_g279_offline_vita_csv_analysis.py
cc -std=c11 -Wall -Wextra -Werror -pedantic -O2 research/b24_unified/g279_vita_walk_persistent_trace/test_g279_bounded_csv_writer.c -lm -o /tmp/g279_test_host_c11
/tmp/g279_test_host_c11
```

The narrow quick CI is `.github/workflows/g279-walk-trace-host-source-only-NO-VPK.yml`. For full game source and VitaSDK `im2_beta` **ELF-only** verification, use the G171 workflow above and verify individual job steps; that compile is *not* device render proof.

## How to proceed, in priority order

1. Read latest source and Action logs, reproduce a **specific** failing check. Fix one root cause per change; never add unrelated G-numbers merely to inflate progress.
2. Finish ground movement's original engine-world root -> camera -> G8 GPU pose vs G75 original surface authority chain. When device trace becomes available, classify cause with G279/G296 CSV, then patch only evidence-backed source. For now choose host-verifiable bugs/tests; record the physical Vita gap.
3. Commit code plus a regression test, inspect fresh green GitHub Actions run, and give an honest short Turkish report: what changed, which CI actually passed, what remains unknown.
4. Preserve the stage order, especially **real original lighting** at stage 5. Full Vita gameplay and performance claims require GPU/device evidence.

Do not ask the user to re-send previously provided links or spend time on repeated Vita3K driver failures. Only request input when technically indispensable.

## G298 renderer and VPK workflow safety (2026-10-20)

- Source `research/b24_unified/b24_gpu_g68_city.c` now explicitly uses `GL_MODULATE` during experimental G95 four-Sun source-position vertex RGB lighting; it restores preceding texture environment for armor/HUD. This is a textured-city **render contract**, not decoded native Gameloft lighting/shadows. G71 source alpha/depth must be unchanged.
- Fast renderer mock/source C test (synthetic-only atlas, no original assets): `.github/workflows/g298-expo-source-light-texture-modulate-alpha-host-NO-VPK.yml`, run **39492824279 SUCCESS**. Full same-source VitaSDK `im2_beta` ARM ELF-only build: G171 run **39492921146 SUCCESS**. Still no physical Vita G298 lighting observation.
- WARNING: historical G106 `.github/workflows/g106-device-feedback-alpha-sky-sun-flight-fire-test-VPK.yml` had a push trigger on city source; G298 source change inadvertently triggered a legacy private test-VPK artifact (NOT installed or approved as next tester). This has been fixed by removing **all automatic push triggers** and placing G255 `--require-ready` as the first manual step. **Do not reinstate auto VPK**, and do not use that old artifact. Final one-VPK policy is still binding. GitHub Actions artifacts from old runs may exist; they are not proof of an approved current build.
- Detailed [G298 Turkish handoff](research/b24_unified/G298_ORIGINAL_EXPO_FOUR_SUN_AMBIENT_TEXTURE_MODULATION_RENDER_QA_NO_VPK_2026-10-20_TR.md). Ground physical QA remains open; Flight Stage2/Rush phase stays primary, source lighting is parallel stage-5 groundwork, not a reordered acceptance gate.

## G299 animated suit environment source light candidate (2026-10-21)

- G298 modulates **textured city** with the **experimental** G95 four source-local CLARA Sun positions. G299 extends only that **candidate** to the existing single animated IM2T/IM2V suit draw: optional uniform moving-actor brightness, `GL_MODULATE` during suit, original atlas alpha and original GL texture mode restored afterward. This is **NOT** original Gameloft native shading, per-triangle normals, world-transformed source Light, shadows, or device-verified improvement.
- Read `research/b24_unified/G299_EXPO_FOUR_SOURCE_SUN_ARMOR_AMBIENT_LIVE_GPU_STATE_NO_VPK_2026-10-21_TR.md`. Host test `.github/workflows/g299-suit-source-ambient-original-four-sun-no-vpk.yml` (**SUCCESS** run 39506543873) compiles real renderer with synthetic/mock VitaGL, not a physical screenshot.
- **Important integration:** G70 can copy current repository `b24_gpu_suit_vitagl.c` (already containing G299 opt-in) into temporary `work` *before* G168 appends its authentic `native_bind_min_z` suit foot fix. G299 installer must then add CMake option only, **never replace G168's foot-bound source with the old unpatched renderer**. See `g299_install_suit_light_after_G168_G279_NO_VPK.py` and guarded tests. Do not mistake an already present opt-in macro in transient `work` for a fatal duplicate if no CMake option was installed. Real Vita ARM full integration status must be checked via latest G171 workflow.
- User's stage order stays flight primary; lighting candidate is parallel stage-5 source work. No VPK, no claim real armor/vehicle lighting or 2010 physical shadow solved.
