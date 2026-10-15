#!/usr/bin/env python3
"""Physical WarMachine G10 photo showed MELEE / SQUARE, not REPULSOR.
Old suit switch preserved B16 last weapon mode; WM inherited MELEE and
R did not emit repulsor. Reset only on real suit change, not each frame.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[2];p=root/'work/src/main.c'
s=p.read_text()
def rep(a,b):
 global s
 n=s.count(a)
 if n!=1:raise RuntimeError('G11 native WM suit mode source drift '+str(n)+' '+a[:110])
 s=s.replace(a,b)
rep('''if(key==SDLK_x||key==SDLK_SPACE){idx=(idx+1)%5;load(idx);world.head_height=b15_suit_head(&model);}''',
'''if(key==SDLK_x||key==SDLK_SPACE){
   idx=(idx+1)%5;
   if(!load(idx))running=0;
   combat.mode=B16_REPULSOR;combat.combo_step=0; /* real newly selected suit */
   world.head_height=b15_suit_head(&model);
 }''')
rep('''                    idx=(idx+1)%5;
                    if(!load(idx))running=0;
                    world.head_height=b15_suit_head(&model);''',
'''                    idx=(idx+1)%5;
                    if(!load(idx))running=0;
                    /* Actual G10 Vita WM screenshot showed MELEE SQUARE;
                       suit switching inherited prior armor weapon selection. */
                    combat.mode=B16_REPULSOR;combat.combo_step=0;
                    world.head_height=b15_suit_head(&model);''')
p.write_text(s)
assert s.count('combat.mode=B16_REPULSOR;combat.combo_step=0;')==2
assert s.count('b16_combat_mode(&combat,')==2
print('PASS G11 WM MELEE HUD root fix: suit selectors reset REPULSOR; Dpad cycles weapons normally. NO VPK')
