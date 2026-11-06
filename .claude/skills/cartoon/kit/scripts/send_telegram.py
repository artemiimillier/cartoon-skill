#!/usr/bin/env python3
"""Deliver files privately through the user's own Telegram bot.

  python3 scripts/send_telegram.py find
  python3 scripts/send_telegram.py send out/my.mp4 --caption-file films/my/description.txt

--dry-run makes no network calls. Create a bot with BotFather and store its token as
TELEGRAM_BOT_TOKEN in .env. The owner must press Start. Never run a second getUpdates
listener for an already-managed bot. Videos over the upload limit get a smaller -tg.mp4
copy; the master stays intact. Captions longer than 1024 characters go separately."""
import argparse, json, shutil, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

from _common import die, load_env, mime_of, multipart, read_setup, redact, update_setup

LIMIT = 49 * 1024 * 1024


def api(token, method, data=None, ctype=None):
    url = f'https://api.telegram.org/bot{token}/{method}'
    req = urllib.request.Request(url, data=data, headers={'Content-Type': ctype} if ctype else {})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            res = json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read()[:300].decode('utf-8', 'replace')
        hint = ' (a webhook or another listener owns this bot; getUpdates is unavailable)' if e.code == 409 else ''
        die(redact(f'Telegram {method}: HTTP {e.code} {body}{hint}', token))
    except urllib.error.URLError as e:
        die(redact(f'Telegram {method}: network unavailable: {e.reason}', token))
    if not res.get('ok'):
        die(redact(f'Telegram {method}: {res}', token))
    return res['result']


def find_chat(token, dry):
    if dry:
        print('[dry-run] GET getUpdates → latest private chat that messaged this bot → setup.json telegram.chat_id')
        return None
    ups = api(token, 'getUpdates')
    chats = [u['message']['chat'] for u in ups if u.get('message', {}).get('chat', {}).get('type') == 'private']
    if not chats:
        die('No private message found. Open your bot, press Start (/start), then run find again.')
    chat = chats[-1]
    update_setup(**{'telegram.enabled': True, 'telegram.chat_id': chat['id']})
    print(f'Private chat found: {chat.get("first_name", "")} (@{chat.get("username", "—")}), chat_id saved in setup.json')
    return chat['id']


def shrink(src):
    if not shutil.which('ffmpeg'):
        die('File exceeds 50 MB and ffmpeg is missing; compress manually')
    for scale, crf in ((1080, 26), (720, 28), (720, 32)):
        dst = src.with_name(src.stem + '-tg.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vf', f'scale={scale}:-2', '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(dst)], check=True)
        if dst.stat().st_size <= LIMIT:
            return dst
    die('Compressed copy still exceeds 50 MB; shorten the video')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    f = sub.add_parser('find')
    s = sub.add_parser('send')
    s.add_argument('file')
    s.add_argument('--caption', default='')
    s.add_argument('--caption-file')
    for p in (f, s):
        p.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    token = load_env().get('TELEGRAM_BOT_TOKEN', '')
    if not token and not a.dry_run:
        die('missing TELEGRAM_BOT_TOKEN in the studio .env (create your bot with @BotFather)')
    if a.cmd == 'find':
        find_chat(token, a.dry_run)
        return
    src = Path(a.file)
    if not src.exists():
        die(f'file not found: {src}')
    caption = Path(a.caption_file).read_text(encoding='utf-8').strip() if a.caption_file else a.caption
    chat = read_setup().get('telegram', {}).get('chat_id')
    big = src.stat().st_size > LIMIT and src.suffix.lower() == '.mp4'
    if a.dry_run:
        print(json.dumps({'chat_id': chat or '<resolved with getUpdates>', 'sendDocument': f'{src.name} ({src.stat().st_size / 1e6:.1f} MB{", first create a smaller -tg.mp4 copy" if big else ""})',
                          'caption': caption[:1024] if len(caption) <= 1024 else '(sent as a separate message)', 'sendMessage': len(caption) > 1024, 'token': 'present' if token else 'missing'}, ensure_ascii=False, indent=1))
        return
    chat = chat or find_chat(token, False)
    path = shrink(src) if big else src
    fields = {'chat_id': str(chat)}
    if caption and len(caption) <= 1024:
        fields['caption'] = caption
    body, ctype = multipart(fields, [('document', path.name, path.read_bytes(), mime_of(path))])
    msg = api(token, 'sendDocument', body, ctype)
    if caption and len(caption) > 1024:
        api(token, 'sendMessage', json.dumps({'chat_id': chat, 'text': caption[:4096]}).encode(), 'application/json')
    print(f'Sent: {path.name}, message_id {msg.get("message_id")}')


if __name__ == '__main__':
    main()
