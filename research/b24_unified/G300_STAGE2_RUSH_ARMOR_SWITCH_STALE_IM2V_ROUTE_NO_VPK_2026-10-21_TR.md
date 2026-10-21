# G300 — Stage2/Rush ve zırh değişiminde eskimiş IM2V animasyonunu kesme (NO VPK)

**21 Ekim 2026 — dal `feature/b24-unified-gameplay` — gerçek PS Vita test edilmedi.**

## Kanıtlı kaynak sorunu

`b24_g83_authentic_timed_router.c` 2010 kaynak G81 süreleriyle tek-seferlik animasyonu tutuyordu. `fly_ftol` (800 ms) seçildikten 30 ms sonra B14 fizik sahibi `RUSH` durumuna geçse bile, seçim 800 ms boyunca eski `fly_ftol` animasyonunu dönüyordu. Aynı hata Mark VI saldırı klibini arada War Machine zırhına taşıyabilirdi. Bunlar **kaynak router mantığından çıkan regresyonlar**, gerçek cihazda gözlenmiş hatalar değil.

## Düzeltme

- Pinned 2010 IM2V animasyonunda başladığı **B14 hareket modu** ve **zırh kimliği** saklanır. Aynı sahipte kaynak süresi korunur; farklı mod/zırh geldiğinde önceki seçim derhal kesilir, yeni orijinal kaynak klip seçilir.
- Önceden tamamlanmamış klipler `completed_one_shots` sayılmaz; yeni `interrupted_one_shots` ölçümü eklenir. Doğrulanmış çarpışma, input/velocity, world root, HUD, GPU, weapon/damage ve orijinal süreler değişmedi.
- G83 testine `fly_ftol → Rush → fly_l`, `Mark VI ground fire → War Machine walk aim`, `WM hover fire → Mark VI hover aim` ve tamamlanma/kesilme sayaçlarının regresyonu eklendi.
- Bu aşama **özgün 2010 klip isimleriyle kaynak yönlendirme** düzeltmesidir. Orijinal iOS buton politikası ya da uçuşun fiziksel Vita'da kusursuz render edilmesi kanıtlanmış değildir.

## Doğrulama ve sonraki sahip

Push ile mevcut `.github/workflows/g83-original-full-movement-aim-combat-no-vpk.yml` kaynak-host/ARM nesne CI koşar; sonuçları gerçekten gözlemlemeden PASS yazılmamalı. Birleştirilmiş gerçek B24 Vita ELF için ayrıca G171 workflow gerekir. **VPK yok.**

Ana 7 aşamalı sıra korunur: 1 orijinal spawn/yürüme cihaz kanıtı açık; **2 hover/Stage2/Rush** bu çalışmanın odağı; 3 G8/War Machine; 4 combat; **5 orijinal Expo çevresel ışık/gölge/sky/alpha**; 6 görev/ses; 7 aynı kaynaktan tüm kapılar geçince tek VPK. G255 pre-VPK 7/7 gate hâlâ kapalıdır.

## 21 Ekim 2026 — gerçek CI sonucu, kesin kanıt düzeyi

- [G83 orijinal klip isim doğrulama, hareket/aim/combat C11 host, G300 yeni Stage2/Rush ve iki yönlü zırh değişimi testleri, Vita ARM .o — **SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39556711267).
- [G171 aynı commit gerçek tek oyun yeniden kurulum ve tam VitaSDK ARM **im2_beta ELF-only — SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39556712665). **60/60 CI adımı başarılı**; G84 optional authored-moveset route CMake ana Vita ELF derlemesinde **ON**. G299 deneysel çevresel ışık da aynı ARM kaynak entegrasyonu içinde yer alır.
- Doğrulanan kaynak commit: [`e9c8e55`](https://github.com/Gh0sTRX/Iron-man-2-os/commit/e9c8e55ccbd17007258f3621e9d937ae7567388d). Bu host/ARM kanıtı **G171/G300'ün PS Vita GPU görünümü/FPS, gerçek Stage2→Rush input davranışı ve kaynak-iOS parity için cihaz kabulü değildir**. G295 Vita3K renderer engeli de çözülmedi. VPK üretilmedi.
