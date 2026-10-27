# Dünya yüksekliği, kalkış ve iniş düzeltmesi — 28 Ekim 2026

Gerçek kaynak yol yüzeyinde `Z=2.693700` iken mevcut Circle olayı uçuş hedefini
mutlak `Z=0.8` yapıyordu. Tek B14 hareket adımı `2.577033` öneriyor, G75 özgün
yüzeyi koruyarak karakteri `2.693700` üzerinde tutuyordu. Dolayısıyla kalkış
girdisi kabul edilse bile karakter bu zeminden havalanamıyordu.

İnişte ayrı bir gerçek hata yeniden üretildi: 1/120 saniyelik test adımlarıyla
aynı yüzeyin `0.450000` üzerinde takılı kalıyordu. Yakın zemin araması aşağıda
0.50 birime kadar yüzey buluyor, mevcut adım koruması yalnız 0.35 birimlik
düşüşü kabul ediyordu. Aradaki boşlukta yüzey “yakın” diye düşüş de duruyordu.

## Değişen davranış

- G75 açıkken B14, kabul edilmiş kaynak zemin yüksekliğini ve kalkış anındaki
  ayak yüksekliğini saklar. Uçuş hedefi ve sınırları bu kalkış düzlemine bağlıdır.
- Circle ve mevcut klavye C yolu aynı B14 uçuş niyeti fonksiyonunu kullanır.
  Duraklatma koruması, mevcut iniş animasyonu ve zaman damgası korunur.
- G75 çözümünden **sonra**, mevcut native-first/isteğe bağlı kaynak-yol
  otoritesiyle ayak ve yüzeyin gerçekten çakışıp çakışmadığı sorgulanır.
  Yakında bir yüzey bulunması temas sayılmaz. Uçuş sırasında ek arama yapılmaz.
- Temas henüz yoksa iniş, mevcut sınırlı düşüş hızıyla devam eder. G75 yakın
  yüzey/adım aralığında da gerçek zemine kadar inmeye izin verir; yüzeyi aşmaz.
- G75 kapalı bağımsız B14 deneme alanının açık `Z=0` davranışı korunur.
- Tek B14 integratörü, tek G75 çarpışma çözümü ve tek animasyon/GPU sahibi
  korunur. Özgün 1.910 çarpışma üçgeni, 1.690 wall işareti, yüz 715, zırh/şehir
  ölçeği ve özgün kaynak varlıklar değiştirilmez.

`.8`, `.35`, `36`, `7` ve hareket hızları mevcut PORT prototipi değerleridir;
özgün Gameloft fizik/sürat/uçuş tavanı keşfi olarak sunulmaz. Yol geometrisi
özgündür; G159'un bu geometriye yüklediği destek politikası deneysel kalır.
Orijinal hikâye başlangıcı hâlâ bilinmiyor; karakter bir başka Z'ye taşınmadı.

## Tekrarlama ve kanıt

Resmi G171 akışı güncel kaynağı ürettikten ve G299 installer tamamlandıktan
sonra `python3 -B research/b24_unified/world_height/patch_world_height.py`
çalışır. Patcher beş gerçek runtime dosyasını tam kaynak eşleşmeleriyle
dönüştürür; kaynak kayması veya ikinci uygulama halinde yazmadan reddeder.

```bash
python3 -B research/b24_unified/world_height/test_world_height.py
python3 -B research/b24_unified/world_height/test_world_height.py --sanitize
python3 -B research/b24_unified/test_b24_pause_flight_event.py
```

Test, gerçek üretilmiş SDL Circle bloğunu çıkarır; gerçek B14, G75,
G108/G159/G160/G171 kodunu gerçek G66C/G66M girdileriyle bağlar. Her çalışmada:

- Özgün veri üzerinde 12 senaryo grubu: kalkış, yere iniş, yerli ve kaynak-yol
  katmanları, 1/120–0.09 saniyelik beş farklı test zaman adımı, duraklatmada
  değişmezlik, kamera takibi, seyir/hızlanma ve daha alçak yüzeye iniş.
- 6 ek grup, yalnız sentetik referans-düzlemi regresyonudur: özgün native
  üçgenlerin RAM'de -40/+40/+200 Z ötelenmiş kopyaları. Bunlar özgün başlangıç
  veya özgün harita dönüşümü kanıtı değildir.
- Toplam 130 tekrarlı kalkış/hover/iniş döngüsü. Strict C11 ve ASan/UBSan
  çalışmaları geçti; bağımsız G75'siz B14 uyumluluk testi de geçti.

Önceki gerçek kaynak yedeğinde aynı kalkış ve iniş regresyonları ayrı ayrı
başarısız oldu; bu negatif kontroller bulut çalışma alanında kaydedildi.
Yeni patcher'ın temiz yedekten ürettiği beş dosya mevcut runtime ile byte
düzeyinde karşılaştırıldı. Eski test VPK'sı yeniden üretilmedi.

G171'in yerelde çalıştırılabilen **48 shell doğrulama adımı geçti**. İki girdi
kontrolü yeniden çalıştırılamadı: `/tmp` temizlendiği için tarihî G9 kaynak
paketi ve G251 16-spawn başlığı yok. Bunlar geçmiş çalışmada doğrulanmıştı;
bu çalışmada geçmiş başarı yeni başarı sayılmaz. Mevcut 669 runtime varlığının
tamamı önceki doğrulanmış snapshot hash'leriyle tekrar eşleşti. Eski kaynak
paketinden gelen araç dokusunun SHA-256'sı ayrıca önceki kayıtla karşılaştırıldı.
Kaynak yeniden üretimi mevcut geliştirme ağacının üzerine yürütülmedi.

G171 CI'ya patcher ve strict/sanitizer entegrasyon adımı eklendi. GitHub API
bu makinede CONNECT 403 döndürdüğü için yeni uzak CI sonucu henüz doğrulanmış
sayılmaz. Yerel tam VitaSDK ARM ELF derlemesi ayrıca çalıştırılır; sonuç
`CODEX_HANDOFF_TR.md` içinde kaydedilir.

Yerel ayrıntılar `/workspace/im2-dev-checks/world-height/` altında baseline,
strict/sanitizer günlükleri ve `regression-results.json` içindedir. Bu host
kanıtıdır; fiziksel Vita yürüyüşü, özgün story spawn veya FPS kanıtı değildir.
Yedi tam-port kabul kapısı açık kalır; bu değişiklik yeni VPK üretmez.
