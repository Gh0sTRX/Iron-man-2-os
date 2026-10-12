# Iron Man 2 — Combat Target Range B8 (October 2026)

**Experimental target practice only, not original game combat code.**
B8 layers on top of known-good B7/B5/B4 builds and retains four original game armors and six baked original-animation pose datasets.

### Feature scope
- Vita right analog aims a 2D on-screen reticle; Square fires a stylized repulsor tracer.
- Three targets, scoring and win state; fixed screen-space circular hit test (radius 21 pixels); cooldown 220 ms.
- Left analog moves, Circle toggles flight, R/L adjusts height; Cross switches suits; Select toggles wireframe, D-pad left/right orbit, Triangle restarts range, Start exits.
- Original B7 animation files retained: Mark VI hover/walk/landing, War Machine hover/walk/forward-flight.
- New, isolated title ID `IM2E00005`, independent VPK `IronMan2_Combat_B8.vpk`; no overwrite of previous installed demo.

### Verification
- B8 C11 unit test: forced miss, shot cooldown, three target hits, win state and HUD rendering.
- B7 animation native test: pose transition and exact rest-pose restoration.
- 4 of 4 original model files verified.
- Build with official VitaSDK container; DO NOT CLAIM Vita hardware tested without user screenshots/measurements.
- Screen-space shooting is NOT 3D bullets, mission logic, enemy AI or the authentic gameplay port.
- The B7 hardware test result is not yet reported. B4 device FPS 13–15. B5 profiling still pending.

Sources: `combat_b8/b8_overlay.zip`; reproducible CI `.github/workflows/combat-b8.yml`.

For resumed work, consult `PROJECT_HANDOFF.md`, current GitHub Actions, and ask user for B7/B8 hardware reports.
