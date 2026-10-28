#!/usr/bin/env python3
"""Compile the actual main contact query with its source collision authority."""
from pathlib import Path
import sys
source=Path(sys.argv[1]).read_text()
start='          float g87_source_floor=0.f;'
end='          g84_input.transition=b24_g87_transition_tick('
if source.count(start)!=1 or source.count(end)!=1:raise SystemExit('Contact block is not unique')
a=source.index(start);b=source.index(end,a)
Path(sys.argv[2]).write_text(source[a:b])
