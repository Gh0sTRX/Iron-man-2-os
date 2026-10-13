#!/usr/bin/env python3
"""Fail the Vita build if regenerated SDL BUTTONDOWN accepts all keys as START.
This checks real work/src/main.c after apply_b24.py and apply_b24_c2_fix.py.
"""
from pathlib import Path
import re
p=Path("work/src/main.c")
s=p.read_text(encoding="utf-8")
matches=list(re.finditer(r'b24_input_latched\s*\|=\s*IM2_BT_START\s*;',s))
assert len(matches)==1, f"Expected ONE event-latch only, got {len(matches)}"
m=matches[0]
prefix=s[max(0,m.start()-200):m.start()]
assert re.search(r'if\s*\(\s*e\.cbutton\.button\s*==\s*SDL_CONTROLLER_BUTTON_START\s*\)\s*$',prefix), (
    "FATAL: unguarded START latch: any controller button would open pause again!\n"+prefix[-180:])
assert re.search(r'if\s*\(\s*e\.type\s*==\s*SDL_CONTROLLERBUTTONDOWN\s*\)',s), "No button down handler"
assert 'b24_buttons|=b24_input_latched;' in s, "event latch not consumed"
assert s.count('b24_input_latched=0;')==2, "event latch should be static init and clear per frame"
assert 'IM2_BT_SELECT' in s, "suit-cycle route lost"
print("PASS regenerated B24 SDL input: START event latch explicitly guarded; no any-button pause")
