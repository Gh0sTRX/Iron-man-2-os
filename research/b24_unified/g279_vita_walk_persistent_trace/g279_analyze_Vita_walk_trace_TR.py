#!/usr/bin/env python3
"""G279 offline strict parser for optional PRIVATE Vita walk CSV.
Never claim a file comes from a real PS Vita automatically: its provenance
must be confirmed by the device owner. Parsing changes NO source game data.
NO VPK, assets, network or external libraries.
"""
from __future__ import annotations
import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import math

COLUMNS=(
 "phase,frame,ms,initial_x,initial_y,initial_z,world_x,world_y,world_z,"
 "gpu_x,gpu_y,gpu_z,camera_x,camera_y,stick_x,stick_y,"
 "b14_path,resolved_path,native_floor_z,active_stick,collision_reject,"
 "gpu_root_mismatch,wall_reject,missing_floor,step_reject,has_native_floor,"
 "world_dx,world_dy,camera_dx,camera_dy,verdict"
).split(",")
FLOATS={
 "initial_x","initial_y","initial_z","world_x","world_y","world_z",
 "gpu_x","gpu_y","gpu_z","camera_x","camera_y","stick_x","stick_y",
 "b14_path","resolved_path","native_floor_z",
 "world_dx","world_dy","camera_dx","camera_dy"
}
INTS={
 "frame","ms","active_stick","collision_reject","gpu_root_mismatch",
 "wall_reject","missing_floor","step_reject","has_native_floor"
}
ALLOWED_VERDICTS={
 "BOOT_SAMPLE","INCOMPLETE_120_RENDERED_GROUND_FRAMES",
 "STICK_INSUFFICIENT_FOR_CAUSAL_INFERENCE",
 "GPU_RENDER_ROOT_DISAGREES_WITH_WORLD","B14_NO_GROUND_TRANSLATION",
 "COLLISION_REJECTS_GROUND_MOTION","WORLD_PATH_SMALL_INCONCLUSIVE",
 "WORLD_MOVED_BUT_NET_SMALL_OR_REVERSED",
 "WORLD_AND_CAMERA_POSITIONS_TRANSLATE_TOGETHER",
 "WORLD_MOVES_CAMERA_OFFSET_CHANGED_CHECK_VIEW"
}
MAX_BYTES=8*1024*1024
MAX_ROWS=30000

@dataclass(frozen=True)
class WalkRow:
 line:int
 phase:str
 verdict:str
 numeric:dict[str,float|int]
 def __getitem__(self,key:str)->float|int:
  return self.numeric[key]

def parse_csv(file:Path)->list[WalkRow]:
 if not file.is_file():raise ValueError("Kayıt dosyası bulunamadı")
 if file.stat().st_size>MAX_BYTES:raise ValueError("Kayıt 8 MiB sınırını aşıyor")
 rows=[]
 with file.open("r",encoding="utf-8-sig",newline="") as fp:
  reader=csv.DictReader(fp,strict=True)
  if reader.fieldnames!=COLUMNS:
   raise ValueError(f"Yanlış G279 sütun başlığı: {len(reader.fieldnames or [])} alan; tam 31 gerekli")
  previous_frame=-1
  for idx,raw in enumerate(reader,start=2):
   if idx>MAX_ROWS+1:raise ValueError("Çok fazla kayıt satırı")
   if None in raw or any(x is None for x in raw.values()):
    raise ValueError(f"Satır {idx}: eksik/fazla CSV alanı")
   if raw["phase"] not in {"BOOT","WALK120"}:
    raise ValueError(f"Satır {idx}: geçersiz evre")
   if raw["verdict"] not in ALLOWED_VERDICTS:
    raise ValueError(f"Satır {idx}: G229 sınıflandırma adı bilinmiyor")
   if raw["phase"]=="BOOT" and raw["verdict"]!="BOOT_SAMPLE":
    raise ValueError(f"Satır {idx}: BOOT sonucuna yürüyüş hükmü yazılmış")
   if raw["phase"]=="WALK120" and raw["verdict"]=="BOOT_SAMPLE":
    raise ValueError(f"Satır {idx}: 120 kare sonucu bulunmuyor")
   numbers={}
   for k in FLOATS:
    try: n=float(raw[k])
    except (TypeError,ValueError):raise ValueError(f"Satır {idx}: {k} sayısal değil") from None
    if not math.isfinite(n):raise ValueError(f"Satır {idx}: {k} NaN veya sonsuz")
    numbers[k]=n
   for k in INTS:
    if not raw[k].isdigit():raise ValueError(f"Satır {idx}: {k} negatif/sayısal değil")
    numbers[k]=int(raw[k])
   if numbers["has_native_floor"] not in (0,1):
    raise ValueError(f"Satır {idx}: zemin bulunma bayrağı yanlış")
   if any(numbers[k]>120 for k in ("active_stick","collision_reject","gpu_root_mismatch")):
    raise ValueError(f"Satır {idx}: 120 kare dışı toplama sayacı")
   if numbers["b14_path"]<0 or numbers["resolved_path"]<0:
    raise ValueError(f"Satır {idx}: yol uzunluğu negatif")
   if numbers["frame"]<previous_frame:
    raise ValueError(f"Satır {idx}: kare sayacı geriye atladı (tek oturum bekleniyor)")
   previous_frame=numbers["frame"]
   rows.append(WalkRow(idx,raw["phase"],raw["verdict"],numbers))
 return rows

def assess_window(row:WalkRow)->str:
 """Independent conservative interpretation, without changing G229 verdict."""
 if row["active_stick"]<80:
  return "YETERLI_GIRDI_YOK"
 if row["gpu_root_mismatch"]>=3:
  return "GPU_KOKU_DUNYADAN_AYRILIYOR"
 if row["b14_path"]<0.001:
  return "B14_HAREKET_URETMEMIS"
 if row["collision_reject"]>=80 and row["resolved_path"]<.1:
  return "C1L1_CARPISMA_HAREKETI_KESIYOR"
 if row["resolved_path"]>=.5:
  return "GERCEK_DUNYA_HAREKETI_VAR"
 return "KESIN_DEGIL"

def summary(rows:list[WalkRow])->str:
 boot=[r for r in rows if r.phase=="BOOT"]
 windows=[r for r in rows if r.phase=="WALK120"]
 lines=[
  "G279 PS VITA YÜRÜYÜŞ ANALİZİ (verilen dosya; cihaz kaynağı ayrıca doğrulanmalı)",
  f"Başlangıç görüntü kareleri: {len(boot)}/3; 120-karelik yerde yürüyüş pencereleri: {len(windows)}"
 ]
 if boot:
  last=boot[-1]
  lines.append(
   f"Son BOOT dünya XYZ=({last['world_x']:.4f},{last['world_y']:.4f},{last['world_z']:.4f}), "
   f"GPU kökü=({last['gpu_x']:.4f},{last['gpu_y']:.4f},{last['gpu_z']:.4f}), "
   f"özgün G66C yakın zemin={'EVET' if last['has_native_floor'] else 'HAYIR'}"
  )
 if not windows:
  lines.append("Hüküm: Yeterli ardışık yerde yürüyüş kaydı yok; karakterin düzeldiği sonucuna varılamaz.")
  return "\n".join(lines)
 verdicts=Counter(x.verdict for x in windows)
 assessments=Counter(assess_window(x) for x in windows)
 lines.append("G229 motor tanıları: "+", ".join(f"{k}={v}" for k,v in sorted(verdicts.items())))
 lines.append("Bağımsız ölçüm yorumu: "+", ".join(f"{k}={v}" for k,v in sorted(assessments.items())))
 for row in windows[:12]:
  lines.append(
   f"Kare {row['frame']}: aktif joystick={row['active_stick']}/120, "
   f"B14 yol={row['b14_path']:.3f}, C1L1 çözülmüş yol={row['resolved_path']:.3f}, "
   f"çarpışma reddi={row['collision_reject']}, GPU hata karesi={row['gpu_root_mismatch']}, "
   f"dünya Δ=({row['world_dx']:.3f},{row['world_dy']:.3f}), "
   f"kamera Δ=({row['camera_dx']:.3f},{row['camera_dy']:.3f}), "
   f"tanı={assess_window(row)}"
  )
 if len(windows)>12:
  lines.append(f"Diğer {len(windows)-12} pencere özetlenmedi; dosyada korunuyor.")
 lines.append(
  "UYARI: Bu sonuç özgün Gameloft iOS fizik/kamera semantiğini veya "
  "gerçek Vita cihaz kaynağını tek başına kanıtlamaz. "
  "G279 oyunu düzeltmez, hareket sorununun hangi katmanda çıktığını daraltır."
 )
 return "\n".join(lines)

def main()->None:
 p=argparse.ArgumentParser(description="Gerçek Vita G279 CSV dosyasının güvenli çevrimdışı analizi")
 p.add_argument("csv",type=Path)
 a=p.parse_args()
 try:
  print(summary(parse_csv(a.csv)))
 except (ValueError,OSError,csv.Error) as e:
  p.exit(2,f"G279 GEÇERSİZ KAYIT: {e}\n")

if __name__=="__main__":
 main()
