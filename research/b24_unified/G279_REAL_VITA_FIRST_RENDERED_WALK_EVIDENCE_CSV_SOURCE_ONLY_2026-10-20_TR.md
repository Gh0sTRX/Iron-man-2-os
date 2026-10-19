# G279 — Vita üzerinde yürüyüş kök nedenini kayda alma (KAYNAK KODU, NO VPK)

**Tarih:** 20 Ekim 2026. **Dal:** \`feature/b24-unified-gameplay\`.

## Kullanıcının gerçek cihaz gözlemi
G161 kurulmuş eski PS Vita testinde yürüyüş animasyonu oynuyordu, fakat yer hareketi ekranda görünmüyordu. Bu gözlem, daha sonra GitHub'da derlenen **G171/G278** kodunu cihazda test etmiş olmak değildir. Dolayısıyla "Vita yürüyüşü düzeldi" sonucu hâlâ verilemez.

## G171 kaynak testinde doğrulanan somut durum

- Önceden G167 testi gerçekte Vita ELF'te **ON** olan \`B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL\` makrosunu **OFF** bıraktığından, özgün \`c1l1_diaosu.tga\` heykel çizim yüzeyini kesin olmayan fizik duvarı sayıp eski **15/120** kilit sonucu vermişti.
- Aynı G171 derleme bayraklarıyla tekrarlanan gerçek B14->G75 C11 host regresyonu başlangıç (0,0,0) için **120/120 ground** ve **120/120 flight** kabul etti. Özgün G66C **1.910 triangle** ve kaynak duvarlar silinmedi. G171 gerçek Vita ARM ELF derlendi, **ama fiziksel Vita yürüyüşü test edilmedi**.
- Kaynak CLARA MC *local* pozisyonu, cihazdaki özgün hikâye başlama ayak koordinatı sanılamaz. Kaynakta olmayan oyuncu teleport/ölçek değişimi yasak.

## Bu tur gerçek yazılan G279

**Hedef:** Bir sonraki *tek bütünleşik VPK* cihaz testinde, VitaShell ile erişilebilecek kaynak-bağlı ve bozulmaya dirençli yürüyüş teşhis dosyası. G279, oyun mekaniğini düzeltmek yerine kullanıcı gözlemine **neden** olan zincirin hangi halkasının farklı olduğunu göstermek için vardır.

- Dosya (Vita'da yazma izni mevcutsa): \`ux0:data/ironman2_g279_walk.csv\`. Açılmazsa oyun yüklenmeye devam eder; bu yol Vita cihazında henüz denenmedi.
- **BOOT**: İlk üç başarılı C1L1 GPU çizim karesinin gerçek G278/B14 başlangıcı, özgün kaynak G66C yakın zemin tespiti, G75 çarpışma reddi, GPU zırh root XYZ, kamera ve pad girdileri. G8 dosya seçimi bu CSV'de ayrıca kaydedilmez; önceki G227-G229 kaynak gözlemcisi animasyon eksikliğini ayrı sayar.
- **WALK120**: G229'un **aralıksız 120 başarılı yerde oynanmış/çizilmiş kare** penceresi kapanınca gerçek B14 önerilen yol, G75 kabul edilen yol, stick var/yok, collision rejected sayısı, GPU root mismatch, aynı pencerenin dünya ve kamera \`dx/dy\` farkı ve G229 sınıflandırma açıklaması yazılır. Son G277 wall/no-floor/step sayıları yalnız *son* G75 alt-sweep'e aittir, pencere toplamı olarak etiketlenmez.
- Orijinal \`B14\`, \`G75\`, \`G8\`, \`GPU\`, kamera döngüsünün **tamamında yalnızca birer** gerçek çağrı kalır. Kod yalnız gerçek G171+G278 dosyasına tekil noktalardan eklenebilir; bozuk kaynak/çift ekleme/VPK bulunduğunda hata ile durur.
- Teşhis varsayılan olarak **OFF**: gelecekte tam oyun derlemesinde isteğe bağlı \`-DB24_G279_WALK_TRACE_FILE=ON\`, ayrıca G227/G171 doğrulama makroları gerekli.
- CSV seri hale getirme: tanımlı BOOT/WALK120 evresi, güvenli G229 sonuç adı, 31 sabit kolon; NaN/Inf ve veri içine virgül/satır enjeksiyonu reddedilir; satır başına \`fflush\` sayesinde test kırıldığında mevcut satırlar diske bırakılmaya çalışılır.
- **No VPK**, otomatik cihaz kurulumu/gerçek Vita runtime kaydı yok.

## Doğrulama

- \`research/b24_unified/g279_vita_walk_persistent_trace/b24_g279_walk_trace.h\`
- \`research/b24_unified/g279_vita_walk_persistent_trace/g279_install_file_trace_after_G278_one_Vita_game_NO_VPK.py\`
- \`research/b24_unified/g279_vita_walk_persistent_trace/test_g279_bounded_csv_writer.c\`
- \`research/b24_unified/g279_vita_walk_persistent_trace/test_g279_real_source_patch_guards.py\`
- GitHub Actions **G279 hızlı C11/negative-source CI SUCCESS**: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39341569074
- Önceki G279 26-kolonlu ilk sürümün **G171 tüm gerçek Vita ARM ELF derleme SUCCESS**: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39341249175
- 31-kolonlu genişletmenin gerçek full VitaSDK ARM ELF + B14/G75 kaynak yürüyüş 120/120 + C11 testleri SUCCESS: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39341569016 (`[100%] Built target im2_beta`). Fiziksel Vita cihazında yürüyüş hâlâ test edilmedi.

## Cihaz logu nasıl yorumlanacak?

- Yüksek \`active_stick\`, yüksek \`B14 no move\` verdict: gamepad/B14 kontrol aktarımı.
- Yüksek \`collision_reject\`, B14 yolu var ama \`resolved_path\` sıfıra yakın: C1L1 zemin/duvar yükseklik/kaynak çarpışma.
- \`gpu_root_mismatch\` büyük: dünya pozuyla çizim kökü tutarsız.
- \`resolved_path\` var ve world\`dx/dy\` + camera\`dx/dy\` beraber: takip kamerası sebebiyle görsel yanılsama ihtimali; özgün iOS kamera davranışına eşdeğerlik değil.
- \`native_floor\` yoksa bunun tek başına gerçek iOS spawn'ını ispat etmediğini unutma.

**Öncelik:** (1) Gerçek başlangıç+ground cihaz teşhisi; sonra mevcut sırayla (2) flight, (3) G8/War Machine anim, (4) özgün combat, (5) orijinal map/sky/ışık/alpha/HUD, (6) Mission000/QTE/ses/NPC, (7) tüm gate'lerden sonra **tek** test VPK. Bu adım bu sıralamayı değiştirmez.

## G279 CSV bağımsız otomatik yorumlayıcı — aynı yürüyüş odağında ek gelişme

- `research/b24_unified/g279_vita_walk_persistent_trace/g279_analyze_Vita_walk_trace_TR.py` kayıt gelince Türkçe çıktı üretir. Özgün Vita dosyası gelmeden herhangi bir gerçek cihaz başarısı iddia etmez.
- Başlık ve 31 sütun 1:1 denetlenir; sahte/eksik sütun, NaN/Infinity, yüksek/negatif sayaç, bilinmeyen G229 sonucu, bozuk kare sırası ve >8 MiB kayıt reddedilir.
- Gerçek veri yüklenirse B14 önerilen dünya yolu, C1L1 çözümlenen dünya yolu, camera/world net hareket, GPU mismatch ve kaynak çarpışma red sayılarıyla, 'girdi yok / B14 hareket üretmedi / çarpışma reddi / GPU dünya kökü farkı / dünya hareket ediyor' sınıfları üretilir.
- Cihazdan gerçek dosya henüz alınmadığı için sadece sentetik host testleri yapıldı. [G279 kaynak/analizci bütün fast CI SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39342242088). **NO VPK**.
