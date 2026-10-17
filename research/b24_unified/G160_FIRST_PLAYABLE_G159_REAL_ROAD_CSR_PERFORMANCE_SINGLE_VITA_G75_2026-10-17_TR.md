# G160 — Gerçek C1L1 yol zemini fizik taramasını azaltan kaynaktan doğrulanmış CSR indeksi

**17 Ekim 2026 · `feature/b24-unified-gameplay` · tek G155 WIP: ilk oynanabilir C1L1 harita/fizik · YENİ VPK ÜRETİLMEDİ**

## Somut runtime kaynak değişikliği

G159 özgün iOS `c1l1_road.tga` atlas12'ye piksel düzeyinde eşleşen 753 G66M kaynak üçgenini G75 native-first tek B14 zemine eklemişti; ancak her `near`/`crossed` kontrolü her seferinde 753 triangle tarıyordu. G75 ana B14 hareketinde yüksek sayıda substep olabildiği için Vita CPU bütçesini gereksiz harcama potansiyeli vardı. G160, aynen bu iki fonksiyonun aday seçimini değiştiriyor; gerçek source polygon XYZ, yükseklik, parça/material, game physics owner, asli 1910 G66C, G108/G156/G134 collider ve G137 mission akışı değişmiyor.

`b24_g160_original_road_spatial.[ch]`: tek seferlik hazırlanan **16 orijinal dünya birimi** XY hücreli sıralı CSR indeksi; her hücre özgün kaynaktaki ilgili triangle ID'lerine gider. Triangles yalnız geometrik AABB'leriyle ve G159 `±0.0001` toleransından büyük payla indekslenir. Orijinal `G159` sorgularında **sadece bu hücre** taranır; G159 kaynak yüzeyindeki barycentric ve native Z kontrolleri aynı kalır. İndeks kurulamazsa **eski full-scan ile birebir önceki hesaplamaya döner**. Oyun karesi başına heap ayırma yok, ikinci movement tick veya yeni collider yaratma yok.

`g160_integrate_CSR_into_G159_one_real_Vita_game_NO_VPK.py`: yalnız G159 + G156 sonra, geçici `work/` içinde G159 `near` ve `crossed` iki çağrısına bağlar. `B24_G160_ROAD_SPATIAL_INDEX=ON` açık **opt-in** CMake; G159 `ROAD_FLOOR_CANDIDATE=ON` zorunlu. G159 baseline kaynak git içerisinde korunur, G160 patch'i kaynağı ayrı konumda test ederek yapılır.

## Gerçek orijinal G66M üzerindeki kontrol

Gerçek 2010 owner kaynak `assets/G66_city.g66m` (G68) okundu. **753 gerçek yol triangle**; uzamsal indeks boyutu **39 × 31 hücre**, **2.361 kaynak face referansı**. 81×81 = 6.561 gerçek dünya XY konumunda 5 farklı ayak yüksekliği ve 4 iniş senaryosu, ayrıca özgün triangle centroid/boundary örnekleriyle **62.065 sorgu** için G159 tam liste ve G160 indeksli fonksiyonlar birebir aynı `hit/no hit` ve destek Z sonucunu üretti. Kaynaktaki gerçek polygon geometrisi/dokusu asla değiştirilmedi.

Bu örnekleme düzleminde sorgulanan **aday yüzey sayısı** önceki **4.940.433** → yeni **22.180** ( **%99,55 daha az** ). Bu sayı **aday triangle tarama azalmasıdır, FPS, CPU süresi veya Vita donanım performansı ölçümü değildir**. İndeksleme ilave RAM yaklaşık 4.840 B offsets + 9.444 B IDs ~=14 KiB, asıl 753 source triangle payload hariç. Bu RAM hesabı orijinal Vita cihazının toplam frame heap durumunu ölçmez.

**[G160 GitHub Actions tam gerçek G75 host/PS Vita ARM derleme](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39053003870)**; sonuç GitHub Actions run outcome olarak doğrulanmalı. CI testi kaynak karşılaştırmasını başarıyla geçti; tam ARM derleme sonucu ayrıca okunmalı.

## Mevcut 1. bölüm engelleri

**G159 yolun iOS native solidness kuralı kanıtı değil, kontrollü bir port çözüm adayı.** G160 sadece CPU aday aramasını optimize eder, yolun gerçek donanımda üzerinde yürünmesini doğrulamaz. G106 sky/alpha, G156 bina penetrasyonu, G83 MarkV Stage2/RUSH animasyonu, G146 QTE1456/PC6, orijinal tam görev ve gerçek 30 FPS kontrolü hâlâ açık. G155 `BLOCKED` durumu geçerli.

**Sıradaki karar:** Bu aşamada artık aynı yol atlasının ısı haritası çıkarılmayacak. G160/G159/G156/G106 bir arada tek anlamlı gerçek Vita QA hedefi hazırlanmalı; test gözlemi olmadan hiçbirine DONE denmeyecek ve rastgele yeni özellik talebine geçilmeyecek. YENİ VPK YOK.
