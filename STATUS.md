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
- Audio catalog/conversion tooling and native music + voice + four effect
  channels are implemented. User pause covers all channels and recovers from
  individual port failures; worker lifecycle
  flags use atomics. Authentic gameplay effect bindings and fade units remain open.
- Empty/truncated looping PCM now terminates instead of hanging audio-worker
  shutdown; regression reproduced a five-second timeout before the fix.
- Suit texture upload failures now release the failed texture and permit retry.
  Current city/suit alpha and lighting-state tests preserve original alpha and
  texture state; they do not establish original lighting or shadows.
- Local checks: 21/21 with external original geometry/tables, 21/21 with ASan/
  UBSan, 16/16 source-only; full 89-translation-unit Vita ARM ELF links. No new
  package or physical device test. CI owner-source inspection is pending.
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
