# G303 — War Machine Ground ↔ Hover ↔ Stage2/Rush G8 repulsor one-shot sahibi (NO VPK)

**21 Ekim 2026 — `feature/b24-unified-gameplay`**

## Kaynaktan tespit edilen hata
Tek G8 orijinal 2010 `IM2V` animasyon oynatıcısı, B16'nın tek bir kabul edilmiş repulsor atışı devam ederken hareket vektörü değişince `b24_g8_motion_repulsor_clip(suit,mode,x,y)` değerini her kare yeniden hesaplıyor. Bu nedenle bir WM `aim_ground_move_F_Att` oynarken stick geriye dönünce ikinci bir gerçek B16 atışı olmaksızın `aim_ground_move_B_Att` dosyasına geçebiliyor. Daha önemlisi B14 ground→hover gerçek durum değişiminde, tek eski kabul edilmiş ground atışı hover'ın `_Att` animasyonunu yanlışlıkla başlatabiliyor. G302 sadece *suit* değişimini engelliyordu.

## Onarım
- G8 çalışan IM2V akışında bir `repulsor_domain` tutulur: gerçek `IDLE/WALK` grounded owner=1, `HOVER/DRIFT` owner=2; Stage2 `CRUISE`, `RUSH`, `RUN`, `LAND` owner=0.
- Aktif tek B16 repulsor animasyonu sadece **aynı domain** içindeki mevcut açılmış **kaynak IM2V ismini** tutar; analog yönünün sonraki kare değişimi yeni `_Att` başlatamaz. Klip süresi dosyanın `stream.duration_ms` metadata'sıdır; uydurma hit/kare süresi eklenmez.
- Kaynak B14 domain değişince eskisinin `repulsor_pending` ve `whole_body_repulsor_active` maskesi söndürülür. Gerçek G84/G83 tarafından seçilmiş normal hareket/hover/flight/WM geçici Rush kaynağına döner. Melee önceliği eski repulsorun sonradan yeniden başlamasını önler.
- G8 biricik orijinal IM2V oynatıcı, tek B14 dünya simülasyonu, B16 tek silah olayı/hasarı, G302 suit sıfırlaması, G301 Stage2 fiziksel yön geçmişi ve G299 deneysel çevresel ışık hiç değişmedi.

## Regresyon ve sınırlar
`test_g303_g8_wm_ground_hover_flight_one_accepted_attack.c` gerçek G8 streaming kaynağını G84/G85/G173 yama sonrası oyun derleme ağacından alarak C11 host'ta sentetik IM2V içerikle dener: WM ground F atış → analog B (aynı özgün klip) → hover (saldırı kesilir) → yeni ground atış (kaynak metadata süresi sonunda kapanır) → WM hover shot → Stage2 → Rush; MarkVI 802v tek atışta yön değişimi. Yeni atış/hasar/ikincil silah yok.

Kaynak klipler **sentetik test fixture** (gerçek 2010 iOS klibi değil); G171 mevcut G174 testinde orijinal 2010 WM 1292v `Aim_M_Ground` 10/10 stream kaydı ayrıca bağımsız çalışacak, tüm oyun Vita ARM **ELF-only** derlenecek. Bu bir gerçek PS Vita test ölçümü değildir, orijinal WM `Aim_M` silah anlamı veya özgün WM Rush klibi bulduk anlamına gelmez. **VPK yok**; G255 7/7 kapısı kapanmadı.
