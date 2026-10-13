#!/usr/bin/env python3
"""Read-only metadata audit of Iron Man 2 iOS IPA files.

Never exports/decompresses original game assets to disk; produces manifest CSVs.
Works with Python 3 stdlib, independent of the original audio codec.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

AUDIO = {'.wav', '.ogg', '.mp3', '.aac', '.m4a', '.caf', '.aif', '.aiff',
         '.flac', '.mid', '.midi', '.adp', '.adpcm', '.fsb', '.bnk', '.wem', '.bank'}
VIDEO = {'.mp4', '.m4v', '.mov', '.3gp', '.avi', '.bik', '.smk', '.mpg', '.mpeg'}
LOCALE = {'.strings', '.srt', '.vtt', '.sub', '.txt', '.xml', '.lua'}
HINTS = ('audio', 'sound', 'sfx', 'music', 'song', 'voice', 'speech',
         'dialog', 'cinemat', 'cutscene', 'movie', 'intro', 'outro', 'subtitle')
FIELDNAMES = ['version', 'entry', 'size', 'compressed_size', 'sha256',
              'signature', 'candidate_category', 'reason']


def signature(head):
    if head.startswith(b'OggS'): return 'Ogg container'
    if head.startswith(b'RIFF') and head[8:12] == b'WAVE': return 'RIFF WAVE'
    if head.startswith(b'RIFF'): return 'RIFF (subtype unknown)'
    if head.startswith(b'FORM') and head[8:12] in (b'AIFF', b'AIFC'): return 'AIFF/AIFC'
    if head.startswith(b'ID3'): return 'ID3 tag (possibly MP3)'
    if head.startswith(b'fLaC'): return 'FLAC'
    if head.startswith(b'caff'): return 'CoreAudio CAF'
    if len(head) >= 12 and head[4:8] == b'ftyp': return 'ISO BMFF / MP4 family'
    if head.startswith(b'BKHD'): return 'Wwise SoundBank candidate'
    if head.startswith(b'FSB4') or head.startswith(b'FSB5'): return 'FMOD sample bank'
    if head.startswith(b'BIK') or head.startswith(b'KB2'): return 'Bink-like stream'
    if head.startswith((b'FWS', b'CWS', b'ZWS')): return 'SWF container (not necessarily cutscene)'
    if head.startswith(b'\x89PNG'): return 'PNG (image, not sound)'
    if head.startswith(b'PK\x03\x04'): return 'ZIP container'
    return 'unrecognized'


def classify(filename, sign):
    name = filename.lower()
    ext = Path(name).suffix
    if ext in AUDIO: return 'audio candidate', 'filename extension'
    if ext in VIDEO: return 'video candidate', 'filename extension'
    if ext in LOCALE and any(s in name for s in HINTS):
        return 'dialog/script candidate', 'name and extension'
    if ext in LOCALE: return 'text/script candidate', 'extension (may be unrelated)'
    if sign in ('Ogg container', 'RIFF WAVE', 'AIFF/AIFC', 'FLAC', 'CoreAudio CAF',
                'ID3 tag (possibly MP3)', 'Wwise SoundBank candidate',
                'FMOD sample bank', 'Bink-like stream', 'ISO BMFF / MP4 family'):
        return 'media signature candidate', 'magic signature'
    if 'SWF' in sign: return 'ui/movie candidate', 'SWF magic; contents unknown'
    if any(s in name for s in HINTS): return 'named media/pack candidate', 'filename keywords'
    return 'other', ''


def scan(ipa_path, version):
    entries = []
    with ZipFile(ipa_path) as archive:
        infos = [i for i in archive.infolist() if not i.is_dir()]
        for info in infos:
            digest = hashlib.sha256()
            with archive.open(info, 'r') as source:
                head = source.read(64)
                digest.update(head)
                while chunk := source.read(1024 * 1024):
                    digest.update(chunk)
            magic = signature(head)
            category, why = classify(info.filename, magic)
            entries.append(dict(version=version, entry=info.filename,
                                size=info.file_size, compressed_size=info.compress_size,
                                sha256=digest.hexdigest(), signature=magic,
                                candidate_category=category, reason=why))
    return entries


def csv_write(path, records, fields):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ipa', nargs='+', type=Path, help='One or two privately owned original iOS IPA files')
    parser.add_argument('--out', type=Path, default=Path('b18_media_manifest'))
    args = parser.parse_args()
    if not 1 <= len(args.ipa) <= 2: parser.error('Provide one or two IPA files')
    for ipa in args.ipa:
        if not ipa.is_file(): parser.error('File not found: ' + str(ipa))
    args.out.mkdir(parents=True, exist_ok=True)
    data = []
    for idx, path in enumerate(args.ipa, 1):
        data.extend(scan(path, 'IPA_' + str(idx)))
    csv_write(args.out / 'ALL_IPA_ENTRIES.csv', data, FIELDNAMES)
    candidates = [r for r in data if r['candidate_category'] != 'other']
    csv_write(args.out / 'MEDIA_AND_SCRIPT_CANDIDATES.csv', candidates, FIELDNAMES)
    groups = Counter(r['candidate_category'] for r in data)
    versions = Counter(r['version'] for r in data)
    changes = []
    if len(args.ipa) == 2:
        old = {r['entry']: r for r in data if r['version'] == 'IPA_1'}
        new = {r['entry']: r for r in data if r['version'] == 'IPA_2'}
        for key in sorted(old.keys() | new.keys()):
            left, right = old.get(key), new.get(key)
            change = ('added' if not left else 'removed' if not right
                      else 'same' if left['sha256'] == right['sha256'] else 'changed')
            if change != 'same':
                changes.append({'entry': key, 'status': change,
                                'IPA_1_sha256': left['sha256'] if left else '',
                                'IPA_2_sha256': right['sha256'] if right else ''})
        csv_write(args.out / 'VERSION_DIFFERENCES.csv', changes,
                  ['entry', 'status', 'IPA_1_sha256', 'IPA_2_sha256'])
    report = {
        'scope': 'Read-only ZIP entries and first 64-byte signature inspection; does NOT unpack audio banks',
        'ipa_sizes_bytes': [p.stat().st_size for p in args.ipa],
        'files_per_version': dict(versions), 'classifications': dict(groups),
        'media_candidate_count': len(candidates), 'changed_files': len(changes),
        'warning': 'File name / magic may be ambiguous; do not infer playable samples or cutscene format from this manifest.'
    }
    (args.out / 'SUMMARY.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
