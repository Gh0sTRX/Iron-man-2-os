# Iron Man 2 (2010 iOS) — G112–G117 doğrudan özgün oyunu çalıştırarak native mekanik ölçümü

**17 Ekim 2026** · `feature/b24-unified-gameplay` · Kullanıcı yönergesi: **gerçek oyundan sistemleri çöz ve tamamla, kesinlikle yeni VPK üretme**. Hedef combat/AI ve materyalleri orijinal iOS kaynak oyunu çalışırken çıkarmak; gözlem yapılmadıkça oynanış sonucu uydurma.

## Dokümante edilmiş touchHLE yeteneği

- Orijinal Iron Man 2, **iOS 1.0.0**, resmi <https://appdb.touchhle.org/apps/451> veritabanında **5 yıldız** çalışır olarak kayıtlı. touchHLE v0.2.3 sürüm notlarında Iron Man 2 destekli oyunlar listesinde.
- Resmi kaynak <https://github.com/touchHLE/touchHLE/tree/trunk/dev-docs> debugging belgesi `--gdb=localhost:9001` gerçek ARMv6 GDB RSP, `gdb-multiarch` breakpoint/register/memory desteği olduğunu gösteriyor.
- Orijinal oyunla **tamamen ayrı** gerçek Linux çalıştırma protokolü: CI üzerinde sahibi tarafından sağlanan 248.613.763 bayt iOS IPA *ephemeral* indirildi, `Payload/IronMan2.app/IronMan2` gerçek ARM yürütülebiliri ve oyunun kaynak varlıkları geçici olarak açıldı; indirilen özel IPA ve orijinal executable artifact veya GitHub git repository'de yayımlanmıyor.

## G112 gerçek ilk touchHLE çalıştırma sonucu — BAŞARISIZ EMULATÖR BAŞLATMA (OYUNU OYNADIK DEME!)

- GitHub CI [39016590908](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39016590908) üçüncü taraf `pkgforge-dev/TouchHLE-AppImage` **v0.3.0 x86_64** üzerinde orijinal IronMan2 1.0.0 bundle kimlik bilgilerini doğru okudu ve OpenGL ES 1.1–GL2 via Mesa softpipe başlatabildi, ancak kod `src/environment.rs:455` içinde **`assert dylib_path startswith("/tmp/CQK/")` ile çöktü**. GDB sunucusu açılmadı, **orijinal hiçbir combat breakpoint'i tetiklenmedi**. CI sonucu otomasyon dosyalarının çıkmasını başarı sayabiliyor; bu gerçek oyunun çalıştığı anlamına gelmez.
- Kaynak `research/b24_unified/g112_real_touchhle_gameplay_trace/g112_run_2010_real_game_touchhle_gdb.py`: doğrudan özgün iOS fonksiyonları `AttackEntity::LoadFromFile 0xA934C`, `EntityData::GetParamValue(int*) 0xD7548`, `Actor::TestMeleeHit 0xDFD94`, `Actor::CanAttack 0xD9278`, `MainCharacter::UpdateMeleeAttackState 0xF1DE4`, `ProjectileEntity::HitImpactActor 0xB44B0` için GDB; orijinal `AttackEntity::LoadFromFile` içindeki `Damage` `GetParamValue` BL çağrısından sonraki **0xA9468** gerçek ARM komutundaki **AttackEntity+0x60 kaynak-native 32-bit int** üzerinde doğrudan ölçüm. **Bu son breakpoint henüz vurulmadı.**
- Kaynak `.github/workflows/g112-original-iron-man-2-2010-touchhle-linux-GDB-source-capture-NO-VPK.yml` son halinde 3. taraf paketini bırakıp **resmi `touchHLE/touchHLE` v0.3.0'ı Cargo ile Linux'ta resmen kaynak derleme** ve kendi özgün oyun IPC GDB izleme akışı kuracak şekilde değiştirildi. Derleme CI [39016727515](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39016727515) ile takip edilir; kesin sonucu CI'de `gdb_server_socket_reached` ve `gdb_original_ios_method_breakpoint_hit_total` görünmeden **asla başardı denmez**.

## G113 iOS özgün Mach-O dinamik bağımlılık gerçeği

G113 gerçek 2010 IPA Mach-O LC_LOAD_DYLIB ve LC_LOAD_WEAK_DYLIB komutlarını **değiştirmeden** çıkardı. 15 bağımlılık kaydı: UIKit, Foundation, OpenGLES, QuartzCore, CoreGraphics, AudioToolbox, OpenAL, SystemConfiguration, MediaPlayer, StoreKit, CoreFoundation Apple framework'leri ve `/usr/lib/libstdc++.6.dylib`, `/usr/lib/libgcc_s.1.dylib`, `/usr/lib/libSystem.B.dylib`, `/usr/lib/libobjc.A.dylib`. Orijinal iOS Mach-O library bağımlılık listesinde **`/tmp/CQK/` YOK**. Bu, host 3. parti AppImage'nin dönüştürülmüş mutlak path davranışından şüphelenmemize dayanak ama resmi touchHLE kaynak derlemesi başlamadan kesin neden diye kanıtlanamaz.
- Analiz: `research/b24_unified/g113_original_macho_runtime_dylib/g113_2010_owner_arm_macho_load_dylib_safety_audit.py`.
- GitHub source artifact [G112+G113 39016590908](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39016590908/artifacts/12095470660) yalnız rapor/log, **oyunun tüm dosyaları yok**.

## G117 gerçek 26 saldırı kaynak veri tiplerinin sert bir sınaması

G101: 26 gerçek orijinal `Attack` (class108) adlı instance'ların her biri **54 gerçek uzunluk-prefixed kaynak data alanı** taşıyor. Class110 `Object` 23 native declared field arasında `Damage` adı var. G105 bu 23 alanın hiçbiri tek parçalı düz contiguous dizi olarak 54 alana uymadığını gösterdi. G117 aynı 26 instance için **orijinal tip boyutlarının tümüyle** hem normal hem ters 23-descriptor *sırayı koruyan ama parçalı* alan hizalaması test etti.

- **[G117 CI başarı 39016940606](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39016940606)**, [rapor 12095705094](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39016940606/artifacts/12095705094).
- Normal yönde **108.409.554** olası type-only subsequence eşlemesi; `Damage` için 12 farklı kaynak slot pozisyonu uygun (ör. 28,30,31,33,34,35,37,38,39,40,42,44).
- Ters yönde **496.123.920** type-only subsequence eşlemesi; `Damage` için 6 farklı konum (25,26,27,28,30,31).
- **Bu kadar fazla matematiksel ihtimal varken hiçbir orijinal sayı `Damage` diye isimlendirilmedi; G111 hasar kapısı açık değil ve hiçbir sahte düşman HP veya combo hit-active penceresi üretilmedi.** Ayrık original EntityData ad↔alan kalıtım haritası veya gerçek oyun ARM runtime gerekir.

## Açık özgün mekanik eksikleri

- 26 typed Attack instance / real attack author damage ve native field mapping; G112 gerçek `Damage` çalışma zamanı izlemesi bu kilidi açabilir **ama henüz izleme olmadı**.
- Native melee 13 durum / gerçek input gesture, hit aktif pencere, combo cancel, projectile ve splash damage; G89 state predicate ve G82 contact gate asıl orijinal durum makinesi yerine geçmez.
- Native `CNPC` AI, spawn/wave/script, hurt/death; G92 dummy original NPC değil.
- Orijinal GLES sky blend, alpha cutout, ambient/sun combiner GPU state; G71, G73, G95 kaynak denemeleri cihazda tekrar görülmedi.
- Render-source G108 7.147 konservatif duvar üçgeni statik kaynaktan seçildi, fakat 2010 **orijinal çarpışma semantiği** ispatlanmadı; Vita FPS/hardware yeniden test edilmedi.

**Yeni Vita VPK YOK.** Yalnız gerçek source metadata, Open Source touchHLE derlemesi, CI ve doğrulanmış C/ARM kaynağı vardır. Gerçek oyunun tamamlandığını ileri sürme. Nihai Vita link [G111 source-only 39013755500](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39013755500).
