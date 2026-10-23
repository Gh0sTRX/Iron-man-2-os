# Mevcut durum cihaz testi — 23 Ekim 2026

Kullanıcının “şimdiye kadar çözdüğümüz her şeyi test edelim” yanıtıyla tek bir
tanılama VPK'sı yetkilendirildi. Yedi tam-port kabul kapısı açık kalır.
`IM2DG0001` / `Iron Man 2 - Device Test` / `00.01`, eski uygulamadan ayrı kurulur.

Önce resmi G171 kaynak üretimini ve aynı kaynak üzerindeki zorunlu testleri/ARM
ELF derlemesini tamamla. Ardından `python3 tools/device_test/build.py` çalıştır.
Bu yardımcı mevcut doğrulanmış ELF'i paketler; kaynak üretimini/derlemeyi yapmaz.
Eski CMake VPK hedefi yerine tüm güncel models/animations/maps/assets dizinlerini
ekler. ZIP CRC, tam dosya kümesi, dosya hash'leri, SELF ve SFO kimliğini denetler.
Çıktı `work/device-test/`; `manifest.json` kaynak/ELF/VPK hash'lerini kaydeder.

## Vita üzerinde test

1. Eski uygulamayı silme. Yeni VPK'yı VitaShell ile kur ve **Device Test** başlığını aç.
2. İlk açılışta şehir, zırh, gökyüzü, doku saydamlığı ve kamera görüntüsünü kaydet.
3. Sol çubuğu ileri en az 15 saniye tut; sonra sağ/sol/geri hareketi dene.
   Dünya üzerinde ilerleme mi, yerinde animasyon mu olduğunu belirt.
4. Yerde START ile duraklat, Circle ile dön: kendiliğinden kalkış olmamalı.
   Circle ile kalk; havada START → Circle: kendiliğinden iniş olmamalı.
   Duraklatma seçeneklerinden Circle ile geri dönüşü de dene.
5. Havada yön tuşları yukarı/aşağı, Triangle basılı hızlanma ve sağ çubuk kamerayı dene.
6. SELECT ile beş zırhı, özellikle War Machine yürüme/uçuş animasyonlarını karşılaştır.
   R ateş, kare yakın dövüş, yön tuşları sağ/sol silah seçimini dene; görülen sonucu bildir.
7. Testten sonra VitaShell ile `ux0:data/ironman2_g279_walk.csv` dosyasını kopyala.
   Her açılış önceki dosyayı silerek yeniden yazar; tekrar açmadan önce koru.
   Dosya ilk BOOT karelerini ve 120 karelik yürüyüş pencerelerini içerir.

Circle duraklatma düzeltmesi, XYZ kök teşhisi, G279/G296 kayıt/floor sorgusu ve
G298/G299 deneysel doku/ışık seçenekleri bu bütünleşik sürümdedir. Işık özgün
motor gölgelendirmesi olarak kanıtlanmış değildir. Özgün dünya başlangıcı,
tarihî yerinde yürüme, tam görev/QTE/NPC/savaş/ses ve cihaz performansı hâlâ
kabul bekler. İki özgün PCM ses girdisi mevcut olmadığı için görev sesi eksiktir.
Paketin derlenmesi cihazda açıldığını veya bunların düzeldiğini kanıtlamaz.
