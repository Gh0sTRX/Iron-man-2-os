# G104 — Kullanıcının onayladığı gerçek PS Vita test VPK'sı / yükleme ve test kılavuzu

**Oluşturma:** 17 Ekim 2026 Türkiye saati (GitHub runner 16 Ekim UTC). Dal: `feature/b24-unified-gameplay`. Bu VPK, kullanıcının "sıradakini yap ve VPK'yı derle, denemek istiyorum" açık onayıyla **bilerek** çıkarılmıştır. Daha önceki G83 11/11 katı özgün oyun tamamlama/yayın kontrolü aynen KORUNUR; G104 cihaz üzerindeki movement/dummy/harita performansını gerçek görüp eksikleri saptama amaçlı **kaynak entegrasyonu tanılama beta**sıdır, orijinal iOS'un tam portu değildir.

## Gerçek indirilebilir VPK

- **Github Actions başarılı job:** [38974292901](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38974292901)
- **Gerçek indirilebilir artifact (VPK + QA JSON):** [12077339955 — G104 gerçek PS Vita test VPK](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38974292901/artifacts/12077339955)
- **VPK dosya adı:** `IronMan2_B24_G104_G95_Stark_Expo_MarkV_248_Original_Movement_Static_Dummy_TEST.vpk`
- **Gerçek 16 baytlık title ID yerine SFO TITLE_ID:** `IM2G10401` (mevcut `IM2G70001`, `IM2G00034` ve diğer eski testleri ezmez)
- **VPK boyutu:** **94.566.476 bytes** (90.1856 MiB veya 94.57 MB)
- **SHA-256:** `d62db58434e527a532232930aa52017f491b24018efc9a60d17defb8e8304a06`
- **QA:** `IronMan2_B24_G104_G95_Stark_Expo_MarkV_248_Original_Movement_Static_Dummy_TEST.qa.json`.

## Ne var?

GitHub Actions kaynakları tekrar indirerek G75→G84→G85→G87→G92/G93/G94/G95 sırasıyla tek fizik/single GPU main kurdu; **VitaSDK ARM gerçek ELF, vita signed eboot.bin, orijinal param.sfo ve VPK** oluşturma adımlarının tamamı başarılı. Gerçek oyun CMake ana build'inin sonucu paketlendi; ayrı HTML maket veya eski G68 VPK'ya yeni isim verilmiş dosya DEĞİLDİR.

- Orijinal 2010 C1L1 Stark Expo G68 şehir GPU sahnesi ve 31 orijinal G66 doku atlası;
- özgün kullanıcı iOS IPA kaynak 1.910 collision yüzey, G75 B14 yürüme/hover/flight/rush/floor-step duvar-yer uyumu (host regresyon OK);
- **Mark V suitcase 629 vertex weighted mesh + 248 gerçek 2010 animasyonunun tüm IM2V dosyaları** VPK'da mevcut. G85 kaynak single-main aktivasyonuna rağmen her klibin kendi input state'i *kanıtlanmadı*.
- G83 yürüyüş/uçuş/aim öncelikli source anim selector, G87 kaynak geçiş olayı kontrolleri, G95 CLARA 4 Sun noktası **tanısal lighting**;
- 1 özgün harita zeminiyle yerleştirilen **hareketsiz, ölümsüz, çarpılınca geçici flash gösteren debug dummy**. Dummy kaynak iOS düşmanına dönüştürülmedi, ölmüyor veya sağlık kaybetmiyor;
- Zorunlu G88 combat güvenlik kapısı doğrulanmamış hit frame/hasar/attacker permission olduğunda **gerçek hasarı engelliyor**; yanlış HP davranışı üretmemek için bilerek.

## PS Vita'da nasıl kurup test edilmeli?

1. GitHub bağlantısından artifact ZIP indir; ZIP'in içindeki **.vpk** dosyasını çıkar. **ZIP dosyasının tamamını değil VPK'yı yükle**.
2. VitaShell'de USB veya FTP bağlantısı ile `.vpk` dosyasını Vita'ya örneğin `ux0:/data/` klasörüne taşı; yeterli geçici boş alan bırak.
3. VitaShell'de VPK üzerine gelip **X** tuşuyla kur. Bubble için yeni `IM2G10401` görünmeli. Mevcut B24 sürümünü silmen gerekmemeli.
4. Açılışta şehir haritası, Mark V/suitcase suit seçim olanağı, yakın/uzak kamera, yürüme/uçuş ve tek sabit dummy davranışlarını test et. Hareket kontrolleri mevcut B24 üzerinden; özgün iOS dokunmatik giriş parity'si henüz ispatlanmadı. Yeni VPK'nın GAMEPAD tuşları için kaynak eylem bağları önceki B24 deneme betasıyla aynı; ek bir menü ya da ikinci input handler yaratılmadı.
5. Çökme/siyah ekran/boş map/haritanın içinden düşme/yanlış karakter dönüşü/15 FPS altı durumları için Vita ekran görüntüsü veya video ve **hangi tuş-hangi durum** bilgisini paylaş. Böylece gerçek donanım hatasını testlerle yeniden üretebiliriz.

**Kurulumdan sonra VitaSHell'in kendi Vita günlüklerine otomatik erişimimiz yok; "cihazda çalıştı" iddiasında bulunma.** Kullanıcı sonucu paylaşmadan gerçek PS Vita startup/performance/screenshot kanıtı yok.

## Bir sonraki özgün source Damage araştırması G105

G105, G101'in **26 gerçek Attack sınıfı × 54 adet** doğrulanmış kaynak bytes property slotunu native class110 `Object` içindeki **23 yerel property** `Damage` dahil tip/uzunluk kalıbıyla otomatik karşılaştırdı. **0 uyumlu kesintisiz offset** çıktı ([run 38974681819](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38974681819)); bu, kaynak class110 alanlarının class108 `Attack` serializer'ına basit bir blok olarak miras geçmediğinin kanıtı, veya descriptor type-map/multiple class layout tahminimizin doğru olmadığını gösterir; **26 gerçek Damage sayısı bulunduğunu iddia etmeyiz**. Native `EntityData::GetParamValue(char const*,int*)` 0xD7548 ve bool 0xD76BC gerçek ARM source girişleri de G105 araştırması için G97 kaynak kaydına eklendi; native getter'ların EntityData inheritance walker'ı hâlâ çözülecek.

## CI ve doğrulama ayrımı

**Doğrulanan:** gerçek GitHub Actions Vita SDK ARM cross-compile + ELF link + SELF/VPK generation; zip testzip, im2v IM2V 20Hz 629 vertex headers, 248 MarkV, 31 G68 atlases, 1.910 G68 collision, eboot SFO unique TITLE_ID ve VPK SHA. G88/G83/G92/G93/G94/G95 kaynak host testleri.

**Henüz doğrulanmayan:** Vita gerçek donanımda açılış, tüm animasyon transition ve frame rate, orijinal iOS touchHLE eşdeğerliği; gerçek hasar/silah sayıları, melee gerçek hit-active kareleri, özgün `Actor::CanAttack` tiplerinin tüm enstrümantasyonu, NPC AI/death/wave mission ve birebir shader.

**ÖNEMLİ:** Yeni VPK bu betanın deneysel gözlemsel testidir. Kullanıcının ileride tam 2010 source moveset/damage çözülmüş ikinci final VPK isteği ayrı kabul koşuludur. G83 release `READINESS_STATUS.json` 1/11 kanıt koşulunun sayısı G104 beta için hiçbir şekilde sahte yükseltilmez.
