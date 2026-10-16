/* G91C actual headless WebGL2 browser run, genuine owner world + armor
 * pose + original atlas, static dummy diagnostic overlay. NOT Vita QA. */
const {chromium}=require('/tmp/g91/browser/node_modules/playwright-core');
const assert=require('assert');
const fs=require('fs');
const src=process.argv[2],screenshot=process.argv[3];
if(!src||!screenshot)throw Error('G91C requires exact source HTML and screenshot path');
(async()=>{
 const executable=process.env.G91_CHROME||'/usr/bin/google-chrome';
 const browser=await chromium.launch({
  executablePath:executable,headless:true,
  args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist',
        '--use-gl=angle','--use-angle=swiftshader','--allow-file-access-from-files']
 });
 try{
  const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  const url='file://'+src;
  await page.goto(url,{waitUntil:'load',timeout:90000});
  await page.locator('#g91near').click({timeout:30000});
  await page.waitForFunction(
   ()=>document.getElementById('g91status')?.textContent.includes('Original IM2V:'),
   null,{timeout:45000});
  // Actually move animated original 2010 Mark V source clip on source city.
  await page.keyboard.down('w');await page.waitForTimeout(350);
  await page.keyboard.up('w');const triggered=await page.evaluate(()=>{document.getElementById('g91melee').click();return {accepted_clip:state91.attack,combo:state91.combo};});assert.strictEqual(triggered.accepted_clip,'suitcase_ironman_ground_combo_1','G91 original combo never triggered');
  await page.waitForTimeout(150);
  const state=await page.evaluate(()=>{
   const c=document.getElementById('g91overlay');
   const map=document.getElementById('game');
   return {overlay_width:c.width,overlay_height:c.height,
    map_width:map.width,map_height:map.height,
    display:document.getElementById('g91status').textContent,
    original_armor_atlas_load:markvTexLoaded91,
    shader_source_webgl_error:gl91.getError(),
    map_source_webgl_error:gl.getError(),
    source_triangles:index91.length/3,
    source_motion_vertex_count:sampled91.length/3};
  });
  assert(state.overlay_width>300&&state.overlay_height>150);
  assert(state.map_width>300&&state.map_height>150);
  assert(state.original_armor_atlas_load,'Original 2010 MC_SuitCase PVR source never actually loaded');
  assert.strictEqual(state.source_motion_vertex_count,629);
  assert(state.source_triangles>100);
  assert.strictEqual(state.shader_source_webgl_error,0,'source actor WEBGL ERROR');
  assert.strictEqual(state.map_source_webgl_error,0,'source PVR city WEBGL ERROR');
  assert(state.display.includes('Original IM2V:'),'Real Mark V original source clip not visible in UI');
  if(errors.length)throw Error('G91 source shader JavaScript runtime errors: '+errors.slice(0,10).join('; '));
  await page.screenshot({path:screenshot,fullPage:false});
  assert(fs.statSync(screenshot).size>30000,'Source original scene screenshot unexpectedly empty');
  console.log('PASS G91C CHROME ACTUAL WEBGL2 DRAW on real original 2010 PVR city+MarkV 512 atlas+629 source animated vertices+static test dummy',JSON.stringify(state));
  console.log('NOT actual Vita screenshot or proved original native combat hit frames. NO VPK.');
 }finally{
  await browser.close();
 }
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
