# G238–G240 — Orijinal 2010 oyun yükleyicisinden silah kaydı, G239 gerçek Vita ARM yürüyüş telemetrisi

**19 Ekim 2026 · `Gh0sTRX/Iron-man-2-os` / `feature/b24-unified-gameplay` · yeni VPK yok, fiziksel Vita testi henüz yok.**

## G238 — Orijinal iOS native WeaponDB'yi gerçekten kim dolduruyor?

[**G238 özgün 2010 Mach-O/CLARA CI SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39220623704). 248.613.763 bayt kullanıcıya ait 2010 IPA geçici özel Actions runner'da okundu; **65.500 özgün C++ Mach-O sembolünden __text kapsamına giren 14.164 gerçek fonksiyon ARM/Thumb duyarlı tarandı**; sıfır 64KB limitli fonksiyon, sıfır karma ISA sembol atlaması raporlandı.

Dört native metodun doğrudan çağıran kaynakları:

| Native doğrudan BL | Gerçek 2010 çağıran | Gerçek 2010 çağrılan |
|---|---|---|
| `0xC3694` | `GS_GamePlay::LoadEntities()` (`0xC2E8C`) | `WeaponDB::AddNewAttackEntity(EntityData*)` (`0xAB894`) |
| `0xC3678` | `GS_GamePlay::LoadEntities()` (`0xC2E8C`) | `WeaponDB::AddNewWeapon(EntityData*)` (`0xABF14`) |
| `0xC365C` | `GS_GamePlay::LoadEntities()` (`0xC2E8C`) | `WeaponDB::AddNewWeaponAccessory(EntityData*)` (`0xABBD4`) |
| `0xDA6AC` | `Actor::InitWeaponData(int)` (`0xDA694`) | `WeaponMgr::InitWeaponData(EntityData*,Entity3D*,int)` (`0xB27E4`) |

C1L1 `level1.bclara` özgün native tipli nesnelerin **26 Attack + 13 Weapon + 1 WeaponAccessory** olduğu ayrıca doğrulandı. Dosyadaki özgün Attack isimleri ve tam bağlam: `Attack_type0` dosya ad-ofset **38804**, scene ID **329**; `Attack_type1` **39308**, ID **332**; `Attack_F22_missile` **148398**, ID **1009**; `Attack_WM_Missile` **157004**, ID **1059**. Bunlar dosya sırası/scene ID'sidir; **WeaponDB[0/1] dizi kimliği değildir**. Böyle bir bağlantıyı ispatlamadan resmi port silah türü diye kullanma.

## G240 — LoadEntities üç native AddNew kolu aynı EntityData döngüsünde

[**G240 son başarılı kaynak CI**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39221185745). Orijinal ARM `GS_GamePlay::LoadEntities()` fonksiyonunda üç gerçek kol ayrı ayrı native disassembly ile incelendi. Ortak kaynak satırları:

```asm
; WeaponAccessory
0xC3654 ADD sl,sl,#1
0xC3658 MOV r1,r6
0xC365C BL WeaponDB::AddNewWeaponAccessory
0xC3660 CMP sl,fp
0xC3664 BNE 0xC2EB8
0xC3668 B 0xC32D0

; Weapon
0xC3670 ADD sl,sl,#1
0xC3674 MOV r1,r6
0xC3678 BL WeaponDB::AddNewWeapon
0xC367C CMP sl,fp
0xC3680 BNE 0xC2EB8
0xC3684 B 0xC32D0

; Attack
0xC368C ADD sl,sl,#1
0xC3690 MOV r1,r6
0xC3694 BL WeaponDB::AddNewAttackEntity
0xC3698 CMP sl,fp
0xC369C BNE 0xC2EB8
0xC36A0 B 0xC32D0
```

Bunlar **aynı dolaşım sayacı `sl`, EntityData parametresi `r6`, `fp` limit kontrolü ve aynı native döngüye dönüş adresi `0xC2EB8`** kullandıklarını kanıtlıyor. Ama döngünün `r6`'ya EntityData nesnelerini gerçekte hangi sırayla sağladığı ve `WeaponDB::AddNewAttackEntity` işleminin bu gerçek runtime sıra ile hangi Attack_type* ismini index0/index1'e yerleştirdiği **henüz ispatlanmadı**. Ayrıca bu üç çağrı koluna girmeyi sağlayan özgün sınıf/ID kontrolünün tüm dallanma koşulları çözülmedi.

İlk G240 CI (run `39220982845`) metadatanın `true_original_native_method_CPP` alanını yanlışlıkla `real_original_native_method_CPP` olarak okuyan test satırı nedeniyle FAIL oldu; gerçekte disassembly çalışmıştı. Workflow assertion düzeltildi ve native `sl/r6` döngü koşulları kaynak adreslerinden ayrı doğrulanarak **`39221185745` SUCCESS** gerçekleşti.

## G239 — yalnız kaynak ELF derlemesinde gerçek 120-kare yürüyüş teşhisi

[**G239 real reconstructed Vita ARM ELF CI SUCCESS**](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39220727358).

- Var olan gerçek G171 tek oyun `work/src/main.c` oluşturma zincirinde `g227_install_passive_real_main_Vita_world_actor_root_diagnostic.py` hemen ardından `g229_install_window_into_real_vita_main.py` eklendi.
- Aynı `B24_G227_WALK_ROOT_DIAGNOSTIC=ON` ile G229 120 ardışık başarılı ground render frame, analog, B14 öneri hareketi, özgün source collision sonrası hareket, GPU oyuncu root ve world ile kamera yer değiştirmesi gerçek oyun derlemesine bağlandı.
- Real-owner kaynak G227 ve G229 host C11 testleri, G229 opt-in installer fixture ve tek tek `B14 world tick` / `GPU draw` / `G8 animation` / `B16 fire` sahibi kontrolleri CI'dan geçti. VitaSDK `im2_beta` **ARM ELF başarılı derlendi**, `*.vpk` yokluğu denetlendi.
- **Henüz PS Vita donanımında bu G239 kaynağı oynatılmadı.** G229 teşhis logu gerçek cihazdan alınmadan `GROUND_WALK` kilidi çözülmüş gibi gösterilmemeli. Bu bir gerçek yürüyüş fizik düzeltmesi değil, G229 teşhisiyle donanım kök nedeninin izlenebilir hâle gelmesidir.

## Güncel açık işler / bir sonraki teslim önceliği

**Demoya geçişin en büyük blokajları:** (1) kullanıcı gözlemi yerde animasyon oynuyor ancak dünya hareket etmiyor; gerçek Vita G229 logu yok, (2) avatar-araba gerçek kaynak dünya/model ölçeği, (3) gece skybox, orijinal ışık/gölge/alfa, (4) saldırı→tam doğrulanmış iOS WeaponDB sıra/kayıt→original G8/WM animasyon→hasar/efekt, (5) Chapter 1 orijinal görev, QTE1456, cutscene ve kontrol/HUD/pause uçtan uca Vita QA.

**G241 önerisi:** `GS_GamePlay::LoadEntities` global EntityData listesi dolaşımının `r6` kaynağı, tip kodu switch ve dizinin gerçek kayıt sırasını G240 native C++ ARM komutlarından doğrula; gerekirse özgün CLARA loader yöntemini incele. Ancak yalnız sembol / dosya adı sayesinde doğru eşleme ilan etme. Aynı anda gerçek Vita G239 ground loguyla kök nedeni kapat. Oyun kodunu varsayımla değiştirme; **VPK hâlâ yok**.
