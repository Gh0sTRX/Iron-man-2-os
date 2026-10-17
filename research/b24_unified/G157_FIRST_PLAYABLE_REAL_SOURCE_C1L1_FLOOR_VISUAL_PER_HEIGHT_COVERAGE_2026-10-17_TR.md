# G157 — İlk bölüm haritasının gerçek zemin ve görsel katman kapsamı

**17 Ekim 2026, özel `Gh0sTRX/Iron-man-2-os`, dal `feature/b24-unified-gameplay`, YENİ VPK YOK.**

## Bu işi niçin yaptık?

G156 native source duvar temasını üç kesitten bütün dikey kapsül yüksekliğine düzeltti. Fakat G104 fiziksel Vita kullanıcısının binalardan geçebilmesi yalnızca duvar yaklaşımıyla ilgili olmayabilir; gerçek G66C native collision source ile ekranda görünen G66M render kaynak yüzeylerini aynı koordinat ve **aynı yükseklikte** eşleştirmeden duvar/zemin arızalarını yanlış sınıflandırırız. G155 WIP=1: ilk bölüm dünya/fizik düzeltmesi. Bu yüzden yeni game subsystem, görev, zırh veya VPK yaratılmadı.

## Doğrudan orijinal iOS kaynaklarıyla tekrar edildi

Önceden gerçek Vita'da kullanıcı tarafından çalıştırılan G104 gerçek kaynak VPK artifact run `38974292901`, **yalnız salt-okunur** CI runner'da açıldı. `assets/G66_city.g66m`: orijinal 2010 sahnesinde **22.441** drawn triangle/32 batch/31 atlas. `assets/G66_original_collision.g66c`: **1.910** özgün native collision triangle; G75'in kaynak eğim sınıflandırmasına göre **1.690 steep-wall** ve **220 nonwall**. 220 nonwall'ın hepsinin orijinal oyun senaryosunda güvenli yürünebilir zemin olduğu **kanıtlanmış değildir**. `G66M` içinde orijinal opaque/steep olmayan **8.768** görsel triangle (alpha veya textureless dışarıda). Kaynak tekstür/transparency sınıfları oyunun G71/G106 denemelerine dayanır; tüm doğrudan iOS solidity bayrakları henüz kanıtlanmadı.

**[G157 son GitHub Actions PASS #39047519031](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39047519031)**. [G157 doğrulanmış SVG/CSV/JSON artefaktı](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39047519031/artifacts/12106615988).

### 6.561 örnek, XY bölgesi −160..+160, adım 4 kaynak birim

- **BÜTÜN yükseklikler XY'e izdüşürüldüğünde:** 6.560 XY hem native nonwall hem opaque visual nonwall, 1 native-only. Bu **OYUN HARİTASI %99,98 TAMAM** demek DEĞİL: çatılarla yer katları üst üste bindiği için yanlış bir çıkarım olur.
- **Z 0.0725 ±0.5:** 3.669 iki kaynak da var, **2.892 native collision var / aynı katmanda görünür opaque nonwall yok**, 0 visual-only. Buradaki native-only, orijinal fizik proxy'si veya farklı material/shader/height olabilir. Kaynak native alt katman bu 320×320 bölgenin tüm örnek XY'lerini kapsıyor; bu kapsam orijinal playable zone kanıtı değil.
- **Z 2.82955 ±0.5:** **203** iki kaynak var, **628 görsel var/native nonwall yok**, **5.730** iki kaynakta da bu yükseklikte zemin yok. 628 için otomatik collider yazmak **YANLIŞ**: bazıları dekor, çatı/üst geçit, farklı z veya kaynakta çarpışmasız yüzey olabilir.
- **Z 6.67306 ±0.5:** 40 görsel-only, 6.521 ikisi de yok. Bu katmanda 4 birimlik raster çok seyrek kalıyor: G75'in kaynak koordinatı **(−1.319,−6.747)** gerçekte **0.0725, 2.8296, 6.6731** üç ayrı orijinal nonwall layer barındırıyor. Dolayısıyla rasterda native hit sayısının sıfır çıkması, **kaynakta çatı yok** demek DEĞİL.
- **Z 15 ve Z 35:** Yalnız tanı amaçlı yukarı kotlar, oyuncu spawn veya izinli uçuş yüksekliği iddia edilmedi. Kaynak rapor ve ayrı SVG'lerde sonuç bulunur.

### Görsellerin doğru yorumu

Her SVG oyun screenshot'ı değil: orijinal üçgenleri belirli Z düzleminde XY barycentrik test eden **salt-okunur analitik üstten görünüm**. Renk ayrımı: hem native/visible, yalnız native, yalnız visible, hiçbiri. Her SVG ayrı yüksekliği gösterir; bütün Z üst üste `G157_source_floor_coverages_only.svg` yalnız yanıltıcı kontrol karşılaştırmasıdır. Üçüncü taraf telifli atlas/pixel/model kaynakları çıktı artifact içinde YOK; yalnız nicel metadata ve SVG. Yeni VPK YOK, fiziksel Vita cihaz denemesi YOK.

## Ürün bakımından sonuç ve sıradaki iş

**Alt seviyedeki 0.0725 kaynak geometri kapsaması, merkez 320×320 XYZ bölgesinde G75 native destek katmanının eksik olmadığına işaret ediyor.** Bu yalnız raster XY/Z-slice bazında güçlü bir gözlem, özgün görev spawn/robotun ayağının ilgili yerde bulunduğunun kanıtı değil. G104 bina penetrasyonu için zemin yok diye bütün görsel yerleri katı yapmayacağız. Asıl açık: dik katı yüzeylerin kaynak/özel Deco/CollisionEntity aidiyeti, görünür bina ile native çarpışma bitişmesi, gerçek oyuncu koordinatı ve kamera/geri bildirim. G156 bütün duvar yüksekliği matematiği doğru olsa da G108'in 7.487 opak görsel adayının **gerçekte solid olup olmadığı** açık.

Sıradaki hedef, **kaynak geometry ve fizik arasındaki konum-bağımlı bina penatrasyonunu** tek G155 workstream'inde tekrar üretmek ve öncelikli elle Vita üzerinde ölçülebilir testi belirlemek. G106 sky/alpha sorunları da ilk aynı donanım test paketiyle ölçülecek; yeni VPK yalnız kullanıcı tarafından yetkilendirilen tek entegrasyon QA aşamasında hazırlanacak. Görev QTE/Wait/audio konuları şimdilik sırada bekliyor.
