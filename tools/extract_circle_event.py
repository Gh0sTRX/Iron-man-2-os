#!/usr/bin/env python3
"""Test helper: compile the actual canonical Circle event, never a copied event."""
from pathlib import Path
import sys
source=Path(sys.argv[1]).read_text()
anchor='if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_B){'
assert source.count(anchor)==1
start=source.index(anchor);depth=0
for end in range(source.index('{',start),len(source)):
    depth+=(source[end]=='{')-(source[end]=='}')
    if not depth:
        Path(sys.argv[2]).write_text(source[start:end+1]+'\n')
        break
else:
    raise ValueError('Actual Circle source block is not closed')
