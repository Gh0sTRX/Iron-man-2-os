# Iron Man 2 iOS — original mission configuration archive (research, 2026-10-12)

Verified directly from the user's 1.0.0 IPA: the named asset package `Payload/IronMan2.app/clev` contains **10 records**, from `level1.bclara` through `level10.bclara`; total archive 2,939,343 bytes, named payload bytes 2,939,140.

In the `.bclara` binary records, human-readable schema labels include:
`Mission`, `Objective`, `NextMission`, `SpawnPoint`,
`MCondition_KillEnemy`, `MCondition_Protect`, `MCondition_Collect`,
`OnStart`, `OnComplete`, `OnFail` and `FightBoss`.

**Accuracy boundary:** this is only archive extraction and schema-marker inspection. No mission state machine, instance values, spawn coordinates, waypoint paths, 3D environment, enemy AI or collision has been decoded. Ten files do **not** automatically prove exactly ten playable missions.

Reproducible Python audit and exact SHA256-indexed CSV:
`research/Original_Level_BCLARA_Audit.zip`. Uses standard Python only and the user's original IPA.

Next: decode BCLARA object graph and references, identify first mission's actual spawn/goal data, then locate matching scene/environment geometry before claiming a restored original mission. The B10 profiler is a separate performance test and does not include a level.

Keep extracted copyrighted game resources in this **private repository**.
