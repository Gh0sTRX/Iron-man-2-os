#!/usr/bin/env python3
"""G83 prevent source route typo and invented original animations.
Assert EVERY G83 source literal exists in the 2010 IPA's independently
audited 304 player-clip B18 catalog. This does not prove gameplay semantics.
"""
from pathlib import Path
import re
base=Path(__file__).resolve().parents[2]
catalog=(base/'B18_COMPLETE_304_PLAYER_ANIMATIONS_CATALOG_TR.md').read_text()
src=(Path(__file__).resolve().parent/'b24_g83_unified_movement_aim.c').read_text()
original=set()
for n in re.findall(r'`((?:IronMan|Ironman|Warmachine)_[^`]+\.anim)`',catalog,re.I):
 stem=n[:-5].casefold()
 original.add(stem.split('_')[0]+'_'+stem)
selected=set(re.findall(r'"((?:ironman|warmachine)_(?:ironman|warmachine)_[a-z0-9_]+)"',src))
assert len(original)==304,(len(original),'expected 2010 source catalog 304')
assert len(selected)>=100,(len(selected),'few named clips')
missing=sorted(selected-original)
assert not missing,('G83 guessed animation names not in original 2010 IPA:',missing)
print('PASS G83',len(selected),'explicit animation names all verified in original 2010 IPA B18 304-source catalog; 248 IM + 56 WM. No Vita VPK')
