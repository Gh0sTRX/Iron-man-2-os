#!/usr/bin/env python3
"""Read-only B24 original-armor struct/CPU renderer audit for GPU migration.
Run only after main B17/B24 sources are reconstructed. No game assets leaked.
"""
from pathlib import Path
import re
root=Path("work/src")
tokens=("IM2Model","IM2Camera","IM2Face","IM2Vertex",
        "im2_render","im2_draw","im2_load","b14_pose_tick",
        "IM2Texture","B13Clip","B13Motion")
for f in sorted(root.glob("*.[ch]")):
 text=f.read_text(errors="replace")
 if not any(x in text for x in tokens):continue
 lines=text.splitlines()
 print("\n=== SOURCE",f.name,"lines",len(lines),"===")
 hits=[i for i,line in enumerate(lines) if any(x in line for x in tokens)]
 captured=set()
 for hit in hits[:35]:
  for j in range(max(0,hit-2),min(len(lines),hit+5)):
   if j not in captured:
    print(f"{j+1:4d} {lines[j][:180]}")
    captured.add(j)
for name in ("main.c","renderer.c"):
 f=root/name
 if not f.is_file():continue
 lines=f.read_text(errors="replace").splitlines()
 for i,line in enumerate(lines):
  if "b14_pose_tick" in line or ("im2_render(" in line and name=="renderer.c"):
   print("\n=== CALL SITE",name,i+1,"===")
   for j in range(max(0,i-4),min(len(lines),i+20)):
    print(f"{j+1:4d} {lines[j][:200]}")
print("\nPASS read-only B24 original armor/animation render interface audit; NO executable, NO VPK")
