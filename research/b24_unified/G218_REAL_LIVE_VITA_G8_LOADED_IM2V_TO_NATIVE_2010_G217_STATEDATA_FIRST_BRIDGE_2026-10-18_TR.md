# G218 — İlk gerçek Vita oyun döngüsünde özgün iOS 2010 G217 StateData/StateTrack bağlantısı

**18 Ekim 2026 · `Gh0sTRX/Iron-man-2-os` · `feature/b24-unified-gameplay` · VPK yok.**

## Gerçek kodda yapılan entegrasyon

Özgün iOS oyununun G213B tam `states` çözümünden G217 tarafından oluşturulan **4 zırh × 194 = 776 otantik, isimli StateData kaydı** ve native `attack/Attack/trail` marker u32 verileri read-only C11 tabloya taşındı. G218 bu gerçek veri tablosunu, G84/G83'ün seçtiği aday ismine değil, **mevcut G8 tek `b24_g8_motion_tick_g84` kaynak akışının gerçekte açabildiği `b24_original_motion.selected` IM2V klip adına** bağladı. `b24_original_motion.active` ve `.missing` guardları nedeniyle dosya açılamazsa/native streamed frame aktif değilse eşleşmiş state raporlanmaz.

Gerçek ana döngü öncesi zincir: **B14 tek fizik tick → G83 kaynak animasyon rotası → G169 Beam1/2/3 (yalnız önceki B16 kabul edilmiş port olayı) → G8 tek özgün IM2V kaynak sampler → G218 pasif native StateData eşleştirme**. G8'in melee/repulsor/beam öncelik sırasına dokunulmadı, ikinci render/motor yaratılmadı; G217 gerçek state tablosu yalnız gözlemci üzerinden kaynak girdisine bağlandı.

Entegrasyon patch'i: `research/b24_unified/g218_source_live_state_bridge/g218_attach_G217_native_source_state_to_REAL_G8_animation_owner_NO_VPK.py`. Tek callsite `b24_g218_observe_actually_loaded_G8_clip`, sadece `B24_G218_SOURCE_STATE_OBSERVER=ON` flag'i ile aktiftir; CMake G84+G85+G169+G173 original tek animator varlığını şart koşar. Tam G171 eski rekonstrüksiyon akışı autentik G217 Actions artifact'ını indirip kaynak header + observer'ı `work/b24/b24_unified/` altına kopyalar, `work/src/main.c` içine yalnız gözlemci çağrısı ekler. Yeni oyun kaynak dosyası IPA veya VPK'a kopyalanmaz.

## İlk eşleştirdiğimiz kaynak durumları

| Gerçek G8 kaynak klip örneği | G217 StateData adı / original index | Orijinal `AttackType` | Orijinal ham `attack` marker |
|---|---|---:|---:|
| `ironman_ironman_ground_idel` | `Idle` / 0 | — | — |
| `ironman_ironman_walk_f` | `Move_Walk` / 2 | — | — |
| `ironman_ironman_run` | `Move_Run` / 3 | — | — |
| `ironman_ironman_fly_f` | `Fly` / 14 | — | — |
| `ironman_ironman_ground_combo_1` | `Attack_Ground_COMBO1` / 40 | 0 | 300 |
| `ironman_ironman_ground_combo_2` | `Attack_Ground_COMBO2` / 42 | 0 | 200 |
| `ironman_ironman_ground_combo_3` | `Attack_Ground_COMBO3` / 44 | 0 | 500 |
| `suitcase_ironman_ground_combo_1` | Mark V `Attack_Ground_COMBO1` / 40 | 0 | 300 |
| `ironman_ironman_aim_m_ground_idle` | `Attack_M_Ground_idle` / 66 | 2 | 260 |
| `warmachine_warmachine_aim_m_ground_idle` | WM `Attack_M_Ground_idle` / 66 | **25** | 260 |
| `warmachine_warmachine_aim_m_float_idle` | WM `Attack_M_Float_idle` / 65 | **25** | 250 |
| `ironman_ironman_aim_ground_beam1/2/3` | **ad benzerliğine göre aday** `Attack_Ground_Beam_prepare/Beam/Beam_out` / 84/85/86 | 4 | `Beam_out` 413 |
| `suitcase_ironman_aim_float_beam3` | Mark V **aday** `Attack_Float_Beam_out` / 89 | 4 | 507 |

Bu eşlemelerin özgün byte-level `.im2v` klip isimleri ve tam orijinal G217 StateData adlarından doğrudan türetilmesi kaynağa dayalıdır. **Native 2010 StateMgr'nin gerçekten bu ID'yi bu `.im2v` adına atadığı ARM runtime branch henüz kanıtlanmadı.** Bu yüzden API alanının adı `source_state_name_correspondence_ONLY`, `actual_2010_StateMgr_runtime_state_PROVEN` her zaman false. `Beam1/2/3` → `prepare/Beam/out` dizi karşılığı güvenli *isim-temelli adaydır*, orijinal oyun mantığının kanıtı olarak sunulmamalıdır. `source_attack_event_start_raw_UNCLASSIFIED` ne milisaniye ne isabet/hit frame/mermi ateş anı olarak kullanılabilir.

WM `_M` dosyası için değer `25` gerçek kaynak kaydıdır, ancak `_M`'nin füze/omuz topu/gatling olmasının delili **değildir**. G84 mevcut giriş tarafında G83 `AIM_M` üretmediği için bu orijinal source kliplerin hepsi **kullanıcı tuşuyla oynanıyor sayılmaz**; C11 doğrudan testle görüntüleme–durum metadata bağlantısı doğrulandı. B16 silah ve B14 fizik hiçbir biçimde değiştirilmedi.

## Testler — kodu gerçekten çalıştırdık

**[G218 C11 host PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39136744369)**: G217 776 gerçek state header indirildi, 16 gerçek source klip–durum–AttackType–marker örnekleri, MarkV/VI/WM üç ayrı model index guard, missing/active fail-closed, bilinmeyen `_att`/silah ayrımı ve true no-damage flags doğrulandı.

**[G218 tam birleştirilmiş `im2_beta` Vita ARM ELF-only PASS](https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/39136868430)**: G171 kaynak gerçek C1L1 dünya, 248 Mark V animasyon, 10 WM `_M` yer animasyonu, G173 kaynak Beam yönlendirmesi G218 sonrası tekrar host testlerle denetlendi; tek `b24_g83_timeline_tick`, tek `b24_g8_motion_tick_g84`, tek `b14_world_tick`, tek B16 accepted fire aynı kaldı; VitaSDK Docker içinden `cmake --build ... --target im2_beta` ARM ELF derlendi, **VPK hiç oluşturulmadı**.

**Sınır:** Gerçek fiziksel PS Vita'da kullanıcı testi yok. Kaynak gözlemci var ama henüz dinamik oyun HUD'una state ID yazmadık veya state machine'i bu kayıtlara göre yönlendirmedik. Fiziksel yürürken yerinde sayma, araç karşısı ölçek, aydınlatma/gölgeler/skybox ve ses, özgün War Machine silah/rocket, combat hit windows ve C1L1 QTE/mission end-to-end halen açık.

## Takip G219

Gerçek `StateTrack::GetEvent(int,int)` üçüncü u32 dönüt ve çağıran `Actor::UpdateStateAttack` tarafından nasıl tüketildiğini native ARM kaynağından çıkar. Eğer original source event `attack` gerçekten projectile/hit/ses yan etkisine dönüştürülüyorsa onu kaynak kanıtıyla sınıflandır; ancak gerçek 2010 tick zaman birimi/normalization doğrulanmadan VPK'da 'şu ms'de vur' hilesi oluşturma.