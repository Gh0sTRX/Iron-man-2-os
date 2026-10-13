# B24 UNIFIED GAMEPLAY — TEK OYUN / TEK SÜRÜM KARARI
**Sahip:** kullanıcı tasarım kararları; **13 Ekim 2026**. Bu dosya bir *aktif geliştirme sözleşmesidir*, salt araştırma planı değildir. **B17'ye geri dönülmez.** B17 sadece doğrulanmış Vita temelidir. B22.6'ya kadar üretilen host modülleri, diğer B19/B21/B22/B22.1/B23 kaynakları ile birlikte **tek B24 oyun çalışma ağacına** taşınacaktır.

## Kullanıcı talebi (önceki planların üstünde öncelik)
> "17'den başlamış gibi görünüyoruz ... birkaç saattir ve birkaç sohbette derlediğimiz B22.6 ... bütün yapmamız gereken ve yapmaya çalıştığımız her şeyi baştan sona ... devam ederek."

Bu talep, *önce tek başına GPU floor demo/VPK çıkart, sonra B22.6'ya dön* yolunu geçersiz kılıyor. **GPU + hareket + savaş + animasyon + HUD + kamera + VFX aynı B24'in sprintleridir.** Uçuş ve kamera PC laboratuvarlarının hazır olması, oyun içine entegre oldukları anlamına gelmez. B24 kabulü için yalnızca .c dosyalarını VPK içine koymak YETERSİZDİR: oyun döngüsü, doğru gerçek zırh pozları, gerçek video/render, giriş ve performans doğrulanmalıdır.

## Tek ürün ve değiştirilemeyecek kurallar
- 2010 Gameloft Iron Man 2 iOS sürümü kaynak varlıklarını kullanır; yeniden yazılan Vita C/C++ motoru. Özgün iOS C++ motoru tam decompile edilmedi. **5 özgün zırh** B17 hardware temelidir.
- B17 PS Vita testinde hareket **çok iyi**. Kök kullanıcı deneyimi ve serbest kamera korunur; yeni full stick analog gate girerken yaklaşık .96, bırakırken .88; gerçek fizik güncelleme ve anim geçişleri dünyayla tutarlı.
- **Ground, hover, Stage2 flight, Stage3 RUSH** doğru fizik + gövde yatış, smooth look-follow third-person chase, RUSH FOV. B17 **Z-up/XY ground** ile B22 flight/camera **Y-up/XZ ground** karıştırılmamalı; tek kabul edilmiş eksen sözleşmesi/adapter gerekir.
- Stage1 hover: **yalnızca AYAK iki itici**; Stage2: **AYAK + EL**; Stage3 RUSH: **AYAK + EL + İKİ SIRT**. Stage2 sırt iticisi **SIFIR**; RUSH bitince sırt parıltısı kalmaz. Gerçek BDAE 'Dummy_Back' bir tek original center node; iki ayrı orijinal çıkış henüz kanıtlanmamış; efekti kaynağa sadık veya açıkça geliştirdiğimiz prototip olarak ayır.
- B21 controls goal: R held repulsor/fire; L missile-only target lock; Square genuine melee; Triangle RUSH; Circle flight toggle; right-stick camera free look; D-pad vertical/weapon switching must have **non-conflicting** layout. B22 classic/hybrid/immersive HUD; B22.1/B23 lock only when missile selected and held with real visible target.
- Ranged attacks arbitrary `shots % 3` Beam1/2/3 random cycling forbidden. One verified repulsor fire/recover pose protocol; WM genuine relaxed walk (not slowed Iron Man run), WM glide preserved (user liked it), WM flight-to-fly leg kick and hover->ground arm spike removed.
- Landing pose must wait actual foot-ground touch/collision (not toggle or animation timer). Genuine melee animation clips and hit boxes.
- B24 renderer aims **Vita GPU geometry/texturing/depth**, old software 480x272 renderer as **one compile-time diagnostic fallback**, not as primary future architecture. Don't attach vitaGL to an SDL_Renderer-owned context simultaneously; choose one present/swap owner and profile real hardware FPS/AN/CPU/UP/COPY/PRES.
- B19 2-wave host loop + enemy hit/collision, genuine drone/boss assets, C1L1 original environment, sound pipeline and original mission scaffolding are **same game feature backlog**, not a claim of completed source restoration.

## Integration ledger — no restart, show truth
| Layer/source from earlier conversations | Currently proven | B24 runtime wiring still needed |
|---|---|---|
| B17 5 armors, camera, physical locomotion | REAL Vita user test DONE, movement loved | Preserve base, eliminate premature threshold, animation bugs, FPS |
| B19 host_gameplay/hit | Host tests | Actual enemy models, one game state/HP, collisions, HUD |
| B21 controls, pause, menu, 480x272 HUD | Host C11 modules | Replace B17 conflicting SDL button mapping, game pause integration |
| B22 visor / B23 missile lock | Host C11 modules | Correct B16 weapon enum/real target ID and projection |
| B22.2 directional 3D flight | Host C11 module | Resolve Z-up↔Y-up and original IM2V frame root pose, real world geometry |
| B22.3 camera | Host C11 module | B17 real view/projection and target lock, smooth shoulder/chase/rush |
| B22.4–6 VFX + rush + melee camera | Host C11 module | Animated source sockets/original particles, correct render pass and B19 enemy |
| B23 BDAE socket recovery | Original Mark VI + WM local/parent names VERIFIED | Rig-to-IM2V pose with B7 quaternion correction, two true back emitters still unknown |
| Post-B17 GPU floor | Host mesh 484 vertices/726 indices + mocked GL call | Vita GL context/swap, original armor GPU textures, A/B actual hardware |
| Original IPA 1.0.3 | Drive metadata 275580565 bytes VERIFIED | Connector raw download >256MiB (HTTP 413); need safe extraction/workaround for original FX data |

## B24 build and acceptance rule
1. **Single work tree**: reconstruct B17 known-good source/asset overlays using existing private pipeline, then apply B24 change set and bring all required prior C sources as *compiled and connected systems*. Retain original B15 fallback.
2. **One world/anim state authority** per frame: input -> movement -> contact -> state/pose -> world target/combat -> camera -> VFX -> renderer -> HUD -> present. No parallel competing B17 and B22 simulation on the same actor.
3. **GPU and all gameplay advance together.** Source-only host code commits are okay, but no separate low-content floor/GPU demo is presented as the new game release. First B24 VPK candidate should contain multiple visible/user-testable improvements at once, not merely a new file copy.
4. **Truth labels**: HOST TEST PASS / VITA SDK LINK PASS / VITA REAL FRAME VISUAL PASS separate; do not claim eye-tested effects before hardware. Every disabled/fallback feature remains clearly listed until enabled.
5. Regression: each suit ground idle/run, WM hover, takeoff, stage2, RUSH, bank, camera back, landing contact, ranged animation + muzzle, missile-only lock, HUD, optional melee focus + enemy, original scene slice, FPS metrics. Acceptable real FPS determined by hardware.
6. A single B24 candidate after validated compile; do not continuously spam Actions or generate multiple half-working VPK releases. This is **NOT** a decision to stop work or wait for a special GPU milestone first.

## Git workflow
The development branch `feature/b24-unified-gameplay` isolates the unified successor from stable `main` B17. No B17 overwrite. C/C11 module integration and graphics pipeline will be tested and maintained as one branch. Commit statuses and exact VPK artifact links only when actually built. This scope supersedes ROADMAP documents that still label B17 untested or recommend separate GPU-only releases.
