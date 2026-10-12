# Iron Man 2 B15 | corrected third-person mechanics / original action census

**USER-VERIFIED B14 limitations:** camera should orbit suit HEAD, horizontal movement & right-stick pitch felt reversed, War Machine and Mark V had frozen ground-idle poses, user wants three analog-proportional flight stages, and three-target clearance locked out firing. Experimental B15 addresses these in independently compiled source. THE NEW B15 HAS NOT YET RUN ON A REAL VITA.

B15 keeps five user-owned original 2010 IPA armors and prior 31 motion streams; adds **5** authentic .anim-derived skinned streams (War Machine own aim ground idle, War Machine IronMan_run retargeted run, Mark V idle, Mark V slow air move, Mark VI slow air move) = 36 original-derived IM2V payloads.

Ground mode: Mark IV/V/VI/Stealth standard idle and normal walk/run; War Machine its own ground idle + retargeted IronMan run. Air mode: small stick = upright slow hover motion; large stick = horizontal flight, hold Triangle-selected boost + strong stick = increased speed and RUSH pose. War Machine never claims native RUSH; uses true WM original horizontal fly with higher velocity at boost. Flight threshold logic is ours, NOT demonstrated original engine physics.

B15 camera rotates around a constant resting suit head-height pivot, including camera pitch orbit sphere. Model heading orientation fixed to agree with camera-relative movement, left-stick horizontal inverted by default because user observed inversion. Right-stick Y inverted by default. D-pad LEFT toggles horizontal move inversion; D-pad RIGHT toggles vertical look inversion; D-pad UP/DOWN zoom distance. Calibration status shown in HUD.

Repulsor continues functioning after third hit; after 1.35s new targets spawn automatically. Shots and total cumulative hits remain tracked internally, collision still uses 2D projected target radius (not full physics). All animation ownership is one pose selection + smooth transition from B14.

**Full original mechanics metadata audit**: research/B15_Original_All_Mechanics_Audit.zip contains 972 decoded animation metadata entries, all 304 original IronMan/Warmachine named keyframe clips, evidence-coded action families, 10,760 symbol strings from original iOS Mach-O, 1,149 filtered game system names, and 119 MainCharacter methods. These are NAMES and motion resources, NOT decompiled complete behaviors or confirmed count of gameplay abilities.

Overlay: mechanics_b15/b15_overlay.zip applied after B14 in CI; new app ID IM2K00010; independent VPK IronMan2_Mechanics_B15.vpk. Hardware FPS/control validation still required. Old B14 and B13 preserved.