#!/usr/bin/env python3
"""G112 actual original Iron Man 2 1.0.0 under touchHLE + GDB RSP.
This runs genuine 2010 iOS ARM Game, not the B24 approximation.
Capture authentic ARM register callsites only; NO VPK, NO raw binaries,
NO proprietary game files in artifact, no inferred hitframe/damage.
GitHub runner invokes under xvfb-run + software Mesa.
"""
import argparse, json, os, pathlib, signal, socket, subprocess, time
from datetime import datetime, timezone
def run(app, exe, out, sec):
 out.mkdir(parents=True,exist_ok=True)
 assert exe.is_file() and app.is_dir()
 assert 10<=sec<=120
 os.environ["APPIMAGE_EXTRACT_AND_RUN"]="1"
 os.environ["LIBGL_ALWAYS_SOFTWARE"]="1"
 touchlog=out/"G112_REAL_ORIGINAL_TOUCHHLE_HOST_LOG.txt"
 gdblog=out/"G112_REAL_ORIGINAL_ARM_GDB_NATIVE_FUNCTION_CALLS.txt"
 app_log=touchlog.open("w")
 proc=None;debug=None
 probes=[
  ("AttackEntity_LoadFromFile",0xa934c),
  ("EntityData_GetParamValue_INT",0xd7548),
  ("Actor_TestMeleeHit",0xdfd94),
  ("Actor_CanAttack",0xd9278),
  ("MainCharacter_UpdateMeleeAttackState",0xf1de4),
  ("Projectile_HitImpactActor",0xb44b0),
 ]
 script=out/"g112_original_owner_dynamic_arm_brk.gdb"
 lines=["set pagination off","set confirm off","set height 0",
        "set logging file "+str(gdblog),"set logging overwrite on","set logging enabled on",
        "file "+str(app/"IronMan2"),"set architecture arm",
        "target remote 127.0.0.1:9001"]
 for name,address in probes:
  ident="g112_"+name.lower()
  lines.extend([
   "set $"+ident+"=0",
   "break *0x%x"%address,
   "commands",
   "silent",
   "set $"+ident+"=$"+ident+"+1",
   "if $"+ident+"<=5",
   'printf "ORIGINAL_IOS_2010_G112_HIT %s count=%%u pc=0x%%x r0=0x%%x r1=0x%%x r2=0x%%x lr=0x%%x\\n", $'+ident+",$pc,$r0,$r1,$r2,$lr"%name,
   "end",
   "continue",
   "end"
  ])
 lines.append("continue")
 script.write_text("\n".join(lines)+"\n")
 start=time.monotonic()
 try:
  proc=subprocess.Popen([str(exe),"--gdb=127.0.0.1:9001",str(app)],
    cwd=str(exe.parent),env=os.environ.copy(),stdout=app_log,
    stderr=subprocess.STDOUT,start_new_session=True)
  online=False
  while time.monotonic()-start<min(26,sec//2):
   if proc.poll() is not None:break
   try:
    conn=socket.create_connection(("127.0.0.1",9001),timeout=.4)
    conn.close()
    online=True
    break
   except OSError:time.sleep(.5)
  if online:
   # One actual GDB remote client. Remote GDB execution and app UI are
   # independent. gdb exits only after input stop/app closure.
   debug=subprocess.Popen(["gdb-multiarch","-q","-nx","-batch","-x",str(script)],
       stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
   # For GDB to run original app and collect dynamic code calls, observe
   # the running game, optionally try menu without claiming input mapping.
   for t in range(0,sec,4):
    if proc.poll() is not None or debug.poll() is not None:break
    time.sleep(4)
    if t in (4,8,16):
     # Attempts are flagged unverified; screenshots reveal actual UI path.
     try:subprocess.run(["scrot",str(out/f"G112_touchHLE_host_real_game_T{t+4:02}.png")],
       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=3)
     except (FileNotFoundError,subprocess.TimeoutExpired):pass
   # Report screenshot at end; NO simulated hit claim without real trigger.
   try:subprocess.run(["scrot",str(out/"G112_touchHLE_host_final.png")],
         stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=4)
   except (FileNotFoundError,subprocess.TimeoutExpired):pass
  else:
   time.sleep(1)
 finally:
  for p0 in (debug,proc):
   if p0 and p0.poll() is None:
    try:os.killpg(p0.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  for p0 in (debug,proc):
   if p0:
    try:stdout,_=p0.communicate(timeout=6)
    except subprocess.TimeoutExpired:
     try:os.killpg(p0.pid,signal.SIGKILL)
     except ProcessLookupError:pass
     stdout,_=p0.communicate()
    if p0 is debug and stdout:
     (out/"G112_REAL_2010_GDB_HOST_PROCESS_STATUS.txt").write_text(stdout[:18000])
  app_log.close()
  # GDB file script contains ONLY original source function addresses, not IPA.
  script.unlink(missing_ok=True)
 content=gdblog.read_text(errors="replace") if gdblog.is_file() else ""
 hits=[x for x in content.splitlines() if "ORIGINAL_IOS_2010_G112_HIT" in x]
 result={
  "original_game":"owner-authentic 2010 Gameloft Iron Man 2 iOS 1.0.0",
  "emulator":"touchHLE v0.3.0 experimental Linux AppImage",
  "original_ARM_binary_ever_published":False,
  "VPK_generated":False,
  "gdb_server_socket_reached":online,
  "gdb_original_ios_gameplay_dynamic_breakpoint_hit_lines":hits[:150],
  "gdb_original_ios_method_breakpoint_hit_total":len(hits),
  "dynamic_damage_values_from_REAL_per_Attack_verified":False,
  "original_active_hit_frame_found":False,
  "original_game_entered_actual_level1":False,
  "screenshots_are_from_true_touchHLE_original_program_if_emulator_booted":True,
  "warning":"No interaction/menu, screenshot or code breakpoint means genuine combat frame not yet observed; NEVER claim success based on prior appDB reputation.",
  "touchhle_process_initial_exited":proc.returncode is not None,
  "trace_script_used":str(script.name)
 }
 (out/"G112_REAL_2010_GAME_TOUCHHLE_BRK_RESULT_NO_VPK.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 print("G112 REAL touchHLE trace REPORT",json.dumps({
  'gdb_reached':online,'original_game_method_hits':len(hits),
  'first_hits':hits[:9],
  'emulator_exit':proc.returncode,
  'host_text_tail':touchlog.read_text(errors="replace")[-1200:]
 },ensure_ascii=False))
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--app",type=pathlib.Path,required=True)
 parser.add_argument("--touchhle",type=pathlib.Path,required=True)
 parser.add_argument("--out",type=pathlib.Path,required=True)
 parser.add_argument("--seconds",type=int,default=40)
 a=parser.parse_args();run(a.app,a.touchhle,a.out,a.seconds)
