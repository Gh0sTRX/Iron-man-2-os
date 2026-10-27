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
Fresh remote CI results require working GitHub API access; local validation
must not be described as a remote green run.

Repository visibility is not assumed private. Original assets and private
links must not be added to the canonical tree or CI outputs. Historical
repository cleanup/visibility changes are outside this source migration.
