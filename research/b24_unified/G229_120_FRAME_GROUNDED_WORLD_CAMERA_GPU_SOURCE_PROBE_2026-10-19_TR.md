# G229 — 120 ardışık Vita karelik yürüyüş / kamera hareket teşhisi

**19 Ekim 2026 · `feature/b24-unified-gameplay` · VPK yok, oynanış fiziği değiştirilmedi.**

## Neden G229?

Fiziksel PS Vita testi G161'de animasyonun oynayıp karakterin yürüyerek haritada ilerlememesi sorununu gösterdi. G171 özgün 2010 geometri duvarlarının kaynak analizinde hatalı çıkarsanmış bir heykel collider'ını ayırdı fakat bunun donanım kök nedenini çözdüğünü iddia edemeyiz. G226 ana kaynak zincirinin B14 → kaynak çarpışması → `camera.player_xy` → GPU armor root dönüşümü olduğunu gösterdi. G227 bir kareye ait sayısal veri topladı; G228 `camera.cam_xy` pozisyonunu yanlışlıkla hedef gibi yorumlayan ve GPU root farkını kaçıran hatalı sonuç sınıflarını düzeltti.

**G229** artık **120 ardışık başarıyla çizilmiş ground kareyi** toplayabilir. 120 kare 2 saniye demek değildir: düşük FPS'de daha uzun sürebilir. `SDL_GetTicks` farkı ayrıca kaydedilir.

## Yeni kaynak ve entegrasyon

- `g229_vita_ground_motion_window/b24_g229_ground_trajectory_window.h`: orijinal G227 snapshot yapısını okuyarak `B14_path`, `accepted_world_path`, `GPU_root_mismatch`, `collision_reject`, `B14_idle`, kamera/world **gerçek yer değiştirme vektörlerini**, G8 kaynak klip bulunamama sayısını toplar. Yalnız B14 kaynak Vita **Z-up dünyasının XY yatay koordinatlarını** inceler. Bir karelik kamera–oyuncu pozisyon farkından takip/lag sonucu çıkarmaz.
- `g229_install_window_into_real_vita_main.py`: **G227 ayrı kurulduktan sonra**, gerçek tek `work/src/main.c` içine aynı `B24_G227_WALK_ROOT_DIAGNOSTIC=ON` compile guard altında gözlemciyi ekler; başka B14 integratörü, sahte root hareketi, collision bypass veya ikinci GPU renderer eklemez. G229, G227 kurulmamışsa/dosyalar yoksa/anchor sayısı farklıysa/tekrarlıysa durur.
- `test_g229_ground_trajectory_window.c`: yedi **sentetik** host C11 olay tipi (kamera izliyor / sabit kamera / B14 hareketsiz / collision reddi / GPU root farklı / analog yok / ileri-geri), ayrıca kare atlama, 250ms'den uzun zaman boşluğu, uçuş, pause ve NaN sıfırlamaları.
- `test_g229_installer.py`: gerçek G227 string anchor biçimiyle hazırlanmış **yapay** bir main üzerinde kurulum, B14/GPU tek sahibi koruma ve duplicate/missing-anchor reddi.
- `.github/workflows/g229-ground-motion-host-no-vpk.yml`: gerçek depodaki G227 header'ıyla G228/G229 host testlerini derleyen **host-only** CI yolu. Bu iş akışı VitaSDK, VPK veya fiziksel Vita çalıştırmaz.

Yerel doğrulama: G229 test C11 `gcc -std=c11 -Wall -Wextra -Werror -pedantic -O2 -fsanitize=address,undefined` **PASS**; Python fixture **PASS**. GitHub'daki dört G229 kod dosyası byte-byte yerel test edilen dosyaların **git blob SHA** karşılığıyla eşleştirildi. **GitHub Actions CI sonucu henüz bu belgede raporlanmamıştır**; ARM `im2_beta` yeniden derlenmedi; gerçek PS Vita ölçümleri yok.

## 120 karelik sonuçlar nasıl okunacak?

| Sonuç | Anlamı | Sınır |
|---|---|---|
| `STICK_INSUFFICIENT_FOR_CAUSAL_INFERENCE` | Yeterli yerde hareket girdisi yok | Fizik arızası kanıtı değildir |
| `B14_NO_GROUND_TRANSLATION` | Girdi varken B14 XY ilerlemesi çoğu karede sıfır | Giriş ekseni/dt/state nedenine ayrı bakılmalı |
| `COLLISION_REJECTS_GROUND_MOTION` | B14 önerisi çoğu karede reddediliyor | İlgili kaynak üçgen/capsule indeksini sonra çıkarmak gerek |
| `GPU_RENDER_ROOT_DISAGREES_WITH_WORLD` | GPU armor root ile kabul edilen world XY farklı | Kameraya suç atılmaz, render root zinciri araştırılır |
| `WORLD_AND_CAMERA_POSITIONS_TRANSLATE_TOGETHER` | Dünyadaki aktör ile kamera yaklaşık birlikte öteleniyor | **Gerçek ekran projeksiyonu/landmark kanıtı değildir** |
| `WORLD_MOVES_CAMERA_OFFSET_CHANGED_CHECK_VIEW` | Aktör ilerliyor, kamera göreli ofseti değişiyor | Kamera davranışı, dönme ve landmark projeksiyonu ayrıca incelenmeli |
| `WORLD_MOVED_BUT_NET_SMALL_OR_REVERSED` | Toplam yol varken net dünya konumu küçük | Geri yürüme/daire çizme hareketsizlik sanılmamalı |
| `WORLD_PATH_SMALL_INCONCLUSIVE` | Yeterince kabul edilmiş dünya yolu yok ama tek neden seçilemedi | Eşik/sürüş fiziği ve kare zamanı incelenmeli |

**Eşikler `0.18` stick / `0.0001` frame delta / `0.005` root uyumu / `0.04` path / `0.15` net / `250ms` gap ve `80/120` çoğunluk değerlendirmesi tanısal prototip varsayımlardır, 2010 kaynak sabitleri değildir.** G229 bunlarla oyun fiziğini etkilemez.

## Kullanım (NO VPK)

Gerçek tek-source B24 build `work/` hazırlığından ve **G227 opt-in installer** uygulandıktan sonra:

```bash
python3 research/b24_unified/g229_vita_ground_motion_window/g229_install_window_into_real_vita_main.py
# Host validation:
d=research/b24_unified/g229_vita_ground_motion_window
gcc -std=c11 -Wall -Wextra -Werror -pedantic -O2 \
  -Iresearch/b24_unified/g227_vita_walk_world_collision_gpu_qa \
  "$d/test_g229_ground_trajectory_window.c" -lm -o /tmp/im2_g229_test
/tmp/im2_g229_test
python3 "$d/test_g229_installer.py"
```

G229 installeri otomatik çalıştırılan varsayılan derleme yoluna henüz eklenmedi; `B24_G227_WALK_ROOT_DIAGNOSTIC=OFF` varsayılan kalıyor. Derlenip fiziksel Vita'da açıldığında log anahtarı `G229_WALK_WINDOW`; gerçek cihazda şu ana kadar bu log alınmadı.

## Tamamlanmamış temel işler

C1L1'ın gerçek mission-level spawn/geometry dünya ölçeği, görünür bina/araç landmarkının ekran projeksiyonu, gerçek Vita yürüyüş kök nedeni, orijinal gece göğü/ışık/gölgeler/PNG alfa, War Machine omuz füze ve gatling semantiği, 2010 `AttackType` kaynak `event.third_u32=0/1/2/3` gerçek oyun etkisi, melee hit window, QTE 1456/Chapter1 bütünlüğü ve gerçek cihaz performansı hâlâ açık. Kamera zaman dizisi bu sorunları çözmüş gibi gösterilmemelidir.
