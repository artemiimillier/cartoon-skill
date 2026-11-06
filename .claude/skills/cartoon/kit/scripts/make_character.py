#!/usr/bin/env python3
"""Make a nine-pose character atlas from a permitted photo.

  python3 scripts/make_character.py prompt [--bg green]
  python3 scripts/make_character.py generate photo.jpg --provider openai

Use --dry-run to inspect the request without sending, and --yes only after approving
the current provider price. Keys stay in .env. Defaults: gpt-image-1 for OpenAI edits,
gemini-2.5-flash-image for Gemini. Output: public/hero/atlas-raw.png; next run atlas_rig.py.
Use your own photo or obtain the pictured person's permission."""
import argparse, base64, json, re, sys, urllib.error, urllib.request
from pathlib import Path

from _common import STUDIO, die, load_env, mime_of, multipart, redact, update_setup

POSES = ['neutral', 'palm', 'point', 'up', 'celebrate', 'think', 'surprise', 'shrug', 'wink']
PRICING = {'openai': 'https://openai.com/api/pricing', 'gemini': 'https://ai.google.dev/gemini-api/docs/pricing'}
BG = {'green': 'plain solid pure green (#00FF00)', 'white': 'plain solid white (#FFFFFF)', 'transparent': 'fully transparent'}


def hero_style():
    """Read the Character style line so generated poses match the studio theme."""
    p = STUDIO / 'style' / 'STYLE.md'
    if p.exists():
        m = re.search(r'^Character style:\s*(.+)$', p.read_text(encoding='utf-8'), re.M)
        if m:
            return m.group(1).strip()
    return 'flat 2D vector cartoon, thick clean dark outline, simple flat colors, soft cel shading, friendly big-eyed proportions'


def build_prompt(style, bg):
    poses = (
        '1 neutral — relaxed, arms down, light smile; '
        '2 palm — explaining, one open palm raised to the side at chest height; '
        '3 point — arm extended, index finger pointing to the LEFT edge of the image; '
        '4 up — index finger raised up next to the face, "important idea"; '
        '5 celebrate — both arms up, joyful, eyes closed in happiness; '
        '6 think — hand on the chin, eyes looking up, thoughtful; '
        '7 surprise — eyes wide, mouth open in an "O", both hands raised; '
        '8 shrug — palms up, shoulders raised, "no idea"; '
        '9 wink — winking, thumbs up'
    )
    return (
        'Create a character sheet of ONE cartoon character based on the person in the attached photo. '
        'Keep the recognizable features (face shape, hairstyle, facial hair, glasses, skin tone, typical clothing) '
        f'but redraw them in this style: {style}. '
        'Layout: exactly a 3x3 grid of nine equal cells, the same character in every cell, same scale and same outfit, '
        'framed from the waist up, facing the viewer, centered in the cell with empty margin around. '
        f'Background: {BG[bg]} across the whole image, no shadows on the background, no text, no numbers, no borders, no grid lines. '
        'Do not use the background color anywhere on the character. '
        f'Poses in reading order (left to right, top to bottom): {poses}. '
        'Mouth closed in all poses except surprise. Same lighting and colors in all nine cells.'
    )


def call_openai(key, photo, prompt, model, size, dry):
    url = 'https://api.openai.com/v1/images/edits'
    fields = {'model': model, 'prompt': prompt, 'size': size, 'n': '1', 'background': 'transparent', 'quality': 'high'}
    data = Path(photo).read_bytes()
    if dry:
        print(json.dumps({'POST': url, 'headers': {'Authorization': 'Bearer ***'}, 'fields': fields, 'files': {'image': f'{photo} ({len(data)} bytes, {mime_of(photo)})'}}, ensure_ascii=False, indent=1))
        return None
    body, ctype = multipart(fields, [('image', Path(photo).name, data, mime_of(photo))])
    req = urllib.request.Request(url, data=body, headers={'Authorization': f'Bearer {key}', 'Content-Type': ctype})
    with urllib.request.urlopen(req, timeout=600) as r:
        res = json.loads(r.read())
    return base64.b64decode(res['data'][0]['b64_json'])


def call_gemini(key, photo, prompt, model, dry):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    data = Path(photo).read_bytes()
    payload = {'contents': [{'parts': [{'text': prompt}, {'inline_data': {'mime_type': mime_of(photo), 'data': '<base64>'}}]}], 'generationConfig': {'responseModalities': ['IMAGE', 'TEXT']}}
    if dry:
        print(json.dumps({'POST': url, 'headers': {'x-goog-api-key': '***'}, 'json': payload, 'image': f'{photo} ({len(data)} bytes)'}, ensure_ascii=False, indent=1))
        return None
    payload['contents'][0]['parts'][1]['inline_data']['data'] = base64.b64encode(data).decode()
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'x-goog-api-key': key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=600) as r:
        res = json.loads(r.read())
    for part in res.get('candidates', [{}])[0].get('content', {}).get('parts', []):
        inline = part.get('inline_data') or part.get('inlineData')
        if inline and inline.get('data'):
            return base64.b64decode(inline['data'])
    die('Gemini returned no image: ' + json.dumps(res, ensure_ascii=False)[:400])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('prompt')
    p.add_argument('--bg', choices=list(BG), default='green')
    p.add_argument('--style')
    g = sub.add_parser('generate')
    g.add_argument('photo')
    g.add_argument('--provider', choices=['openai', 'gemini'], required=True)
    g.add_argument('--model')
    g.add_argument('--size', default='1024x1536', help='openai: 1024x1536 (portrait, cell ~341×512)')
    g.add_argument('--style')
    g.add_argument('-o', '--out', default=str(STUDIO / 'public' / 'hero' / 'atlas-raw.png'))
    g.add_argument('--dry-run', action='store_true', help='show the request without sending it')
    g.add_argument('--yes', action='store_true', help='send after the user has approved the cost')
    a = ap.parse_args()

    style = a.style or hero_style()
    if a.cmd == 'prompt':
        print(build_prompt(style, a.bg))
        return
    if not Path(a.photo).exists():
        die(f'file not found: {a.photo}')
    bg = 'transparent' if a.provider == 'openai' else 'green'
    prompt = build_prompt(style, bg)
    model = a.model or ('gpt-image-1' if a.provider == 'openai' else 'gemini-2.5-flash-image')
    env = load_env()
    kname = 'OPENAI_API_KEY' if a.provider == 'openai' else 'GEMINI_API_KEY'
    key = env.get(kname, '')
    if not a.yes and not a.dry_run:
        print(f'Plan: {a.provider} / {model}, photo {a.photo}, one image {a.size if a.provider == "openai" else ""}, background {bg}.')
        print(f'Key {kname}: {"present in .env" if key else "MISSING — add it to .env"}.')
        print(f'Current pricing: {PRICING[a.provider]}. Explain the cost and run with --yes after approval.')
        return
    if a.dry_run:
        print(f'[dry-run] key {kname}: {"present" if key else "missing"}; no network request')
    elif not key:
        die(f'missing {kname} in the studio .env')
    try:
        img = call_openai(key, a.photo, prompt, model, a.size, a.dry_run) if a.provider == 'openai' else call_gemini(key, a.photo, prompt, model, a.dry_run)
    except urllib.error.HTTPError as e:
        die(redact(f'{a.provider}: HTTP {e.code} {e.read()[:400]!r}', key))
    except urllib.error.URLError as e:
        die(redact(f'{a.provider}: network unavailable: {e.reason}', key))
    if img is None:
        return
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img)
    update_setup(**{'hero.kind': 'atlas', 'hero.photo': str(Path(a.photo)), 'hero.atlas': str(out.relative_to(STUDIO)) if out.is_relative_to(STUDIO) else str(out)})
    print(f'{out}  ({len(img)} bytes). Next: python3 scripts/atlas_rig.py {out} --install')


if __name__ == '__main__':
    main()
