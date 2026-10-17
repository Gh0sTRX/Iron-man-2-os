# G174 — 10 gerçek 2010 War Machine Aim_M_Ground IM2V animasyonunun tek oyunda stream testi

**18 Ekim 2026** · `Gh0sTRX/Iron-man-2-os` · `feature/b24-unified-gameplay` · **VPK yok.**

## Kanıt

G172 orijinal B18 klip adları/sürelerini G83 seçiciye ekledi. Ancak bu, dosyanın gerçek G8 runtime oynatıcıya yüklenmesiyle aynı şey değildir. G174 `research/b24_unified/g174_warmachine_true_native_ground_stream/test_g174_real_2010_WM_10_M_ground_stream_one_animator.c` kaynak testinde:

- G9/G8 iş akışından derlenmiş orijinal 2010 `work/animations/*.im2v` bankası kullanıldı; sentetik veya uydurma .im2v test dosyası kullanılmadı.
- Gerçek `warmachine.im2t` için önceden doğrulanmış **1292 skin vertex** ile G83 War Machine `AIM_M_UNCLASSIFIED` seçildi. Ground idle, F/B/L/R ve bunların saldırı `_att` karşılıkları: **10/10**.
- Her seçimin `B18` özgün klip süresi G172 isim/süre tablosuyla eşleştirildi. Her seçim, mevcut **tek G8/G85 orijinal skinned IM2V streamer** üzerinden açıldı; `animator.active`, açık gerçek stream, seçili özgün dosya adı, `stream.nv=1292` ve metadata duration kontrol edildi.
- Eski B16 repulsor beklemesi veya sahte `whole_body_repulsor_active` tetiklenmedi. **Gerçek oyun silah atışı üretilmedi.**
- Gerçek host test **GitHub Actions 39075264633 içinde G174 adımı PASS**. Aynı GitHub Actions koşusundaki tam VitaSDK ARM `im2_beta` **ELF-only derlemesi de SUCCESS**; [Actions 39075264633](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39075264633). Bu başarı gerçek PS Vita cihaz testinin kanıtı değildir.

## Bilmiyoruz — kullanıcı için çok önemli

- `M` orijinal 2010 iOS oyunda roket/gatling/başka bir aim silahı anlamına geliyor mu **native ARM hareket controller işlevinden kanıtlanmadı**.
- G84 canlı Vita input hâlâ `AIM_M_UNCLASSIFIED` üretmiyor. G174 testinde bu seçim hedefli test girdisiyle verildi. Bu **10 ek oynanabilir gerçek cihaz animasyonu** demek değildir.
- WM orijinal `Gun01…Gun04` / `Dummy_Gun_L/R` modeli/soketleri efekt-tetikleyici olarak henüz bağlanmadı. Mevcut B24 sol roket–sağ gatling modelleme 2010 native weapon mapping kanıtı değil, port tasarımıdır.
- G173 özgün MarkV/VI üç aşamalı Beam kaynak geçişi mevcut B16 kabul edilen port olayına bağlı; native iOS Uni-Beam hasar/id, FX, projectile veya giriş hareketi çözülmedi.
- G171 heykel çarpışmasının native iOS geçişi, gerçek Vita G171/G173/G174 runtime, C1L1 ışık, gölge, hikâye Mission000 QTE/cutscene, full melee enemy gameplay bekliyor.

**Sonraki doğruluk kapısı:** 2010 orijinal Mach-O `MainCharacter::ThrowMissile`, `WeaponDB::GetAttackEntityByIndex`, `SetAttackTypeEnabled` ilişkisini asli animasyon state/gun socket bağlamına eşlemeden, `Aim_M`'yi roket/ateş tuşuna otomatik bağlama. Yeni VPK üretme.
