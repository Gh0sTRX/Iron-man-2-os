# B17 gerçek PS Vita testi sonrası — GPU probe ve kontrol/iniş kapıları
**Tarih:** 13.10.2026. Bu dosya B17'nin ilk gerçek cihaz testi sonrasında hazırlanmıştır. **B17 artık cihazda test EDİLDİ.** B15 sağlam geri dönüş sürümüdür. Bu yeni kaynaklar tamamen **HOST / GPU port hazırlığı**dır; B17'nin içeriği değiştirilmedi, VitaGL/GXM cihaz denemesi, VPK ve Actions derlemesi henüz yapılmadı.

## Kullanıcının birebir B17 fiziksel test gözlemleri
- Genel hareketler çok iyi; mevcut B15/B17 hissiyatı korunmalı.
- Sol analog belirgin biçimde sonuna getirilmeden yürüyüş→koşu ve hover→flight hemen geçiyor. **İstek:** neredeyse FULL joystick hareketiyle geçiş.
- Repulsor ateşi alakasız farklı animasyonlar arasında gidip geliyor; tüm zırhlarda saldırı animasyonları uyumsuz. B17'de gerçek yakın dövüş klipleri hâlâ yer almıyor.
- War Machine yürürken normal yürüyüş yerine yavaşlatılmış koşma pozu kullanıyor; süzülme animasyonu iyi; uçuşa geçişte bacağı anormal yukarı kalkıyor; hover→ground sırasında kol kalkıyor.
- Hover'dan ground'a dönünce **zemine temas edilmeden** yerde/inişteymiş gibi animasyon tetikleniyor (birden fazla zırh).
- Kullanıcı düşük FPS gördü, şüpheleri renkli zeminde; ölçülmüş yeni AN/CPU/UP/COPY/PRES ms değerleri henüz verilmedi. İstek GPU tabanlı gerçek 3D renderer çalışmasına başlamak.

## Kod kökü, doğrudan B17 apply_b17.py kontrolü
- `src/b14_world.c` kaynak replacement ile yürüyüş hızı `len>=.78f` durumunda 2.4, altında 1.1. Yürüyüş/koşu animasyonu `src/main.c` `const int ground_run=!world.flying && world.speed>=.78f;` koduna bağlı. `world.speed` değeri gerçek analog ölçeğiyle doğrulanmadan runtime patch yayımlama.
- Repulsor ateşinde `b16_attack_begin(&attack,now,world.flying,palm==attack.palm_l,combat.shots%3)` çağrısı her başarılı repulsor atışına bağlanıyor. `%3` farklı Beam1/2/3 assetlerini döndürüyor; bunların tek atış cycle'ı mı, farklı durum/animasyon klibi mi olduğu özgün anim gösterimleriyle teyit edilmeli. Başarılı tek ateş döngüsünde sabit clip + kontrollü idle→fire→recover, shot hit/animation event ve uygun tamamlanma geçişi hedefleniyor; 3'lü rasgele rotasyon KALDIRILMALI.
- War Machine yürüyüş `if(idx==2 && mode==B14_WALK...) chosen=&motion13.clips[B13_RUN]`; bu B17 bilinçli geçici farklı zırh koşu retarget seçimi. Gerçek özgün normal WM yürüyüşü kodda yok. WM `B14_FLY` için `B13_FLY_NORMAL` seçimi ve `stage==3` sırasında `b17_rush_lean(&model,0.43f)` prosedürel global tilt kullanılıyor. Uçuşta bacak kalkmasının hangi pose/blend bağlantısı olduğu **henüz ispatlanmadı**; yalnızca bu yollar kaynak açısından riskli.
- `src/renderer.c` B17 patch `b17_world_floor()` dünya Z=-1 zemininde 11x11 adet 2x2m kutuyu `b17_floor_tri()` ile **piksel piksel** rasterize ediyor, iki üçgen/karo; CPU depth buffer ve ardından SDL_UpdateTexture ile ekran sunumu. Eski B10 gerçek Vita ~20FPS: CPU yaklaşık 20–22ms, SDL_UpdateTexture `UP` ~29ms; bu B17 FPS ölçümü değil, yalnız neden GPU öncelikli araştırmanın mantıklı olduğunu gösterir.
- Gerçek B17 kök eksen: Z-up, dünya zemini z=-1, XY yatay! Yeni B22.2 flight/ B22.3 camera host laboratuvarları Y-up. **Bu iki koordinat sistemi uygun matris eşlemesi olmadan birleştirilmemeli.**

## Bu turda gerçek yazılan/test edilen C11 kodu

1. `gpu_floor_mesh.[ch]`: aynı 121 zemin panelini tam 484 float vertices/726 uint16 indices (242 indexed triangles) ile GPU için hazırlıyor. Renkler ve dünya Z=-1 uygun; B17 CPU triangle rasterizer'ını çağırmıyor. 20.000 konum + sınırlar GCC ASan/UBSan host PASS. Her karo için ayrı draw call değil, tek düzenli index buffer.
2. `gpu_floor_vitagl.c`: tek `glDrawElements(GL_TRIANGLES,726,GL_UNSIGNED_SHORT,...)` çağrılı **opt-in** GPU draw adapter. Başlatılmış gerçek vitaGL context ve **B17 kamera view/projection matrisi harici şart**; bu dosya henüz gerçek VitaSDK ile derlenmedi. Host'ta `tests/mock_vitagl/vitaGL.h` ile mock OpenGL çağrıları başarıyla test edildi. Mock başlık gerçek VitaGL DEĞİL. GPU pipeline'ın çalıştığı/performans kazandığı iddia edilemez.
3. `b17_input_landing_gate.[ch]`: analog tam çevirme tasarımı, ground run ve forward flight için girerken 0.96, çıkarken 0.88 hysteresis. İleri uçuş için forward bileşeni en az 0.55, yan analog tek başına hızlı flight başlatmaz. B17 Z-up dünyasında iniş isteği görünür yüzeyle gerçek ayak teması (±0.08 geçici limit) ve aşağı/neredeyse sabit hız olmadan animasyon sinyali üretmez. 20.000 randomized host PASS. Mevcut gerçek `world.flying` kaynağı and/or landing animation seçimine **henüz bağlanmadı**.

### Host testleri
```sh
cd research/b18_gpu_probe
gcc -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g -fsanitize=address,undefined \
  gpu_floor_mesh.c test_gpu_floor_mesh.c -lm -o /tmp/test_gpu_floor
/tmp/test_gpu_floor

gcc -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g -fsanitize=address,undefined \
  -Itests/mock_vitagl gpu_floor_mesh.c gpu_floor_vitagl.c test_gpu_draw_adapter.c \
  -lm -o /tmp/test_gpu_adapter
/tmp/test_gpu_adapter

gcc -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g -fsanitize=address,undefined \
  b17_input_landing_gate.c test_b17_input_landing_gate.c -lm -o /tmp/test_b17_gate
/tmp/test_b17_gate
```
**PASS** native Linux tests ≠ actual VitaGL compilation/runtime/FPS. Do not expose/mock-link the stub header to VitaSDK build.

## Bir sonraki gerçek GPU mühendislik adımları
- 1. Ayrı `B18_GPU_AB` VitaGPU context prove-out: confirmed available VitaGL headers, shader runtime, actual screen/context creation, `glClear` + `glDrawElements` + `vglSwapBuffers` (or supported swap after inspecting the real SDK sample). Do not mix an independent vitaGL context with SDL_Renderer's GPU context, or blindly call both present functions. Once correct pass chosen, preserve old CPU renderer as a compile-time/reference A/B mode. Need actual VitaSDK build before device claim.
- 2. Correct B17 Z-up `cam player_x/y`, depth, projection and culling vs GL matrix convention. Draw 121-cell floor, compare exact same position/zoom/armor, then convert one original armor mesh with UV and original texture to indexed vertex buffer. CPU-skinned .im2v frame stream may feed animated vertex-buffer upload; avoid uploading full 480x272 software frame every frame.
- 3. Benchmark separately `AN`, CPU prep, GPU submission, buffer upload, frame present and FPS; old CPU+B10 telemetry preserved. No FPS improvement promises before controlled real Vita A/B.
- 4. Synchronize authoritative input/animation and ground-contact events; use original verified skinned attack clip (not guessed three-way Beam rotation), proper WM normal walk, WM fly/ground air transition, unanimated melee replaced with real baked Combo state. Preserve working WM hover animation.
- 5. Follow original scope: user approved hover feet only, Stage2 hands+feet, RUSH additional twin-back nozzles only, new soft melee camera and partial speed-streaks; don't add unverified effects on a shaky GPU backend.

## Non-goals / honest status
Bu kaynak **VitaGPU hardware-ready release** değildir; asset/driver integration remains. B17 device-test status is now **TESTED WITH DEFECTS**. User need not retest B17; if FPS comparison desired later, capture B17 same-view CPU/UP/FPS data, but optional, not prerequisite for starting source work. Full IPA `Iron Man 2 iOS 3.0.ipa` metadata size 275580565 confirmed through Drive; connector streaming download currently returns 413 (256MiB limit), so original new WM/melee/FX source recovery is not unblocked by simply seeing metadata.
