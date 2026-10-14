#!/usr/bin/env python3
"""Expand B14 world travel/flight to actual ORIGINAL C1L1 C1WC source coordinates.
Not a change to old B14 fallback: G8 native GPU pipeline only and applied
AFTER G7 original 2010 C1L1 source collision physics patch.
Bounds from ORIGINAL 1908-triangle BDAE source CI 38581897365:
 x [-271.42,274.37], y [-298.87,192.99], z [-3.75,33.925].
Leave margin INSIDE source collision scene. Flight over rooftops ~36 units.
No guessed collision surfaces, HUD, or synthetic city content.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/"work/src/b14_world.c"
s=p.read_text()
old="w->x=cl(w->x+vx*velocity*dt,-20,20);w->y=cl(w->y+vy*velocity*dt,-20,20);"
new="""/* G8 TRUE ORIGINAL 2010 C1L1 map coverage: source C1WC BDAE extents,
     not B14's independent tiny +/-20 demo arena. No fabricated wall. */
  w->x=cl(w->x+vx*velocity*dt,-270.f,273.f);
  w->y=cl(w->y+vy*velocity*dt,-297.f,191.f);"""
if s.count(old)!=1:raise RuntimeError("G8 original B14 movement limits drift")
s=s.replace(old,new)
old="if(w->flying)w->target_z=cl(w->target_z+vertical*1.6f*dt,.35f,3.2f);"
new="""if(w->flying)
     w->target_z=cl(w->target_z+vertical*1.6f*dt,.35f,36.f); /* 33.925 original rooftop source max */
  """
if s.count(old)!=1:raise RuntimeError("G8 original B14 flight ceiling drift")
s=s.replace(old,new)
p.write_text(s)
print("PASS G8 native C1L1 source geometry world travel x[-270,273] y[-297,191] flight z<=36; G7 original CPU collision remains active")
