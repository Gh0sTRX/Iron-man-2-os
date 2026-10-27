# Historical reconstruction index

The original reconstruction recipes and per-stage reports remain at their
existing paths so historical evidence and links stay reproducible:

- `research/b24_unified/*apply*`, `*install*`, `*patch*`, `g*/`: old source
  transformations and research evidence; do not apply them to `src/`.
- `.github/workflows/g171-…NO-VPK.yml`: manual-only historical ZIP/artifact
  reconstruction. It no longer owns or builds the current canonical tree.
- `work/`: ignored historical generated snapshot, preserved locally for audit.

Active implementation is `src/`, with `CMakeLists.txt`, `cmake/`, `tests/` and
`tools/`. Active build is `.github/workflows/source-build.yml`. Historical
generators are not automatically replayed on new source changes. They are
retained in place instead of moving hundreds of linked evidence files.
