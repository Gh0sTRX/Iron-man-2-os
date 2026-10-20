# G296 — Gerçek özgün Expo G66C zeminini 120 render-kare yürüyüş penceresinde ölçme; Codex / Claude Code devir

**20 Ekim 2026 — `feature/b24-unified-gameplay` — NO VPK, fiziksel Vita testi yok.**

## Tek kök sorun ve yapılan kaynak değişikliği

G278, ilk 3 başarılı GPU çizimindeki kaynak G66C zemini ölçer. G279 ilk 3 BOOT örneğini CSV'ye geçirir ancak ardından 120 ardışık render-kare yürüyüşünde **`has_native_floor` / `native_floor_z` değerlerini hiç doldurmuyordu**: 31-kolon CSV sıfır değerleri gerçek "kaynak zemin yok" diye yanlış okunabilirdi. Bu, eski G161 fiziksel Vita walk-in-place sorununun nedenini çıkarmak için gereken ölçümde bir boşluktu.

`research/b24_unified/g279_vita_walk_persistent_trace/g279_install_file_trace_after_G278_one_Vita_game_NO_VPK.py` içindeki *tek gerçek G229 WALK120 tamamlanma* kaydında artık, aynı orijinal oyun çarpışma verisi `b24_original_walls` ve özgün `b24_g74_near_original_floor(...world.x,world.y,world.z,&g279_win.native_floor_z)` kullanılarak **oyuncunun 120 başarılı render karesi sonundaki çözümlenmiş dünya XYZ'sinde** yakın gerçek G66C zemin sorgulanıyor. Sorgu read-only; açılıştaki boot-floor örneğiyle karıştırılmıyor. Yazılan `has_native_floor` ve `native_floor_z` CSV kolonları zaten vardı, **dosya biçimi değişmedi**.

B14 hareket, G75 capsule collision, G8 animasyon, GPU çizimi ve kamera sahibi tek çağrıda bırakıldı. Harita duvarı silinmedi, oyuncu teleport edilmedi, ölçek/hız değiştirilmedi, gameplay düzeltildi iddiası yok.

## Kaynak testler ve sonuç

- [G296 C11 gerçek CSV yazıcı + Python parser / fail-closed kaynak yama regresyonu **SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39488245937) — aynı çizimde BOOT `Zup=0.07250` ile WALK120 `Zup=2.82955` sentetik testleri ayrıştırılıyor, eksik özgün C1L1 zemin sahibi reddediliyor; sahte/NaN CSV engelleniyor.
- [G296 gerçek tek oyun G171→G279 birleştirilmiş kaynak, G66C/B14/G75 host testleri ve VitaSDK ARM `im2_beta` ELF derleme **SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39488245976) — 59 GitHub Actions iş adımı tamamlandı, 0 hata. **Bu ELF-only CI gerçek Vita donanımı ya da Vita3K oynanış testi değildir.**
- G296 kaynak son dosya commit: [`1542a4d`](https://github.com/Gh0sTRX/Iron-man-2-os/commit/1542a4ddcf6d36c7979c576d35eda7baaf467071). Sonraki `AGENTS.md` ve `CLAUDE.md` yalnız geliştirici/ajan devridir.

## Nasıl yorumlanacak?

`ux0:data/ironman2_g279_walk.csv` cihazdan ileride alınırsa `python3 research/b24_unified/g279_vita_walk_persistent_trace/g279_analyze_Vita_walk_trace_TR.py <cihazdan-alinan-csv>` komutuyla `WALK120` pencere sonundaki orijinal 2010 G66C destek bayrağı ve Zup okunabilir. Cihaz kaydı **henüz mevcut değil**. Zemin bulunmaması tek başına özgün iOS spawn'ını ya da root hareketinin kesin bozuk olduğunu ispatlamaz; G277 wall/step/no-floor ve G229 stick/B14/resolved/GPU/camera ile birlikte yorumlanmalı.

## Ajan devri ve sonraki tek odak

PC'de Codex veya Claude Code geldiğinde proje kökündeki **`AGENTS.md`** ve **`CLAUDE.md`** direkt okunabilir. Gerçek kod, test, engel, izin verilmeyen kestirmeler ve tüm sıra tek yerde kayıtlıdır. Özellikle standart GitHub-hosted Vita3K G295 Vulkan exception'ını yeni kanıt olmadan yeniden denemeyin.

**Sıra:** 1 özgün MC runtime spawn ve gerçek yürüyüş ayrışması (henüz cihaz kanıtı yok); 2 uçuş; 3 G8/War Machine anim; 4 özgün combat; **5 Expo sky, alpha, çevresel ışık ve gölgeler zorunlu**; 6 görev/ses/NPC; 7 tüm gate'lerden sonra tek Vita VPK. [Ön-VPK kapıları](g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json) henüz **7/7 hazır değil**.
