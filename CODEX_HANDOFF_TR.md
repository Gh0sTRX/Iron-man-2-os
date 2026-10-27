# CODEX DEVİR VE ÇALIŞMA TALİMATNAMESİ — Iron Man 2 iOS (2010) → PS Vita

**28 Ekim 2026 — gerçek kaynak yolunda kalkış ve iniş düzeltmesi:**
Kullanıcının son talimatı **Vita kurulumu yapmadan kaynak geliştirmeye devam**
etmektir. `ee346c9` bu kapsamda iki gerçek hareket hatasını düzeltir:

1. Gerçek yol `Z=2.693700` üzerindeyken mevcut SDL Circle hedefi mutlak `0.8`
   yapıyordu. Gerçek B14 `2.577033` öneriyor, G75 yüzeyi koruyarak karakteri
   zeminde tutuyordu. Aynı negatif regresyon eski kaynakta başarısız oldu.
   Yeni gerçek olay yolu `3.493700` hedefleyip ilk karede `2.810367` kabul eder.
2. G75 inişte 0.35 adım düşüş sınırı ile 0.50 yakın-yüzey araması arasında
   boşluk bırakıyordu. Eski kaynakta iniş `Z=3.143699` yani zeminin 0.450000
   üzerinde takıldı. Aynı test düzeltilmiş kaynakta tam `2.693700` üzerine iner.

Kalıcı kaynak sahibi `research/b24_unified/world_height/` içindedir. Patcher
G171 resmi yeniden üretiminde G299'dan sonra çalışır. B14 tek integratör ve
G75 tek çarpışma çözücüsü kalır. Kalkış düzlemi, gerçekten kabul edilmiş
ayak/yüzey teması ve sınırlı iniş birleştirildi; yeni spawn seçilmedi. G75
kapalı B14 alanının eski Z=0 davranışı ayrı uyumluluk testiyle korunur.
Eski prototip hız/hover/tavan sabitleri özgün Gameloft keşfi olarak sunulmaz.

**Bu kaynak için doğrulama:**
- 48 güncel G171 shell doğrulama adımı yerelde geçti. İki girdi kontrolü yeni
  çalıştırılmış sayılmaz: /tmp temizlenince eski G9 kaynak VPK kabı ve G251
  16-spawn başlığı kayboldu. Araç dokusunun önceki doğrulanmış hash'i ve mevcut
  669 runtime varlığının tamamının snapshot hash'leri tekrar eşleşti.
- Yeni gerçek kaynak entegrasyon testi: 12 özgün veri + 6 açıkça sentetik
  Z-öteleme senaryo grubu, her çalışmada 130 kalkış/hover/iniş döngüsü,
  beş zaman adımı; strict C11 ve ASan/UBSan altında başarılı. Sentetik
  ötelemeler orijinal dünya/spawn dönüşümü değildir. Gerçek yolda yürüme,
  seyir, rush, daha alçak yüzeye iniş ve duraklatmada değişmezlik geçti.
- G248'in mevcut G75 bayrağı ve post-reconcile destek köprüsüyle 96 yön/mod
  vakası; G5 gerçek B21 duraklatma olayları; G279 kaynak/CSV testleri geçti.
- Temiz eski beş runtime dosyasına patcher uygulanıp güncel üretilmiş
  dosyalarla byte düzeyinde eşleştiği doğrulandı. Geliştirme ağacının üzerine
  bütün eski yeniden üretim zinciri çalıştırılmadı.
- Son **tam oyun VitaSDK ARM ELF link** başarılı:
  `work/build-G171-ELF-ONLY/im2_beta`, ARM EABI5 statik ELF32.
  SHA-256 `db7aa0b00121ef7040e4f8fb762578d0b8cd7cdac938b62896058a3697bfcb50`.
  Günlük `/workspace/im2-current/world-height-final-arm-build.log`.
- Kod commit'i özel dala push edildi. Yeni CI entegrasyonu eklendi, fakat
  GitHub API bu makinede CONNECT 403 verdiği için uzak CI sonucu **doğrulanmadı**.
  CI'ya başarı atfetme; yerel ARM ve host kanıtıyla karıştırma.

Detaylar: `research/b24_unified/world_height/README_TR.md`, yerel günlükler:
`/workspace/im2-dev-checks/world-height/` (`baseline-takeoff.log`,
`baseline-landing.log`, `strict.log`, `sanitizers.log`, `g248-final.log`,
`runtime-hashes.json`, `regression-results.json`). Özgün başlangıç ve tarihî
G161 cihazda yerinde-yürüme sorunu hâlâ açık; cihaz/FPS kanıtı yok. Yedi kabul
kapısı false kalır. **Yeni VPK üretilmedi.** Eski `55f3392` tanılama paketi bu
düzeltmeyi içermez; `/workspace/im2-current/authorized-device-test-55f3392/`
altına korunarak taşındı, eski `work/device-test` yolu uyumluluk symlink'idir.
Kullanıcı tekrar istemeden o eski paketin teslim/yükleme işini sürdürme.
Sonraki kaynak hedefi hâlâ gerçek MC model/world/CollisionData başlangıç bağıdır.

**23 Ekim 2026 — kullanıcının mevcut-durum cihaz testi kapsam onayı:**
Yedi kapı açık olduğu belirtilerek sorulan soruya kullanıcı “şimdiye kadar
çözdüğümüz her şeyi test edelim” yanıtını verdi. Bu, AGENTS.md'de kayıtlı
**tek tanılama VPK'sı** istisnasıdır; tam-port kapıları değiştirilmedi.
`55f3392` kaynak/paketleme commit'i üzerinden güncel ELF tekrar başarıyla
derlendi. Circle gerçek olay regresyonu (5 senaryo) ve G279 CSV analiz testi
tekrar geçti. `tools/device_test/build.py`, eski eksik CMake VPK hedefi yerine
beş zırh dahil 669 güncel runtime varlığını paketledi; ZIP CRC, tam dosya kümesi,
tüm varlık SHA-256'ları, SELF ve SFO kimliği doğrulandı.

- Paket: `work/device-test/IronMan2_Current_Device_Test.vpk`, 94.734.243 bayt.
- SHA-256: `c35443c1796544d9c371e07ca0147989be50629b770f347743fdc76a7a9596ec`.
- Ayrı kimlik: `IM2DG0001`, `Iron Man 2 - Device Test`, `00.01`.
- Manifest: `work/device-test/manifest.json`; test sırası: `tools/device_test/README_TR.md`.
- Fiziksel Vita kurulumu/çalışması yapılmadı. Kaynak başlangıcı/yürüyüş, tam
  görev/savaş/ses, özgün ışık ve FPS hâlâ cihaz/kaynak kabulü bekliyor.
- Özel GitHub draft release ID `421792594`, tag `device-test-2026-10-23-55f3392`
  oluşturuldu; **asset yüklemesi başarısız, release boş**. `uploads.github.com`
  ağ erişimi reddedildi. Alan adı mevcut özel izin listesine eklenerek ortam
  taslağı kaydedildi; kullanıcı ayarlardan kaydedip yayımlayana kadar etkinleştiği
  iddia edilemez. Etkinleşince aynı paketi `gh release upload` ile yükle;
  yeni VPK üretme, eski artifact'ları silme, draft'ı genel sürüm diye yayımlama.
- `/mnt/data` bu makinede yok; oluşturma/kopyalama Unix dosya izni yüzünden
  başarısız. Sohbet indirme eki teslim edildiğini iddia etme. Dosya gerçek ortak
  çalışma alanında mevcut. VPK hedefi için tekrar kullanıcı onayı isteme.
- Yerel/saklanan ELF derleme komutunun VPK yokluk kontrolü artık yalnız önceden
  yetkilendirilmiş `work/device-test` çıktı dizinini dışlar; hedef hâlâ `im2_beta`.
  Ortam başlangıç talimatına bu istisna eklendi; yayımlama kullanıcıya aittir.

**Belge tarihi:** 23 Ekim 2026  
**Proje sahibi hedefi:** Gameloft'un orijinal **Iron Man 2 iOS 1.0.0/1.0.3** oyununu PS Vita için aslına sadık, gerçekten oynanabilir bir sürüm olarak yeniden çalıştırmak/portlamak. Ana öncelik Chapter 1 / Stark Expo'nun orijinal açılışı ve mekanikleridir.  
**Özel depo:** `Gh0sTRX/Iron-man-2-os`  
**TEK AKTİF geliştirme dalı:** `feature/b24-unified-gameplay`; eski `main` üzerinde çalışıp güncel değişiklikleri ezme.  
**Bu devir anında dal HEAD:** `e1de61940e57db4bf9ad722eb8761cdf21c5963b` — G305 devir raporu, yalnızca doküman güncellemesi. İlk görevde `git fetch` yap, gerçek HEAD'i tekrar kontrol et; burada yazan SHA'yı ileride güncel sanma.

**23 Ekim 2026 — yürüyüş teşhisinde XYZ düzeltmesi:** G227 tek-kare ve G229
120-kare gözlemcileri GPU kökü ile çözülmüş dünya kökü farkını yalnız XY'de
ölçüyordu. Eşit XY, dünya Z=`0.07250`, GPU Z=`2.82955` sentetik regresyonu eski
başlıklarda yanlışlıkla uyumlu sayılıyordu. Fark artık XYZ'de ölçülüyor; mevcut
eşik ve tanı öncelikleri korunuyor. `world.z → camera.player_z → frame_pose.z`
aynı köktür; G168 `native_bind_min_z` düzeltmesi sonraki mesh matrisindedir.
İki regresyon eski kaynakta başarısız, düzeltilmiş kaynakta strict C11 ve
ASan/UBSan altında başarılıdır. G229 installer ve G279 kaynak/CSV testleri de
geçti. İki teşhis test programı VitaSDK ile ARM ELF olarak derlenip bağlandı;
ARM testleri cihazda çalıştırılmadı. G229 dar CI aynı kontrolleri içerir.
Fizik, çarpışma, kamera, mesh dönüşümü ve CSV biçimi değiştirilmedi.
**Gerçek Vita yerinde-yürüme nedeni hâlâ açık; yeni VPK yok.** `d752c82`
için [G229](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39941485764)
ve [G279](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39941485758)
CI başarılıdır. Aynı commit'in
[G171 akışı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39941485761)
dokuz özgün kaynak girdisini geri yükledi ve G226 dahil kontrolleri geçti;
ara teşhis yüklemesi depo artifact kotasına takılınca kalan yedi zorunlu
kontrol/ELF adımı **çalışmadı**. G171'in isteğe bağlı rapor yüklemesi bu yüzden
tüm zorunlu kontrollerden sonraya taşındı ve yükleme hatası engelleyici
olmaktan çıkarıldı. Kod testleri ve ELF derleme komutları zorunlu kalır.
Yeni standart-kütüphane regresyonu bu sırayı ve hata ayrımını korur.
GitHub API erişimi artık çalışıyor; yerel artifact indirme ve ayrıntılı
günlükler için gereken belirli depolama hostları ortam taslağına eklendi.
Eski B16E ELF başarısını güncel tam G171 oyun derlemesiyle karıştırma;
ilgili commit'in gerçek son ELF adımının tamamlandığını ayrıca kontrol et.

**Tam doğrulama sonucu:** Kaynak commit `df9a1687a762396cd0466bac967816b9a637af41`
için [G171 tam kaynak/ELF CI](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39944848054)
ve [G229 CI](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39944848051)
başarılıdır; zorunlu adım atlanmadı. İsteğe bağlı G226 raporu kota nedeniyle
yüklenemedi. Aynı kaynağın 50 zorunlu shell adımı bulut makinesinde de geçti;
`work/build-G171-ELF-ONLY/im2_beta` ARM ELF olarak bağlandı. G248 mevcut
prototip boot `(0,0,0)` noktasından +Y yönünde 120/120 kabul edilen kare ve
yaklaşık `10.0702` yol ölçüyor; bu, özgün hikâye başlangıcını veya cihazdaki
SDL/GPU davranışını kanıtlamaz. En erken açık kaynak bağı, orijinal MC
parent/world başlangıç dönüşümüdür. Güncel ana döngüde B14 → G75 → world XYZ
→ camera.player XYZ → GPU frame_pose arasında kaybolan bir öteleme
kanıtlanmadı. Gerçek cihaz verisi olmadan tarihî G161 yerinde-yürüme
sorununun çözüldüğünü söyleme; G279 kaydının eski G161 paketinde bulunduğunu
varsayma. Yeni VPK üretilmedi, kaynak kabul kapıları değiştirilmedi.

**Circle / duraklatma ve özgün başlatma tüketicileri:** `c224822` kaynak
düzeltmesi, duraklatılmış menüde Circle ile devam ederken B14 uçuş/iniş
durumunun da değişmesini engeller. G5'in gerçek üretilmiş olay yolu, gerçek
B21 menü denetimiyle beş host senaryosunda ve ASan/UBSan altında doğrulandı;
normal oynanıştaki kalkış/iniş davranışı korunur. `d2f57ca` için
[tam G171 CI](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39947952911)
bu regresyonu ve tam Vita ARM ELF derlemesini geçti; yerelde de 51 zorunlu
shell adımı geçti. Bu, tarihî G161 cihaz yürüyüşünün düzeldiği kanıtı değildir.

[G254 özgün kaynak taraması](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39948307708)
`5e06a63` üzerinde özgün yürütülebilir SHA-256'sını doğrulayıp üç eksik
tüketicinin sembol-sınırlı ARM çözümlemesini aldı: `Entity3D::Init` (`0x139F0`),
`Entity3D::GetPosition` (`0x12EA4`) ve `WCollision::Init` (`0xA54FC`). Sonuncu
512 kayıt sınırını aştığı için sınır 1024'e çıkarıldı; artık üç pencere de
kesilmeden alınıyor. Bu doğrusal çözümleme literal havuzlarını da komut gibi
çözebilir; her satırı yürütülmüş komut veya runtime izi sayma.

Özgün getter, model varsa `Model::GetPosition()` sonucunu döndürüyor;
model yoksa PositionData `+4/+8/+0xC` alanlarını kopyalıyor. Entity3D init,
model yolu üzerinde PositionData konumunu Object3D sanal slot `+0x10`'a
iletiyor; slotun tam hedefini yalnız bu argüman akışından uydurma.
Actor `+0x3D4` alanının `CollisionData` nesnesi olduğu, özgün ctor çağrısı
`0xDABDC` ve pointer yazımı `0xDABF0` ile bağlandı. WCollision init, bu pointer
varsa CollisionData `+0x18/+0x1C/+0x20` değerlerini PositionData konumuna ekleyip
collision primitive kurucusuna iletiyor. Bunlar doğrulanmış bellek/veri
akışlarıdır; alanların CLARA adları, MC'ye özgü değerleri, model/world/feet
eşdeğerliği ve sonraki hareket callback'leri henüz kanıtlanmadı. Oyun
başlangıcını `25.054` veya başka bir katmana taşıma. Entity3D/Actor/MainCharacter
dar sembol envanterinde `GetAbsolutePosition` bulunmadı; bunu bütün motorda
mutlak dönüşüm olmadığı şeklinde yorumlama. Sıradaki dar kaynak hedefi,
model konumu/sanal setter ve MC CollisionData alanlarının özgün bağını çözmek.

## 0. Senin rolün / çalışma biçimi

Sen yalnızca plan üreten veya sohbet eden bir AI değilsin: **repo içinde çalışan, kod değiştiren, tersine mühendislik kanıtlarını denetleyen, kendi testlerini yazan, CI sonuçlarını okuyup gerektiğinde kendi değişikliğini düzelten baş geliştirici ajan** olarak davran.

- İşini kanıtlanmış kaynağa göre yap, her adım sonunda gerçekten kod/test/derleme ilerlemesi bırak. Aynı raporu farklı G numarasıyla tekrar yazma.
- Kullanıcı defalarca `devam et` demek zorunda kalmasın. Görevin tanımlı ve araç erişimin olduğu sürece bir sonraki güvenli mühendislik adımına kendin geç. Uygun araç/süre bittiğinde sonuçları repo içinde kalıcı raporla; **24/7 çalışma, arkada çalışma veya daha sonra kendiliğinden teslim** iddia etme.
- Sırf kullanıcı yeni bir fikir söyledi diye mevcut önceliği bozma. Yeni istekleri uygun iş aşamasına koy; tek kök neden/tek hedef odaklı kal.
- Kritik mantıksal hata, yanlış port varsayımı veya geçmişte yazılmış G/B kodunda orijinal iOS ile tutarsızlık bulursan **önce yeniden üret, sonra orijinal kaynakla kanıtla, sonra düzelt, regresyonla doğrula**. Geçmiş kodun kutsal değil. Ama kaynağı kanıtlanmadan çalışan her şeyi de silme.
- Rutin source edit/test/commit için tekrar tekrar izin isteme; kullanıcı onayı gerektiren dış işlemler, dağıtım, firmware, cihaz kurulumu ve **VPK** için dur.

## 1. BAĞLAYICI belgeler ve kaynak hiyerarşisi

Çalışmaya başlamadan aşağıdakileri gerçekten oku:

1. **`AGENTS.md`** — projenin asıl ve öncelikli mühendislik sözleşmesi. Bu belgeden daha yetkili; çelişki varsa onu izle.
2. **`CLAUDE.md`** — başka ajanlara aktarım için geçmiş kısa notlar.
3. Bu **`CODEX_HANDOFF_TR.md`** — Codex için son aktarım ve iş sırası.
4. `research/b24_unified/g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json` — bütün kaynak kabul kapıları.
5. Son kaynak kod, `git log`, açık issue/PR varsa onlar ve **GitHub Actions gerçek CI logları**. Eski tarihli raporlar otomatik olarak güncel gerçek kabul edilmez.
6. İlgili modülün `G*.md` teknik devir dosyası, orijinal iOS decode / Mach-O ARM / CLARA Lua / G8 IM2V veri kanıtı.

**Kanıt hiyerarşisi:**  
A: Orijinal 2010 iOS IPA'dan doğrulanmış byte/opcode/animasyon/StateData/scene bilgisi.  
B: Bu kanıta dayalı host test, orijinal kaynak veriyle tekrarlanmış karşılaştırma.  
C: Tek oyun kaynağından VitaSDK ARM object / ELF compile+link.  
D: Vita3K'da gerçekten render edilip input kullanılan çalışır test (desteklenen grafik altyapısı şart).  
E: Kullanıcının gerçek PS Vita cihazında gördüğü/test ettiği çalışma, log/video/ekran ve performans.  
**B veya C, D/E yerine geçemez.** Sentetik .im2v, mockGL, stilize PNG, G8 isim benzerliği veya 120/120 CPU testi gerçek Vita oynanışı değildir.

## 2. OYUNUN ASLINA SADAKAT — kesin yasaklar

- **Yeni VPK YOK.** Kullanıcı, tüm gerekli kaynak kapıları tamamlanmadan test VPK'sı istemiyor. Otomatik VPK üreten eski Actions/workflow'larını yanlışlıkla tetikleme; push/path trigger ve build target'larını incele. VPK oluşturma, paketleme, yayımlama, kullanıcının cihazına yükleme.
- Eski kullanıcıya ait IPA, ses, animasyon, PVR veya firmware dosyalarını GitHub'a rastgele yükleme, kamuya ifşa etme, CI artifact'larında ham kaynak dağıtma. Özel depoda bile hassas dosya taşımadan önce yetki/kapsamı doğrula.
- Orijinal iOS kaynakta **olmayan** hız, damage, hit window, input, attack, collider, rig, spawn, renk, ışık veya görev davranışını **orijinalmiş gibi** yazma. Mecburi geçici prototip varsa `EXPERIMENTAL` / `UNKNOWN_ORIGINAL` / opt-in diye etiketle, açık kabul kapısı bırak.
- Özgün C1L1 görünmez duvarlarını/çarpışmaları topluca silme, ground root sorununu karakteri rastgele ışınlayarak çözme. Yanlış moon UV'yi tahminle döndürme, karakter boyunu varsayımla 2x yapma.
- Orijinal animasyon süresi, özgün saldırı olayının zamanı ve *düşmana hasar/isabet anı* aynı kavram değildir. Bir `_att` dosyası görmek bir mermi veya hasar olayı kanıtı değildir.
- Kullanıcı **etkileşimli HTML istemiyor**. Doğrudan sohbette görüntülenebilen sahici kaynak-render PNG/GIF uygundur. Yapay zekâ ile üretilmiş oyun ekranı, başka oyundan sahte önizleme veya hayalî 60 FPS verisi üretme.
- “Sorun çözüldü” ifadesini yalnızca gerçekten test edildiği seviye için kullan.

## 3. Teknik mimari — TEK SAHİP kuralı

Bu proje çok sayıda aşama kodu (B1/B14/B24/G8/G83/G84/G171/G305 vb.) barındırıyor. Kod kimliklerini ezberlemek yerine gerçek `work` kaynağını test et:

- **B14**: dünya konumu/hareketin tek fizik integratörü. G75/G66C kaynak collision doğrulama katmanlarıyla birlikte. İKİNCİ hareket entegratörü veya animasyondan sahte root-motion ekleme.
- **G83 → G84**: fizik moduna/inputa göre kaynak 2010 IM2V animasyon adı seçme ve ana döngüde bütünleme. G301 fiziksel uçuş yönünü, hâlâ ekranda oynayan önceki pinned dönüş animasyonundan ayırdı. Animasyon rotası, orijinal iOS controller semantiğinin ispatı değildir.
- **G8**: özgün IM2T/IM2V animasyon dosyasını oynatan tek ana renderer/stream. G302 suit switch sırasında önceki repulsor olayını temizledi; G303 aynı suit içinde tek kaynak shot klibini yön değiştirmede koruyup ground/hover/Stage2/Rush geçişinde sahte ikinci shot pozunu engelledi. Var olan G169/G173 üç fazlı Uni-Beam animatör önceliğini bozma. War Machine G172/G174 özgün 1292-vertex `Aim_M_Ground` dosyaları kanıtlı, ancak `Aim_M` otomatik `missile` demek değildir.
- **B16**: mevcut port kabul edilmiş silah input/shot sahibi; **G82/G88/G111**: kaynak izni/gerçek temas ve hasar için dar doğrulama kapıları. Native saldırı olayını klip adına bakıp ikinci kez oluşturma.
- **G213B/G217/G197/G218**: özgün 2010 `states` ve ARM `DoAttack` kaynak kanıtı. Orijinal 55 StateSet, 1487 StateData, 3658 StateTrack; 4 zırh ×194 native state. G305 G218'de 60 karede aynı ham saldırıyı 60 olay diye sayma hatasını düzeltti; kaynak `AttackType` ile orijinal jump table statik okunuyor, **native StateMgr runtime input/weapon identity kanıtlanmadı**.
- **G68/G71/G95/G298/G299**: Expo geometri/PVRTC atlas, alpha, deneysel statik şehir ve suit ışıklandırma. Kaynak dört `Sun001..004` düğüm konumları biliniyor; orijinal shader/falloff/ışık tipi/gölge davranışı henüz çözülmedi.
- **Mission000 / G137/G146/G152**: özgün LUA görevi, sahne ve QTE başlangıç verileri; tam özgün oynanabilir görev akışı değil.

`work/src/main.c` CI sırasında script zincirinden **geçici olarak inşa edilir**. Depoda var olmayan hayalî root `src/main.c` dosyalarını değiştirme. Entegrasyon sırasını `.github/workflows/g171-2010-source-sculpture-false-wall-ground-walk-G169-full-ARM-NO-VPK.yml` üzerinden incele.

## 4. Şu anda KESİN bildiklerimiz ve bilmediklerimiz

### Doğrulanan kaynak/CI bilgisi
- Gerçek C1L1 G66C collision bankası **1910 özgün üçgen** içeriyor; bazı yüzeyler çok katlı Z koordinatlı ve görünür haritadan farklı sınırlara sahip olabilir.
- G8 özgün dosyalarından Mark VI, Mark V, War Machine hareket/aim/melee/beam animasyonlarının bir kısmı decode edildi ve host kaynaktan akıtılıyor. **Tüm input/moveset/runtime bitmiş değil.**
- Gerçek Mark VI `AttackType=2` ile WM `25` aynı statik ARM branch `0xF6648`; Mark VI `1` ile WM `18` `0xF6930` ortak. Ortak branch ≠ aynı silah, füzeye basılan tuş, hit zamanı veya `WeaponDB` index.
- `DoUniBeamAttack`, özgün `WeaponDB::GetAttackEntityByIndex(4)` çağırıyor; bu `AttackType=4` ya da C1L1'daki `Attack_type4` isim sırası demek değil. `WeaponDB[0/1/4]` tam sahne kayıt eşlemesi halen eksik.
- G304 özgün animasyon `_att` ve combo ismini ikinci native hasar/ateş olayı sanan eski G83 bayrağını iptal etti. G305 özgün G217 ve ARM G197 statik kanıtını G218 read-only gözlemciye bağladı.
- Son **kaynak** doğrulama: [G218/G305 host başarı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39582453239); [G171 bütünleşik Vita ARM ELF-only başarı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39582416284), kaynak commit `826a3dda...`. Bu başarı **fiziksel oyun QA değil**. 23.10.2026 branch HEAD `e1de619...` belge commit'idir; yeni source commit'leri öncesi koşuyu kontrol et.

### Açık kritik problemler
1. **Ground walk-in-place / ilk gerçek world root:** Kullanıcının gerçek PS Vita testinde yürüme animasyonu oynarken karakter dünya içinde yürümüyordu. Yeni G171/G279/G296/G305 kaynak derlemeleri gerçek Vita'da yürütülmedi; kök neden kapanmadı. Araç/karakter ölçeği de sorunlu.
2. **Flight/hover/rush:** Mod ve G8 klip geçişleri host düzeyinde ilerledi fakat fiziksel uçuş, animasyon-poz/gerçek konum ve native permission hâlâ uçtan uca kanıtlanmadı.
3. **War Machine silahları:** `Aim_M` veya `Gun01..04` adından tahmini missile/gatling kontrolü uydurma. Gerçek native WeaponDB/state/input bağını araştır.
4. **Combat:** Özgün melee combo/hit frame/actor permission/damage, dummy düşmanın hasar alması, roket/Uni-Beam seçim/effect ve lock-on eksik. G11 Stage2/Rush'ta ateş yasağı bizim port politikamız; native iOS özdeş kural olarak ispatlanmadı.
5. **Expo görselleri:** Şehir modeli ve collision kaynağı var; fakat güncel gerçek GPU gösteriminde orijinal gece aydınlatması, çevresel ışık, araç/armor ışığı, skybox/PVRTC moon/stars, gölge, PNG/PVR alpha, orijinal model/araç oranı, kamera/UI tam kabul edilmiş değil.
6. **Mission000:** Orijinal level1 Lua, intro/QTE, enemy waves, ses/cutscene/pause ve başarı/yeniden başlatma uçtan uca tam oyun akışı değil.
7. **Cihaz testi / release:** B1/G1 eski gerçek GPU testinde VitaGL splash/SceGxm çökmesi yaşandı; bunu başarılı sürüm diye sunma. G295 CPU-runner Vita3K Vulkan `enumeratePhysicalDevices ErrorInitializationFailed` çıkıyor; değişmeyen GPU ortamında kör tekrarlama. G255 tüm `source_ready` kapıları **false**.

## 5. Değiştirilemez sıra — hedef kabul kriterleri

**Birinci:** Özgün ilk MC world-root ve G66C/G75 collision üzerinden **gerçek dünya konumu değişen yer yürüyüşü**. B14 kaynak tick → dünya XY/Z → collision proposal/resolve → avatar GPU root → kamera root ayrımını tek bir test zincirinde izleyip kök nedeni açıkça sınıflandır. G279/G296 `ux0:data/ironman2_g279_walk.csv` read-only izlemesini ve `g279_analyze_Vita_walk_trace_TR.py` raporunu kullan. CSV yoksa gerçek Vita kanıtı varmış gibi davranma; source-reproduction ve en küçük gözlemci düzeltmesi yap. Gerçek cihazdan iz gereken aşamayı kullanıcıya tek net testle açıkla.

**İkinci:** Hover/Stage 2/Rush hareket, irtifa, speed, crosshair/kamera ve kaynak kliplerin sırayla doğru seçilmesi; B14 tek dünya sahibi.

**Üçüncü:** G8 özgün 2010 zırh hareket bankası: yürüyüş, nişan, hover, uçuş, melee, repulsor/Beam pozları ve War Machine. Farklı rig vertex bankalarını karıştırma.

**Dördüncü:** Özgün WeaponDB → StateMgr/AttackType → input → gerçek orijinal G8 poz → Actor/EntityData izin/hasar. Geçici test etkinliklerini native gerçek diye işaretleme. Dummy, lock-on, rockets/gatling/Uni-Beam burada kaynakla bağlanır.

**Beşinci (ATLAMAK YASAK):** Stark Expo çevresi, materyal alfa, orijinal ölçek, gece gökyüzü ve ay, çevresel **IŞIKLANDIRMA**, dinamik armor/araç ışığı, gerçek gölgeler/floor contact, kamera/omuz üstü HUD. Her renderer değişikliğinde GL texture environment ve alpha/depth eski durumları geri yüklenmeli. Şehir gece ışığını yalnız bir flat tint ile 'tamam' sayma.

**Altıncı:** Orijinal Mission000 intro/QTE, düşman/NPC dalgaları, cutscene, sesler, tutorial/pause, başarı/failed/retry.

**Yedinci:** Aynı commit üzerinde gerçek C11 regresyon + native Vita ARM ELF-only tam oyun ve **G255'teki yedi kaynak kabul kapısının tamamı** nesnel kanıtlarla yeşil. Kullanıcının daha sonra vereceği açık onayla sadece **tek bir test VPK** hazırlanabilir. Kapıları testten önce `true` yapma, bypass etme.

## 6. Her görev için çalışma döngüsü

1. `git fetch`, dalı kontrol, `git status`; ilgilendiğin problemi, **gerçek önceki kullanıcı gözlemi** ve özgün iOS veri kanıtıyla tanımla.
2. Mevcut code owner ve CI patch zincirini oku. Eski G numaralı bir talimatı otomatik doğru kabul etme. Tam olarak yanlış davranışı üreten küçük testi **önce** yaz.
3. Kaynakla uyumlu en küçük değişikliği yap. Belirsizse açıkça `unknown`/fail closed kalsın; tahmini weapon/physics davranışını dayatma.
4. Dar host C11/Python/fixture testlerini çalıştır. Ardından ilgili gerçek G171 geçici oyun kaynağını toplayıp VitaSDK `im2_beta` **ELF-only** compile/link yaptır. Eski workflow testini kırdıysan logu oku, yanlış beklentiyi de kaynakla düzelterek **aynı yeni HEAD** için tekrarla.
5. Önceki yeşil modüllerin regresyonunu doğrula; yeni sınıflandırıcı/animator/physics sahibini çoğaltma.
6. Anlamlı kaynak editini **commit** et, CI sonucu gerçek linklerle raporla. Başarılı olduğundan emin olmadığın bir CI'yi 'başarılı' ilan etme.
7. Kısa Türkçe rapor: **[Kanıt / Değişen dosya / Gerçek test düzeyi / Hâlâ bilinmeyenler / Sonraki tek engel]**. Repo içinde gerekiyorsa tek güncel handoff dosyasını güncelle. Sırf rapor üretmek için seri G numarası verme.

**Hızdan çok doğruluk; ama bir dosyada takılı kalıp tekrar tekrar boş araştırma raporu üretmek de yok.** Yüksek etkili bir bug'ı gerçek testle çözüp sıradaki bloke edici adıma geç.

## 7. Kodex ilk açılış komutları ve İLK SOMUT GÖREV

Özel depoya erişim sağlandıktan sonra:

```bash
git clone git@github.com:Gh0sTRX/Iron-man-2-os.git
cd Iron-man-2-os
git fetch origin
git switch --track origin/feature/b24-unified-gameplay
git status --short
git log -6 --oneline
```

Repo daha önce klonlandıysa ikinci clone yapma; mevcut clone üzerinde `git fetch` ve doğru dalı aç.

**İlk somut görev:** `AGENTS.md`, `research/b24_unified/g279_vita_walk_persistent_trace/`, G276/G278/G279/G296/G305 handoff'ları ve son G171 tam source-ci adımlarını incele. G161 **gerçek cihaz yerinde yürüyüş** raporunun karşısında B14 world XY, G75 source collision, G278 visual root/camera ve G279 world-path telemetrisi arasında *kanıtlanabilir en erken kayıp noktası* var mı kontrol et; varsa aynı geçici Vita main üzerinden C11 gerçek kaynak testini üreterek düzelt. **Böyle bir kayıp kanıtı yoksa tahmini teleport/hız değişimi yapma**: mevcut G279 CSV'yi cihazdan almak için en dar, önceden hazırlanmış QA planını ve kaynakta ilave gözlemci gerekiyorsa onu teslim et. Bir yandan eski G11/B14/WMachine kaynak varsayımlarını G213B/G217/G197/G241 kanıtlarıyla denetle; fakat bu iş yürüyüşe odaklanmayı dağıtmasın.

**Örnek ilk testler:**

```bash
python3 research/b24_unified/g279_vita_walk_persistent_trace/test_g279_real_source_patch_guards.py
python3 research/b24_unified/g279_vita_walk_persistent_trace/test_g279_offline_vita_csv_analysis.py
cc -std=c11 -Wall -Wextra -Werror -pedantic -O2 research/b24_unified/g279_vita_walk_persistent_trace/test_g279_bounded_csv_writer.c -lm -o /tmp/g279_test_host_c11
/tmp/g279_test_host_c11
```

**Bitirme raporunun taslağı:**
- Hedeflediğim tek problem:
- Özgün iOS kaynak kanıtı / belirsiz kısmı:
- Düzelttiğim kod ve commit:
- Dar host CI sonucu / URL:
- Gerçek Vita ARM ELF-only sonucu / URL:
- Vita3K veya gerçek PS Vita'da bizzat kanıt var mı?:
- Hâlâ eksikler ve bir sonraki bloke edici adım:
- VPK üretildi mi?: **Hayır**

Bu belge bir **projeyi Codex'e devam ettirme** talimatıdır; yeniden sıfırdan oyun/motor/prototip oluşturma talimatı değildir. Kullanıcının temel beklentisi: **Orijinal Iron Man 2 iOS oyununu gerçekten sadık biçimde PS Vita'da oynanabilir hâle getirmek.**
