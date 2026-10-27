#!/usr/bin/env python3
"""Fetch only explicitly provided Drive source; keep private links out of logs."""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
from urllib.parse import parse_qs,urlparse
import zipfile


def drive_id(value):
    if re.fullmatch(r'[A-Za-z0-9_-]{15,80}',value):return value
    u=urlparse(value)
    if u.scheme!='https' or u.hostname!='drive.google.com':
        raise ValueError('Expected the provided HTTPS Drive file link')
    match=re.fullmatch(r'/file/d/([A-Za-z0-9_-]{15,80})(?:/view)?/?',u.path)
    result=match.group(1) if match else parse_qs(u.query).get('id',[''])[0]
    if not re.fullmatch(r'[A-Za-z0-9_-]{15,80}',result):raise ValueError('Invalid Drive file identifier')
    return result


def verify(path):
    from prepare_audio_assets import EXE_SHA,sha_file
    if path.stat().st_size!=248613763:raise ValueError('Wrong source IPA size/version')
    with zipfile.ZipFile(path) as archive:
        exe=archive.read('Payload/IronMan2.app/IronMan2')
        if len(exe)!=7480208 or hashlib.sha256(exe).hexdigest()!=EXE_SHA:
            raise ValueError('Original executable SHA256 mismatch')
        if archive.testzip() is not None:raise ValueError('Source archive CRC failure')
    return dict(ipa_bytes=path.stat().st_size,ipa_sha256=sha_file(path),executable_sha256=EXE_SHA)


def fetch(link_file,output):
    repo=Path(__file__).resolve().parents[1];output=output.resolve()
    if output.is_relative_to(repo):raise ValueError('Keep the original IPA outside the checkout')
    if output.exists():return verify(output)
    import gdown
    values=[v.strip() for v in link_file.read_text().splitlines() if v.strip() and not v.startswith('#')]
    ids=[drive_id(v) for v in values]
    if not ids:raise ValueError('No provided source link')
    output.parent.mkdir(parents=True,mode=0o700,exist_ok=True)
    pending=output.with_suffix(output.suffix+'.part')
    if pending.exists():raise ValueError('Preserve or inspect the existing partial input first')
    errors=[]
    for file_id in ids:
        try:
            # gdown exceptions/messages may include private/signed URLs.
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                result=gdown.download(id=file_id,output=str(pending),quiet=True,use_cookies=False)
            if not result:raise ValueError('Download did not complete')
            os.chmod(pending,0o600);report=verify(pending)
            pending.replace(output);return report
        except Exception as error:
            errors.append(type(error).__name__)
            if pending.exists():pending.unlink() # our unverified temporary output only
    raise RuntimeError('Source download blocked/unavailable; error classes='+','.join(errors))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--drive-link-file',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:print(json.dumps(fetch(args.drive_link_file,args.output),indent=2))
    except Exception as error:
        # Do not echo arbitrary downloader messages, link file contents or URLs.
        print(json.dumps({'status':'input_unavailable','error_class':type(error).__name__}))
        raise SystemExit(2)
