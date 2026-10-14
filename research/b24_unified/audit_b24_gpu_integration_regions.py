#!/usr/bin/env python3
"""Source-only actual B24 main GPU handoff context; prints source without VPK."""
from pathlib import Path
p=Path("work/src/main.c")
a=p.read_text().splitlines()
for left,right in [(1,36),(90,170),(165,250),(290,353),(350,413)]:
 print("===== MAIN LINES",left,right,"=====")
 for i in range(left-1,min(right,len(a))):print(f"{i+1:4d} {a[i]}")
p=Path("work/src/renderer.h")
a=p.read_text().splitlines()
print("===== RENDERER HEADER =====")
for i,line in enumerate(a):print(f"{i+1:4d} {line}")
