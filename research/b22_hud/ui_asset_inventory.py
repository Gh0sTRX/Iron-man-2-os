#!/usr/bin/env python3
"""Read-only UI/Flash asset candidate search in the user's own Iron Man 2 IPA.

Does NOT export copyrighted source bytes or assert that a candidate is a working SWF.
"""
import argparse
import json
from pathlib import Path
import zipfile

UI_WORDS = ('hud', 'ui', 'menu', 'swf', 'flash', 'font', 'sprite',
            'button', 'radar', 'minimap', 'reticle', 'health', 'armor',
            'unibeam', 'atlas', 'crosshair', 'interface', 'upgrade')
UI_EXTS = {'.swf', '.fla', '.gfx', '.fnt', '.sprite'}
IMAGE_EXTS = {'.png', '.tga', '.pvr', '.bmp', '.jpg', '.jpeg'}
SWF_TYPES = (b'FWS', b'CWS', b'ZWS')


def plausible_swf(data, i):
    if i < 0 or i + 8 > len(data) or data[i:i+3] not in SWF_TYPES:
        return False
    version = data[i+3]
    length = int.from_bytes(data[i+4:i+8], 'little')
    return 1 <= version <= 50 and 8 <= length <= 128 * 1024 * 1024


def candidate(filename, head):
    name = filename.casefold()
    ext = Path(name).suffix
    if ext in UI_EXTS:
        return 'ui_extension'
    if any(x in name for x in UI_WORDS):
        return 'ui_name_hint'
    if plausible_swf(head, 0):
        return 'swf_magic'
    if head.startswith(b'\x89PNG\r\n\x1a\n') or head.startswith(b'PVR\x03'):
        return 'generic_image'
    if ext in IMAGE_EXTS:
        return 'generic_image_extension'
    return 'other'


def scan_entry(archive, info, max_probe):
    if info.is_dir():
        return None
    if info.flag_bits & 1:
        return {'entry': info.filename, 'file_size': info.file_size,
                'category': 'encrypted_zip_entry', 'magic_swf_offsets': [],
                'bytes_scanned': 0, 'warning': 'ZIP encryption flag set'}
    seen = 0
    head = b''
    tail = b''
    offsets = set()
    with archive.open(info) as source:
        while seen < max_probe:
            block = source.read(min(1024 * 1024, max_probe-seen))
            if not block:
                break
            if not head:
                head = block[:32]
            window = tail + block
            base = seen - len(tail)
            for marker in SWF_TYPES:
                start = 0
                while True:
                    i = window.find(marker, start)
                    if i == -1:
                        break
                    if plausible_swf(window, i):
                        offsets.add(base+i)
                    start = i+1
            seen += len(block)
            tail = window[-7:]
    cls = candidate(info.filename, head)
    if offsets and cls == 'other':
        cls = 'embedded_swf_signature_candidate'
    return {'entry': info.filename, 'file_size': info.file_size,
            'compressed_size': info.compress_size,
            'category': cls, 'magic_swf_offsets': sorted(offsets)[:100],
            'bytes_scanned': seen,
            'warning': 'probable SWF headers only; embedded offsets require independent format validation'
                       if offsets else ''}


def inspect(path, limit_mb=16):
    rows=[]
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            result = scan_entry(z, info, limit_mb * 1024 * 1024)
            if result is not None:
                rows.append(result)
    counts={}
    for row in rows:
        counts[row['category']]=counts.get(row['category'],0)+1
    return {'ipa_name': Path(path).name, 'entries': len(rows),
            'max_probe_per_entry_mb':limit_mb, 'category_counts':counts,
            'scan_limit_warning': 'Entries larger than the scan limit may contain unobserved assets.',
            'records':rows}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('ipa', type=Path)
    p.add_argument('--limit-mb', type=int, default=16)
    p.add_argument('--out', type=Path, default=Path('b22_ui_asset_inventory.json'))
    args=p.parse_args()
    if args.limit_mb < 1 or args.limit_mb > 1024:
        p.error('--limit-mb must be between 1 and 1024')
    result=inspect(args.ipa,args.limit_mb)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('ZIP entries:',result['entries'],'UI candidates:',
          sum(v for k,v in result['category_counts'].items() if k != 'other'))
    print('Saved:',args.out)


if __name__ == '__main__':
    main()
