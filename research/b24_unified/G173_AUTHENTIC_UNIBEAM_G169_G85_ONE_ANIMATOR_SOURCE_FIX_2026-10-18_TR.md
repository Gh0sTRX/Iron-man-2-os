# G173 — Özgün 2010 Uni-Beam animasyonu G169 → G8/G85 kaynak yönlendirme hatası

**Tarih:** 18 Ekim 2026. Dal: `feature/b24-unified-gameplay`. **VPK üretme.**

## Gerçek hata

Önceden entegre G169, başarılı B16 Unibeam port olayı için gerçek 2010 `Beam1 → Beam2 → Beam3` kaynak IM2V klibini G83 üzerinden seçiyordu. Ancak G84/G8 animasyon sahibi şu önceliğe sahipti:

`if(g84_source_clip&&!melee&&!a->repulsor_pending)desired=g84_source_clip;`

Yani bekleyen port repulsor pozu G169'un verdiği özgün Uni-Beam hareketini engelleyebilirdi. İkinci ve daha kesin hata: G169 Mark V için `suitcase_ironman_aim_...beamN` döndürürken G85 Mark V isim dönüştürücüsü yalnız `ironman_` ile başlayan stem'leri kabul ederek `suitcase_` önekini *kendisi* ekliyordu. G169'un zaten eksiksiz Mark V dosyası, G85 tarafından `return 0` ile reddedilebilirdi.

## G173 kod düzeltmesi (tek animasyon motoru)

- `g173_unibeam_single_animator_priority/b24_g173_authored_beam_priority.h` 2010 G169'da mevcut **tam 12** gerçek source stem'i tanır: Mark V/VI × ground/float × Beam1/2/3. Diğer animasyon, War Machine, combo veya bilinmeyen beam adı bu geçişten yararlanamaz.
- `g173_unibeam_single_animator_priority/g173_fix_real_G169_G85_beam_source_priority_NO_VPK.py` yalnız mevcut G8/G85 tek animasyon sahibini düzeltir. Onaylı G169 Beam aktör kaynağı bir poz seçerse, bu poz bekleyen eski port repulsor önceliğinin üzerine geçer; eski repulsor pose pending temizlenir. **Melee daha üst önceliklidir.** Mark V özgün `suitcase_ironman_...` stream ismini ikinci kez dönüştürmez. Diğer bütün eski source `ironman_` → `suitcase_` eşlemesi değişmez.
- `test_g173_exact_g169_beam_priority_gate.c`: 12 tam beam ID, yanlış zırh/Mod/WM/attack reddi, melee önceliği.
- `test_g173_REAL_2010_IM2V_G169_G8_G85_full_host_owner.c`: Geçici **gerçek orijinal 2010** `work/animations` sahibi üzerinde native G169 kaynak phase seçimi → tek G8/G85 pose stream açma/regresyonu (Mark V 629, VI 802), önceki pending repulsor'un seçimi ezmemesi, melee korunması. Yalnız host; fiziksel Vita değildir.
- G171 ortak CI pipeline'a G173 kaynak uygulaması, hem C host testi hem `-DB24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY=ON` ile gerçek Vita ARM `im2_beta` **ELF-only** derlemesi eklendi. **Yeni VPK veya telifli IPA dosyası depo içine eklenmez.**

## Durumun dürüst sınırları

Doğrudan B16 accepted Unibeam olayı şu an *Vita portunun* silah olayıdır; native 2010 Gameloft gesture/WeaponDB AttackType to animation binding kanıtı değil. G169 source clip phase süreleri özgün IM2V metadata'sından gelir; kaynak chest Dummy/soket VFX, projectile, target hit frame, hasar sayısı, şok dalgası ve oyun içi cooldown eşlemesi **henüz çözülmemiştir**. G173 bunları eklemez.

G172'nin 10 War Machine Aim_M Ground kaynak animasyonu G83 seçiciye eklendi; mevcut G84 main hala `AIM_M_UNCLASSIFIED` olayını doğrulanmış 2010 input'a bağlamıyor. WM M harfi missile anlamında *kanıt değil*. Bir sonraki kaynak işi gerçek Native `MainCharacter::ThrowMissile`, `WeaponDB::GetAttackEntityByIndex` ve `SetAttackTypeEnabled` native arg/anim controller event eşleşmesini incelemek; yanlış roket animasyonu ekleme.

G171 orijinal G66C 1910 collider korunur; heykel görünürlükten kanıtsız solid çıkarımı geri alınmıştır. G168 Mark V kaynak ayak hizası düzeltilmiştir ama world parent ölçeği ve gerçek cihaz doğrulanmamıştır. Skybox, ışık/gölge, QTE/cutscene, native melee hit windows, gerçek düşman AI/ses ve oynanabilir tam görev **açık** kalır.

**CI sonuçları ayrı değerlendirilmelidir.** Önceki ilk G173 workflow hata `G85 live sole G8 clip priority exact owner drift` (Python metin eşleşmesi 3 boşluk/4 boşluk), test başlamadan geri döndü; `3f5d871b` commit'inde gerçek G85 patch çıktısından literal anchor düzeltildi. İkinci koşunun başarı/başarısızlık sonucu GitHub Actions üzerinde doğrulanmadan PASS ilan edilmez.

## 18 Ekim CI doğrulaması

- G173 gerçek özgün `.im2v` dosyalarıyla dört MarkV/VI × ground/hover üç aşamalı G169→G8/G85 bütünleşik host oynatıcı testinde **PASS**.
- G171 asli collider teması, G172 on gerçek WM M-ground klibi seçicisi ve G173 host animasyon öncelik testi **PASS**.
- Aynı tek oyunun `-DB24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY=ON` VitaSDK ARM **`im2_beta` ELF-only** derlemesi **PASS**; VPK üretilmedi. Tek koşu: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39075029040 .
- Bu PC kaynak/binary derleme kanıtıdır; yeni bir PS Vita kurulum/görüntü testinin sonucu değildir. Doğrulanmayan orijinal silah ve görev semantiği önceki bölümdeki gibi açık kalır.
