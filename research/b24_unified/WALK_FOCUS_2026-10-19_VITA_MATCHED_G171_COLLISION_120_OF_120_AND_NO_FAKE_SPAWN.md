# Walking-only root-cause result — G171 Vita source parity 120/120

Date 2026-10-19. Branch `feature/b24-unified-gameplay`. **NO NEW VPK / NO REAL PS VITA DEVICE TEST THIS TURN**.

## Concrete bug we found and fixed (in TEST configuration, not by moving the player)

In actual reconstructed Vita `work/src/b14_world.c`, `b14_world_init()` initially sets XYZ=(0,0,0); movement from left-stick enters `b14_world_tick`, then original C1L1 G75 collision. Real GPU actor root already receives camera.player world XYZ; this is not an automatically missing GPU translation.

Original 2010 authenticated G66C 1910 triangles test **at XYZ=(0,0,0)** permits 8/8 first small moves. Therefore prior hypothesis that the port origin inherently has no floor / that we should set arbitrary Z was **falsified**. A source-valid foot Z0.0725 at that same XY also permits 8/8, and inventing a new 'native 2010 start position' would be an error. Unmerged experimental code to auto-teleport to candidate original floor was **deleted** from GitHub and NEVER integrated into Vita game.

The historical G167 actual B14+G75 120-frame test originally compiled `B24_G108_SOURCE_VISUAL_WALLS=1` but OMITTED **`B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL=1`**, whereas the real Vita ARM ELF CMake has `-DB24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL=ON`. Without G171 strict, source `c1l1_diaosu.tga` render-only opaque sculpture triangles were imported as unverified physics walls. The archived host test under the WRONG flags reported **15/120 ground move frames; only 0.9802 original map units**, flight **9/120, 0.8845**. This was not trustworthy evidence of a Vita runtime root problem.

The G167 host test was recompiled with EXACT same G171 strict wall policy as real Vita ELF. [**SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39325585211):
- **Ground B14+G75: 120 accepted / 120 proposed, 10.0702 original map units in 120 frames**
- **Flight: 120 accepted / 120 proposed, 22.7642 map units**
- Actual source road at (-160,-160,Z2.6937): grounded 120/120, air 120/120
- Raw MC CLARA *local* XY(-1.319,-6.747) footZ0.0725 remains blocked 0/120; this is NOT proven original runtime MC world feet XYZ. Never teleport there just because sourced from local record.

The C11 `replay_g167_real_B14_G75_from_initial_spawn.c` now contains a **fail-closed assertion under `B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL`**: 120/120 exact real B14/G75 grounded and flight and >9 grounded world units; an accidental future revival of pseudo-wall collision now fails the full Vita game workflow. The real G171 workflow's G167 C flags were corrected, and its path trigger now includes G167 source. The actual 2010 G66C authored walls/triangle positions and B14 speed/animation/flight physics were **not changed**. This is a valid source-test regression correction, not a new physical Vita build or an original iOS gameplay code port.

## Why the user may still see a stationary character on their PS Vita

The user's prior on-device VPK is OLDER than the source/ELF-only corrections. G171 compiled a real Vita ARM `im2_beta` ELF successfully in GitHub earlier but did not create/distribute a new VPK, under user's instruction to wait for one full integrated package. Thus **the prior physical observation does not test this latest G171 source**. It would be incorrect to say the device bug is fixed until a real VPK/install/debug log tests it. G227/G229/G277/G278 read-only Vita observability has also been compiled but has no real hardware logs.

**Priority remains ONE:** ground input→B14 world proposal→G75 real collision→GPU actor in full Vita runtime. No other research/lighting changes, no VPK, no invented player spawn. Existing lighting mandate in step 5 stays in its original order.
