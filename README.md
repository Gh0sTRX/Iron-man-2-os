# Iron Man 2 — PS Vita Asset Beta

Experimental homebrew 3D model viewer built from the owner's iOS game asset files.

**This is NOT a full Iron Man 2 game port.** The project currently displays four extracted armor models. Flight, missions, enemy AI, and animation are not implemented.

## Build

The private `source/IronMan2_Vita_GitHub_Ready_CI.zip` contains the C11 renderer, four model/texture data files, model integrity checker and CMake configuration.

GitHub Actions -> **Build Iron Man 2 Vita Asset Beta** runs tests and builds `IronMan2_Asset_Beta.vpk` with `vitasdk/vitasdk:2026.08`.

When the workflow succeeds, download the `IronMan2_Asset_Beta_VPK` artifact from the run's Artifacts section. Actual PS Vita hardware testing and frame rate measurement are still required.

Because the original game assets are copyrighted, **keep this repository private** and do not publicly redistribute the game content.

## Controls

Left analog: rotate camera. Right analog / D-pad up/down: zoom. Cross: next model. Square: wireframe toggle. Triangle: reset camera. Start: exit.

## Source lineage

The ZIP was generated from previously shared V3 source files with an additional missing desktop preview tool restored. Model geometry is experimental; visual fidelity and rig/hierarchy restoration remain unverified.
