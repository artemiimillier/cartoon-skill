#!/usr/bin/env python3
"""Record guidance, clone a permitted voice, or synthesize a complete script with ElevenLabs.

  python3 scripts/voice.py record
  python3 scripts/voice.py clone sample.wav --name "My voice"
  python3 scripts/voice.py say films/my/voice.txt -o public/my/voice.mp3

Commands show a plan by default. --dry-run shows a redacted request without network access.
--yes sends a paid request after cost approval. Keep ELEVENLABS_API_KEY in .env.
Check current plan eligibility and prices at elevenlabs.io/pricing. Only clone a voice
you own or have permission to use. New takes require a new output filename."""
import argparse, json, platform, sys, urllib.error, urllib.request
from pathlib import Path

from _common import STUDIO, die, load_env, mime_of, multipart, read_setup, redact, update_setup

API = 'https://api.elevenlabs.io/v1'


def post(url, key, body, ctype, accept='application/json'):
    req = urllib.request.Request(url, data=body, headers={'xi-api-key': key, 'Content-Type': ctype, 'Accept': accept})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def cmd_record():
    osn = platform.system()
    if osn == 'Darwin':
        cmd = 'ffmpeg -f avfoundation -i ":0" -t 120 -ac 1 -ar 44100 sample.wav'
        note = '":0" is the first microphone; list devices: ffmpeg -f avfoundation -list_devices true -i ""'
    elif osn == 'Windows':
        cmd = 'ffmpeg -f dshow -i audio="Microphone (...)" -t 120 -ac 1 -ar 44100 sample.wav'
        note = 'microphone name: ffmpeg -list_devices true -f dshow -i dummy'
    else:
        cmd = 'ffmpeg -f pulse -i default -t 120 -ac 1 -ar 44100 sample.wav'
        note = 'or -f alsa -i default'
    print('Voice sample: one to three minutes of clean speech in a quiet room, microphone six to eight inches away, no music or echo.')
    print('Speak as you would in your videos, with natural expression. A phone voice recorder is fine.')
    print(f'Mac/PC: {cmd}\n  ({note})')


def cmd_clone(a, key):
    files = [Path(f) for f in a.samples]
    for f in files:
        if not f.exists():
            die(f'file not found: {f}')
    size = sum(f.stat().st_size for f in files)
    if not a.yes and not a.dry_run:
        print(f'Plan: create an instant voice clone «{a.name}» from {len(files)} file(s), {size / 1e6:.1f} MB.')
        print(f'Key ELEVENLABS_API_KEY: {"present" if key else "MISSING — add it to .env"}. Check your plan and current pricing: https://elevenlabs.io/pricing')
        print('Clone only your own voice or one you have explicit permission to use. After approval, repeat with --yes.')
        return
    fields = {'name': a.name, 'remove_background_noise': 'true'}
    if a.dry_run:
        print(json.dumps({'POST': f'{API}/voices/add', 'headers': {'xi-api-key': '***'}, 'fields': fields, 'files': [str(f) for f in files]}, ensure_ascii=False, indent=1))
        return
    if not key:
        die('missing ELEVENLABS_API_KEY in .env')
    body, ctype = multipart(fields, [('files', f.name, f.read_bytes(), mime_of(f)) for f in files])
    res = json.loads(post(f'{API}/voices/add', key, body, ctype))
    vid = res.get('voice_id')
    if not vid:
        die('ElevenLabs returned no voice_id: ' + json.dumps(res, ensure_ascii=False)[:300])
    update_setup(**{'voice.mode': 'elevenlabs', 'voice.voice_id': vid})
    print(f'Clone created; voice_id saved in setup.json{" (voice verification is required on the website)" if res.get("requires_verification") else ""}')


def cmd_say(a, key):
    text = Path(a.text).read_text(encoding='utf-8').strip()
    st = read_setup().get('voice', {})
    vid = a.voice_id or st.get('voice_id')
    model = a.model or st.get('model') or 'eleven_multilingual_v2'
    out = Path(a.out)
    if out.exists():
        die(f'{out} already exists — save a new take under a new filename')
    if not vid:
        die('No voice_id: run clone first or pass --voice-id')
    if not a.yes and not a.dry_run:
        print(f'Plan: synthesize {len(text)} characters in one request, model {model}, voice from setup.json → {out}.')
        print(f'Key: {"present" if key else "MISSING"}. Characters count toward your ElevenLabs plan. After approval, use --yes.')
        return
    payload = {'text': text, 'model_id': model, 'voice_settings': {'stability': 0.45, 'similarity_boost': 0.8, 'style': 0.2, 'use_speaker_boost': True}}
    url = f'{API}/text-to-speech/{vid}?output_format=mp3_44100_128'
    if a.dry_run:
        print(json.dumps({'POST': url.replace(vid, '<voice_id>'), 'headers': {'xi-api-key': '***'}, 'json': {**payload, 'text': f'<{len(text)} characters>'}, 'out': str(out)}, ensure_ascii=False, indent=1))
        return
    if not key:
        die('missing ELEVENLABS_API_KEY in .env')
    audio = post(url, key, json.dumps(payload).encode(), 'application/json', 'audio/mpeg')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(audio)
    print(f'{out}  ({len(audio)} bytes). Next: python3 scripts/prep.py … --audio {out} --whisper small')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('record')
    c = sub.add_parser('clone')
    c.add_argument('samples', nargs='+')
    c.add_argument('--name', default='My voice')
    s = sub.add_parser('say')
    s.add_argument('text')
    s.add_argument('-o', '--out', required=True)
    s.add_argument('--voice-id')
    s.add_argument('--model')
    for p in (c, s):
        p.add_argument('--dry-run', action='store_true')
        p.add_argument('--yes', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'record':
        return cmd_record()
    key = load_env().get('ELEVENLABS_API_KEY', '')
    try:
        cmd_clone(a, key) if a.cmd == 'clone' else cmd_say(a, key)
    except urllib.error.HTTPError as e:
        die(redact(f'ElevenLabs: HTTP {e.code} {e.read()[:400]!r}', key))
    except urllib.error.URLError as e:
        die(redact(f'ElevenLabs: network unavailable: {e.reason}', key))


if __name__ == '__main__':
    main()
