#!/usr/bin/env python3
"""Inspect original B24 right/left repulsor aim mask and chest Unibeam.
Read-only; no VPK. Avoid patching unknown bone animation logic.
"""
from pathlib import Path
for path,start,end in [
 ("work/src/b16_action.c",31,95),
 ("work/src/main.c",352,385),
 ("work/src/renderer.c",440,490)]:
 p=Path(path);s=p.read_text().splitlines()
 print("=== ORIGINAL B24",p,"===")
 for i in range(start-1,min(end,len(s))):
  print(f"{i+1:4d} {s[i]}")
