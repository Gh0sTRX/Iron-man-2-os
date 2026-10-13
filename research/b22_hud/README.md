# B22 HUD Forensics and Dual-Suit Visor Prototype (HOST ONLY)

**Date:** 13 Oct 2026. **B17 PS Vita not yet tested; no new VPK.** Private developer research. This folder never contains recovered copyrighted original iOS HUD texture/SWF image bytes.

## Contents
- `b22_visor.[ch]`: portable C11 480×272 RGB overlay. Three independent UI modes: `B22_ORIGINAL_LAYOUT` (2010 screenshot-guided **approximation**, not recovered original graphics), `B22_HYBRID`, `B22_IMMERSIVE`.
- Iron Man cyan+gold palette / War Machine muted metal + amber palette. Both consume **the same game stats**, mode changes only draw appearance.
- Target-lock brackets, top armor HP meter, circular lower-left map placeholder, Unibeam progress, optional shield/energy rails, warning edge marks, pause/main-menu/upgrade/mission results placeholder screens. Screen-center left unobstructed.
- `test_b22_visor.c` validates color separation, same source layout across suit variants, clean center, three modes, pause/main menu/upgrade/results, negative and NaN inputs, clipping/memory guards, and 200 deterministic out-of-frame input cases.
- `original_ui_asset_probe.py` plus `test_original_ui_asset_probe.py`: read-only candidate finder for user-owned **original IPA**. Finds likely GUI-related top-level paths and top-level/embedded `FWS/CWS/ZWS` signature candidates. Only writes manifest/summary, never dumps SWF images or copies original asset payloads. Signature hits can be false positives; **real original asset inventory remains pending**.
- `../B22_ORIGINAL_UI_ASSET_FORENSICS_AND_DUAL_VISOR_MASTER_PLAN_TR.md`: complete original Mach-O class/function evidence and authentic screenshot provenance.

## Host validation actually executed
Local reference implementation was compiled with:

```bash
gcc -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g \
    -fsanitize=address,undefined -fno-omit-frame-pointer \
    b22_visor.c test_b22_visor.c -lm -o test_b22_visor
./test_b22_visor
python3 -m unittest -v test_original_ui_asset_probe
```

Results:
```text
PASS B22 VISOR: classic fidelity layout, distinct suits, hybrid/immersive, menus, clipping/guards, 200 fuzz cases
Ran 2 tests ... OK
```
The GitHub copies are functionally equivalent to the locally host-tested source; comments were refined for private-repo use after compilation. This does **not** assert a VitaSDK compilation or on-device performance test.

The read-only scanner was also run on the actual already-built `IronMan2_Arena_B17.vpk`. The VPK contains 69 ZIP members (5 model `.im2t`, 59 `.im2v`, 3 `.im2m`, `eboot.bin` and `param.sfo`), and the GUI scan yielded **zero** named/UI/SWF candidates. This is expected for our prototype and **does NOT imply the original Gameloft IPA contains no GUI assets.**

## Roadmap and critical separation
- **Layer A: original game UI**. Restore `GamePlayUI::DrawMCArmorAndHP`, `DrawMinimap`, `DrawFullScreenInjuryMask`, `MainCharacter::DrawUnibeamProgress`, `MenuManager::LoadSWFFile`, and real original UI atlas only AFTER data is found and its visual content verified.
- **Layer B: optional Vita visor**. An added aesthetic skin on top of real game stats; Iron Man and War Machine are independent themes, not verified original UI variants. Never silently imply generated visuals were extracted from the 2010 game.
- Existing B21 `b21_hud_canvas.c` is a simpler separate prototype. B22 expands research and rendering; these two HUD modules must be **consolidated**, not double-painted, in a single future Vita integration.
- Current renderer is CPU software; later GPU pixel/raster and color-alpha/channel adapter depend on performance. No fake or placeholder game stats in release gameplay.
- Need original user IPA 248.6/275.6 MB and SWF/ASprite atlas source to actually recover true UI assets. Until then the source-style classic is a screenshot-guided layout, NOT pixel-perfect restoration.

## Usage once source IPA becomes available
```bash
python3 original_ui_asset_probe.py /private/path/original.ipa --out /private/ui_inventory
```
Output `UI_ASSET_CANDIDATES.csv` and `SUMMARY.json` (asset-candidate offsets, not extracted sprites). Manually validate SWF container, per-asset IDs, images and original appearance before remaking menus.
