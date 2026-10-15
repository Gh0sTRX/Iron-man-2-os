#!/usr/bin/env python3
"""G58A: reversible, source-only host daylight shader for G57 C1L1.
Uses original 296 node-linked 2010 BRES meshes and 24 original PVR atlases.
Daylight/ambient/fog are *new diagnostic host shaders*, not the original
Gameloft shader. Never rewrite source XYZ, UV, material assignments or IPA.
No Vita VPK. Native Sun001-004 properties remain un-interpreted metadata.
"""
from __future__ import annotations
import argparse,base64,io,json,re,hashlib
from pathlib import Path
import numpy as np
from PIL import Image

def replace_once(s,old,new):
    n=s.count(old)
    if n!=1:
        raise ValueError('G58 source HTML expected exactly one occurrence '
                         +str(n)+' '+repr(old[:60]))
    return s.replace(old,new)

def tag(s,name):
    m=re.search(r'<script id="'+re.escape(name)+r'"[^>]*>(.*?)</script>',s,re.S)
    if not m:raise ValueError('missing '+name)
    return m.group(1)

def build(source,out,report):
    s=source.read_text(encoding='utf-8')
    d=json.loads(tag(s,'payload'))
    tris=np.frombuffer(base64.b64decode(tag(s,'rawindices')),dtype='<u4').reshape(-1,3)
    pos=np.frombuffer(base64.b64decode(tag(s,'rawpositions')),dtype='<f4').reshape(-1,3)
    uv=np.frombuffer(base64.b64decode(tag(s,'rawuv')),dtype='<f4').reshape(-1,2)
    assert len(tris)==22919 and len(pos)==len(uv)==37946
    assert d.get('G57_native_meshes',d.get('G57_original_G55_native_source_parent_pivot_meshes'))==296
    assert len(d['originalPVRs'])==24 and len(d['suns'])==4
    assert {x['source_name'] for x in d['suns']}=={'Sun001','Sun002','Sun003','Sun004'}
    valid=np.zeros(22919,dtype=bool)
    textured=0
    for b in d['batches']:
        start=b['start']//3;end=start+b['tris']
        assert 0<=start<end<=22919
        valid[start:end]=True
        if b.get('tga') and b.get('original_uv_mesh_positive'):textured+=b['tris']
    assert valid.sum()==22441 and textured==18774
    alpha_names=[]
    for a in d['originalPVRs']:
        im=Image.open(io.BytesIO(base64.b64decode(a['base64']))).convert('RGBA')
        if int(np.asarray(im)[:,:,3].min())<255:alpha_names.append(a['name'])
    assert alpha_names==['c1l1_earth.tga']
    controls="""<div id="g58host" style="padding:12px;background:#182f40;display:flex;flex-wrap:wrap;align-items:center;gap:15px">
<label>Ortam <input type="range" id="g58Ambient" min="0" max="110" value="48"></label>
<label>Güneş <input type="range" id="g58Sun" min="0" max="150" value="82"></label>
<label>Yükseklik <input type="range" id="g58Elev" min="10" max="85" value="55"></label>
<label>Yön <input type="range" id="g58Az" min="-180" max="180" value="-40"></label>
<label>Pozlama <input type="range" id="g58Exposure" min="40" max="200" value="105"></label>
<label><input type="checkbox" id="g58Fog"> Deneysel uzaklık atmosferi</label>
<label><input type="checkbox" id="g58Alpha"> earth.tga alfa kesme deneyi</label>
<button type="button" id="g58Day">Gündüz</button>
<button type="button" id="g58Evening">Akşam</button>
<small>G58 host ışık modeli: gerçek 2010 motor shader/alpha/ışık davranışı değildir.</small>
</div>"""
    s=replace_once(s,'<div class="canvas"><canvas id="game"',controls+'<div class="canvas"><canvas id="game"')
    s=replace_once(s,'<input type="checkbox" id="shade"> Deneysel yönlü gölgeleme (özgün değil)',
                   '<input type="checkbox" id="shade" checked> G58 host yönlü ışık')
    tick=chr(96)
    shaderprefix='gl.attachShader(p,shader(gl.FRAGMENT_SHADER,'+tick+'#version 300 es'
    a=s.index(shaderprefix)
    b=s.index(tick+'));',a)+len(tick+'));')
    shaderbody="""gl.attachShader(p,shader(gl.FRAGMENT_SHADER,TICK#version 300 es
precision highp float;
in vec3 worldP;in vec2 sourceUV;
uniform sampler2D originalPVR;
uniform vec3 baseColor;uniform vec3 g58L;uniform vec3 g58Eye;
uniform float enableOriginalPVR,diagShade,g58Ambient,g58Sun,g58Exposure,g58Fog,g58Alpha;
out vec4 outColor;
void main(){
 vec4 tx=enableOriginalPVR>0.5?texture(originalPVR,sourceUV):vec4(baseColor,1.);
 if(g58Alpha>0.5&&tx.a<0.5)discard;
 vec3 N=normalize(cross(dFdx(worldP),dFdy(worldP)));
 float lambert=abs(dot(N,normalize(g58L)));
 float illumination=g58Ambient+(diagShade>0.5?g58Sun*lambert:0.);
 vec3 rgb=tx.rgb*illumination;
 rgb=vec3(1.)-exp(-rgb*g58Exposure);
 rgb=pow(max(rgb,vec3(0.)),vec3(1./2.2));
 if(g58Fog>0.5){
   float f=clamp(1.-exp(-pow(length(worldP-g58Eye)*0.00075,2.)),0.,0.65);
   rgb=mix(rgb,vec3(.62,.70,.76),f);
 }
 outColor=vec4(rgb,1.);
}TICK));""".replace('TICK',tick)
    s=s[:a]+shaderbody+s[b:]
    old='let pr=null,projU=null,viewU=null,colorU=null,shadeU=null,indexTotal=0,samplerU=null,usePVRU=null;'
    new=old+'let g58AmbU,g58SunU,g58EyeU,g58LU,g58ExpU,g58FogU,g58AlphaU;'
    s=replace_once(s,old,new)
    s=replace_once(s,'shadeU=gl.getUniformLocation(pr,"diagShade");',
       'shadeU=gl.getUniformLocation(pr,"diagShade");'+''.join(
        n+'=gl.getUniformLocation(pr,"'+k+'");' for n,k in
        [('g58AmbU','g58Ambient'),('g58SunU','g58Sun'),('g58EyeU','g58Eye'),
         ('g58LU','g58L'),('g58ExpU','g58Exposure'),('g58FogU','g58Fog'),
         ('g58AlphaU','g58Alpha')]))
    drawinit='gl.uniform1f(shadeU,shade.checked?1:0);'
    src=drawinit+"""let elev=Number(document.getElementById('g58Elev').value)*Math.PI/180;
let azSun=Number(document.getElementById('g58Az').value)*Math.PI/180;
gl.uniform3fv(g58LU,[Math.cos(elev)*Math.cos(azSun),Math.cos(elev)*Math.sin(azSun),Math.sin(elev)]);
gl.uniform3fv(g58EyeU,eye);
gl.uniform1f(g58AmbU,Number(document.getElementById('g58Ambient').value)/100);
gl.uniform1f(g58SunU,Number(document.getElementById('g58Sun').value)/100);
gl.uniform1f(g58ExpU,Number(document.getElementById('g58Exposure').value)/100);
gl.uniform1f(g58FogU,document.getElementById('g58Fog').checked?1:0);
gl.uniform1f(g58AlphaU,document.getElementById('g58Alpha').checked?1:0);"""
    s=replace_once(s,drawinit,src)
    tail="""for(const id of ['g58Ambient','g58Sun','g58Elev','g58Az','g58Exposure','g58Fog','g58Alpha']){
  document.getElementById(id).addEventListener('input',render);
}
document.getElementById('g58Day').onclick=()=>{
 let p={g58Ambient:48,g58Sun:82,g58Elev:55,g58Az:-40,g58Exposure:105};
 for(const [k,v]of Object.entries(p))document.getElementById(k).value=v;
 render();
};
document.getElementById('g58Evening').onclick=()=>{
 let p={g58Ambient:24,g58Sun:112,g58Elev:18,g58Az:-75,g58Exposure:108};
 for(const [k,v]of Object.entries(p))document.getElementById(k).value=v;
 render();
};
"""
    s=replace_once(s,'refreshList();updateCam();setFocus();',tail+'refreshList();updateCam();setFocus();')
    proof={'stage':'G58A','original_2010_source_BRES_meshes':296,
      'original_2010_source_triangles':22441,
      'original_PVR_UV_triangles':18774,'authentic_original_atlases':24,
      'original_CLARA_Sun_entities':4,'only_original_alpha_atlas':alpha_names,
      'native_sun_properties_recovered_not_shader_interpreted':True,
      'host_engineering_diffuse_ambient_tonemap_and_fog':True,
      'host_shadow_map_or_real_iOS_shader_validated':False,
      'native_gameplay_Vita_tested':False,'VPK_produced':False}
    out.parent.mkdir(parents=True,exist_ok=True);report.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(s,'utf-8')
    proof['source_html_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    proof['host_G58_html_sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
    report.write_text(json.dumps(proof,indent=2,ensure_ascii=False)+'\n')
    print('G58A PASS source topology/PVR exactly retained; lighting HOST diagnostic only')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--g57html',type=Path,required=True)
    p.add_argument('--html',type=Path,required=True);p.add_argument('--json',type=Path,required=True)
    a=p.parse_args();build(a.g57html,a.html,a.json)
