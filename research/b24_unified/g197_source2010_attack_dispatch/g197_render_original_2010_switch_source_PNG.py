#!/usr/bin/env python3
"""G197 visual proof only: exact ORIGINAL 2010 MainCharacter::DoAttack()
ARM jump-table 26 entries from authenticated G196B source; no invented
weapon names, Vita input mappings, VPK or interactive HTML.
"""
import argparse,json
from pathlib import Path

def main(src:Path,out:Path):
 d=json.loads(src.read_text())
 assert d["NO_VPK"]
 assert d["source_2010_original_native_dispatch_cmp_r5_25_jump_table_proven"]
 entries=d["source_original_2010_attack_id_switch_0_to_25"]
 assert len(entries)==26
 defaults=sum(int(e["original_target_VM"],16)==0xf6598 for e in entries.values())
 assert defaults==19
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 from matplotlib.patches import Rectangle
 fig,ax=plt.subplots(figsize=(15,5),dpi=140)
 ax.set_xlim(0,13);ax.set_ylim(-.3,3)
 ax.set_axis_off()
 for i in range(26):
  col=i%13;row=1 if i<13 else 0
  a=entries[str(i)]
  target=int(a["original_target_VM"],16)
  nondefault=target!=0xf6598
  ax.add_patch(Rectangle((col+.04,row+.30),.91,.79,
                         linewidth=1,fill=nondefault))
  ax.text(col+.49,row+.91,str(i),fontsize=15,ha="center",va="center",
          weight="bold" if nondefault else "normal")
  ax.text(col+.49,row+.60,f"0x{target:05X}",fontsize=9,
          ha="center",va="center")
 fig.suptitle("Iron Man 2 iOS (2010) — original DoAttack 26-entry ARM selector",
              fontsize=17)
 ax.text(6.5,2.57,"Filled: native branch different from common fallback | Unfilled: 0xF6598",
         fontsize=11,ha="center")
 ax.text(6.5,-.07,"SOURCE-only ARM jump table: 7 specialized entries, 19 common | Attack IDs are not proved weapon names",
         fontsize=11,ha="center")
 out.parent.mkdir(parents=True,exist_ok=True)
 fig.savefig(out,bbox_inches="tight")
 plt.close(fig)
 print("G197 original native switch source PNG",out,"bytes",out.stat().st_size,
       "native nondefault",26-defaults,"common",defaults)
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--source",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 p=a.parse_args()
 main(p.source,p.out)
