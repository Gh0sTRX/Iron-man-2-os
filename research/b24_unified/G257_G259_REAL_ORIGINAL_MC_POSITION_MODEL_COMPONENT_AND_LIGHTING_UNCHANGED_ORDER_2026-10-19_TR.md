# G257–G259 — Orijinal MC Position/Model bileşenlerini çözme + ışıklandırmayı sırasını değiştirmeden zorunlu kabul aşamasına ekleme

**Tarih: 19 Ekim 2026. Depo: `Gh0sTRX/Iron-man-2-os`, `feature/b24-unified-gameplay`. VPK YOK.**

## Talimat: mevcut iş sırası değişmedi, ışıklandırma harita/görsel aşamasında zorunlu

**GitHub kaynak kabul sırasını birebir koruduk**:

1. Orijinal `MainCharacter` başlangıç dünya root/PositionData/yer yüksekliği, G75 çarpışma
2. Movement: yere yürüme, hover, Stage2 flight, rush; tek B14 dünya integratörü ve gerçek G66C
3. Orijinal IM2V/G8 animasyon, 338 player clip rig/state/input/events, WM animasyonları
4. Özgün WeaponDB/Combat: repulsor, missile, WM gatling, melee combo, hit/damage/target dummy
5. **Harita + orijinal ışıklandırma**: karakter/araç gerçek ölçeği, özgün gece sky/moon, bütün şehir/yol, Sun001..004 kaynak sınıfı, ambient + armor/vehicle/building illumination, gerçek gölge/zemin teması, transparan PVRTC/PNG alpha ve materyal sorting, kamera/HUD
6. Özgün Mission000 intro QTE1456, ses/cutscene, spawn enemy waves, mission success/end
7. Aynı kaynak commit'te tüm gerçek oyunla host + VitaSDK ARM ELF derleme kabulü; **ardından tek VPK**, cihaza kurulduktan sonra gerçek Vita QA

**Değişiklikler:** `g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json` 5. maddedeki `test_details` kesin lighting kabul şartlarını ayrıntılandırır; `g83_final_vpk_gate/READINESS_STATUS.json` post-VPK gerçek cihaz lighting/alpha/shadow QA şartını genişletir. **Yedinci/sıra veya toplam gate sayısı değişmedi (7 before test VPK, 12 after)**. `g255_fail_closed_one_vpk_only_after_original_vita_gameplay_qa.py` 7 kaynak maddeyi bu **tam sırasıyla** kontrol eder; 5. maddenin `lighting`, `Sun001..004`, `ambient`, `shadow`, `alpha`, `armor`, `vehicle` şartlarını çıkarma girişiminde **CI başarısız olur**. Mevcut tamamlanmış kaynak gate **0/7**, tek VPK sonrası kalite gate **1/12** (yalnız 972/972 animasyon index source). Bu rakamlar oyun motoru yüzdesi değildir. Test VPK veya Vita hardware QA henüz yok.

**Özgün ışıklandırmaya ilişkin doğrulanmış kaynaklar / henüz belirsizler:**
- G30 gerçek `level1.bclara` içinde **4 özgün tipli `Light` sınıfı nesne**: `Sun001, Sun002, Sun003, Sun004`, gerçek yerel CLARA transformları ve `0xFFBEAEFF` benzeri orijinal ham özellik. Ancak ham kayıtların nihai renk/yoğunluk/type ve dünya dönüşüm semantiği henüz kanıtlanmadı.
- G72 gerçek özgün `C1L1_sky_001.bdae` **6 mesh/96 triangle**; `C1L1_sky_02.tga` ve `C1L1_sky_03.tga` PVRTC kaynak iki gökyüzü atlasi. Nihai native shader material–atlas eşleşmesi kesin çözülmedi.
- G71 city `31` original texture banks, alfa taşıyan `7` material atlas ve 1282 orijinal translucent triangle; source depth-pass A/B var, fiziksel Vita görüntü testi yok. Mevcut G72/G75 CPU vertex tint/fake moon/ambient patch'i **orijinal 2010 shader kanıtı değil**; CI derlenmesi gerçek çevresel ve karakter aydınlatması/shadow parity kanıtı değildir.
- Bu aşama geldiğinde şehirde sabit baked light tek VBO, armor/araçlar için gerçek runtime malzeme ışıklandırması, kaynak alfa/depth, yer gölgesi ve sky ile birlikte QA. Salt koyu arka plan veya CPU tahmini aydınlatma **lighting gate PASS** olmayacak.

## G257 — Gerçek orijinal 2010 Entity3D kaydında iki farklı kaynak bileşen

[**G257 original iOS source CI SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39240927287).

- Gerçek özgün `Entity3D::LoadFromFile(EntityData*)` native `0x12C78`: `0x12C88 BL Entity::LoadFromFile`, `0x12C98 BL PositionData::PositionData`, `0x12CB0 BL EntityData::GetParamComponent`; ardından `0x12CC0 BL ModelData::ModelData`, `0x12CD8 BL EntityData::GetParamComponent`.
- Orijinal oyuncu `MainCharacter` sınıfının kaynağı `MC` sahne düğümü (nodeID 1062), gerçek child rigid transform nodeID **1064**, kaynak yerel `(-1.319,-6.747,25.054001)` quaternion identity/scale1. Bu **kesin runtime/ayak dünya XYZ** değil, kaynak authored transform.
- Gerçek `Entity3D` bellek alanları: `PositionData* +0x70`, `ModelData* +0x74`; source `STR r4,[r5,#0x70]`, `STR r4,[r5,#0x74]`. Burada orijinal MC başlangıç world Z henüz bilinemiyor.

## G258 — Artık özgün bileşen adları TAHMİN değil, native gerçek C string

[**G258 original iOS ARM PC-relative literal source CI SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39241268978).

- 2010 Mach-O `0x12C9C` PC literal pool `0x12CE0`; `ADD r1,pc,r2` `0x12CA4`; gerçek `EntityData::GetParamComponent` argüman native C string adresi `0x49BAF0`: **`"Position"`**. Bellek `Entity3D +0x70`.
- Aynı şekilde `0x12CC4` literal pool `0x12CE4`, `0x12CCC` ADD, gerçek string adresi `0x49BAFC`: **`"Model"`**. Bellek `Entity3D +0x74`.
- Bu, `MainCharacter::LoadFromFile → Actor::LoadFromFile → Entity3D::LoadFromFile → GetParamComponent("Position"/"Model")` gerçek 2010 source veri yolunu açıyor. **Sahne ebeveyn/alt transform dünya birleştirmesi, gerçek boot player root XYZ ve Vita'da yere yürüyüş düzeldi iddiası hâlâ YOK**. Sıradaki kaynak iş bu `Position` component'in gerçek `PositionData` alanlarını ve karakter boot yerleştirmesini izlemektir.

## G259 — Kullanıcı sırasını ve ışıklandırmayı otomatik koruma

[**G259 seven-workstream CI source preflight test**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39241435788). Tek VPK öncesi ışıklandırma 5. iş akışından atılırsa veya ilk 7 adım sırası değişirse `--require-ready` öncesinde bile script hata verir. Anim, combat, sky/shadow henüz bitti ilan edilmedi. VPK oluşturulmadı.
