# B24 G65 — PS Vita ilk kaynak harita / hareket / collision betası (G66 derlemesi)

> **Gerçek VPK oluşturuldu ve GitHub Actions üzerinde doğrulandı.** PS Vita cihazında henüz çalıştırılıp doğrulanmadı; oyun içi FPS, render çıktısı ve bütün çarpışmalar kullanıcı cihaz testi bekliyor.

**CI:** https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38879471661  
**VPK:** \`IronMan2_B24_G65_Playable_Beta.vpk\` (CI artifact içine paketlendi).  
**Vita Title ID:** \`IM2G65001\` — eski B24/G10/M1/M2 testlerinin üzerine yazılmaz.

## İçerik ve sınırlamalar

- **G65 özgün 2010 C1L1 kaynak sahnesi:** G55/G57/G64/G65 araştırmalarındaki **296** yerleştirilmiş BRES mesh, **22.441** özgün kaynak üçgeni; gerçek kaynak UV ve **31 özgün PVR atlasının** 2010 IPA'dan çözülen pikselleri. WebGL G65 GLB sahnesinin gerçek koordinatları korunur. Vita paketinde GPU'ya uygun **32 materyal batch'i**, **67.323 çizim köşesi** vardır.
- **Iron Man Mark VI:** Kullanıcıya ait B11 arşivindeki özgün **970 üçgenlik** Mark VI modeli ve dokusu. Bu standalone G66 derlemesinde **kaynak G10 IM2V iskelet animasyonları henüz entegre edilmemiştir**. Hareket eden nesne özgün statik Mark VI modelidir, orijinal animasyonlu oynanış olarak tanıtılmamalıdır.
- **Çarpışmalar:** G59 özgün **19 collision mesh / 1.910 triangle** kaynak verisinden ayrı CPU sistemi: 3 torso yüksekliğinde gerçek üçgen-duvar kesitleri, 0,39 m karakter yarıçapı, zemin barycentrik yüksekliği, yerel 0,22 m yer değiştirme alt-adımları, hızlı RUSH duvar atlama riskini azaltır. Yine de **orijinal fizik sisteminin birebir kopyası değildir**, özellikle collider kapsamının dışındaki + dış bina üst örtüsü + kesit köşeleri cihaz testinde doğrulanmalıdır. Kaynak collision kapsama alanı dışına geçiş bu ilk betada engellenir.
- **Kamera:** Z-up omuz üstü; nişangâh merkezde kalır, karakter solda görünür, uçuştaki cruise / rush durumunda merkez takibe geçer.
- **Grafik:** VitaGL tek GPU sahne sahibi, dokular gerçek, ışık ve alfa **yaklaşık host port shader**. Özgün 2010 görsel gölge, depth, HDR, sis, film sahnesi ve 74 küçük özel mesh'in görünürlüğü tam çözüldü denemez.
- **Görev/HUD:** Bu bir **serbest dolaşım hareket/çarpışma beta testi**; orijinal Mission000 script ve düşman AI henüz yok. HUD merkez nişangâh + temel durum çizgileri kullanır; tam orijinal HUD değildir.

## PS Vita kontrolleri

| Tuş | İşlev |
|---|---|
| Sol analog | Yürü / uçuşta yatay ilerle |
| Sağ analog | Omuz üstü kamera |
| X (Cross) | Hover / kara modu |
| Üçgen (havada) | Yüksel |
| Daire (havada) | Alçal |
| R (havada) | RUSH hızlan |
| D-Pad Yukarı | Referans C1L1 başlangıç noktasına dön |
| START | Durdur / sürdür |
| SELECT | Tanısal arayüz seçimi (bu build'de görünür açıklama metni henüz yok) |

## VitaShell ile kurulum

1. VPK'yi indir (GitHub Actions artifact ZIP içinden ya da sohbet eki olarak doğrudan).
2. USB/FTP üzerinden \`ux0:/downloads/\` içine kopyala.
3. VitaShell ile VPK dosyasını seç ve kur.
4. LiveArea'dan **Iron Man 2 - B24 G65 Playable Beta** uygulamasını başlat.
5. İlk denemede şu kontrolleri test et: kamera, yürüme, bir bina duvarına yaklaşma, hover, RUSH, zemine inme.
6. **Özellikle binadan geçme / yere düşme / siyah ekran / FPS düşüşü** olursa fotoğraf veya kısa video gönder. Yeni TitleID başka testleri etkilememelidir.

## Kaynak-only, tekrar üretilebilir derleme

Yalnızca kullanıcının yetkili orijinal IPA'sı, B11 gerçek BRES/Mark VI arşivi ve G64 kaynak doğrulama çıktısı kullanılır. G65 G66 runtime sahne/animasyon verileri otomatik olarak CI içinde yeniden çıkarılır; **IPA GitHub source'a commit edilmez**. Başarılı CI sonunda özgün IPA geçici dosyaları temizlenir; VPK test amaçlı orijinal materyal içerir.

- \`g66_rebuild_owner_g65.py\`: G64->G65 kaynak orijinal FVF24 UV/RGBA ve özgün PVR atlası.
- \`g64_native_shader_recovery.py\`: 20/40/60B kaynak BRES sampler kanıtı.
- \`g66_pack_scene.py\`: G65 GLB + orijinal Mark VI + G59 collision -> G66 portable binary.
- \`main.c\`: tek VitaGL GPU, controller, serbest hareket/kamera ve 3D collision.
- \`CMakeLists.txt\`: ayrı uygulama ve gerçek PSVita VPK.

**Açık:** Fizik temaslarının ve GPU render'ın gerçek Vita üzerinde doğrulanması, kaynak animasyon kliplerinin aynı actor skeleton vertex sırasına bağlanması, G65'in kalan 74 özel mesh'inin/alpha-blending'inin iyileştirilmesi, orijinal görev scriptleri.
