# G299 — Orijinal Expo'nun dört Sun konumuyla zırhın canlı çevre aydınlatmasını başlatma (NO VPK)

**21 Ekim 2026 · özel `Gh0sTRX/Iron-man-2-os` · `feature/b24-unified-gameplay`.**

## Gerçek ilerleme ve sınır

G298'de **dokulu C1L1 şehir VBO'su** için orijinal dört `Sun001..004` *yerel CLARA konumu* ile deneysel opak materyal ışıklandırması, GPU `GL_MODULATE` düzeltmesi ve kaynak alpha koruması test edilmişti. Ancak kaynak `b24_gpu_suit_vitagl.c` içinde **gerçek her kare zırh renderer'ı daima saf beyaz `glColor4f(1,1,1,1)`** veriyordu: şehir renk modülasyonu değiştirilse bile Mark V/VI veya War Machine üzerine aynı aday ışık uygulanmıyordu.

**G299** yalnız isteğe bağlı `B24_G299_SUIT_ENVIRONMENT_CANDIDATE` makrosuyla, mevcut **tek G168 animasyonlu IM2T GPU zırh draw** öncesinde:
- Gerçek B14/G75/G168 oyuncu **o kare dünya root** `(pose->x,y,z)` değerlerini, kaynağın G30 `Sun001..004` yerel pozisyonlarını içeren **G95 `b24_g75_light_factor`** yardımcı hesabına verir.
- Kaynak 2010 vertex normals/Light class düşüş fonksiyonu/renk-space/CLARA world transform **henüz bulunmadığından**, yalnız karşılaştırılabilir **tekdüze actor RGB ambient** uygular; fake specular, 3D shadow ve orijinal Gameloft shader'ı iddiası yok.
- `GL_TEXTURE_ENV_MODE` önceki değeri kaydedilir; `GL_MODULATE` ile test ışığı/zırhın **orijinal IM2T RGBA atlası** birleşir; alpha = 1 sayesinde kaynak doku alfa baytları değiştirilmez; çizim sonunda önceki mod ve beyaz renk geri yüklenir (HUD/sonraki actor etkilenmez).
- Ne B14 hareket hızı/route ne G75 çarpışması, G8 IM2V ve G168 **native_bind_min_z ayağa basma hizalaması** değişir.

Bu görsel şimdilik **deneysel**, fiziksel Vita/gerçek oyun ekranı **doğrulanmadı**.

## Gerçek kod ve otomatik test

- `research/b24_unified/b24_gpu_suit_vitagl.c` yalnız `#ifdef` altında canlı renk/stage ekler, varsayılan görüntüyü değiştirmez.
- `research/b24_unified/g299_suit_environment_vitagl/g299_install_suit_light_after_G168_G279_NO_VPK.py` önce gerçek **G168 foot alignment uygulanmış** `work/b24/b24_unified/b24_gpu_suit_vitagl.c` dosyasına bu opt-in davranışı ekler; kaynağı geri eski hizalamaya çevirmek üzere repo dosyasını kör kopyalamaz. Kaynak aralıkları kaymışsa, aynı sahnede duplicate GPU draw, eksik B14/G8, VPK varlığı veya G95 yoksa kaynak fail-closed reddedilir.
- `test_g299_install_guarded_original_source.py`: pozitif, double injection, G168 kaybolması ve yanlış VPK testi.
- `test_g299_real_suit_source_light_alpha.c`: **gerçek VitaGL suit C renderer** syntetik 3-vertex suit / RGBA atlas ile derlenir; orijinal kaynak PVR/IPA yeniden dağıtılmaz. Proximity değişimi, texture state save/restore, alpha değişmemesi ve bir draw / frame senaryoları test edilir.
- [G299 hızlı gerçek kaynak-mock VitaGL regresyonu — **SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39506543873).
- [G299 2010 gerçek tek Vita oyunu kaynağı / G168 + G279 / ARM ELF-only](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39506543817) — bu rapor yazılırken **tam build sonucu henüz doğrulanmamıştı**; bağlantıdan tamamlanmış sonucu kontrol edin.

## Orijinal ışıklandırmada kalanlar

- G30 dört ışığın özgün **yerel** transformları mevcut, ama **world chain, native Light türlerinin anlamı, renk/enerji, yüzey normali / PBR benzeri shader semantiği** yok. Burada güvenilir shader parity sağlandı denemez.
- Zırh uniform RGB testi, gerçek yüzey başına yönlü light/specular/gölge değildir. Araba/sahne geometrisine gerçek zamanlı ışık, ışık yansımaları, true shadow caster, moon/world skyline ve source material-alpha depth hâlâ stage5'tedir.
- `G161` cihaz eski demo; G171 / G296 / G297 / G298 / **G299** kaynak değişiklikleri gerçek PS Vita **oynanış/görüntü testi geçmedi**.
- Ana sıra: 1 gerçek ground/spawn Vita doğrulaması açık; 2 hover→Stage2→Rush flight; 3 G8 / WM özgün animasyon; 4 genuine combat; 5 Expo scale, **environment LIGHTING + shadow/sky/alpha**; 6 QTE/mission/sound; 7 aynı commit 7/7 gate ve SONRA bir VPK. `g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json` hâlâ 7/7 değil.
