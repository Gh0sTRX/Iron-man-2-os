# B6 Original Animation Decoder — VERIFIED 2026-10-12

## What has actually been decoded

Two original user-supplied iOS IPAs:

| IPA | App version | Animations | Parsed end-to-end |
| --- | --- | ---: | ---: |
| IronMan2_1.0.0_ios_2.2.1.ipa | 1.0.0 | 972 | 972 |
| Iron Man 2 iOS 3.0.ipa | 1.0.3 | 989 | 989 |

All 972 shared `.anim` binary payloads are **byte-for-byte identical** between both IPAs. The 17 additional 1.0.3 animations are `man1_*_IPad.anim` (9) and `woman1_*_IPad.anim` (8).

Source fingerprints SHA-256:
- 1.0.0: `4c338c71cdd2817afb10099b90834c911d3c82e94adc477f24a9f9f4e0479c94`
- 1.0.3: `a118b887cb59f76268ef1814a84a8b64812f218a636002ebd953d60e885356ec`

## Binary format (directly validated on both game versions)

The `anims` asset archive uses its known length-prefixed filename/entry index. Each entry contains:
1. `u16 name_count`; `name_count` repetitions of `u16 length + Latin-1 name bytes`.
2. Exactly `name_count` **translation channels** (name order):
   - mode `0x01`: 3 little-endian float32 constants.
   - mode `0x00`: little-endian u16 frame count; each frame is **signed int32 time_ms + 3 float32 translations**.
3. Exactly `name_count` **rotation channels** (same name order):
   - mode `0x01`: 4 little-endian signed int16 packed quaternion components.
   - mode `0x00`: u16 frame count; each frame is signed int32 time_ms + 4 signed int16 quaternion components.

Packed quaternions normalize to approximately 1.0 when divided by 32767. A special enemy spider clip begins at -66 and -33 ms, requiring signed timestamps. Original quaternion component convention, scene basis, skeleton hierarchy and vertex skinning are **not yet independently proven**.

1.0.0 has **5,419 animated translation channels**, **18,619 animated rotation channels**, and **962,221 total constant/keyframe values**. All 972 clips consumed without trailing garbage. 1.0.3 has 5,520 animated translation and 18,957 animated rotation channels and 983,310 total values, every clip consumed exactly.

## Working source/runtime

Private source bundle: `research/B6_Animation_Decoder_Runtime.zip`
- `anim_decoder_b6.py`: full per-bone animation decoding and complete 972/989 audits.
- `export_im2a.py`: converts selected IPA clips to compact .im2a files.
- `im2a_player.c/.h`: C11 .im2a loader and normalized quaternion/translation interpolation; can be compiled for Vita.
- `test_im2a.c`, `verify_b6.py`: compiled native C player and 45 sample evaluations successful; 5 IM2A binary round-trips matched.
- `clips/`: 5 original Iron Man / War Machine motion datasets plus a negative-timestamp spider test.
- `IronMan2_B6_Orijinal_Animasyon_Hareket_Goruntuleyici.html`: offline **joint-local quaternion** inspector, not a skinned 3D armor animation.
- Two CSVs of fully parsed clips.

**No new VPK yet**. This is a real code and animation data milestone, NOT skeletal animation visibly running on Vita.

## Next work to ACTUALLY animate armor on Vita

1. Recover BDAE **node parent graph, rest/bind poses, mesh joint indices and weights**. BDAE is game-specific; don't blindly apply newer Gameloft BDAE templates.
2. Confirm quaternion ordering and coordinate transform against real model or original animation.
3. Bind decoded positions and rotations to the original Mark VI or War Machine mesh with correct skinning. Create independent B6 hardware test VPK while preserving B4/B5.
4. Check performance. B4 actual ~13-15 FPS; B5 Vita diagnostic FPS/CPU/SDL still unreported, so no invented claims.
5. Only then expand to full movement, repulsor, real map and missions.

## Context carryover

User asks for steady progress without re-explaining when token context ends. Read `PROJECT_HANDOFF.md` and this research note first. Private repo must stay private due to extracted game data.
