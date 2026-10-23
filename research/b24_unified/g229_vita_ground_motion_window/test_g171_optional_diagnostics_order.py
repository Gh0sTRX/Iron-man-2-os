#!/usr/bin/env python3
"""Keep optional diagnostic delivery from skipping required game validation.

The G171 run for d752c82 stopped at an artifact storage quota error before
seven required source/build steps. This source-only guard does not execute
Actions, fetch assets, or create a package. It uses the workflow's explicit
step indentation, rather than adding a YAML dependency to the narrow CI.
"""
from pathlib import Path
import re
import unittest

WORKFLOW = Path(__file__).resolve().parents[3] / ".github/workflows/g171-2010-source-sculpture-false-wall-ground-walk-G169-full-ARM-NO-VPK.yml"
REQUIRED = (
    "test_g302_no_old_suit_repulsor_on_wm_switch.c",
    "test_g303_g8_wm_ground_hover_flight_one_accepted_attack.c",
    "test_g304_true_G217_StateTrack_vs_G83_guessed_secondary_hit.c",
    "test_g174_real_2010_WM_10_M_ground_stream_one_animator.c",
    "test_g159_one_native_G75_capsule_with_true_city.c",
    "test_g156_continuous_original_wall_height.c",
    "cmake --build work/build-G171-ELF-ONLY --target im2_beta --parallel 4",
    "test -s work/build-G171-ELF-ONLY/im2_beta",
    'test -z "$(find work -type f -name "*.vpk" -print -quit)"',
)


def steps(source):
    starts = [m.start() for m in re.finditer(r"^      - (?:name|uses):", source, re.M)]
    return [source[start:end] for start, end in zip(starts, starts[1:] + [len(source)])]


def validate(source):
    blocks = steps(source)
    uploads = [block for block in blocks if re.search(r"^        uses: actions/upload-artifact@|^      - uses: actions/upload-artifact@", block, re.M)]
    if len(uploads) != 1 or blocks[-1] != uploads[0]:
        raise AssertionError("Optional diagnostic upload must follow all required checks and ELF build")
    upload = uploads[0]
    if not re.search(r"^      - name: .+", upload, re.M):
        raise AssertionError("Optional diagnostic upload needs a visible step name")
    if not re.search(r"^        continue-on-error: true$", upload, re.M):
        raise AssertionError("Artifact delivery must be nonblocking on storage quota failure")
    required = "".join(blocks[:-1])
    for command in REQUIRED:
        if command not in required:
            raise AssertionError("Missing required pre-upload source/build check: " + command)
    if re.search(r"^        continue-on-error: true$", required, re.M):
        raise AssertionError("Required source/build checks must still fail the job")


class OptionalDiagnosticOrderTests(unittest.TestCase):
    def test_current_pipeline(self):
        validate(WORKFLOW.read_text())

    def test_early_upload_reproduces_historical_skip(self):
        source = WORKFLOW.read_text()
        blocks = steps(source)
        upload = next(block for block in blocks if "uses: actions/upload-artifact@" in block)
        early = source.replace(upload, "", 1)
        early = early.replace(blocks[0], upload + blocks[0], 1)
        with self.assertRaisesRegex(AssertionError, "must follow"):
            validate(early)

    def test_quota_failure_must_not_fail_validation(self):
        source = WORKFLOW.read_text().replace("        continue-on-error: true\n", "")
        with self.assertRaisesRegex(AssertionError, "nonblocking"):
            validate(source)

    def test_required_elf_target_cannot_be_dropped(self):
        source = WORKFLOW.read_text().replace(REQUIRED[6], "echo skipped ELF build")
        with self.assertRaisesRegex(AssertionError, "Missing required"):
            validate(source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
