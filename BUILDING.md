# Canonical source build

`src/main.c`, `src/b24/` and root `CMakeLists.txt` are the current game source.
Build these files directly. No ZIP extraction, source patch chain, old VPK,
GitHub artifact, original executable or original game data is needed to compile.
The canonical build has **no SELF/VPK target**. Its default Vita configuration
preserves the feature definitions from the verified `ee346c9` game build.

## Host checks

Requires C11 compiler, Python 3 and CMake 3.21 or newer:

```bash
bash tools/test_host.sh
IM2_HOST_BUILD=build-sanitized IM2_SANITIZERS=ON bash tools/test_host.sh
```

These run synthetic parser, telemetry, controls and animation-owner regressions
without original assets. To additionally exercise the original geometry locally:

```bash
IM2_ASSET_ROOT=/absolute/path/to/owner-assets bash tools/test_host.sh
```

The external directory contains `assets/G66_city.g66m`,
`assets/G66_original_collision.g66c`, and optionally `data/source_tables.im2d`.
No original inputs are downloaded or uploaded by these commands or canonical CI.

## Full Vita ARM ELF

The SDK is pinned in `tools/build_vita.sh`. Pull it once if not already present:

```bash
docker pull vitasdk/vitasdk@sha256:8227da1b596d981f4513cd9b36bda1e43857f6dae5bcf4312c1cd40167f7d9bb
bash tools/build_vita.sh
```

Compilation runs with container network disabled. Output: `build-vita/im2_beta`.
`source-build.yml` executes host checks with/without sanitizers and this full
ELF build directly from tracked code. It does not upload an ELF, VPK or data.
Successful linking does not prove device boot, GPU output or performance.

## External original data

Models, animations, maps, textures, audio and original state/script tables belong
in an external owner asset directory. Preserve their existing runtime paths.
The two previously embedded generated tables are now a single versioned binary
asset loaded from `app0:data/source_tables.im2d`. It is not tracked in Git.
Missing/invalid tables leave original mission dispatch and state observation
unavailable; no fabricated states, QTE acknowledgment or mission completion.
The existing practice renderer is otherwise unchanged.

If the locally authorized generated source inputs already exist, convert them:

```bash
python3 tools/export_original_tables.py \
  --states-header /owner/source/state-table.h \
  --mission-c /owner/source/mission-prefix.c \
  --output /owner/assets/data/source_tables.im2d
```

This conversion runs once on external data, not during builds. It does not
execute the input files or fetch an IPA. The IM2D v1 format is little-endian:
32-byte header (`IM2D`, version, suit count, states/suit, event count, Lua row
count, string-pool length, reserved), four name offsets, 776 24-byte state rows,
224 20-byte event rows, up to 72 24-byte Lua rows, then bounded ASCII strings.
The reader validates exact sizes, indices, null termination and Lua prefix order
before publishing any pointers. Original raw attack ticks remain unclassified.

Local full conversion validation compares all **1028** suit/state/track/mission
rows field by field using `tests/check_table_migration.py` and the independent
C decoder. Original data and generated test dumps must stay outside Git/CI.

## Frame telemetry

Default `IM2_FRAME_DIAGNOSTICS=ON` writes the bounded optional file
`ux0:data/ironman2_frame_profile.csv`. It samples the first 3 rendered frames
and every 60th frame, caps at 4096 rows, and flushes periodically. Copy it before
relaunch: each launch replaces the previous file. Missing/unwritable storage
never stops the game. The existing G279 walk CSV schema is unchanged; join by
`frame` to correlate the two files.

Recorded: raw start-to-start interval; the actual world step and unified-control
dt; actual animation **blend** dt; total CPU frame wall time; model stream,
camera, scene/suit/HUD submission and swap wall time; world/GPU XYZ; pause state;
CPU/GPU/BUS/XBAR frequencies read from the system. Clock rates are not changed.
Animation clip age still uses its existing source clock. Differing dt caps are
made observable, not replaced by a speculative physics/timing model.

```bash
python3 tools/analyze_frame_trace.py /path/to/ironman2_frame_profile.csv
```

These are sampled CPU/frame observations, not GPU occupancy or continuous FPS.
`gpu_busy_available=0`; host clock frequencies are unknown (`-1`).

## Authorized original audio (external data only)

`tools/prepare_audio_assets.py` validates the complete original IPA and executable SHA256, the
803-entry native inline sound-name table and both previously proven Lua IDs,
then converts the original WAV data to 48 kHz stereo signed 16-bit PCM using
FFmpeg. It writes an external catalog and resumable hash manifest. It does not
infer gameplay event timing or fabricate button-to-sound mappings.

```bash
python3 tools/prepare_audio_assets.py --ipa /external/owner.ipa --asset-root /external/assets
```

Runtime catalog: `app0:data/audio_catalog.im2a`; PCM:
`ux0:data/ironman2/audio/`. Missing catalog keeps only the two previously verified
music/voice IDs. The native backend has separate music, voice and four effect
channels; the effect API requires a validated catalog. Channel tests use mocks,
not physical audio output. Original effect events and fade units remain open.

For an authorized Drive input, keep the supplied link in an external text file;
install `gdown==5.2.0` into the Python environment, then use the existing refresh
pipeline. It downloads only when needed, verifies inputs, prepares audio, runs
host checks with sanitizers and builds the ARM ELF. It never creates a package.

```bash
bash tools/refresh_owner_audio.sh --ipa /external/owner.ipa --asset-root /external/assets --drive-link-file /external/owner-link.txt
```

`owner-source-inspection.yml` temporarily reads the already supplied owner input
and deletes it on exit. Only bounded native method structure and audio conversion
counts/hashes can be saved on its separate evidence branch. No original bank,
PCM, model, IPA, binary or package is published.

The source-build workflow also saves a small `diagnostics/source-checks.json`
receipt on `evidence/source-checks-<run-id>`. It identifies the exact source
commit and host/ARM job results, without uploading a binary. A receipt is not
device playback, native lighting parity or a readiness-gate acceptance.
