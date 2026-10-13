# B18 — Orijinal Gameloft iOS Oyununun 9 Bölümü: Başlık/Saat Referansı ve 10 BCLARA Açmazı

**Kaynak ayrımı:** Bunlar **2010 Gameloft iOS/iPad oyunu** içindir; Sega PS3/X360/PSP/Wii Iron Man 2 oyunlarının bölüm veya ara sahneleri değildir.

## Bağımsız bölüm sayısı kanıtı
- Aayush Arya, *Macworld*, 21 Mayıs 2010: oyun **nine levels**, ilk bölüm öğretici işlevli; uçuş, checkpoint, süreli görev ve bulmaca içeriği. https://www.macworld.com/article/205532/ironman2review.html
- Daniel Perez, *IntoMobile*, 7 Mayıs 2010: **9 levels**, ilk oyun kısmında Tony'nin Suitcase prototipi sahnesi; sonraki görevlerde Iron Man ve War Machine karakter seçimi. Yalnız Iron Man'in upgrade edilebildiğini gözlemlemiş; iki karakterin de melee, repulsor, missiles ve hover/fly yapabildiğini yazıyor. https://www.intomobile.com/2010/05/07/review-iron-man-2-for-iphone-ipad/
- Mike Rose, *Pocket Gamer*, 4 Mayıs 2010: **nine locations**; Ultimo, Firepower, Whiplash düşmanlarından söz ediyor. https://www.pocketgamer.com/iron-man-2-ipad/iron-man-2-flies-onto-ipad/

## Orijinal iOS tam oynanış video referansı (BAĞIMSIZ, kaynak veriye henüz eşlenmedi)
2022'de Longplay Express tarafından paylaşılan *Iron Man 2 iOS Full Longplay* videonun açıklamasında aşağıdaki sırayla **9 level** zaman damgası verilmiş: https://www.youtube.com/watch?v=kOzFwwlHmqE . Bunlar topluluk kaydı etiketleridir; henüz orijinal `level*.bclara` içindeki görev isimleriyle ikili düzeyde eşlenmedi.

| # | iOS longplay bölüm adı | Video başlangıcı |
|---:|---|---|
| 1 | Media Mayhem | 00:00:08 |
| 2 | Rush Hour Raid | 00:12:17 |
| 3 | Hostage Crisis | 00:25:30 |
| 4 | The Dishonorable Host | 00:41:28 |
| 5 | Under Water, Under Siege | 00:57:36 |
| 6 | Lashing Out | 01:06:38 |
| 7 | Airborne Assault | 01:23:19 |
| 8 | Power Suits | 01:33:39 |
| 9 | The Elusive Mastermind | 01:39:54 |
| | Credits | 01:48:22 |

**Not:** 10 dosyalı `Payload/IronMan2.app/clev` arşivi daha önce doğrulandı: `level1.bclara` … `level10.bclara`. Video/dönem incelemesi 9 oynanabilir bölümü desteklese bile **level10.bclara'nın neden var olduğu çözülmüş değildir**. Tutorial (ilk bölüm mü ayrı mı?), credits, dev test, kullanılmayan content, cutscene veya meta yapı hipotezleri ayrı ayrı kontrol edilmeli; şu an bunlardan biri kesin denemez.

## Orijinal görev sistemine eklenen gereksinimler
*IntoMobile* iOS oynanış incelemesinin yeniden okuması, önceki B17 planımızda eksik bıraktığımız ayrıntıları ortaya koydu:
- Bazı görevlerde **bombayı etkisizleştirmek için kaydırmalı karo/görsel eşleme mini oyunu** bulunuyor. Sadece kill-enemy ve fetch görevleriyle tam oyun olmaz.
- Görev bazında **uçuş yükseklik sınırları** değişebiliyor. B17 prototipinin sabit `z` sınırını orijinal mekanik diye kullanmayın.
- Dönem yorumcusu **upgrade sistemini yalnız Iron Man'e açık**, War Machine için kapalı gördüğünü yazıyor. Bu yazılı basın tanıklığıdır, kesin binary unlocking matrisi değildir. İleride level ve upgrade script ile doğrulansın.
- XP ile görev arası Iron Man zırh saldırıları/kalkan/combos geliştirildiği yazıyor. B31 progression bu kaydı temel alarak doğrulanmalı.
- İki karakter de ground melee, repulsor, missiles ve flight kullanabiliyor olabilir; "sadece WM missiles, sadece IM Unibeam" gibi katı matris **kaynağa dayanmadan** kodlanmamalı.

## Her bölümün geri kazanılması için BCLARA eşleştirme matrisi
Her `levelN.bclara` için:
`config hash → mission classes → scene references → objective nodes → spawn positions → scripted actors/boss → puzzle states → camera/cutscene IDs → voice/music/SFX IDs → checkpoint/save schema → Vita doğrulaması`.

Bu 10x9 çapraz tablo dolmadan dokuzlu video adını doğrudan `level1-9` ile bire bir eşlemeyin. Orijinal dialog ve ara sahnenin codec/timeline verileri henüz çıkarılmadı.
