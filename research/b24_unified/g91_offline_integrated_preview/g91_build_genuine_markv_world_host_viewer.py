#!/usr/bin/env python3
"""G91: VPK-free host WebGL: genuine 2010 G58 BRES/PVR world + genuine
Mark V B13 skinned source IM2V pose and topology + immobile DEBUG dummy.
G83 route names exported by actual C source; light is documented HOST
shader, NOT original iOS shader. NO claimed real hitframes/WeaponDB damage,
PS Vita B14 physics, original input protocol or in-game screenshot.
"""
import argparse,base64,hashlib,json,struct,sys,zipfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_hover_fire_authentic_pose_preview import source_meshes
def rep(s,a,b):
 if s.count(a)!=1:raise ValueError('G91 exact owner G58 source viewer anchor changed '+str(s.count(a))+' '+a[:70])
 return s.replace(a,b,1)
def assemble(src,ipa,anims,routes,out,report):
 body=src.read_text()
 if len(body)<4500000 or 'g58Ambient' not in body or 'originalPVRs' not in body:
  raise ValueError('G91 needs original already-authored G58 source world and source lighting')
 router=json.loads(routes.read_text())
 if not router['G83_selector_called_from_original_C']:raise ValueError('G83 C router missing')
 with zipfile.ZipFile(ipa) as z:
  packed=z.read('Payload/IronMan2.app/models')
 original=get_exact(packed,decode(packed,'.bdae'),'suitcase.bdae')
 matching=[m for m in source_meshes(original) if len(m['positions'])==629]
 if len(matching)!=1:raise ValueError('genuine source B13 MarkV weighted geometry missing')
 triangles=np.asarray(matching[0]['faces'],dtype=np.int64).reshape(-1,3)
 if len(triangles)<100 or triangles.min()<0 or triangles.max()>=629:
  raise ValueError('2010 original Mark V face topology invalid')
 names={r['markv'] for r in router['source_routes']}
 names.update(['suitcase_ironman_ground_combo_1','suitcase_ironman_ground_combo_2',
  'suitcase_ironman_ground_combo_3','suitcase_ironman_aim_ground_idle_att'])
 source_clips={}
 for name in sorted(names):
  raw=(anims/(name+'.im2v')).read_bytes()
  if len(raw)<20:raise ValueError('original IM2V not found')
  magic,nv,frames,fps,ms=struct.unpack_from('<4sIIII',raw)
  if magic!=b'IM2V' or nv!=629 or fps!=20 or ms>120000 or not(1<=frames<=4000):
   raise ValueError('G85 original animation header corrupt '+name)
  if len(raw)!=20+frames*629*12 or frames!=((ms-1)//50+2 if ms else 1):
   raise ValueError('G85 original MarkV sample count invalid '+name)
  if not np.isfinite(np.frombuffer(raw,dtype='<f4',offset=20)).all():
   raise ValueError('nonfinite owner pose '+name)
  source_clips[name]=base64.b64encode(raw).decode('ascii')
 if len(source_clips)<14:raise ValueError('too few REAL original G83 clip streams')
 payload=json.dumps({'routes':router['source_routes'],'streams':source_clips,
    'source_triangles_u16':base64.b64encode(np.asarray(triangles,dtype='<u2').tobytes()).decode('ascii')},
    separators=(',',':')).replace('</','<\\/')
 controls='''<div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:11px;background:#15273a">
<strong>G91 • Özgün Mark V + gerçek BRES/PVR + hareket + antrenman hedefi</strong>
<button id="g91near">Oyuncuya yaklaş</button><button id="g91ground">Zemin</button>
<button id="g91hover">Hover (H)</button><button id="g91flight">Uçuş (F)</button>
<button id="g91rush">Rush (Shift)</button><button id="g91aim">Nişan (L)</button>
<button id="g91melee">Kombo (J)</button><button id="g91shot">Repulsor poz (K)</button>
<span id="g91status" style="font:12px monospace;flex:1"></span>
<div style="width:100%;font-size:12px;color:#c9dcea">WASD hareket | Fareyle kamera | Kaynak 2010 BRES 3B harita / PVR dokuları / G85 629 köşe ve GERÇEK üçgenler / G83 C animasyon seçimleri. G58 ışık ayarları tanısaldır, özgün iOS shader değildir. Sahnedeki turkuaz kutu kullanıcı testi için sabit ve ölümsüz dummy'dir. J isabet geri bildirimi yalnız tanısal mesafe, kaynak oyunun gerçek hasar/vuruş karesi DEĞİL. WASD hız ve yüksekliği B14 Vita fiziği değildir. NO VPK.</div>
</div>'''
 body=rep(body,'<div class="canvas"><canvas id="game"',controls+'<div class="canvas"><canvas id="game"')
 body=rep(body,'<svg id="markers"></svg>',
   '<svg id="markers"></svg><canvas id="g91overlay" style="pointer-events:none;background:transparent;z-index:5"></canvas>')
 body=rep(body,'<script>\n"use strict";',
   '<script type="application/json" id="g91data">'+payload+'</script><script>\n"use strict";')
 overlay=r"""
/* Genuine B13 weighted original geometry/clip; host controls/projection
 * and practice dummy ARE DIAGNOSTICS, not original iOS game logic. */
const a91=JSON.parse(document.getElementById('g91data').textContent);
const cv91=document.getElementById('g91overlay'),gl91=cv91.getContext('webgl2',{alpha:true,depth:true});
const state91={x:d.mc_xyz[0],y:d.mc_xyz[1],z:d.mc_xyz[2],mode:0,aim:0,
 held:new Set(),attack:'',attackTime:0,combo:0,flash:0,notice:'',age:0};
const dummy91=[d.mc_xyz[0],d.mc_xyz[1]+6,d.mc_xyz[2]+1];
const decode91=s=>Uint8Array.from(atob(s),v=>v.charCodeAt(0));
const streams91={};
for(const [name,b64] of Object.entries(a91.streams)){
 const raw=decode91(b64),view=new DataView(raw.buffer);
 const nv=view.getUint32(4,true),frames=view.getUint32(8,true),ms=view.getUint32(16,true);
 if(nv!==629||raw.byteLength!==20+frames*629*12)throw Error('source stream mismatch');
 streams91[name]={poses:new Float32Array(raw.buffer,20),frames,ms};
}
const index91=new Uint16Array(decode91(a91.source_triangles_u16).buffer);
let shader91=null,vert91=null,attrib91=-1,iu91=null,vu91=null,pu91=null,su91=null,cu91=null;
function g91sh(type,src){
 const shader=gl91.createShader(type);gl91.shaderSource(shader,src);gl91.compileShader(shader);
 if(!gl91.getShaderParameter(shader,gl91.COMPILE_STATUS))throw Error(gl91.getShaderInfoLog(shader));
 return shader;
}
if(gl91){
 shader91=gl91.createProgram();
 gl91.attachShader(shader91,g91sh(gl91.VERTEX_SHADER,
 '#version 300 es\nin vec3 xyz;uniform mat4 p,v;uniform vec3 shift;uniform float scale;out vec3 world;\nvoid main(){world=xyz*scale+shift;gl_Position=p*v*vec4(world,1.);}'));
 gl91.attachShader(shader91,g91sh(gl91.FRAGMENT_SHADER,
 '#version 300 es\nprecision highp float;in vec3 world;uniform vec4 color;out vec4 rgba;\nvoid main(){vec3 n=normalize(cross(dFdx(world),dFdy(world)));float light=0.3+0.7*abs(dot(n,normalize(vec3(.4,.2,.89))));rgba=vec4(color.rgb*light,color.a);}'));
 gl91.bindAttribLocation(shader91,0,'xyz');gl91.linkProgram(shader91);
 if(!gl91.getProgramParameter(shader91,gl91.LINK_STATUS))throw Error('G91 WebGL overlay program');
 attrib91=gl91.getAttribLocation(shader91,'xyz');
 iu91=gl91.getUniformLocation(shader91,'shift');
 vu91=gl91.getUniformLocation(shader91,'v');
 pu91=gl91.getUniformLocation(shader91,'p');
 su91=gl91.getUniformLocation(shader91,'scale');
 cu91=gl91.getUniformLocation(shader91,'color');
 vert91=gl91.createBuffer();const ib=gl91.createBuffer();
 gl91.bindBuffer(gl91.ELEMENT_ARRAY_BUFFER,ib);
 gl91.bufferData(gl91.ELEMENT_ARRAY_BUFFER,index91,gl91.STATIC_DRAW);
 gl91.enable(gl91.DEPTH_TEST);gl91.disable(gl91.CULL_FACE);
}
const sampled91=new Float32Array(629*3);
const first91=streams91['suitcase_ironman_ground_combo_1']||Object.values(streams91)[0];
let lo91=[1e8,1e8,1e8],hi91=[-1e8,-1e8,-1e8];
for(let i=0;i<629;i++)for(let k=0;k<3;k++){
 const v=first91.poses[3*i+k];lo91[k]=Math.min(lo91[k],v);hi91[k]=Math.max(hi91[k],v);
}
const scale91=2.1/Math.max(0.001,hi91[2]-lo91[2]);
const origin91=[-(lo91[0]+hi91[0])/2,-(lo91[1]+hi91[1])/2,-lo91[2]];
function attack91(name){
 if(streams91[name]){state91.attack=name;state91.attackTime=performance.now();state91.age=0}
}
function melee91(){
 state91.combo=(state91.combo%3)+1;
 attack91('suitcase_ironman_ground_combo_'+state91.combo);
 let dist=Math.hypot(state91.x-dummy91[0],state91.y-dummy91[1]);
 state91.notice=dist<2.5?'Yakınlık testi: HEDEF MENZİLDE, gerçek hasar YOK':'Yakınlık testi: ISKA';
 if(dist<2.5)state91.flash=performance.now()+190;
}
document.getElementById('g91near').onclick=()=>{center=[state91.x,state91.y,state91.z+1];dist=15;el=.21;render()};
document.getElementById('g91ground').onclick=()=>state91.mode=0;
document.getElementById('g91hover').onclick=()=>state91.mode=1;
document.getElementById('g91flight').onclick=()=>state91.mode=2;
document.getElementById('g91rush').onclick=()=>state91.mode=3;
document.getElementById('g91aim').onclick=()=>state91.aim=1-state91.aim;
document.getElementById('g91melee').onclick=melee91;
document.getElementById('g91shot').onclick=()=>attack91('suitcase_ironman_aim_ground_idle_att');
document.addEventListener('keydown',event=>{
 const k=event.key.toLowerCase();
 if(!['w','a','s','d','h','f','l','j','k','shift'].includes(k)||event.target.matches('input,select,textarea'))return;
 event.preventDefault();if(event.repeat&&!['w','a','s','d','shift'].includes(k))return;
 if(k==='j')melee91();else if(k==='k')attack91('suitcase_ironman_aim_ground_idle_att');
 else if(k==='h')state91.mode=state91.mode===1?0:1;
 else if(k==='f')state91.mode=state91.mode===2?0:2;
 else if(k==='l')state91.aim=1-state91.aim;
 else if(k==='shift')state91.mode=3;
 else state91.held.add(k);
});
document.addEventListener('keyup',event=>{
 const k=event.key.toLowerCase();state91.held.delete(k);
 if(k==='shift'&&state91.mode===3)state91.mode=2;
});
function clip91(now){
 if(state91.attack){
  const c=streams91[state91.attack];
  if(c&&now-state91.attackTime<c.ms)return state91.attack;
  state91.attack='';
 }
 const x=Number(state91.held.has('d'))-Number(state91.held.has('a'));
 const y=Number(state91.held.has('w'))-Number(state91.held.has('s'));
 const direction=Math.abs(x)>Math.abs(y)?(x<0?3:4):(y<0?2:1);
 const row=a91.routes.find(q=>q.mode===state91.mode&&q.aim===state91.aim&&q.direction===direction);
 return row?row.markv:'';
}
let lastClip91='',start91=0;
function actor91(view,projection,width,height){
 if(!gl91)return;
 const w=Math.max(2,Math.floor(width*Math.min(devicePixelRatio||1,2)));
 const h=Math.max(2,Math.floor(height*Math.min(devicePixelRatio||1,2)));
 if(cv91.width!==w||cv91.height!==h){cv91.width=w;cv91.height=h;gl91.viewport(0,0,w,h)}
 gl91.clearColor(0,0,0,0);gl91.clear(gl91.COLOR_BUFFER_BIT|gl91.DEPTH_BUFFER_BIT);
 gl91.useProgram(shader91);gl91.uniformMatrix4fv(vu91,false,view);gl91.uniformMatrix4fv(pu91,false,projection);
 gl91.bindBuffer(gl91.ARRAY_BUFFER,vert91);
 gl91.enableVertexAttribArray(attrib91);gl91.vertexAttribPointer(attrib91,3,gl91.FLOAT,false,0,0);
 const now=performance.now(),key=clip91(now),anim=streams91[key];
 if(key!==lastClip91){lastClip91=key;start91=now}
 if(anim){
  let tick=key===state91.attack?Math.min(now-state91.attackTime,anim.ms):
    anim.ms>0?(now-start91)%anim.ms:0;
  const frame=anim.frames>1?Math.min(Math.floor(tick/50),anim.frames-2):0;
  const left=frame*50,right=frame===anim.frames-2?anim.ms:left+50;
  const mix=anim.frames>1&&right>left?(tick-left)/(right-left):0;
  for(let i=0;i<sampled91.length;i++){
   let a=anim.poses[frame*sampled91.length+i];
   let b=anim.frames>1?anim.poses[(frame+1)*sampled91.length+i]:a;
   sampled91[i]=a+(b-a)*mix;
  }
  gl91.bufferData(gl91.ARRAY_BUFFER,sampled91,gl91.DYNAMIC_DRAW);
  gl91.uniform3fv(iu91,[state91.x+origin91[0]*scale91,
    state91.y+origin91[1]*scale91,state91.z+origin91[2]*scale91]);
  gl91.uniform1f(su91,scale91);gl91.uniform4fv(cu91,[.85,.18,.14,1]);
  gl91.drawElements(gl91.TRIANGLES,index91.length,gl91.UNSIGNED_SHORT,0);
 }
 // One fixed practice cube; no original gameplay AI, no authored hit window.
 const r=.46,lines=new Float32Array([
 -r,-r,-r,r,-r,-r,r,-r,-r,r,r,-r,r,r,-r,-r,r,-r,-r,r,-r,-r,-r,-r,
 -r,-r,r,r,-r,r,r,-r,r,r,r,r,r,r,r,-r,r,r,-r,r,r,-r,-r,r,
 -r,-r,-r,-r,-r,r,r,-r,-r,r,-r,r,r,r,-r,r,r,r,-r,r,-r,-r,r,r]);
 gl91.bindBuffer(gl91.ARRAY_BUFFER,vert91);
 gl91.bufferData(gl91.ARRAY_BUFFER,lines,gl91.DYNAMIC_DRAW);
 gl91.uniform3fv(iu91,dummy91);gl91.uniform1f(su91,1);
 gl91.uniform4fv(cu91,now<state91.flash?[1,.8,.17,1]:[.17,1,.93,1]);
 gl91.drawArrays(gl91.LINES,0,lines.length/3);
 document.getElementById('g91status').textContent=
 ['GROUND','HOVER','FLIGHT','RUSH'][state91.mode]+' | Original IM2V: '+key+' | '+state91.notice;
}
let t91=0;
function tick91(t){
 if(t-t91>=49){
  const dt=Math.min(.1,t91?(t-t91)/1000:0);t91=t;
  const x=Number(state91.held.has('d'))-Number(state91.held.has('a'));
  const y=Number(state91.held.has('w'))-Number(state91.held.has('s'));
  const n=Math.hypot(x,y);
  if(n){state91.x+=x/n*dt*2.8;state91.y+=y/n*dt*2.8}
  render();
 }
 requestAnimationFrame(tick91);
}
requestAnimationFrame(tick91);
"""
 body=rep(body,'function render(){if(!gl||!pr)return;',overlay+'\nfunction render(){if(!gl||!pr)return;')
 body=rep(body,'markers(v,p,w,h)}','markers(v,p,w,h);actor91(v,p,w,h)}')
 if body.count('id="g91overlay"')!=1 or body.count('actor91(v,p,w,h)')!=1:
  raise ValueError('G91 original source host view modified inconsistently')
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(body)
 info={'original_owner_C1L1_source_BRES_triangles':22441,
   'original_owner_C1L1_parented_meshes':296,
   'original_owner_PVR_diffuse_atlases':24,
   'MarkV_authentic_2010_weighted_skin_vertices':629,
   'MarkV_authentic_original_source_triangles':len(triangles),
   'MarkV_original_2010_20hz_clips_renderable':len(source_clips),
   'real_G83_C_router_directly_used':True,
   'real_G58_host_lighting_shader_used':True,
   'native_2010_real_iOS_shader_claimed':False,
   'browser_B14_physics_live':False,
   'practice_dummy_static_infinite_health':True,
   '2010_attack_hitframes_and_damage_known':False,
   'VPK_generated':False,'sha256':hashlib.sha256(body.encode()).hexdigest()}
 report.parent.mkdir(parents=True,exist_ok=True)
 report.write_text(json.dumps(info,indent=2,ensure_ascii=False)+'\n')
 print('G91 AUTHENTIC original BRES+PVR 2010 world + MarkV rig',len(triangles),
  'source faces',len(source_clips),'2010 motion clips source C G83 maps; diagnostic dummy & host sun. NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ('g58-html','ipa','anims','routes','out','report'):
  p.add_argument('--'+n,required=True,type=Path)
 a=p.parse_args()
 assemble(a.g58_html,a.ipa,a.anims,a.routes,a.out,a.report)
