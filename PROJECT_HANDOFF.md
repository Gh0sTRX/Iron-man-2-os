# IRON MAN 2 — KALICI DEVIR / CURRENT PROJECT STATE
Updated: 2026-10-12 (Türkiye) — authoritative cross-conversation handoff

## Source of truth
Private repo: https://github.com/Gh0sTRX/Iron-man-2-os
Primary branch: main. Keep repository PRIVATE because it contains original game assets.
Original IPAs are in the user's connected Google Drive:
- `IronMan2_1.0.0_ios_2.2.1.ipa` (248,613,763 bytes; minimum iOS 2.2.1; 32-bit ARM Mach-O)
- `Iron Man 2 iOS 3.0.ipa` (275,580,565 bytes; actual game version 1.0.3; 32-bit ARM Mach-O)
No decrypted complete original C/C++ source has been recovered. Work is reverse engineering of assets and limited ARM symbols.

## IMPORTANT REAL DEVICE MILESTONE — VERIFIED BY USER
On 2026-10-12 the user installed `IronMan2_Asset_Beta.vpk` on their real modded PS Vita and supplied a screenshot showing the in-app Mark VI textured mesh. They explicitly confirmed **ALL FOUR** playable viewer selections — Mark VI, Mark IV, War Machine, and Stealth — display successfully and can be inspected with Vita controls. This is VERIFIED HARDWARE FUNCTIONALITY, not a desktop mockup. They did not yet report a measured FPS.
The result is **a standalone PS Vita textured model viewer**, not a port of the original Iron Man 2 game. No walking, missions, flight, combat, enemy AI, game audio, rigging or original gameplay exists in this VPK.

## Latest green CI build
Workflow: `.github/workflows/vita-build.yml`
Successful GitHub Actions run #4: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38176491645
Commit: `91466c220a030c30192e745412b9a1b8a4ff5325`
Artifact: `IronMan2_Asset_Beta_VPK` (artifact ID 11715913190).
Private source archive tracked at `source/IronMan2_Vita_GitHub_Ready_CI_R2.zip`, 1,839,515 bytes.
Pipeline: unzip; check four `.im2t` models; desktop C renderer preview; official VitaSDK `vitasdk/vitasdk:2026.08` build; validate eboot.bin; upload VPK.

## Engineering details
- Rendering: software textured triangle rasterizer in C (SDL2 for display/control), internal resolution 480x272; Vita display scales to 960x544.
- IM2T contains vertex positions/UV, triangle indices, RGBA atlas.
- Four source models and original dithered PVRTC-derived textures work on real Vita.
- Initial reverse engineering extracted 49 of 207 inspected named BDAE meshes with a heuristic parser; earlier intermediate packaging sometimes counted more geometry exports. Do not equate that with full model correctness. Other geometry layouts/rigs remain unsolved.
- Y-up GLB axis was corrected for external viewers. V3.1 HTML was fixed for WebGL-less iPhone preview, confirmed by user.
- User said Meshy viewers sometimes showed models not matching their appearance; model hierarchy/material/rig fidelity remains open.
- IPA's native ARM code contains C++/Lua-related symbol names; decompilation is incomplete and there is no playable engine port.

## Near-term roadmap (highest value)
1. Preserve a reproducible VPK baseline and documented hardware proof.
2. Prototype 2 controls in a NEW, separately named Vita test VPK: left analog movement, circle takeoff/land, R ascend and L descend, optional camera right analog. This is an ORIGINAL implementation using original game assets; **do not call it the original gameplay port**.
3. Verify this VPK via GitHub Actions and real PS Vita. Do not overwrite the known-good beta accidentally.
4. In parallel inspect original IPA `.anim` rig/hierarchy; move toward authentic run/flight animations. Eventually port level geometry, collision, enemies, missions, etc.
5. Keep project docs and version states updated at each verified milestone. Never claim background tasks ran after the chat ended.

## Continuation recipe for a fresh ChatGPT chat
Ask: "Continue the Iron Man 2 PS Vita reverse-engineering project. Read the private GitHub repo Gh0sTRX/Iron-man-2-os, especially PROJECT_HANDOFF.md and the latest GitHub Actions run. Four armors work on actual PS Vita. Continue the next verified gameplay prototype; preserve the existing VPK."

## User preference
Prioritize visibly useful milestones, efficient engineering, rigorous verification and straightforward instructions (the user isn't a programmer). The user mentioned future selectable fan-made armor packs; defer until engine/movement is established.