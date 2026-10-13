# B24 Unified — canlı entegrasyon kaydı

## Aktif kaynak ağacı
- Çıkış tabanı: gerçek Vita'da kullanıcı tarafından test edilmiş `IronMan2_Arena_B17`; eski B15/B17 kaynakları değiştirilmedi.
- Yeni dal: `feature/b24-unified-gameplay`. Paket hedefi: `IronMan2_Unified_B24.vpk`, TITLE_ID `IM2B00024`.
- `assemble_b24_modules.py`: B19, B21, B22 HUD, B23 missile lock, B22.2 3D root math, B22.3 camera, B22.4–6 FX, B18 analog and indexed floor source; **tek** CMake im2_beta hedefi.
- `b24_unified.[ch]`: bir dünya pozisyonu + uçuş aşaması, orijinal B17 Z-up'tan yeni host Y-up'a koordinat adaptörü; aynı tic içinde B21, B23, B22 UI, kamera, speed FX, thruster gate ve B19 host state. Ayrı bir ikinci actor physics güncellemesi yapmaz.
- `apply_b24.py`: gerçek B17 main/World C kaynaklarına fail-fast değişiklik; analog girerken .96 çıkarken .88; WM iyi hover modelini aynen tut; repulsor shots%3 rastgele anim varyantını kaldır; R fire/L missile lock/Square melee/Start pause/D-pad mapping; sahne render'dan sonra B22 HUD ve RUSH ekran kenarı çizgilerini eski CPU fallback framebuffer üzerine çizer.
- `test_b24_unified.c`: B19/B21/B22/B23/B22.2/B22.3/B22.4–6 tek host test; 20,000 test girişi, füze dışındayken kilitlenmeme, Stage 2 sırt partikülleri daima kapalı.
- `unified-b24.yml`: önce tüm özgün asset/anim ve eski regresyon testlerini çalıştırır, sonra B24 tüm C kaynaklarını tek ASan/UBSan host executable olarak sınar; yalnız bütün testler geçerse VitaSDK aynı VPK'yı oluşturur.

## Henüz gerçekten çözümlenmeyenler
- **Orijinal komple GPU framebuffer**: indexli GPU floor mesh ve vitaGL prototipleri mevcut ama `B24` henüz gerçek sceGxm/vitaGL owned context geçişini yapmıyor, B17 CPU yazılım renderer fallback ile çalışır. **Bu gelecek asıl kritik mühendislik işi.** Sırf GPU denemesi için ayrı düşük-içerikli VPK yayınlamayacağız.
- **War Machine original animasyon problemleri**: kullanıcının sevdiği WM hover korunur; normal yürüme, uçuşta bacak kalkması, inişte kol yükselmesi, orijinal melee/repulsor geçişlerinin tamamı henüz animasyon rig/IM2V düzeyinde düzeltilmedi. Shots%3 mekanik hatasının kaldırılması ilk safha.
- **Thruster 6 gerçek socket**: B24 modül mantığı derlenip çalıştırılıyor; altı soketi gerçek orijinal BDAE/anim gövdesine eşleme HENÜZ yapılmadı. Sırttaki iki gerçek nozül source'a uygun doğrulanmadan `valid=1` kullanılmıyor; Stage2 back kesin kapalı.
- **Gerçek melee kamerası**: B22.6 clip trigger + dünya hedef 3D pozisyonu olmadan doğru bir yakın dövüşe girildiğini varsaymıyor. Gerçek combo/hit ve hedef modeli ayrıca gerekir.
- **Uçuş/camera**: B24 modülü B17 tek world authority ile kamera mesafesini ve yönsel body pose hedefini hesaplar; tam root roll/3D pitch fiziksel motoru ve gerçek GPU kamera matrisleri henüz Vita renderer'a uygulanmadı.
- **Gerçek düşmanlar/görevler**: B19 çekirdek bağlandı, ancak gerçek enemy visual/AI adapter olmayınca gizli düşman savaşı başlatılmıyor. B17 sphere eğitim ortamı bunun yerine kalıyor.
- **B22 HUD**: mevcut CPU fallback ekranına çizilen yeni tasarım; orijinal Gameloft HUD texture kesin çözüm değildir, B17 legacy overlay ile görsel çakışmalar Vita testinde incelenecek.
- **IPA**: Drive dosyasının `275580565` bayt metadata'sı doğrulandı, tek-istek indirme bağlantısı 256 MiB sınırında 413 veriyor.

## CI sonuç geçmişi
- İlk B24 Actions #1 (`38436136118`), host B7/B8/B9/B10/B13/B14 PASSED, B15 yeni .96 analog eşiği karşısında eski .80->Stage2 beklentisi yüzünden RED. Kod derleme hatası veya Vita GPU testi değil. B24 `apply_b24.py` regresyonu .80 Stage1, .99 Stage2 olarak güncellendi; kullanıcı tercihi korundu, test atlanmadı.
- B24 resmi release değildir; Actions VPK artifact üretse bile **CI yeşil**, animasyon/GPU Vita performansı ve fiziksel doğruluk anlamına gelmez. B24 bütünleşme ilerledikçe tek kaynak dalında gelişecek.

## Net taahhüt
B17'ye dönüp sıfırdan başlama yok; tek B24 geliştirilmeye devam eder. B22.6 ve öncesi modüller silinmez, sadece bağımsız host durumundan tek gameplay runtime durumuna bağlanır. GPU entegrasyonu bu çalışmanın paralel **render** ayağıdır, ilerleme için önce bitirilmesi gereken ayrı oyun demosu değildir.

- B24 Actions #2 (`38436614662`) native B7/B8/B9/B10/B13/B14/B15 PASS; B16 legacy `.85` Stage2 assertion failed because this was written for old `.78/.67` thresholds. Updated B16 native test to `.99` enter, `.91` hold, `.82` exit with `.96/.88` rules; no test bypass. Next combined build checks the full host loop and VitaSDK.
