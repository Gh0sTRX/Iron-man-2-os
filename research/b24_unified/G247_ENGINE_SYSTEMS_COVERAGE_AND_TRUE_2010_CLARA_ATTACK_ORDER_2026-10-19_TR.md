# G247 — Iron Man 2 iOS (2010) → PS Vita: özgün oynanış motoru ilerleme ve kaynak dürüstlüğü

**19 Ekim 2026 · kullanıcı istediği motor değerlendirmesi ve gerçek G247 araştırması · `feature/b24-unified-gameplay` · VPK YOK.**

## Hızlı mühendislik değerlendirmesi: “motorun yüzde kaçı çözüldü?”

**Mutlak bir motor tamamlama yüzdesi bilimsel biçimde üretilemez.** Orijinal Gameloft iOS 2010 motorunun toplam çalışması gereken davranış/satır/oynanış sayısı tanımlı bir kabul test listesi olarak mevcut değil. Aşağıdaki bantlar kişisel mühendislik yargısıdır; bağımsız ölçüm/test sonucu değildir:

- **Karakter hareketi–animasyon–saldırı alt motorunun özgün 2010 iç işleyişini anlama: kabaca %35–45.** Esas kaynak akışına giriş, state tabloları ve bir kısım asli native çağrı topolojisini biliyoruz, fakat hareket fiziğinin orijinal parametreleri, gerçek StateMgr canlı state seçimi, input, hit-frame/damage, kurulu silah/armor anlamı ve tam NPC AI hâlâ çözümlenmedi. *Bütün oyunun genel motoru için bu bandı doğrudan kullanmak yanlış.*
- **Vita'ya aktarılan ve derlenebilen oynanış iskeleti: kabaca %30–40.** Gerçek oyun derlemesinde B14 tek movement integratörü, G75 kaynak geometrisi çarpışması, G8 özgün IM2V anim, G83 routing, B16 port accepted-fire, G218 read-only state observer, G229 telemetry birleştirilmiştir. **Bunların tümünün doğru çalıştığı donanım parity kanıtı yok.** Bunlar özgün iOS motoru kodunun PS Vita üzerinde birebir çalıştığını da ifade etmez.
- **Orijinal Media Mayhem / Chapter 1'in tam, görsel açıdan doğru, oynanabilir demosu: tahmini %15–30 aralığında**; tam, fiziksel cihazda geçilmiş bir Chapter 1 görev kabul testi yok. Bunlar *tamamlanan 11 gate oranı* değildir.

Bu aralıklar öznel olduğu için birbirleriyle toplanamaz ve kesin kalan saat/tarih hesabı çıkarılamaz. İlerleme çoğunlukla **orijinal assets/metadata ve C++ fonksiyon kaynağı çözümü**, daha az ölçüde **gerçek Vita oynanış doğrulaması**dır.

## Kesin ölçülebilir veri: bunlar motor/oynanış tamamlanma yüzdesi değildir

| Veri / kod | Gerçek ölçüm | Ne anlama gelir / sınır |
|---|---|---|
| Orijinal `anims` bankası | **972 / 972** özgün klip girişinin iskelet pozisyon/quaternion/timing kaydı çıkarıldı | Tümünün Vita'da oynadığı, her zırh rigine uyarlandığı veya animasyonun tuşa bağlandığı anlamına gelmez |
| Özgün oyuncu adayı klipleri | 248 IronMan + 56 WarMachine + 34 UnderwaterArmor = **338** | Bu 338 dosya runtime gerçek oyun klip seçimi değildir |
| G83 yönlendirici katalog | **109** özgün hareket/nişan adı ve süre ile route; 109/109 stream dosyası G84 kaynakta mevcut | **109/338 ≈ %32 isimsel yönlendirme kapsaması**, geçerli fiziksel zırh poz/komut hit rate'i değildir |
| Orijinal serialized `states` | **361.393/361.393 bayt**, **55 StateSet**, **1.487 StateData**, **3.658 StateTrack**, **379 AttackType entry** | Veritabanı formatının çözümü güçlü; orijinal StateMgr gerçek zaman seçimi ve tüm state→IM2V eşlemeleri tam değil |
| G217 oyuncu StateData | **4×194 = 776** gerçek original state ve events kaynak C tablosuna aktarıldı | G218 gerçek G8 streamed clip adına **gözlemci** ile eşleştiriyor, özgün iOS oyun logic state driver değil |
| Orijinal C++/ARM | `LC_SYMTAB` **65.500 sembol**, G238 **14.164** gerçek method boundary tarandı | Tüm 14.164 metodun semantiği veya motorun 65.500 işlevinin çözüldüğü **anlamına gelmez** |
| Orijinal C1L1 `level1.bclara` | **587** typed record; **26 Attack, 13 Weapon, 1 WeaponAccessory** | Kaynak sınıf üyeleri, özgün WeaponDB runtime index değil |
| Güncel yeni-release readiness | `g83_final_vpk_gate/READINESS_STATUS.json` içindeki **11 gate'den yalnız animasyon bankası source-index gate'i verified** (2026-10-16 snapshot) | Güncel diğer host/ELF kanıtlarına rağmen tüm oyun gameplay/hardware gate'leri kapanmış değil; stale tarihli kartı motor %9 olarak yorumlama |

## Alt motorlara göre somut durum

### 1. Movement / ground / collision — **kısmen aktarılmış, cihaz hatası açık**

B14 `b14_world_tick` gerçek birleşik oyun ana döngüsündeki tek dünyayı değiştiren hareket tick'idir; G75 orijinal C1L1 collider kaynağından yaklaşık **1.910 orijinal triangle** ile deneysel üç-yükseklik capsule temasını değerlendirir. Gerçek Vita gözlemi: **yerde yürüme animasyonu var, dünya hareket etmiyor**; uçuşta yer değiştirme var. B14 sabit hızları ve G75 öneri hızları **özgün Gameloft fiziği değil, port geliştirmesi**. Orijinal iOS ivme/root motion/ground state/kamera bileşimi henüz %100 belirlenmedi.

**[G239 gerçek bütün Vita ARM `im2_beta` ELF PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39220727358):** G227+G229 **120 başarılı render frame** analog girdi, önerilen B14 world XY, G75 kabul edilen world XY, GPU karakter root ve kamera pozisyonu tanısı derleme ana zincirine kuruldu. Ama **cihazdan 120 karelik gerçek log yok**. Derleme başarısı yürüyüş düzeltmesi değildir. 120 frame süresi FPS'ye bağlıdır, zorunlu 2 saniye değil.

### 2. Hover / Flight / Rush — **temel sahne hareketi var, orijinal davranış eksik**

Port B14 normal yerde hareket, Stage1 hover, Stage2 flight ve Rush/boost ayrımını tutuyor; G83 gerçek IM2V flight/roll/dodge kliplerini ad ve süreleriyle seçebiliyor. Uçuş kullanıcı tarafından gerçek Vita'da hareketli görüldü, ama **yerine kurduğumuz hız/ivme/kamera kalkış/frenleme orijinal 2010 touch davranışından doğrulanmadı**. Mark V ilk görev uçuş izni orijinal Lua/Mission000 kurallarıyla eşleştirilmeli. Stage2/Rush nişan/ateş erişimi kullanıcı talimatına göre ayrıca denetlenmeli.

### 3. Animasyon/rig/moveset — **format çözüldü, runtime bağların tümü değil**

G81 gerçek 972 kaynak anim track formatını çözdü. G83 109 özgün yönlendirme klibini, süre bilgisini, dört yön walk/hover/flight/aim, Mark VI 3'lü `Ground_Combo_1/2/3` ve WM `Aim_M` adayını kayıtlar üzerinden sağlıyor. G84/G85 ve G169/G173 bunu G8 tek gerçek IM2V animatöre port oyun ana döngüsünde bağladı; Mark V `suitcase` önek ve UniBeam geçiş priorite hatası düzeltildi. G8 gerçek klip örneklerinin **tümü oyun içinde test edilmiş değil**; Mark V 629v, IronMan 802v, WM 1292v farklı rig; tam 338 clip/armor rig parity yok. WM'nin `M` eki füze olduğunun kanıtı değildir.

### 4. Özgün StatesMgr ve saldırı event motoru — **en güçlü native mantık bulgumuz**

2010 iOS native `StateData::GetParam("AttackType") → StateTrack::GetEvent(prev,now) → original event [index].third u32 → Actor::UpdateStateAttack → vtable MainCharacter::DoAttack(AttackType,event)` kaynak ARM olarak kanıtlandı. `DoAttack` içte 4 kollu native event tablosu; G233 gerçek C++ `GetWeapon(0)`, `GetAssistantWeapon(0)`, `GetAttackEntityByIndex(0/1)`, `DoUniBeamAttack` kaynak çağrı sembolleri ve branch kimliklerini doğruladı.

**ÇÖZÜLMEDİ:** iOS gerçek canlı current StateMgr state'in hangi girişle hangi clip/hit’e yol açtığı, event.third 0/1/2/3'ün bütün AttackType'lerde ateş/silah/hasar semantiği, B16 kabul edilmiş port ateşinin özgün olay olma kanıtı, orijinal status/AI zamanlama. G218 dosya adı temelli state eşlemesini zaten `actual_2010_StateMgr_runtime_state_PROVEN=0` olarak tutar. G235 referans tablosu sahte roket/damage üretmiyor.

### 5. Combat / melee / repulsor / füze — **yapı çözüldü, oynanış tamam değil**

G76 `Actor::Damage` iki kaynak float dayanıklılık alanı math, G77 gerçek `TestMeleeHit` 0.5 model BBox source genişliği, G82 üç native combo süre/önceliği, G85 ve G169 accepted port repulsor/UniBeam animasyonunu destekliyor. G233–G245 `WeaponDB` ayrı pointer/capacity/count dizilerini, gerçek native load zincirini buldu; G247 C1L1 saldırı kayıtlarını sıralama adaylarına dönüştürdü. **Eksik:** 26 original Attack hasar değerlerinin kayıttan bütün silahlara gerçek runtime eşlemesi, active hit-frame/cancel, melee çoklu combo ve counter/throw, füze lock-on, WM gatling/shoulder, düşmana sağlık ve ölüm/hurt reaksiyonu, orijinal input gesture. Dummy gerçek enemy AI değildir.

### 6. Mission, AI, input, audio, visuals — **yapısal/ön çalışma**

Özgün Mission000 Lua, açılış QTE1456, MarkV uçuş izni, native mission StateMgr ve bazı NPC/AI C++ methodları çıktı; ama başlangıç→oynanış→düşman→görev başarı loop Vita’da kapanmadı. TouchHLE orijinal ana menü ve Media Mayhem brifingini açtı, Linux mutex hatasında düşüp gerçek 2010 combat input/hit verisi elde edilemedi. HUD ve omuz kamera örneği var fakat doğru 3D ekran/world scale ve ışık, skybox/ay/gölge/PNG alfa PS Vita QA'ı yok. G139/141/145/146 özgün ses ve görev müziği kaynak altyapısı var ama full audio/mission parity yok.

## G247 — bu turda gerçek yeni kaynak ilerlemesi

**[G247 gerçek orijinal 2010 iOS CLARA CI PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39229249239)**:
- `g247_authentic_C1L1_Attack_record_name_offset_vs_native_index_hypothesis.py` gerçek 2010 `level1.bclara` 587 typed entry üzerinden 26 Attack, 13 Weapon, 1 WeaponAccessory'yi özgün G241 type switch ve G245 `EntityData+0x14` alanlarına bağlayarak *aday* file-offset/node-ID sıralamaları hesaplıyor.
- **26/26 Attack, 13/13 Weapon ve 1/1 Accessory kayıtlarında dosya içi original name-offset sırası ile original scene node-ID artan sırası aynı.** Bu, iki bağımsız source sıralama ipucu olarak faydalı, canlı ClaraFile list/WeaponDB insert sırasının kesin kanıtı değildir.
- `Attack_type0` source file rank 0, scene ID 329; `Attack_type1` source rank 1, scene ID 332; `Attack_F22_missile` source rank 13, scene ID 1009; `Attack_WM_Missile` source rank 25, scene ID 1059. **Ranklar WeaponDB[0/1/13/25] değildir** ve motor/füze bağlantısı olarak oyun koduna uygulanmadı.
- C1L1 başka `Attack` kaynak kayıtları, başka mission dosyaları ve global/load sıra bağımsız kontrol edilmedikçe weapon DB array index kuralı söylenemez. Orijinal semantic değerler UI'ya veya combat'a taşınmadı.

## İleride cihazda bitmiş saymak için

Sahneye giriş, gerçek dünya XY (yer yürüyüş), tavan/duvar collision, tüm hedef zırhların orijinal rig clip bağlantısı, orijinal projectile/melee hit ve düşman hasarı/hurt, gökyüzü/ışık/ölçek/HUD, Mission000 QTE/cutscene ve başarı koşulu **aynı Vita build’inde ve gerçek donanımda** geçmeli. G83 release gate'deki kullanıcı talimatı gereği bundan önce yeni VPK yok. **Bir sonraki kritik teknik iş G229 logunun fiziksel Vita'dan alınması ve orijinal WeaponDB sıranın canlı stream verisiyle doğrulanmasıdır.**
