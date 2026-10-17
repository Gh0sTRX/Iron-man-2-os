# G161 gerçek PS Vita fotoğraf testi → G163–G165 gerçek oyun motoru düzeltmeleri ve kalan ilk bölüm engelleri

**17 Ekim 2026 / `feature/b24-unified-gameplay` / G155 WIP=1 ilk oynanabilir orijinal C1L1**

## Gerçek cihaz kanıtı: G161 kullanıcıdan 2 fotoğraf ve yazılı gözlem geldi

- **G161 gerçek Vita üzerinde AÇILDI**; 2010 Stark Expo şehir model/dokuları, Mark V, HUD, nişangâh ve Stage2/Rush ateşi mevcut. İki fotoğrafta kaynak sahne parlak düz zemin ve gece yalnızca yıldız göğü görünür. Bir fotoğrafta görünür HUD'da 69 rakamı olabilir; **bu bir devamlı FPS benchmarkı değildir**. Fotoğraf/video olmaksızın Stage2 gerçek saniyelik FPS iddiası yok.
- Kullanıcı: Stage2 ve RUSH'da repulsor ateşi var, fakat hareket/pose hissi eksik; şehir silüeti ve ay yok; ışıklandırma/emissive çevre gölgesi yok, Unity demo hissi; karakterin boy/kadrajı küçük; nişan alırken bile hareket yönüne geriye/yan dönüyor; sadece üç yakın dövüş spam poz döngüsü; WM grounded/rush eksik animasyon; roket/Uni-Beam hareketleri yok; gerçek hikâye başlangıç konumu kullanılmıyor.
- **Bu bütün özelliklerin hazır olduğuna dair iddia YASAK.** İki fotoğraf sadece kullanılan kareyi kanıtlar; gerçek çevresel dinamik shadow, tam hareket, cutscene ve doğru storyline intro hâlâ çözülmedi.

## Orijinal veri – model ölçeği, kamera ve hikâye

- **Native source `models/suitcase.im2t` Mark V rest model Z min 0.0133 max 2.2488 = 2.2355 orijinal model yerel birim**, Mark VI 2.247213, War Machine ~2.250262. Bunlar yerel mesh boyudur; orijinal oyunun kamera/scene unit conversion/actor world parent scale'i kanıtlamaz. Kaynak avatar model ölçeği büyütülmedi.
- **G162 tek gerçek G161 B14 runtime kaynak inspeksiyonu**: `b14_world_init` `camera_distance=4.35`; GPU `b24_gpu_runtime_draw` `FOV 72deg`, `c->camera_distance`; `B14World` heading hareket `vx/vy` yönünden atan2f hesaplanıyor, aiming state'e bakmıyor. Ana oyun `world.orbit` G75 kamera recenter ve G83 aim selector kullanıyor. Native orijinal 2010 FOV/distance YOK.
- **Orijinal CLARA MainCharacter id1062 yerel XYZ (-1.319, -6.747, 25.054)**, parent-world/move scene chain çözülmemiş; bu gerçek story spawn dünya konumu iddiası DEĞİL. Native Mission000 starts with MissionPause PC1, QTE `InteractiveObj_QTE` ID1456 Show PC6, intro `Camera_start_show` ID1864 -> `PD_start`1848, `Camera_start_show2`1868 -> `PD_start_end`1852. Orijinal giriş QTE/camera gerçek akışı olmadan `B14World` oyuncuyu keyfî olarak id1062 yerel Z25'e teleport etmek kaynak sadakati değil. Doğru spawn sahne parent transform ve gerçek ilk cutscene kamera path sonrası yapılacak.

## Somut oyuna G161 üstünde entegre edilen kod

1. **G163 gerçek aim/strafe kaynak bug'ı**: B14 daima `w->heading`i hareket yönüne döndürüyordu; main'de repulsor L aim ve ground/hover için tek post-B14 heading now camera orbit shortest-arc with 22 rad/s response, independent B14 velocity & camera/reticle, Stage2/Rush unchanged. C11 host sample 60fps angular wrap/aim-off failclosed test ve **tam Vita ARM ELF başarı #39066411272**. Bu, özgün iOS aim input nativeliğinin kanıtı değil, port davranışı düzeltmesidir.
2. **G164 authentic 2010 real sky**: G73 kaynağı gerçek `C1L1_sky_001.bdae` 6 batch/288 vertex + 2 PVR. Atlas0 orijinal Manhattan gecesi/şehir silüeti (alpha), atlas1 orijinal yıldız + ay/bulut yüzü. G161 sky draw normal WORLD camera translation ile (0,0) orijinli sphere/crosstree'yi şehirden uzaklaşıldıkça sürüklüyordu; yeni GPU main sky pass yalnız rotation-only view[12..14]=0 yapar, glPush/glPop ile restore eder, hiçbir sky mesh/UV atlas ID'si icat etmez. Native original material mesh↔PVR assignment, ayın azimut yeri, dynamic shaders kesinleşmedi.
3. **G164 küçük zırh kamera QA**: aynı 2.2355 birim orijinal source Mark V modeliyle Ground/Hover 0.87× camera distance /68° FOV, Stage2/Rush eski 1.0×/72° korunur; B22 shoulder blend .0..1, yumuşak geçiş. **Physical actor/vehicle/map scale BIT-BIT aynı, yalnız oyuncu kadrajı değişir**. Kaynak orijinal iOS FOV/distance bu yeni sayılar değildir. C11 + real `im2_beta` PS Vita ARM SUCCESS #39066747904.
4. **G165 WM native original source animation routing**: G83 `aim=NONE` yerde stem NULL olduğundan animate owner eski yanlış G8 fallback'a dönüyordu. G165 `warmachine_warmachine_aim_ground_idle` + dört `aim_ground_move_[f,b,l,r]` REAL 2010 cliplerini geçici neutral directional alternatifi olarak seçer; dedicated original relaxed-idle asset/mapping halen YOK. WM Rush-specific real clip de yok; native `warmachine_warmachine_aim_fly_m` gerçek flight clip'i geçici fallback. **Yeni keyframe uydurulmadı, WM source weapon cooldown/gun rig/rocket/uni beam/firing damage değişmedi.** Real G83/G8 Vita ARM source compile hedefi #39066999083; CI sonucu ayrıca görünmelidir.

## Hâlâ eksik – gerçek orijinal oynanabilir ilk seviye

- Sky fotoğrafta yıldızlar dışında ay/skyline eksik. G164 yalnız kamera/world-view translasyonu düzeltmesi, **donanımda henüz test edilmedi**. Olası atlas/material/sky render-pass ve occlusion sorunları açık. Source skyline pixelleri mevcut.
- Lighting: G95 dört orijinal Sun kaynağına göre yalnız statik heuristik vertex tint, orijinal per-fragment shader, gerçek bina/oyuncu gölgesi ve emissive/mat property fidelity YOK. Cihazda ışık bazı kısımlarda patlıyor, gerçek global illumination değil.
- Mark V 248 orijinal klibin sadece azı gerçek G83/G8 input/event durumuna bağlı. 3 spam kombinasyon bunun sonucu; native melee combo input buffer, 13 state/8 branch, hit windows, 26 typed attack damage kaynak doğrulama hâlâ gerekli. Kullanıcıya 248/248 tam aktif deme.
- Rocket/Uni-Beam: Orijinal `aim_m_*` veya `fly_att_m` source stems var; `m` harfinin gerçek missile/unibeam olduğu kanıtlanmadı. Weapon/attack ID ile animations kaynağı bağlanmadan 2010 gerçek silah hareketleri tam diye gösterilmez.
- War Machine G165 selector düzeltmesi var ama orijinal WM dört omuz tabanca Gun01–04 rigler ve aiming/fire feedback cihazda yeniden doğrulanmalı, uçuş/rush native source mapping tamam değil.
- Original first mission PC6 gerçek QTE ID1456 visible/touch ACK, asli kamera/cutscene ve `MissionResume` olmadan gerçek hikâye başlama sahnesi/oynanabilir bölüm sonu hâlâ BLOCKED.
- CPU physics: G159 deneysel source road material solidness ve G160 CSR test başarılı ama tüm duvar native author solidity fiziksel G161 resimlerle kanıtlanmış değil. Donanım performansı tek kare sayıyla PASS olamaz.

## Süreç

G161 kullanıcı fotoğrafı üzerine gerçek motor C kaynak düzeltmeleri yapıldı, CI ile Vita ARM ELF oluşturuldu. **YENİ VPK YOK**. Sıradaki tek cihaz paketi, yüksek öncelikli diğer asli PC6 first-scene/lighting/weapon source sorunları makul düzeye inince hazırlanmalı; `G155 first_playable` release BLOCKED kalır.
