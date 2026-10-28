# Port status — 28 October 2026

Current source: **`src/main.c` + `src/b24/`**. Build/test instructions:
[BUILDING.md](BUILDING.md). CI: `source-build.yml`. Generated `work/` and the
G171 reconstruction pipeline are historical references, not source owners.

- Source-floor-relative takeoff and the 45 cm landing stall were reproduced
  and fixed in `ee346c9`; both fixes are preserved in canonical source.
- Grounded wall clearance now also checks the accepted floor height, so a
  legal step cannot place head/feet into a wall that was clear at proposal Z.
  Safe sliding and existing step limits are preserved in host regressions.
- The complete game compiles to a Vita ARM ELF without game assets or patchers.
- Mark IV and Stealth now use the geometry-verified 802-vertex original VI
  animation bank throughout movement/aim/beam selection; their event ownership
  stays separate. Three geometry payloads match exactly; textures remain distinct.
- Mark V now routes its seven existing transition streams through G8. Its
  consecutive accepted-shot filename conversion defect is fixed in source.
- Audio catalog/conversion tooling and native music + voice + four effect
  channels are implemented. User pause covers all channels and recovers from
  individual port failures; worker lifecycle
  flags use atomics. Authentic gameplay effect bindings and fade units remain open.
- Empty/truncated looping PCM now terminates instead of hanging audio-worker
  shutdown; regression reproduced a five-second timeout before the fix.
- Suit texture upload failures now release the failed texture and permit retry.
  Current city/suit alpha and lighting-state tests preserve original alpha and
  texture state; they do not establish original lighting or shadows.
- Current source checks: 30/30 with external original geometry/tables and
  30/30 with ASan/UBSan; 22/22 source-only plus seven separate Mach-O tests.
  Full 89-unit Vita ARM ELF links. Physical Vita and owner-input inspection
  remain unverified. The preserved diagnostic uses older source bccac1c.
- Remote CI run [40604417762](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/40604417762)
  passed both host configurations and the full ARM ELF for source `05d9206`.
  Source-only receipt: branch `evidence/source-checks-40604417762`,
  `diagnostics/source-checks.json`; it explicitly records no device test/package.
- Current host tests cover world height, pause/control timing, animation suit
  ownership, external-table validation, bounded telemetry and offline analysis.
- At migration, 181 of 191 imported code files matched the previous source byte
  for byte; eight changed interfaces/includes/observations and two only removed
  trailing whitespace. `cmake/migration-baseline.json` records that origin;
  subsequent source fixes are tracked normally in Git.
- Two original data tables were removed from the source payload. All 1028 rows
  match after conversion through the new external asset format and C reader.
- G279 walking trace remains compatible. A separate frame/dt/phase/clock CSV
  can be correlated by frame number. No new measured device result exists.

**Physical Vita:** latest user-tested version remains historical G161, with
walk-in-place and visual problems. Newer source fixes have not been tested on
the user's hardware. No new VPK or installation is part of current work.

**Still open:** authentic initial MC model/world/collision transform; physical
walking; original flight/combat/mission completeness; native lighting/shadows;
actual frame performance. Existing experimental policies remain labeled as
such. The seven full-port readiness gates remain false.

**Next gameplay blocker:** establish the original MC initial world/feet transform
from native/source evidence. Device root/FPS claims require actual telemetry.
GitHub API is blocked in the current environment. Exact-commit remote CI
results can now be read through the source-only receipt branches using Git;
local validation alone must not be described as a remote green run.

Repository visibility is not assumed private. Original assets and private
links must not be added to the canonical tree or CI outputs. Historical
repository cleanup/visibility changes are outside this source migration.

The owner authorized Drive IPA extraction for remaining assets. Cloud proxy
currently blocks that download; the local 803-sound conversion has therefore
not run on original input. A separate ephemeral CI inspection attempts the
provided input and publishes structural diagnostics only, without asset data.

Runtime network diagnosis: the managed instance reports current observations,
restricted policy enforced and no custom allowed hosts. Drive hosts are saved
in the configuration draft, not active in this runtime. Setup/start instructions
and the canonical repository revision were refreshed and exercised locally;
environment publication remains a user action. Source build/test automation runs
on matching pushes; it does not represent a developer running after chat ends.

## Latest explicitly requested device diagnostic

The owner now explicitly requests one current test VPK and supplies an IPA.
This overrides the earlier no-new-package scope for one diagnostic only; the
seven full-port gates stay false and no device/firmware installation is allowed.
The Sediment transfer rejected the IPA because it exceeds the executor's 32 MiB
limit. It has not been read. Existing verified external assets remain available.

`tools/device_test/build.py --diagnostic-current-state` now builds canonical
source, runs host and sanitizer checks, produces the SDK SELF/SFO, and verifies
one locally retained package. It includes 669 baseline-matching resources plus
the external original table bank, uses IM2DG0001 / 00.02, and records all inputs
and checks. New packaging boundary tests reject stale title/version, changed
payload/SELF hashes, duplicate/traversing paths and truncated SFO allocations.
The original audio bank and native lighting parity remain absent/unverified.

## Gameplay fixes before the requested VPK

The owner clarified: fix subsequent project problems before packaging. No new
VPK has been produced yet. Two pause defects were reproduced as failing tests:
G83/G8 source ages advanced across the menu pause, and the actual main fire
block still accepted a repulsor shot while paused. One shared pause-adjusted
clock now feeds pose/shot/beam/rigid-attachment owners. Paused presses are not
queued; paused attack transforms, WM skill/cooldown ticks and hover bob stop.
Raw SDL/G279/frame timing remains wall time. Authored durations/rates and the
single B14 world integrator are unchanged. Baseline failures and current logs
are external in `/workspace/im2-current/pause-gameplay-*.log`.

The remote branch's four Mach-O feasibility commits were merged without source
replacement; its seven synthetic parser tests remain separate compatibility
research. A static parser is not an original engine loader or boot proof.

## Produced current diagnostic — 28 October 2026

After the pause gameplay fixes, one package was built from `bccac1c`:
`/workspace/im2-current/source-test-2026-10-28/IronMan2_Source_Test_00.02.vpk`.
Title IM2DG0001 / 00.02; 94,835,736 bytes; 670 verified resource files.
SHA256 `b32029e2af3f7314ab66e8cb5769bdd57637bbee6960d802b3bd2b8338abe856`.
The packaging pipeline reran 24/24 original-data CTest checks plus seven separate
synthetic Mach-O checks, repeated with ASan/UBSan, and built the full ARM ELF.
SDK SELF/SFO, ZIP CRC, full inventory, every resource hash and identity passed.
Source-only 19/19 CTest plus seven Mach-O checks also passed. Native lighting,
original audio bank, initial story-world root and device boot remain unverified.

No original asset or package was pushed to Git or CI. The package, full manifest,
SHA256SUMS and logs remain outside the checkout. Actual chat attachment delivery
is not available through current tools; `/mnt/data` does not exist and its parent
is not writable. The active proxy excludes GitHub upload/API/Drive destinations;
those destinations are saved only in the unpublished configuration draft. Do not
claim a workspace path is a delivered attachment or create another VPK merely
to retry delivery. Preserve both this package and the earlier 00.01 diagnostic.

## Continued gameplay work — 29 October 2026

The owner asked for more development after the diagnostic. Three further
source defects were reproduced before changes:

- Main's landing query acknowledged a floor 4cm before contact and disagreed
  with the existing G75 road fallback. It now uses exact G75 support, matching
  movement's native-first/optional-road authority. This does not establish that
  original iOS treated every rendered road triangle as solid.
- Seven existing Mark V transition streams were excluded by G83 despite matching
  629-vertex bank/duration metadata. The current supported IronMan transition
  path now includes Mark V; G8 keeps its existing suitcase conversion. Landing
  still requires source support. No WM rig, native input or weapon rule is added.
- Airborne descent checked floor crossing only at old XY. Entering a platform's
  XY footprint in the same step could leave feet below its floor. Every actual
  candidate/slide now queries the crossed source floor and checks head clearance
  at accepted Z. No triangles, step limits or extra physics integrator changed.

Local checks passed: 28/28 original-data CTest, the same28 with ASan/UBSan,
seven separate synthetic Mach-O tests, and full Vita ARM ELF link. Additional
coverage: 532 original road-only support samples; 312 suit/route original-stream
matches with first/middle/end sampling; seven Mark V transition streams played
through real G8;16 synthetic descending edge/obstruction cases at shifted Z.
These are source/host observations, not physical Vita acceptance.

The existing `00.02` VPK from `bccac1c` is preserved; **these newer fixes are not
in that package**. No replacement package, installation or asset upload occurred.
Original IPA access, native initial root, sound events, lighting/shadows and
physical performance remain unresolved. Full-port gates remain false.

A fourth, more severe Mark V defect was then reproduced using BOTH synthetic
and original streams: the first accepted repulsor opened a suitcase_ clip;
the next G8 frame tried to convert the pinned native-bank name again and
returned0. Main treats that as a fatal animation error. The already opened,
vertex-validated Mark V shot now retains its bank name. Other new selections
still pass normal conversion; no weapon/hit/event policy changed. Consecutive
stationary and direction-changing frames, exact clip end, hover and cancellation
are covered. Original-data host30/30 and ASan/UBSan30/30 pass; source-only22/22
plus the seven separate Mach-O tests pass; full ARM ELF links.

Remote source CI run40774394201 passed host OFF/ON and ARM for the first three
fixes at `b968905`. The final Mark V consecutive-shot fix is being submitted
separately; that older green run must not be attributed to the final fix.

Final remote CI [40774875755](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/40774875755)
passed host OFF/ON sanitizers and the full ARM ELF for runtime source `a710a9d`,
including the Mark V consecutive-shot fix. Its exact-commit source-only receipt
is `origin/evidence/source-checks-40774875755:diagnostics/source-checks.json`.
No device test, package or owner-data publication was performed by CI.

## Owner-approved Mark IV test opponent and geometry lighting — 29 October2026

The latest owner request explicitly authorizes one refreshed00.03 diagnostic
AFTER adding combat testing and lighting work. No original enemy mesh exists
locally; owner chose the existing original Mark IV model as a clearly labelled
TEST OPPONENT, not original enemy AI. Original802v idle/hurt/combo1/death streams
are preflighted. Test HP, stationary close-range retaliation and L+SELECT reset
are separate from the native mission and its unknown health rules. B19 remains
inactive: no invisible enemies/waves. Placement requires existing source support,
body clearance and collision line-of-sight; current-origin host probe finds a
clear supported point near(0,5,.0725), a diagnostic placement, not native spawn.

Prototype B16 combat binds this real visible actor, using the GPU camera's
centred reticle and source collision occlusion for test hits. Repulsor, beam,
missile, melee, prototype retaliation, pause, reset and no mission mutation
have host coverage. New geometry lighting uses current-pose indexed normals and
the exact suit draw transform with existing experimental G75 parameters. Source
geometry/UV/atlas alpha remain unchanged; persistent scratch has uniform fallback.
This is not native enemy AI, original damage timing, or native lighting/shadows.

The new manual package version is00.03/IM2DG0001/Combat Test;00.02 stays unchanged.
All original assets still remain external. Full-port gates stay false. The
uploaded IPA remains unread due the32MiB transfer limit; original sound bank
and genuine enemy assets remain unavailable. No hardware installation occurred.
