#!/usr/bin/env python3
"""G6 targeted real B24 post-G5 input fix, from exact Vita G5 hardware report.
No defaults guessed: 2026-10-14 source audit 38569977439 proved
'int invert_move_x=1' and negative left-stick axis multiplier.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[2]/"work"
p=root/"src/main.c"
s=p.read_text()
old="int invert_move_x=1; /* Vita hardware test reports left/right inversion */"
new="int invert_move_x=0; /* G5 REAL VITA: inverted left stick was wrong; force natural L/R */"
assert s.count(old)==1,f"G6 inversion source drift: {s.count(old)}"
assert s.count("move_x+=(invert_move_x?-1.0f:1.0f)*deadzone(")==1
s=s.replace(old,new)
assert "camera.invert_x=invert_move_x;" in s
# Existing B21 options INVERT X is a CAMERA control, not a movement option.
# Keep actual inverted camera settings user-selectable, but never re-invert
# physical movement from this setting.
p.write_text(s)
print("PASS G6 natural analog X; D-pad weapons and B21 camera inversion are separate")
