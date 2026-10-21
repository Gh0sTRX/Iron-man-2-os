# G302 — Mark VI / War Machine zırh değişiminde eski repulsor animasyonu yeni zırha taşınmasın (NO VPK)

**21 Ekim 2026 · `feature/b24-unified-gameplay`**

## Tam kaynak sorunu
`research/b24_unified/b24_g8_live_original_motion.c` özgün G8 IM2V oynatıcısında `b24_g8_motion_tick` önce mevcut `repulsor_pending` olayına göre hedef `_att` klibini seçiyordu. Yeni suit/1292–802 vertex geçişini temizleyen `fresh()` ise bundan SONRA çalışıyordu. Dolayısıyla MarkVI'da kabul edilmiş bir B16 repulsor olayının bir sonraki WM karede, yeni WM ateş olayı OLMADAN `warmachine_*_att` pozu seçilmesi mümkündü. Tersi de geçerli.

**Düzeltme:** `a->nv>0 && a->suit_index!=suit` olduğunda önce mevcut kaynak animasyon durumu ve eski bekleyen atış güvenli `b24_g8_motion_release(a)` ile sıfırlanır, **ondan sonra** yeni suit için doğru klip seçilir. Çarpışma, atış/hasar sistemi, B14, G83/G301 Stage2 fiziksel analog yönü, orijinal IM2V dosyaları, clip duration ve G299 Expo ışığı değişmez. İlk kare/gerçek G8 stream yükü eski sahipten ayrılır.

## Regresyon
`g302_g8_suit_attack_owner/test_g302_no_old_suit_repulsor_on_wm_switch.c` G8'in **aynı gerçek Vita hedefli C kaynağını** sentetik IM2V fixture ile çalıştırır. MarkVI hover accepted repulsor → WM hover (yeni saldırı yok) → WM accepted repulsor → MarkVI (yeni saldırı yok) → WM source-flight → WM Rush kayıpsız kontrol edilir. Kimse sahte native iOS shot veya özel WM Rush klibi icat etmez. G171'in G174 öncesi adımı gerçek `work/b24/b24_unified/b24_g8_live_original_motion.c` (G84/G85/G173 patch uygulanmış) ile bu testi derler. Mevcut tüm G174 original 1292-vertex source bank adımları ve final Vita ARM ELF derlemesi ayrıca çalışır.

**Test düzeyi:** Host gerçek renderer-animator kod yolu, *sentetik* klip byte'ları, ardından aynı kaynaktan Vita ARM ELF-only bütünleşik oyun build; bu gerçek PS Vita veya 2010 iOS input semantiği değildir. CI bitmeden PASS demiyoruz. Orijinal MW/WM muhtemel native Missile, Aim_M/Gatling anlamları çözüldü demiyoruz. Bütün G255 pre-VPK kaynak kapıları açık değil; VPK üretmeyin.

**Sonraki:** War Machine gerçek 2010 1292-vertex ground/hover/flight geçiş bankası ve input/weapon anlamını kaynakla ayır; sonra mevcut gameplay/combat ve Expo **LIGHTING/sky/shadows/alpha**, Mission000/audio, 7/7 gate + tek VPK. Fiziksel G171 yürüyüş/initial world root kanıtı bekliyor.

## 21 Ekim 2026 — gerçek CI / başarı kanıtı

- [G302 tam **G171** kaynak birleşimi ve VitaSDK ARM `im2_beta` **ELF-only SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39558787652), kaynak commit [`ef4ffe8`](https://github.com/Gh0sTRX/Iron-man-2-os/commit/ef4ffe89116eb6cb83737d52d5338d688a1c4975).
- Aynı kaynak koşusunda **G302 yeni gerçek G8 streamer C11 sentetik IM2V fixture testi PASS**, G174 mevcut **10/10 orijinal 1292-vertex WM Aim_M_Ground IM2V** test adımı PASS ve final birleştirilmiş Vita ARM game ELF build PASS. 61 workflow step + cleanup tamamlandı; job success.
- Bu, gerçek orijinal WM animasyonlarının tüm hareket/weapon anlamının çözüldüğünü veya fiziksel PS Vita görüntüsünü kanıtlamaz. **Yeni VPK yok**, fiziksel G171/G302 PS Vita oynanış testi hâlâ yapılmadı. G255 7/7 henüz açık değil.
