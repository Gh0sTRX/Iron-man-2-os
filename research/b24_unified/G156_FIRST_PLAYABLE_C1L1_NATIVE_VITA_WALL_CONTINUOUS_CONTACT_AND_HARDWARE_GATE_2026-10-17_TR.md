# G156 — İlk oynanabilir bölüm: G75/G108 özgün duvar üçgenlerinde tüm düşey yüksekliğin kesintisiz temas kontrolü

**17 Ekim 2026 · feature/b24-unified-gameplay · G155 WIP=1 harita/fizik önceliği · YENİ VPK YOK**

## Neyi düzeltiyor?

Özgün 2010 G66C 1910 collision face kullanan G75 ve G66M orijinal opak dik yüzeyleri sınırlı **aday** olarak değerlendiren G108, oyuncu kapsülü ve duvar teması için yalnızca yükseklik aralığının **alt, orta ve üst 3 kesitinde** üçgen-XY çizgi kesişimi arıyordu. Eğik ve dar dik üçgende gerçek kesişim örneklenen yükseklikler arasında kalabilir. Kaynak C1L1 seviyesindeki 3-boyutlu geometriyi yalnız üç farklı yüksekliğe indirgemek, algoritmik false negative'e izin verir.

G156 yeni statik-inline C11 kaynak algoritması, orijinal triangle XYZ 3 köşesini oyuncunun [foot+.005, foot+height-.005] Z aralığına Sutherland–Hodgman ile keser; kalan gerçek planar ve konveks çokgenin XY izdüşümüne yarıçaplı kapsül ekseninin yakınlığını hesaplar. Bu, G75/G108 eski 3 nokta örneklemesini matematiksel olarak sürekli düşey XY disk temasına çevirir; **orijinal üçgen koordinatlarını değiştirmez**, eski sahneye yeni duvar mesh eklemez, ikinci B14 physics owner oluşturmaz.

## Testte kanıtlanan hata

Tekrarlanabilir source XYZ biçimindeki eğik dik üçgen `(-1,-1,0),(1,-1,4),(1,1,4)` ve oyuncu ayak z0/yükseklik4/radius0.35, XY(-0.55,-0.78): Eski örnek yükseklikleri ~0.005, 2.0, 3.995 noktasında duvara uzaklık >0.35 olduğundan tümü temiz görünür. Oysa gerçek Z ~0.9 düzeyindeki kaynak üçgen yüzeyi oyuncu kapsül eksenini keser. G156 bu teması yakalar. G156 ayrıca dik ve izdüşümü çizgiye inen üçgeni test eder, yanlardan uzak, yükseklik dışında ve görünür boş alandaki noktaları duvar ilan etmez.

Bu testin sentetik koordinatları **orijinal oyuna ait özel bina veya iOS orijinal duvarın aynısı olarak sunulmaz**; gerçek G75/G108 original-format koordinatlarını işleme algoritmasının açığını gösteren bir kontrol örneğidir. G108'in 'orijinal materyal bu görsel dik üçgeni gerçekten katı yapıyor mu' sorusu hâlâ ayrıdır.

## Kaynak ve entegrasyon

- `research/b24_unified/g156_exact_source_sweep/b24_g156_exact_vertical_triangle_contact.h` — tek dosyalık saf C11 matematik/geometri; GPU yok.
- `research/b24_unified/g156_exact_source_sweep/test_g156_continuous_original_wall_height.c` — eski algoritmanın kaçırdığı temas + yeni algoritma pozitif/negatif kontroller.
- `research/b24_unified/g156_exact_source_sweep/g156_patch_exact_wall_contact_into_G153_single_Vita_game_NO_VPK.py` — yalnız G153 B14/G75/G108 birleşik main kaynaklarında gerçek çarpışma kontrolünü yerinde günceller; G134 uzun kare güvenliği ve G83 anim sahibi korunur.
- **[G156 geometri C11 Actions SUCCESS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39045513940)** ve **[G156 bütün tek PS Vita ARM kaynak derleme iş akışı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39045662773)**. İkincinin durumu ACTIONS RUN sonucuna göre okunur; CI tamamlanmadan cihazda çalışıyor sayılmaz.

## İlk oynanabilir resminde gerçekten ne değişti?

Kaynak fizik algoritmasındaki gerçek bir **üç-kesit kaçırma** sınırlandırıldı. Ancak bu, G104 Vita'da bildirilen tüm binalardan geçme sorununu çözmüş olduğunu kanıtlamaz. Oyun özgün render geometry'si 22,441 üçgenken kaynak collision verisi 1910 üçgendir; G108 yüzey adaylarının solidity semantiği tamamen orijinalle eşleştirilmedi. G106 kaynak gökyüzü/alpha düzeltilmiş olsa da cihaz üzerinde henüz doğrulanmadı. Gerçek cihaz FPS ve mission QTE PC6 hâlâ ayrı bloklardır.

**Bundan sonraki sıradaki test:** G156 gerçek C1L1 birleşik kaynak ARM ELF + mevcut G134/G108 kaynak regresyonları; ardından yalnız uygun zamanda bir PS Vita konsol testi ile duvar/corner/roof, Stage2/RUSH ve sky/alpha görüntü gözlemi. Yeni armor, mission2, co-op veya audio/Wait ayrıntı kazısına geri dönme; G155 WIP=1 kararını koru.
