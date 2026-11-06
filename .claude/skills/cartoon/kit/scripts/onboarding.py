#!/usr/bin/env python3
"""Track setup in setup.json; never store secrets here.

  python3 scripts/onboarding.py init
  python3 scripts/onboarding.py status
  python3 scripts/onboarding.py set steps.mcp=true viralex.credits=null
  python3 scripts/onboarding.py doctor

Values use JSON when possible; otherwise they are strings. Verify MCP before marking its step complete."""
import json, platform, re, shutil, subprocess, sys
from datetime import datetime, timezone

from _common import EXAMPLE, SETUP, STUDIO, read_setup, set_path, write_setup

ORDER = [
    ('mcp', 'Viralex AI MCP — required'),
    ('lang', 'language'),
    ('niche', 'niche and profile'),
    ('style', 'visual style from a reference'),
    ('hero', 'character from a photo'),
    ('voice', 'voice'),
    ('env', 'environment and npm install'),
    ('telegram', 'Telegram bot (optional)'),
    ('done', 'ready'),
]


def next_step(data):
    st = data.get('steps', {})
    for k, title in ORDER:
        if not st.get(k):
            return k, title
    return None, None


def cmd_init():
    if SETUP.exists():
        print(f'{SETUP.name} already exists')
    else:
        SETUP.write_text(EXAMPLE.read_text(encoding='utf-8'), encoding='utf-8')
        print(f'created {SETUP}')
    cmd_status()


def cmd_status():
    data = read_setup()
    st = data.get('steps', {})
    for k, title in ORDER:
        print(f"  {'✓' if st.get(k) else '·'} {k:<9} {title}")
    k, title = next_step(data)
    if not data.get('steps', {}).get('mcp'):
        print('GATE: connect and verify Viralex AI MCP before any other work.')
    print(f'Next step: {k} — {title}' if k else 'Setup complete: ready to create videos.')


def cmd_set(pairs):
    data = read_setup()
    for p in pairs:
        if '=' not in p:
            sys.exit(f'expected key=value: {p}')
        k, v = p.split('=', 1)
        try:
            val = json.loads(v)
        except json.JSONDecodeError:
            val = v
        if k.lower().endswith(('token', 'api_key', 'apikey', 'secret', 'password')):
            sys.exit('Never store secrets in setup.json; use .env.')
        set_path(data, k, val)
    if not data.get('steps', {}).get('mcp'):
        allowed = ('viralex.', 'steps.mcp')
        if any(not pair.split('=', 1)[0].startswith(allowed) for pair in pairs):
            sys.exit('GATE: verify Viralex AI MCP before configuring other steps.')
    if data.get('steps', {}).get('mcp') and not data.get('viralex', {}).get('connected'):
        sys.exit('GATE: record a successful Viralex AI account check before completing MCP setup.')
    if data.get('steps', {}).get('done') and not all(data['steps'].get(k) for k, _ in ORDER if k != 'done'):
        sys.exit('Setup is incomplete: verify every required step before marking done.')
    if any(p.startswith('viralex.') for p in pairs):
        set_path(data, 'viralex.checked_at', datetime.now(timezone.utc).isoformat(timespec='seconds'))
    write_setup(data)
    cmd_status()


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ''


def cmd_doctor():
    if not read_setup().get('steps', {}).get('mcp'):
        sys.exit('GATE: verify Viralex AI MCP before checking the environment.')
    osn = platform.system()
    hints = {
        'Darwin': {'node': 'brew install node', 'ffmpeg': 'brew install ffmpeg'},
        'Linux': {'node': 'sudo apt install nodejs npm  (or nvm: https://github.com/nvm-sh/nvm)', 'ffmpeg': 'sudo apt install ffmpeg'},
        'Windows': {'node': 'winget install OpenJS.NodeJS.LTS', 'ffmpeg': 'winget install Gyan.FFmpeg'},
    }.get(osn, {'node': 'https://nodejs.org', 'ffmpeg': 'https://ffmpeg.org/download.html'})
    ok = True
    node = run(['node', '--version']) if shutil.which('node') else ''
    m = re.match(r'v(\d+)', node)
    node_ok = bool(m and int(m.group(1)) >= 18)
    print(f"  {'✓' if node_ok else '✗'} Node.js 18+: {node or 'missing'}" + ('' if node_ok else f'   → {hints["node"]}'))
    npm = shutil.which('npm')
    print(f"  {'✓' if npm else '✗'} npm: {'present' if npm else 'missing'}")
    ff = shutil.which('ffmpeg') and shutil.which('ffprobe')
    print(f"  {'✓' if ff else '✗'} ffmpeg + ffprobe: {'present' if ff else 'missing'}" + ('' if ff else f'   → {hints["ffmpeg"]}'))
    py_ok = sys.version_info >= (3, 9)
    print(f"  {'✓' if py_ok else '✗'} Python 3.9+: {platform.python_version()}")
    try:
        import faster_whisper  # noqa: F401
        fw = True
    except ImportError:
        fw = False
    print(f"  {'✓' if fw else '·'} faster-whisper (optional): {'present' if fw else 'missing'}" + ('' if fw else '   → pip install faster-whisper'))
    nm = (STUDIO / 'node_modules' / 'remotion').exists()
    print(f"  {'✓' if nm else '✗'} node_modules: {'installed' if nm else 'missing'}" + ('' if nm else f'   → cd {STUDIO.name} && npm i'))
    ok = node_ok and npm and ff and py_ok and nm
    data = read_setup()
    set_path(data, 'env.node', node or None)
    set_path(data, 'env.ffmpeg', bool(ff))
    set_path(data, 'env.whisper', fw)
    set_path(data, 'env.npm_installed', nm)
    if SETUP.exists():
        write_setup(data)
    print('Environment ready.' if ok else 'Required dependencies are missing. Install them and run doctor again.')
    sys.exit(0 if ok else 1)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        return
    c = sys.argv[1]
    if c == 'init':
        cmd_init()
    elif c == 'status':
        cmd_status()
    elif c == 'set':
        cmd_set(sys.argv[2:])
    elif c == 'doctor':
        cmd_doctor()
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
