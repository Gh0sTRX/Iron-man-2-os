#!/usr/bin/env python3
"""Compile-test the actual canonical main fire block, without SDL/Vita devices."""
import re
import sys
from pathlib import Path
source=Path(sys.argv[1]).read_text()
pattern=r'        if\(trigger\b.*?(?=\n#ifdef B24_GPU_ENGINE\n        /\* B14 has already computed)'
blocks=re.findall(pattern,source,re.S)
if len(blocks)!=1:raise SystemExit('Expected one canonical accepted-fire block')
Path(sys.argv[2]).write_text(blocks[0]+'\n')
