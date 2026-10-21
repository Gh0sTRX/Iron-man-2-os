# G304 — Özgün iOS kaynak kanıtı denetimi, yanlış pozitif G83 hit bayrağı iptali

**21 Ekim 2026 — aktif `feature/b24-unified-gameplay` — VPK YOK.**

## Orijinal 2010 kaynak ile önceki B/G kodu karşılaştırması
B13/B18 ile kurtardığımız özgün IM2V isimleri ve animasyon süreleri **gerçek**, ancak bunların native controller/hasar/temas ve görev tarafından hangi karede tetiklendiği aynı veri değil. G213B özgün 361393-byte `states` verisinden 55 set / 1487 StateData / 3658 StateTrack, G217 4×194 oyuncu StateData ve ham native track değerleri doğruladı. G221/G222 orijinal `Actor::UpdateStateAttack → MainCharacter::DoAttack` parametre kaynağını buldu; gerçek hedef/temas, sahne izinleri, iOS controller eşlemesi ve raw event zaman birimi hala kanıtlanmadı.

G83 önce `needs_2010_hit_event=1` bayrağını (a) yalnız bir `_att` IM2V seçildi diye ve (b) G82 kombo pozu seçildi diye atıyordu. **Bu, gerçek iOS isabet olayı bulmuş olduğumuz şeklinde yanlış yorumlanabilecek bir kaynak uyumsuzluğu.** Özgün 2010 StateTrack'in `attack` ham kaydı var diye her `_att` klipte bir hasar olayı atamak veya G8 klip süresi yüzdesini hasar penceresi yapmak kaynak kanıtı değildir. Özellikle orijinal `Attack_Ground_COMBO1` native ham event `start=300`, orijinal 2010 G8 klip süresi 266ms; **ham olay birimi doğrulanmadığı için 300'ü ms diye yorumlama**.

## Somut düzeltme ve koruma
- `g83_full_motion_aim/b24_g83_unified_movement_aim.c`: G83 `needs_2010_hit_event` legacy API bayrağı **daima 0**, gerek hedefli ranged gerek G82 true authored combo. Bu bayrak önceki gibi yanlış ikinci hasar yolu açamaz. **B16 tek var olan kabul edilmiş atışı, G8 tek orijinal IM2V oynatıcısı, G82 native veri/izin/gerçek temas gerektiren ayrı hasar çözücüsü korunur.**
- Aynı başlıkta sözleşme güncellendi, G83 yürüyüş, hover/flight/rush, WM, gerçek süreli G300/G301 regresyon testleri `_att`/kombo için ek isabet olmayacak şekilde yeniden doğrulanır.
- `g304_original_ios_hit_provenance/test_...` G171 gerçek kaynak birleştirilmiş ağacındaki **G217 tam orijinal header** üzerinden özgün MarkVI Combo1/2/3 native AttackType=0 ham starts 300/200/500, MarkVI Aim_M=2, WM Aim_M=25, Beam=4 karşılaştırır. Sonra aynı gerçek G83/G82 runtime C kodunda saldırı kliplerinin yeni native hit olayı üretmediğini ve kanıtsız G82 contact'ın reddedildiğini ispatlar. Sentetik raw source veya uydurulmuş native Damage eklenmez.
- B14/G75 fizik hızları 2.7/5.2/4.2/12/24 port ayarıdır, **orijinal iOS hız değerleri DEĞİL**. B14 tek hareket engine sahibi korunur, burada keyfi yeniden ayarlanmaz. G165 WM neutral/Rush başka *orijinal* kaynaktan alınmış **geçici** pozlar, gerçek native `Neutral` veya `Rush` olayı kanıtı değil. G172 Aim_M gerçek 10 animasyon dosyası fakat M'nin füze mi gatling mi olduğu bilinmiyor. B1/G1 GPU ilk Vita build'i **gerçek crash** yaşamıştır (G1 vitaGL Splashscreen SceGxm), eski G1 = kararlı oynanış iddiası geçersizdir.
- G299 G95 four-Sun aydınlatma gerçek kaynak *konumlarına* dayalı **deneysel** rendering. Gerçek renk/ışık türü/gölge/ay halen çözülmedi. İleride bu adayları native kanıt yerine kullanmayacağız.

**Güven sırası:** (A) özgün iOS byte/ARM/StateData/IM2V kanıtı; (B) host orijinal source fixture; (C) ARM ELF derleme; (D) cihaz gerçek oynanış. A olmadan bir B14/G8/B1 varsayımını 'orijinal oyun böyleydi' diye onaylama. Değiştirmediğimiz prototip sistemlerini topluca silmek de yanlış: kaynakla ölçmeden oyuncu ilerlemesini bozmayalım. G255 7/7 hâlâ false, VPK yok.

**Eksikler:** fiziksel Vita yerinde yürüyüş, orijinal MC world-root, Stage2 Rush native input, War Machine gerçek mermi tetikleyici, özgün hit / projectile, C1L1 ışık/sky/shadow, Mission000 QTE; öncelik sırası aynı.
