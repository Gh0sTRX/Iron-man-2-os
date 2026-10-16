# G67 — B24 G65 gerçek kaynak sahne / CPU çarpışma sertleştirme / ilk doğrulanmış Vita derlemesi
Tarih: 16 Ekim 2026 (Türkiye). Bu belge önceki G66 hardware beta ve G65 native UV/PVR kaynak çalışmasının üzerine gelir.

## Kaynak ve CI kanıtı
- Repo: https://github.com/Gh0sTRX/Iron-man-2-os (PRIVATE; özgün oyun materyalleri asla public repo'ya taşınmamalı).
- Dal: `feature/b24-unified-gameplay`
- G67 C ve VitaSDK kaynak commit'i: `b548f400b315933b072848961625e5320c29173a`
- CI: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38881118548 — **completed/success**.
- Workflow adı: B24 G67 PS Vita source triangle anti-tunneling collision beta.
- Artefakt: `IRONMAN2_B24_G67_NATIVE_COLLISION_HARDENED_VITA_BETA`, ID `12038005743`, Actions ZIP 5,127,888 bytes, ZIP SHA256 `9f415a48b069ad2f12870d3d41348e057e58e3f7b3b01a0bcd323a944cdc9570` (bu ZIP **VPK'nin hash'i değil**).
- Son tarih GitHub artefakt saklama: 30 Ekim 2026 09:33 UTC.
- İçerideki VPK: `IronMan2_B24_G67_Collision_Beta.vpk`, Vita `TITLE_ID=IM2G67001`.
- Önceki G66 G65 VPK derlemesi: https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/38880036578, `IM2G65001`; önceki dosyayı G67 üzerine yazmaz.

## G67 somut değişiklikleri
- `g66_playable/g67_collision.h`: kaynak 1.910 collider üçgeninden gerçek Z-kesiti ve finiteness/bound checks. Sabit .27/.94/1.61 metre torso üç yüksekliğinin kaçırdığı ayak ve baş hizası duvarlarda dinamik, duvar-oyuncu Z-overlap dilimleri.
- `g66_playable/main.c`: `sphere_clear_at` ortak G67 CPU yordamını kullanır; VitaGL renderer ve G65 orijinal atlaslara dokunulmadı. Uçuşta yatay hareket için kaynak floor üçgeni aranmaz; yerde yakın gerçek floor şartı kalır, 0.35m'den büyük zemin aşağı farkına anlık sıçrama reddedilir. 0.22m hareket alt-adımları korunur; uzak zemine tek-tick aşağı teleport kaldırıldı.
- `test_g67_collision.c`: düşük panel, üst panel, duvar kenarları, kaynak map sınırları, havadaki no-floor, zemindeki no-floor ve büyük iniş sıçraması regresyonları. CI host test adımı yeşil; gerçek VitaSDK/VitaGL/VPK doğrulama da yeşil.
- `CMakeLists.txt`: G67 ayrı TitleID ve adı. CI kaynak G65 22.441 sahne üçgenini, Mark VI 970 orijinal üçgenini ve 1.910 özgün collider üçgenini tekrar paketledi.

## YANLIŞ İDDİADAN KAÇIN
- GitHub CI **gerçek PS Vita donanım testi değildir**. Gerçek cihazda G67 açılış, FPS, renk/materyal, sahne-alfa, kamera/duvar/çatı/RUSH çarpışması gözlenmedi.
- Bu bir özgün iOS motorunun birebir portu **değil**; G65 orijinal source-derived assetli özgün VitaGL oynanabilir traversal beta'dır.
- Mark VI mesh hâlâ **statik pose**. Orijinal G10 304 anim katalog ve G10 animasyonları bu bağımsız betaya henüz bağlanmadı.
- Collider eksikleri, dik olmayan yüzeyler, sürekli sweep ve küçük dekor/74 mesh'in görünürlüğü/özel orijinal shader belirsiz; %100 geçilmeyen harita taahhüdü yok.
- En değerli sonraki doğrulama: gerçek Vita B24 G67'daki açılış ekranı, yürüyüş + binaya yandan çarpışma, hover/RUSH, alt/üst geçiş, FPS. Sonra G10 aktör animasyon stream'inin özgün G65 koordinatlarıyla ve GPU skinning maliyetiyle entegrasyonu.

Sonraki sohbet kaynak yolu: `research/b24_unified/G67_GITHUB_BUILD_VERIFIED_2026-10-16_TR.md`; her devamda GitHub branch son SHA ve Actions run karşılaştır.
