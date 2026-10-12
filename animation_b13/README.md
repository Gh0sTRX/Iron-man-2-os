# Iron Man 2 Vita – Authentic Motion B13

Private independent B13 experimental original animation prototype built on B10. **Not** the original Gameloft engine port.

- Restored 19 new 2010 IPA-based skinned .im2v streams (original BDAE inverse bind and vertex skin weights) using `animation_b13/B13_Reproducible_Source.zip`. All five suits load; Mark IV/Stealth reuse compatible Mark VI topology.
- Mark VI normal walk `IronMan_Walk_F`, run `IronMan_run`, flight `Ironman_Fly_F`, rush pose stages `RUSH01/06/12/full`, ground idle, fly start/end.
- Mark V gets its own baked normal walk, run, flight and rush poses.
- War Machine retains tested own aim-walk and original flight; B13 uses `Warmachine_Aim_Float_move_F` for slow hover motion. The known inaccurate 'landing' retarget is suppressed during its descent; **genuine landing not recovered yet**.
- Triangle switches NORMAL to RUN/RUSH. Circle toggles grounded/flight. Square shoots; Cross changes suit; Select VSync A/B retained. Rush transitions and velocities are NEW controller logic, not validated original game state machine.
- Original B8 combat demo survives. B10 HUD measurements remain, with hardware known bottleneck SDL_UpdateTexture (~29ms) from B10 photo.
- Five-armor C test `b13_validate` PASS locally along with B7/B8/B9 and corrected tolerant floating point B10 test. GitHub CI + real Vita test require separate verification.
- Original tested B9/B10 apps are untouched. B13 title ID `IM2H00008`. Overlay chunks `animation_b13/b13-overlay.part00..05` SHA256 of joined ZIP **ec9b66b9b48ecf223fddd0b33e8c3889027de36be789516e721c9e1cc1fb0c13**. Workflow verifies digest, build, and 19 animation payload SHA256 values.
- RUSH01/06/12 are intentionally sparse illustrative stages: not the full native 12-step engine blend; no assertions of original gameplay runtime transition.

**Source of truth:** PROJECT_HANDOFF.md + research/B13_ORIGINAL_ARMOR_ANIMATION_AUDIT.md.
