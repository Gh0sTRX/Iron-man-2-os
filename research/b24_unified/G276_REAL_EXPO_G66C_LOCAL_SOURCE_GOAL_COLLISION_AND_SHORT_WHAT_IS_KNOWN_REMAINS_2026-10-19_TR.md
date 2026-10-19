# G276 — Gerçek ilk bölüm yer çarpışması karşılaştırma denemesi ve kısa ilerleme hesabı

**19 Ekim 2026 / `feature/b24-unified-gameplay` / VPK ÜRETİLMİYOR.**

## Bu tur gerçek kod işlemi

- [G275 özgün kaynak C11 PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39272740265) sonrasında `research/b24_unified/g276_original_Mission000_Position1_vs_true_G66C_world_source/test_g276_true_original_Mission000_Position1_local_vs_G66C.c` eklendi. Gerçek iOS kaynak Lua `MoveEntityToEntity(1062,1892,3000)`, 137 özgün `PositionDummy` sınıfı `Num=0→Position1`, ilk özgün `PD_IM_jump_goal` source child1893 authored local `(-.493,-28.062,3.705)` değerlerini **oyun dünyası/ayak konumu olarak kabul etmez**, sadece kaynak konum adayı olarak orijinal 1910 G66C triangle host resolver testine verir.
- `.github/workflows/g276-original-Mission000-Position1-versus-real-C1L1-G66C-no-vpk.yml` şunları yapar: doğrulanmış G275 kaynak header'ını ve tarihî G68 Vita paketinden **yalnız özgün G66C çarpışma varlığını** salt-okunur olarak alır (yeni paket oluşturmaz); 1910 triangle/1690 dik duvarı doğrular; 8 yön × ground/flight × dört kaynak hipotezi test eder: özgün script goal local, özgün authored MC local, G249 düşük MC support, G249 orta MC support; yerde hareket kabul/reddini kayıt eder. Gerçek G66C varlığı geçmiş pakette çıkmazsa uydurma geometri yerine CI **fail** eder.
- [**G276 GitHub CI**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39283072821) sonucu GitHub işinin çalışmasıyla doğrulanmalıdır. Kodun commit edilmiş olması **PASS veya Vita donanımı test edildi** demek değildir. G66C local/authored vs gerçek dünya dönüşümü aynı olmadığı için bu test de son oyuncu feetZ'yi ispatlamaz.
- `G229_WALK_WINDOW` 120 frame orijinal Vita logu gelmedi. `G66C` wall 715 silinmedi, rastgele doğrudan actor teleport yapılmadı, oyun animasyon/G8, combat ve ışıklandırma değişmedi. **Yeni VPK yok.**

## Bildiğimiz / bilmediğimiz — kullanıcının anlayacağı kadar

| Sistem | Kaynak düzeyinde bildiğimiz | Çalışan demo için açık kabul |
|---|---|---|
| Hareket/yürüme | B14 input/world sim ve G75 gerçek Expo çarpışması, orijinal MC ve kaynak yerel konum kayıtları; yer kilidi host'ta yeniden üretildi | Gerçek Vita açılış world/ayak XYZ ve aynı donanımda ground hareketinin çalışması |
| Flight | Hover/Stage2/rush ayrımı, kaynak hareket/animasyon yönleri | Tüm yön ve geçişlerin oyun içinde kontrolü |
| Animasyon | Orijinal klipler/rig ve ciddi sayıda komut/state eşleşmesi | Her zırhta eksiksiz G8/War Machine/world-root timing |
| Combat | Orijinal WeaponDB indeks/metot kaynakları, Uni-Beam/repulsor/walkfire dalları | Tam silah, hedef, hasar, kilit/füze, yakın dövüş/kombo |
| Harita/ışık | Gerçek Expo mesh, C1L1 collision, sky atlas/ay, dört özgün Sun ışığı | Ölçek, GPU dynamic armor+city lighting, gölgeler, transparan alfa, gerçek Vita görüntüsü |
| Mission/audio | `Mission000` Lua script, QTE izleri, source audio, 2010 açılış hedef kodu | Tam açılış/cutscene, QTE/ses, düşmanlar, görev tamamlanması |
| Tek sürüm QA | Ayrı orijinal kaynak CI'ları ve daha eski ARM ELF derlemesi | **Aynı commit'teki 7/7 tam entegre host+Vita ELF QA**, ardından bir VPK ve fiziksel cihaz QA |

**Kalan:** Yedi pre-VPK kaynak kabul kapısının **0/7'si tam**. Bu, küçük adımlarla kaynak kodu ilerlemediği anlamına gelmez; orijinal metotların çözülmesi oyun motoru davranışlarının aynı uygulamada sağlam çalıştığını doğrulamaz. Kısa test demo için bile ilk gerçek oyuncu yer hareketi, tam animasyon/combata bağlama, görseller + ışıklandırma, görev ve son sistem derlemesi ciddi entegrasyon işidir. Takvim/oyunun yüzde tamamlanma hesabını ölçen veri yok; sahte bitiş tarihi ve yüzde verilmemeli.

**Kullanıcının iş sırası kesin:** (1) MC / yerde yürüme, (2) movement+flight, (3) animasyon, (4) combat, **(5) Expo/ölçek + gerçek çevresel/dinamik ışıklandırma/gölge/sky/alfa/HUD**, (6) orijinal görev ses/QTE, (7) tek ELF/host QA → tek VPK → Vita gerçek donanım QA.
