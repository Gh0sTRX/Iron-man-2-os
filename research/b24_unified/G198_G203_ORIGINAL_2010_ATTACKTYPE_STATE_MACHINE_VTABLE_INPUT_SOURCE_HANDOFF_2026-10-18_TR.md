# G198–G203 — Iron Man 2 iOS (2010) özgün saldırı durum makinesi: Actor → StateData::GetParam("AttackType", -1) → MainCharacter::DoAttack

**Tarih:** 18 Ekim 2026 · **Dal:** `feature/b24-unified-gameplay` · **VPK yok.**

## Kullanıcının gerçek hedefi

Orijinal iOS 2010 `MainCharacter::DoAttack(int,int)` 26 girişli saldırı tablosunu (G196–197) varsayımsal tuş/silah atamalarıyla Vita'ya taşımak yerine özgün **oyun state, source animasyon ve native kontrol** bağlantısını bul. Gerçek Vita'da yürüme, ölçek, sky/ışık, War Machine silahları, melee/QTE problemleri ayrıca açık kalır.

## G198: 2010 özgün native DoAttack niçin doğrudan çağrılmıyor?

Orijinal kullanıcı IPA içindeki ARM Mach-O'da **14.164** kaynak native ARM C++ methodu tarandı: `MainCharacter::DoAttack(int,int)` (**0xF64F8**) için **0 doğrudan BL/BLX** ve **0 direct tail branch**. Bu bir "ölü kod" ispatı değil. Asıl kanıt: file-backed Mach-O `__DATA/__const` bölümünde **0x4BD974 adresinden 0xF64F8'i işaret eden** gerçek pointer.

G198 CI PASS: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39125515371. G198 taraması kesiştiği register dolaylı çağrıların nihai `r1` attack selector değerlerini ve runtime yürütülmeyi kanıtlayamaz; bu eksiklik gizlenmedi. `__common`/BSS offset 0 hayalî veri okunmadı.

## G199: MainCharacter özgün C++ vtable yuvası 68 doğrulandı

Gerçek 2010 özgün C++ symbol **`vtable for MainCharacter` adresi 0x4BD85C**. Native ABI vtable entry header +8 kabul edildiğinde `0x4BD974 - 0x4BD85C - 8 = 272 = 0x110`, **sıfırdan başlayan sanal fonksiyon yuvası 68**. Bu slotta gerçek original `MainCharacter::DoAttack(int,int)` pointer'ı **0xF64F8**.

Gerçek özgün komşu sanal yöntemler: `StartMeleeAttack` (yuva 58), `IsInUniBeam` (66), `DoAttack` (68), `GetManualAttackRange` (69), `GetAimData` (72), `PlayAttackSound` (74); vtable'daki diğer temel `Actor` override'ları da gözlemlendi.

G199 CI SUCCESS: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39125721045. `G199_2010_MAINCHARACTER_SOURCE_VTABLE_NEIGHBORS.png` **gerçek kaynak CPP isimlerinden statik PNG**; oyun/vita ekranı veya animasyon değil. C++ vtable varlığı tek başına runtime kontrolcünün bu entry'yi çağırdığını ispatlamaz.

## G200: Tüm sınıflarda aynı byte offset kullanan sahte eşleşmeleri ayıkladık

Orijinal 14.164 native methodun *hepsini* G199 sınırlamasından bağımsız taradık: `+0x110` için **513** native `ldr` operandı ve **45** yakın indirect CALL/branch kalıbı ortaya çıktı: 26 `ldr pc`, 19 register indirect. Bunlardan çoğu **Irrlicht, gameswf, GLLive vb. başka sanal sınıfların** `+0x110` ofseti; otomatik olarak MainCharacter saldırısı sayılamaz.

**Önemli gerçek aday:** `Actor::UpdateStateAttack(int, State*)` native **0xDB610** içinde **0xDB6D8 `LDR PC,[R3,#0x110]`** gerçek sanal CALL görülüyor ve hemen önce **`MOV LR,PC`**. G200 CI PASS: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39125917524.

## G201: Özgün Actor sanal metodunu MainCharacter override'ına kaynak seviyesinde bağladık

**Actor base `vtable for Actor` = 0x4BD474**, yine yuva **68**: file-backed gerçek pointer adresi **0x4BD58C**, pointer hedefi **`Actor::DoAttack(int,int)`**. Derived `MainCharacter` vtable aynı yuvada **`MainCharacter::DoAttack`** override'ına işaret ediyor.

Gerçek original ARM `Actor::UpdateStateAttack` kaydı:

```asm
0xDB6BC  LDR  R0,[R5,#0x3DC]
0xDB6C0  LDR  R3,[R5]             ; this->vtable
0xDB6C4  ADD  IP,R0,#1
0xDB6C8  MOV  R1,SL               ; DoAttack 1. integer argument
0xDB6CC  STR  IP,[R5,#0x3DC]
0xDB6D0  MOV  R0,R5               ; this
0xDB6D4  MOV  LR,PC
0xDB6D8  LDR  PC,[R3,#0x110]      ; virtual call slot68
```

Bu kaynak, orijinal `Actor` saldırı durum update'inin **`DoAttack(int,int)` sanal metodunu çağırdığını** ve MainCharacter için o yuva override'ının bulunduğunu gösteriyor. Oyun sırasında bir nesnenin gerçekten MainCharacter olması ve hangi control/input event ile hangi state'e girmesi ayrıca izlenmedi. Bu ayrım korunmalı.

G201 CI PASS (ilk workflow key typo düzeltildi): https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39126166403.

## G202–G203: Beklediğimiz gerçek saldırı değişkeninin ADI açıldı!

`Actor::UpdateStateAttack` içinde orijinal ARM:

```asm
0xDB61C  LDR R1,[R2,#0x58]         ; State indeks/özel veri
0xDB630  LDR SL,[R2,#4]
0xDB634  LDR R0,[R2,#0x90]         ; StateData argümanını taşıyan pointer
0xDB64C  MVN R2,#0                ; C++ 2. parametre = -1
0xDB654  LDR R1,[PC,#0x120]
0xDB658  ADD R1,PC,R1              ; gerçek native PIC string
0xDB65C  BL  0x9C340               ; StateData::GetParam(char const*,int)
0xDB660  CMP R0,#1
0xDB664  CMPNE R0,#0x12           ; 18
0xDB668  MOV SL,R0
0xDB66C  BNE 0xDB730
...
0xDB6C8  MOV R1,SL
0xDB6D8  LDR PC,[R3,#0x110]
```

Gerçek owner source ARM literal pool **0xDB77C** ve signed PC-relative delta ile ASCII string **`"AttackType"`** gerçek iOS owner Mach-O metninden çözüldü (**key VM 0x49F410**). Native `0x9C340` özgün C++ isim `StateData::GetParam(char const*,int)`. Yani oyun, `StateData::GetParam("AttackType",-1)` sonucunu işlemden geçirip özgün Actor saldırı durumuna bağlı **`DoAttack` sanal çağrısına** taşıyor. Native compare 1 ve 18 görülüyor ama farklı branch/back-edge'ler bulunduğu için "yalnızca 1 ve 18 silahları var" demek **yanlış**.

Aynı orijinal native Actor state fonksiyonundaki yardımcı C++ yöntemleri:
- `0xA14F0 StateTrack::GetEvent(int,int)`
- `0xB1CF4 WeaponMgr::GetCurrentWeapon()`
- `0xC0BEC WeaponEntity::IsAnyTrailEnabled()`
- `0xC0C0C WeaponEntity::EnableAllAccesoriesTrails(bool)`
- `0x6A0B8 Model::IsAfterTime(int)`
- `0x6A0A4 Model::IsBeforeTime(int)`

G202/G203 son CI SUCCESS: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39126493408.

**Çok önemli semantik uyarısı:** `"AttackType"` parametresi bulunan *orijinal state verisi* ile daha önce Level1 Lua içinde görülen `SetAttackTypeEnabled(1,true/false)` aynı kavrama benzese de **kaynak storage/enum özdeşliği ve gerçek missile, gatling, repulsor, Beam veya `Aim_M` animasyonu eşlemesi henüz kanıtlanmadı.** G196'nın 26 entry ID'lerini bu duruma rastgele atama.

## Kesin bir sonraki aşama (G204)

Özgün `StateData` kaynak varlık dosyalarında `AttackType` metni ve bu parametrenin gerçek int değerleri, `StateData::Load` parsing yolu, `StateTrack` attack event zamanları ile `WeaponMgr::GetCurrentWeapon` gerçek kaynak edge'i araştırılmalı. Sonra G195 **altı gerçek Uni-Beam BRES animation frame/socket verileri** G83/G169 gerçek runtime sequencer'a **kaynak kontrollü** bağlanabilir.

**Açık diğer büyük Vita maddeleri:** yerinde yürüyen karakter/harita ölçeği (G168/G171 Vita cihaz sonucu), skybox/gece çevre ışıkları/gölgeler ve ay, War Machine özgün shoulder/gatling/rocket hareketleri, melee hit windows, C1L1 QTE ve tam mission flow. G198–203 yalnızca original ARM/native statik kaynağı; **yeni Vita ELF ya da VPK üretilmedi**.
