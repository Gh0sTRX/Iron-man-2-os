# Vita saat hızı artırımı (performans)

**Seviye:** host-static kaynak testi + syntax derlemesi. **Fiziksel Vita'da doğrulanmadı.**

## Neden
G69 gerçek cihaz fotoğrafındaki PSVshell satırı: `CPU 333 / GPU 111 / BUS 222 / XBAR 111 MHz`.
Uygulama Vita'nın düşük güç saatlerinde çalışıyordu; GPU normal azami değerinin yarısındaydı.
Renderer 960x544'te tam ekran gökyüzü + şehir + zırh + HUD çizdiği için doldurma (fill-rate) ağırlıklıdır.

## Ne değişti
`b24_gpu_owner_vitagl.c` → `b24_gpu_owner_init()` içinde, `vglInit`'ten **önce**:

| Saat | Önce | Sonra |
|---|---|---|
| CPU (ARM) | 333 | 444 |
| GPU | 111 | 222 |
| BUS | 222 | 222 |
| GPU XBAR | 111 | 166 |

Çağrılar yalnızca `__vita__` altında derlenir; host/mock testleri etkilenmez.
`ScePower_stub` tüm B24 CMake hedeflerinde zaten bağlıdır, CMake değişikliği yoktur.

## Bedeli
Daha hızlı pil tüketimi ve ısınma. Oyun zaten tam performans hedefliyor; sorun olursa
yalnızca ilgili satırlar düşürülebilir.

## Nasıl ölçülür (fiziksel Vita)
1. PSVshell'i açık tutarak aynı sahnede 60 sn bekle (önceki G69 ile aynı kamera).
2. Önce/sonra için şunları kaydet: FPS, `CPU/GPU/BUS/XBAR` MHz satırı, MEM/VMEM.
3. Saat satırında `444/222/222/166` görünmüyorsa PSVshell veya başka bir eklenti saatleri
   eziyor olabilir; bu durumda kazanç beklenmemeli.

## Test
```bash
python3 -I research/b24_unified/perf_vita_clocks/test_vita_clock_boost_guard.py
```

## Bilinmeyenler
- Gerçek FPS kazancı (ölçülmedi).
- VMEM 112/112 MB dolu; doku belleği ayrı bir sorun olabilir, bu değişiklik ona dokunmaz.
- GPU mu CPU mu darboğaz: PSVshell'de saat artışından sonra FPS hâlâ düşükse sıradaki adım
  `b24_gpu_cpu_profile` fazlarını (SCENE/SUIT/HUD/SWAP) cihazda okumaktır.
