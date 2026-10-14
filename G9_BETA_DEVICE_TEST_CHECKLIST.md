# Iron Man 2 PS Vita — G9 experimental beta / hardware test checklist (2026-10-14)

**G9 build ID:** `IM2G00034`. Independent from existing G8 `IM2G00033` (no uninstall).
**Status:** experimental candidate; real Vita device FPS/visual fidelity has NOT yet been verified. This sheet does not guarantee fully textured maps, working enemy AI, weapon particles or authentic original mission progression.

## Exactly what C1L1 integrates
- Original 2010 C1L1 GPU scene: 370 actual source meshes, 37,946 render vertices, **22,919 GPU triangles**; grouped terrain/buildings/cars/light fixtures.
- Separate original static legacy CPU debug map removes 3 degenerate faces (**22,916 triangles**), not the GPU scene.
- Original verified city collision C1WC: **1,908 triangles**, of which 1,690 steep wall candidates. Check if invisible surfaces incorrectly block traversal on Vita.
- Enlarged B14 traversal to original subset x[-270,273], y[-297,191], max altitude 36. This is NOT a recovered authored mission boundary/spawn; collision level source spans beyond these rough bounds.
- Authentic C1L1 UV and 94 source-material labels, but **unknown source material→diffuse texture bindings** for roads/buildings. Vehicle atlas only is independently source-authentic and already passed C1TX conversion. Therefore a gray/pseudocolored city or texture artifacts are EXPECTED; not proof that no map geometry exists.
- Actual enemy spawns, target locks, in-game objectives, lighting effects, original mission scripts still incomplete.

## New in G9 candidate (compared with G8)
- Preserve 59 original shipped stream aliases and B14/B16/G6–G8 controls/physics.
- Stage 304 new original 2010 source-skinned player clip streams (Mark VI 802v and War Machine 1292v), lazy 2-frame playback on supported stages. They are **not** all 304 live selectable gameplay states.
- Mark VI original directional walk, hover, cruise, RUSH + 3-hit source melee chain; WM original hover, fly and directional repulsor full-body _Att selected on accepted shot, fallback G8 59 if absent.
- WM six original 2010 rigid-Gun01–04 and Green source marker IM2K diagnostic streams; one synchronized stream follows B14 world state. **No proof** that marker tip is a real projectile muzzle; **no live Gatling bullets, missile particles or enemy damage**.
- WM 20s active/20s cooldown prototype source logic has NO target data in G8: do not expect independent shoulder Gatling to acquire nonexistent actors.
- Underwater 34 partially skinned clips intentionally **NOT** in playable G9; 29 original auxiliary vertices not bound.

## Recommended real Vita QA sequence
1. Install G9 as a **separate app alongside G8**; do not delete the G8 title. On first boot photograph the menu, version/title, any black screen, boot failure. Note install error code precisely.
2. Record FPS in stock clock ground idle for 20–30s, HUD/crosshair center and shoulder position; inspect if city geometry is visible behind model. If game exits, send `ux0:data/` G8/G9 boot trace/crash logs if available.
3. Move left/right/forward and hit building/wall. Check natural joystick, visible collision, character stuck in wall, camera attachment, FPS drops.
4. Hover/flight Stage 2 and RUSH: crosshair stays centered, actor centers during advanced flight, full-city traversal and max altitude ~36.
5. Switch to Mark VI: short walk→hover→left+right repulsor. Repeat with War Machine. Inspect smooth clip transitions, hand position and working laser/shot event.
6. Mark VI melee Square bursts: single, double, triple in the current combat mode. Check if 3 real source clips animate. **Do not expect authentic hit reaction until enemies implemented.**
7. Pause and return to main menu; test resume and all buttons. Compare G8 and G9 before rating performance. Send 30–60 seconds video and separate still screenshots if practical.

**Beta acceptance:** Title ID G9, actual VitaSDK full compilation, VPK ZIP integrity, mandatory 5 suits, original 22919 GPU geometry, C1WC, owner car C1TX, 59 +304 IM2V and 6 WM IM2K, original source selection string consistency.

**Known non-goals:** original material textures for road/buildings, all 2010 boss/enemy actors, real rocket/gatling muzzle emissions, original authored full mission path, verified 60FPS physical hardware performance.
