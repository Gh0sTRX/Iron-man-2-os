# G224–G226 — özgün 2010 DoAttack olay argümanı + Vita'da yerinde yürüyüşün fizik→GPU çizim kaynağı

**18 Ekim 2026 · `Gh0sTRX/Iron-man-2-os` / `feature/b24-unified-gameplay` · VPK YOK.**

## G224 — orijinal `MainCharacter::DoAttack(int,int)` iki parametresinin gerçek ARM kaydı

[G224 özgün kaynak test PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39145102276). **2010 owner iOS** C++ method `0xF64F8` tam gerçek **646 ARM opcode** verisi, G221 tam StateTrack `Actor::UpdateStateAttack` olay çağrısından geçmiş kaynakla karşılaştırıldı.

```asm
0xF6508 MOV R4,R0              ; original MainCharacter this
0xF650C MOV R5,R1              ; original 2010 authored AttackType u32
0xF6518 MOV R8,R2              ; actual 12-byte StateTrack event[GetEvent()].third_u32
0xF6524 CMP R5,#25
0xF6528 ADDLS PC,PC,R5,LSL #2 ; 26 real native branch entries
0xF652C B 0xF6598            ; default outside range
```

**Do not rename the second `int` as missile/hit/damage/time**: original u32 source distribution `0/1/2/3` is known but semantic effect is not. G224 confirmed 13 body CMP candidates, only further true native CFG / second register dataflow analysis can assign meaning.

## G225 — 26 kaynak saldırı türü ve gerçek base Actor fallback

[G225 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39145356582). Exact native source original second event value saved in **callee-saved `R8`** and default branch back into original base C++ `Actor::DoAttack(int,int)` **0xDA5B8** without rewriting its two integers:

```asm
0xF6598 MOV R0,R4
0xF659C MOV R1,R5
0xF65A0 MOV R2,R8
0xF65A4 BL 0xDA5B8          ; Actor::DoAttack(int,int)
```

Verified native 26 ID dispatch includes **IronMan AttackType 1 and WM 18 → `0xF6930`**, **IronMan 2 and WM 25 (also ID12) → `0xF6648`**, **Beam ID4 → `0xF65C4`**. This only identifies exact code branches; it does NOT prove true 2010 user touch button or WM weapon semantics. Unlike earlier G218 metadata, G224/G225 is native original ARM proof, still **research only**.

## G226 — orijinal Vita kaynak oyunu içinde `walk→world→GPU root` köprüsünü tek tek bulduk

[**G226 başarılı tam Vita ARM ELF-only source trace**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39145998224). Old source-level audit searched `glTranslatef` in `src/main.c` and failed because current game **uses GPU renderer elsewhere**; fixed the audit to follow the real G68/G164/GPU modules; validated same native `im2_beta` ELF compiles, no VPK. The real final `work/src/main.c` source on CI:

- Left analogue / WASD → `move_x`, `move_y` (lines 444–462).
- **line 498** single `b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)`.
- Lines 509–517 genuine G75 source capsule/collision reconcile → `world.x=b75_x;world.y=b75_y;world.z=b75_z`.
- **line 736** `camera.player_x=world.x; camera.player_y=world.y;camera.player_z=world.z` and line 739 camera translated follow pos.
- **line 962** `b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)`.
- The actual runtime GPU source `b24_gpu_runtime.c` captures `frame_pose=(B24GpuSuitPose){c->player_x,c->player_y,c->player_z,...}` and calls one suit GPU renderer.
- The real suit `b24_gpu_suit_vitagl.c` computes original Z-up matrix with `m[12]=p->x;m[13]=p->y;m[14]=p->z-center_z`, G168 uses original native bind **min Z** for foot placement, then calls `glMultMatrixf(root)` and `glDrawElements`.

**Source architecture result:** no separate independently stationary GPU actor/root matrix was found in the patched flow; if `world.x/y` ACTUALLY moves, player model receives it. Host G171 with authentic 2010 G66C collider and recovered visible-wall fix had accepted ground walking, but there is NO physical Vita G226 run. Therefore **the user's actual stationary character remains UNRESOLVED**. The likely remaining source regions are: B14 actual input axis/proposed delta, collision reconciliation zeroing/sweep path, camera-follow making actor visually anchored (which is normal for third-person but environment should move), GPU/scene world coordinate mismatch, and map/model units. These are HYPOTHESES, not demonstrated causes. **We did not fake a collision bypass, player scale, physics speed, or keyboard input mapping to claim success.**

## Current honest project state / not fixed

- 2010 `states` source binary: 361393/361393 original bytes completely decoded, **55 StateSets, 1487 states, 3658 tracks**, not 100% of full IPA or entire game.
- 2010 ARM attack event chain true source: `StateData.AttackType→StateTrack::GetEvent index→event[index].third_u32→MainCharacter::DoAttack` proven by G220–225.
- G217 776 original armor states G218/G223 READ-ONLY linked to **actually loaded** G8 source IM2V frame, and unified Vita ARM ELF CI passes, not Vita hardware QA.
- **Unsolved**: grounded actor seemingly stationary on user's Vita, true world/character/vehicle scale, sky/lighting and model alpha, full War Machine Gatling/missile input & genuine Aim_M weapon semantics, original melee damage hit windows, C1L1 intro QTE/mission full progression/voice/cutscenes, complete iOS touch mappings, actual full original combat activation.

**Next meaningful hardware-oriented improvement G227:** build opt-in in-game diagnostic on real Vita which records left stick input, **B14 proposed world XY**, after G75/G171 collision accepted XY, final `camera.player_xy`, GPU `frame_pose.xy`, plus scene landmark screen displacement over 2 seconds. This will distinguish `input=0`, `collision blocking`, `world moves but camera/scene mismatches` without forcing fake movement or asking user to install frequent incomplete VPK. Keep no VPK until the original gameplay stage is ready, per user preference.