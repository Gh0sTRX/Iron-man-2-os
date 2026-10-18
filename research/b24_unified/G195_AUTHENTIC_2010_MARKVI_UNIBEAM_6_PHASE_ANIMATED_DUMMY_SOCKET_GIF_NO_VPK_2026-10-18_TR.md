# G195 — Gerçek 2010 iOS Mark VI Uni-Beam animasyonlu dummy matrisi / kaynak GIF

**18 Ekim 2026 | Dal: `feature/b24-unified-gameplay` | VPK yok**

## G195 somut ilerleme

Önceki G193 native kaynak zinciri 2010 `SceneImpl` dummy gruplarının **14=`Dummy_Chest`**, **33=`Dummy_Foot_L`** olduğunu, G194 de bu isimlerin BDAE'deki kaynak isimli bone/dummy node eşleşmelerini ve sadece dinlenim pozu matrislerini ispatlamıştı. G195, başka tahmini animasyon yazmak yerine gerçek B13 decoder API'sini inceledi: **`worlds(nodes,anim,ms)`** her orijinal `.anim` zamanında gerçek BRES node hiyerarşisini (ana-baba matrix çarpımları) örnekliyor; **`bake_pose(data,anim,ms)`** gerçek skinned IM2T/BRES mesh'i kaynak ağırlık ve inverse-bind ile anime ediyor.

Mark VI orijinal **`Iron_man_mark6.bdae`**, **96 düğüm, 802 kaynak vertex** ve B13 gerçek joint paleti / inverse bind kullanıldı. Sadece gerçek source mesh face indeksleri PNG/GIF çiziminde var, başka iskelet/motion/keyframe üretilmedi. GIF materyal shader renderı değildir; orijinal 2010 textürleri/oyun HUD'u simüle edilmedi.

| Kaynak Uni-Beam klibi | Oyun kaynak süresi | Kaynak mod |
|---|---:|---|
| `IronMan_Aim_Ground_Beam1.anim` | 400 ms | Ground |
| `IronMan_Aim_Ground_Beam2.anim` | 400 ms | Ground |
| `IronMan_Aim_Ground_Beam3.anim` | 1000 ms | Ground |
| `IronMan_Aim_Float_Beam1.anim` | 600 ms | Hover |
| `IronMan_Aim_Float_Beam2.anim` | 400 ms | Hover |
| `IronMan_Aim_Float_Beam3.anim` | 1266 ms | Hover |

**G195 CI PASS:** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39121506867. Kaynak faz süreleri toplam ground **1800 ms** / hover **2266 ms**. Orijinal keyframe örnekleme t=0,100,... ms ve kesin klip sonu değerleri; **ground 21** ve **hover 26** gerçek kaynak frame. Her kare için `Dummy_Chest-node` (parent `Bip01_Spine1-node`) ve `Dummy_Foot_L-node` (parent `Bip01_L_Foot-node`) gerçek 4×4 **BRES rig-local animated-world** matrisleri JSON'a kaydedildi.

Kaynak matrislerine göre Mark VI Ground'da göğüs düğümünün XYZ konum aralığı yaklaşık `[0.2396,0.7096,1.5367]`, ayak `[0.1980,0.0929,0.3901]`; Hover göğüs `[0.1715,0.7838,1.4352]`, ayak `[0.1135,0.2643,0.3470]` **BDAE yerel birim koordinat farklarıdır**, Vita oyun dünyasındaki metre / mermi kaynağı değil.

**İçerik:** CI artifact içinde iki GIF (`G195_REAL_2010_MARKVI_GROUND_UNIBEAM_ANIMATED_DUMMY14_33.gif` ve `...HOVER...gif`), bir PNG (`G195_ORIGINAL_2010_MARKVI_GROUND_HOVER_DUMMY14_33_SOURCE_MOTION_TRAJECTORIES.png`), matris/clip manifest JSON vardır. GIF'de gerçek Mark VI skinned source mesh ve turuncu Chest/yeşil Foot node gösterilir. **G195 ilk görüntüsünde okunabilirlik için mesh face subset kullanılmış, son revizyonda tüm gerçek BRES yüzeyleri kullanılarak delikli/clay önizleme düzeltilmiştir.**

## Doğruluğun sınırları ve bir sonraki gerçek oyun adımı

- Bu bir **host-orijinal kaynak animasyon** görünümü ve hesaplanan BDAE rig-local socket pozisyonudur. Vita ekran görüntüsü veya gerçek 2010 particle shader/beam görseli **değildir**.
- iOS native `DoAttack` içindeki 14/14/33 parametrelerinin **oyun durumu ve zırha göre hangi varyantta** seçildiği hâlâ çözülmeli; 33 sol ayak olduğu için otomatik saçma/yanlış diye değiştirmedik.
- Kaynak rig node matrisi B14 world coordinate / G168 suit foot + G83/G8 current pose owner ile henüz bütünleştirilmedi. Gerçek Vita Uni-Beam projeksiyonu/emitter ve hasar çalışıyor olarak işaretlenemez.
- Eski sorunlar: **karakter gerçek Vita'da yerinde yürüme, ölçek, çevre ışıklandırma/gölgeler/sky, War Machine gerçek native rocket/gatling, melee hit windows ve açılış QTE** açık; G195 bunları çözmedi.
- **G196 öncelik:** source native `DoAttack` 14/14/33 branche trigger conditions + G169 current B16/G8 animator same-frame timeline mapping; sonra gerçek World matrix ve beam effect/hit pencerelerinin ispatlı bağlanması. Yeni VPK hazırlama.
