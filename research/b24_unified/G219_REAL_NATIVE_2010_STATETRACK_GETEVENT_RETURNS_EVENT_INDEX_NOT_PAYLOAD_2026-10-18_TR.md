# G219 — Iron Man 2 iOS (2010) özgün StateTrack::GetEvent sonucu 3. alan DEĞİL, gerçek olay indeksidir

**18 Ekim 2026; source-only native ARM; Vita oyun olay/damage motoru değiştirilmedi; VPK yok.**

### Kaynak ARM kanıtı

[Başarılı G219 gerçek orijinal owner-IPA ARM test](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39137453641). Özgün 2010 `StateTrack::GetEvent(int,int)` ARM method adresi **0xA14F0**; `Actor::UpdateStateAttack` C++ method adresi **0xDB610**. Tam gerçek code body owner game binary'den çözüldü, 12 bayt olay kayıtları G211/G213B source verisiyle karşılaştırıldı:

```asm
0xA14FC LDR R8,[R0,#0x10]      ; gerçek olay sayısı
0xA1508 LDR R0,[R0,#8]         ; StateTrack native olay dizisi pointer
0xA150C LDR IP,[R0]            ; olay başlangıcı
0xA1510 LDR R3,[R0,#4]         ; olay süresi
0xA1514 ADD LR,IP,R3           ; başlangıç+süre
0xA15A0 ADD R4,R0,#0xC        ; sonraki olay kaydı +12
0xA15F8 MOV R0,R6             ; olay kayıt sırası (INDEX) return!
0xA1638 MVN R0,#0             ; hiçbir aralık örtüşmüyorsa -1
```

Gerçek 2010 `GetEvent` fonksiyonu olayı zaman aralığı örtüşmesine göre seçiyor ve **olay indeksini** döndürüyor, `event[2]` üçüncü `u32` değerini **bu fonksiyonda okumuyor**. ARM `r0` içinde dönen `r6` indexed olay numarasıdır, `GetEvent` olay payload/damage veya weapon ID'si değildir. 12 baytlık kaydın üçüncü alanı kaynak dosyadan korunuyor ama hangi C++ consumer'ın bunu nasıl yorumladığı bilinmiyor. `300, 413, 507` vb. orijinal raw marker'lardan '300 ms vuruyor' sonucu çıkarılmaz.

### G218 canlı bağlantıdaki güvenlik ve sonraki görev

Orijinal G217 776 gerçek state / `AttackType` / `next_state` / `loop` / track başlangıç bilgisi G218 tarafından gerçek G8 kaynak IM2V load sonunda PASİF okunuyor, G219 bu ilişkiyi değiştirmedi. Gerçek iOS runtime event-to-damage/animation binding kanıtı olmadan `GetEvent` indeksine göre mermi/füze/UniBeam/hasar veya combo girdi olayı türetilmeyecek. Sonraki araştırma doğrudan `GetEvent` dönen olay indeksini gerçek `Actor::UpdateStateAttack` ve `StateTrack` accessors üzerinden kimlerin nasıl tükettiklerini takip etmektir.

**[G218 birleşik tam Vita ARM ELF-only başarı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39136868430).** Fiziksel Vita oynanış testi yok, yeni VPK üretilmedi.