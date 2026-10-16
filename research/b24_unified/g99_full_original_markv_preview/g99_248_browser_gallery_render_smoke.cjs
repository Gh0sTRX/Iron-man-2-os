/* G99 Chrome WebGL2 actual 2010 source 248 clips gallery browser runtime QA.
 * The selection has NO 2010 native gameplay attack semantics. NO VPK.
 */
const {chromium}=require('/tmp/g99/browser/node_modules/playwright-core');
const fs=require('fs'),assert=require('assert');
const [src,png]=process.argv.slice(2);
if(!src||!png)throw Error('G99 expects full source gallery HTML path and screenshot');
(async()=>{
 const executable=process.env.G99_CHROME||'/usr/bin/google-chrome';
 const browser=await chromium.launch({executablePath:executable,headless:true,args:[
  '--no-sandbox','--enable-webgl','--ignore-gpu-blocklist',
  '--use-gl=angle','--use-angle=swiftshader','--allow-file-access-from-files']});
 try{
  const page=await browser.newPage({viewport:{width:1600,height:980},deviceScaleFactor:1});
  page.on('pageerror',e=>console.error('G99 owner source render page error:',String(e)));
  await page.goto('file://'+src,{waitUntil:'load',timeout:160000});
  await page.waitForFunction(()=>typeof a91!=='undefined' && Object.keys(a91.streams).length===248,
      null,{timeout:60000});
  const world=await page.evaluate(()=>{
   return {streams:Object.keys(a91.streams).length,
    sourceMapWebGL2Canvas:document.getElementById('game')?.width>300,
    trueMarkVTexture:markvTexLoaded91,
    originalWeightedVertices:sampled91.length/3,
    sourceFaces:index91.length/3,
    G91worldGL:gl.getError(), G99actorGL:gl91.getError()};
  });
  assert(world.sourceMapWebGL2Canvas===true);
  assert(world.trueMarkVTexture===true);
  assert(world.streams===248);
  assert(world.originalWeightedVertices===629);
  assert(world.sourceFaces>100);
  assert.strictEqual(world.G91worldGL,0);
  assert.strictEqual(world.G99actorGL,0);
  await page.locator('#g99search').fill('ground_combo');
  const visible=await page.locator('#g99choice option').count();
  assert(visible>=3,'original all 3 native Ground Combo clips missing from gallery');
  await page.locator('#g99choice').selectOption('suitcase_ironman_ground_combo_2');
  await page.locator('#g99play').click();
  await page.waitForTimeout(70);
  const now=await page.evaluate(()=>({
   sourceGalleryClip:state91.galleryClip,
   sourceActualDraw:document.getElementById('g91status').textContent,
   sourceCharacterGL:gl91.getError()
  }));
  assert.strictEqual(now.sourceGalleryClip,'suitcase_ironman_ground_combo_2');
  assert(now.sourceActualDraw.includes('ground_combo_2'));
  assert.strictEqual(now.sourceCharacterGL,0);
  await page.screenshot({path:png});
  assert(fs.statSync(png).size>25000);
  await page.locator('#g99stop').click();
  assert.strictEqual(await page.evaluate(()=>state91.galleryClip),'');
  console.log('PASS G99 Chrome actual original 2010 source real WebGL2 full 248 list rig+PVR world, original combo_2 play, G83 normal return, saved screenshot:',JSON.stringify(world));
  console.log('248 native MarkV source visual sequences inspected as files, NOT all 248 original inputs/combat transitions. NO VPK.')
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
