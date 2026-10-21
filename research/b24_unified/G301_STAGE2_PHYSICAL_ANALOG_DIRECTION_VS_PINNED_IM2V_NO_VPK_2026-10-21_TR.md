# G301 — Stage2 fiziksel analog yönü ile G83 pinned IM2V animasyon yönünü ayır (NO VPK)

**21 Ekim 2026, `feature/b24-unified-gameplay`**

## Gerçek hata ve düzeltme
`g84_apply_original_g83_to_G75_G9_MAIN_NO_VPK.py` orijinal B24 ana döngüsüne `g84_last_flight_dir=world.flying?g84_route.direction:...` koyuyordu. `g84_route.direction` 2010 kaynak süresi (ör. fly_ftol 800ms) bitene kadar görsel animasyon tarafından *pinned* tutulabilir; gerçek B14 analog girişi o karede çoktan başka yöne dönmüş olabilir. Dolayısıyla geçmiş yön hatalı güncellenip sonraki gerçek `ltof/ftol` klibi kaçırılabilir veya yanlış başlatılabilir. Rush ve Hover da `world.flying` true olduğu için Stage2 dışı yön geçmişi taşıyabiliyordu.

Yeni `b24_g83_physical_flight_dir(mode,axis_x,axis_y)` G83'ün mevcut 0.18 deadzone/ana eksen ayrımını kullanır, ancak yalnız **B14 tarafından seçilmiş `FLIGHT` (Stage2)** durumunda yön döndürür. `GROUND/HOVER/RUSH` için IDLE; geçersiz NaN/sonsuz veya [−1.01,1.01] dışındaki analog eksenleri için de IDLE. G84 `g84_last_flight_dir` değerini **G83 animasyon çıktısından değil aynı kare B14 analog girdisinden** günceller.

- Orijinal IM2V klip adları/süreleri, G300 one-shot owner, B14 tek dünya hareket integratörü, G8 tek animasyon oynatıcı, G75 çarpışma, G82/B16 combat, G299 deneysel ışıklandırma ve G168 zırh ayak hizalaması korunur.
- Regresyon: `fly_f → fly_ftol(pinned LEFT) → fiziksel F` sırasında görsel LEFT kalırken fiziki geçmiş F güncellenir ve 800ms sonra yanlış `ltof` çıkmaz; `RUSH → FLIGHT L` sırasında geride F/L tutulmaz; `FLIGHT → HOVER` temizlenir.
- G84 kaynak yaması fail-closed assertion ile `g84_route.direction` geri kullanımını reddeder.
- Bu **host mantığı ve Vita ARM derlemesi**, cihazda sahne renderi veya özgün iOS touch davranışı kanıtı değildir.

**Test çalıştırma:** push üstüne `.github/workflows/g83-original-full-movement-aim-combat-no-vpk.yml` (C11 ve Vita ARM .o), `g171-...-NO-VPK.yml` (same-commit birleşik gerçek oyun Vita ELF-only) otomatik çalışır. Sonuçları gerçekten kontrol etmeden başarılı diye rapor verme.

**Sıra değişmedi:** G171 gerçek yerde hareket donanım ölçümü açık → Stage1/Stage2/Rush → özgün G8/War Machine → gerçek combat → Expo **LIGHTING/sky/moon/alpha/gölge** → QTE/görev/ses → G255 7/7 ve tek VPK. Yeni VPK üretme.
