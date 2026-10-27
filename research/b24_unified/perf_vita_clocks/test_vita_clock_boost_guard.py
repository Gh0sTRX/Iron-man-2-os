#!/usr/bin/env python3
"""Source guard: Vita max-clock boost in the single B24 GPU owner.

Host-only static check. This proves the clock calls exist, are Vita-only and
run before vitaGL starts. It does NOT prove any FPS gain on a physical Vita.
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
src = (root / "b24_gpu_owner_vitagl.c").read_text()

# 1. All four clocks, with the standard homebrew maximums.
expected = {
    "scePowerSetArmClockFrequency": 444,
    "scePowerSetBusClockFrequency": 222,
    "scePowerSetGpuClockFrequency": 222,
    "scePowerSetGpuXbarClockFrequency": 166,
}
for fn, mhz in expected.items():
    assert re.search(rf"{fn}\(\s*{mhz}\s*\)", src), f"missing {fn}({mhz})"

# 2. Header and calls are Vita-only so host/mock builds stay unchanged.
inc = src.index("#include <psp2/power.h>")
assert src[:inc].rstrip().endswith("#ifdef __vita__"), "power.h include not guarded"
helper = src.index("static void b24_gpu_owner_apply_max_clocks")
body = src[helper:src.index("int b24_gpu_owner_init")]
assert "#ifdef __vita__" in body and "#endif" in body, "clock calls not guarded"
assert "psp2/power.h" not in src.replace("#include <psp2/power.h>", ""), "stray include"

# 3. The boost runs inside init, before vglInit.
init = src[src.index("int b24_gpu_owner_init"):]
boost = init.index("b24_gpu_owner_apply_max_clocks();")
vgl = init.index("(void)vglInit(0x1000000)")
assert boost < vgl, "clocks must be raised before vglInit"

# 4. Existing CI contract strings stay intact.
assert "(void)vglInit(0x1000000)" in src
assert "if(!vglInit(" not in src
assert "vglSwapBuffers(GL_FALSE)" in src

print("PASS Vita max-clock boost source guard (host-static, no Vita FPS claim)")
sys.exit(0)
