#!/usr/bin/env python3
"""G279 offline parser regression, adversarial malformed columns & samples.
Host-generated fixture is never represented as physical PS Vita capture.
"""
from pathlib import Path
import csv
import importlib.util
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("g279_analyzer",HERE/"g279_analyze_Vita_walk_trace_TR.py")
a=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=a
spec.loader.exec_module(a)

def specimen(phase,frame,verdict):
 r={k:"0" for k in a.COLUMNS}
 r.update(phase=phase,frame=str(frame),ms=str(frame*17),verdict=verdict)
 if phase=="WALK120":
  r.update(active_stick="120",b14_path="10.0702",resolved_path="10.0702",
           world_dy="10.0702",camera_dy="10.0691",
           has_native_floor="1",native_floor_z="2.82955")
 return r

def make(path,rows,header=None):
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=header or a.COLUMNS,extrasaction="ignore")
  w.writeheader()
  for row in rows:w.writerow(row)

with tempfile.TemporaryDirectory(prefix="g279_vita_csv_parser_host_") as t:
 r=Path(t)/"walk.csv"
 boot=specimen("BOOT",1,"BOOT_SAMPLE")
 moving=specimen("WALK120",120,"WORLD_AND_CAMERA_POSITIONS_TRANSLATE_TOGETHER")
 make(r,[boot,moving])
 loaded=a.parse_csv(r)
 assert len(loaded)==2
 assert a.assess_window(loaded[-1])=="DUNYA_KOKU_NET_YER_DEGISTIRIYOR"
 report=a.summary(loaded)
 assert "10.070" in report and "kamera" in report
 assert "net XY=10.070" in report
 assert "özgün G66C pencere sonu zemin=EVET" in report
 assert f"zemin_Zup={float(moving['native_floor_z']):.4f}" in report
 assert "cihaz kaynağı ayrıca doğrulanmalı" in report
 # Real G229 may accumulate 10m of accepted back-and-forth path but end
 # at the same XY. This MUST NOT be called net world displacement.
 roundtrip=dict(moving)
 roundtrip["frame"]="240"
 roundtrip["world_dx"]="0.0";roundtrip["world_dy"]="0.0"
 roundtrip["camera_dx"]="0.0";roundtrip["camera_dy"]="0.0"
 roundtrip["verdict"]="WORLD_MOVED_BUT_NET_SMALL_OR_REVERSED"
 make(r,[boot,roundtrip])
 assert a.assess_window(a.parse_csv(r)[-1])=="YOL_VAR_NET_YER_DEGISTIRME_KUCUK_VEYA_TERS"
 assert "net XY=0.000" in a.summary(a.parse_csv(r))
 # Match G229 source-only net 0.15 threshold, not a recovered iOS constant.
 near=dict(roundtrip);near["world_dx"]="0.14"
 make(r,[boot,near])
 assert a.assess_window(a.parse_csv(r)[-1])=="YOL_VAR_NET_YER_DEGISTIRME_KUCUK_VEYA_TERS"
 near["world_dx"]="0.16"
 make(r,[boot,near])
 assert a.assess_window(a.parse_csv(r)[-1])=="DUNYA_KOKU_NET_YER_DEGISTIRIYOR"
 blocked=dict(moving)
 blocked["frame"]="240";blocked["b14_path"]="10.0";blocked["resolved_path"]="0.0"
 blocked["collision_reject"]="120"
 blocked["has_native_floor"]="0";blocked["native_floor_z"]="0"
 blocked["verdict"]="COLLISION_REJECTS_GROUND_MOTION"
 make(r,[boot,blocked])
 assert a.assess_window(a.parse_csv(r)[-1])=="C1L1_CARPISMA_HAREKETI_KESIYOR"
 assert "özgün G66C pencere sonu zemin=HAYIR, zemin_Zup=YOK" in a.summary(a.parse_csv(r))
 noinput=dict(blocked);noinput["active_stick"]="0"
 make(r,[boot,noinput])
 assert a.assess_window(a.parse_csv(r)[-1])=="YETERLI_GIRDI_YOK"
 def fail(rows,header=None):
  make(r,rows,header)
  try:a.parse_csv(r)
  except ValueError:return
  raise AssertionError("Malformed Vita capture unexpectedly accepted")
 fail([boot],a.COLUMNS[:-1])
 poison=dict(boot);poison["world_x"]="nan";fail([poison])
 poison=dict(moving);poison["active_stick"]="999";fail([boot,poison])
 poison=dict(moving);poison["verdict"]="MALICIOUS,COMMA";fail([boot,poison])
 poison=dict(moving);poison["world_x"]="inf";fail([boot,poison])
 poison=dict(moving);poison["native_floor_z"]="nan";fail([boot,poison])
 poison=dict(moving);poison["frame"]="0";fail([boot,poison])
 poison=dict(moving);poison["resolved_path"]="-1";fail([boot,poison])
 poison=dict(moving);poison["has_native_floor"]="2";fail([boot,poison])
 poison=dict(moving);poison["phase"]="BOOT";fail([boot,poison])
 make(r,[boot])
 assert "Yeterli ardışık yerde yürüyüş kaydı yok" in a.summary(a.parse_csv(r))
print("G279 PASS offline G229 31-column analyzer: accumulated path vs net XY displacement, roundtrip and threshold, original G66C endpoint floor, collision and malformed CSV; synthetic host only; NO Vita claim, NO VPK")
