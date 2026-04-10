#!/usr/bin/env python3
"""
404x9-evil-kit — Local Backend Server
by @xfraylin
"""

import subprocess
import threading
import queue
import json
import os
import signal
import time
import re
import logging
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_cors import CORS

# ── Silence Flask/Werkzeug access logs, keep errors ──────────────────────────
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)

active_procs = {}
proc_lock    = threading.Lock()
job_queues   = {}

# ── Impacket path resolver ────────────────────────────────────────────────────
IMPACKET_SEARCH_PATHS = [
    '/usr/bin', '/usr/local/bin', '/usr/share/doc/python3-impacket/examples',
    '/usr/share/impacket/scripts', '/opt/impacket/examples',
]
IMPACKET_TOOLS = ['psexec.py','wmiexec.py','smbexec.py','atexec.py',
                  'secretsdump.py','GetUserSPNs.py','GetNPUsers.py',
                  'ntlmrelayx.py','lookupsid.py','samrdump.py']

def resolve_impacket(script):
    """Return absolute path for an impacket script or None."""
    # 1. Check PATH via which
    r = subprocess.run(['which', script], capture_output=True, text=True, timeout=3)
    if r.returncode == 0:
        return r.stdout.strip()
    # 2. Fallback to known dirs
    for d in IMPACKET_SEARCH_PATHS:
        p = os.path.join(d, script)
        if os.path.isfile(p):
            return p
    return None

_impacket_cache = {}
def get_impacket(script):
    if script not in _impacket_cache:
        _impacket_cache[script] = resolve_impacket(script)
    return _impacket_cache[script]

# ── JOHN format mapper ────────────────────────────────────────────────────────
JOHN_FORMAT_MAP = {
    'md5':    'raw-md5',
    'sha1':   'raw-sha1',
    'sha256': 'raw-sha256',
    'sha512': 'raw-sha512',
}
def john_format(fmt):
    return JOHN_FORMAT_MAP.get(fmt.lower(), fmt)

# ── Sanitiser ─────────────────────────────────────────────────────────────────
def sanitize_cmd(cmd):
    BLOCKED = [
        r'\brm\s+-rf\s+/',
        r'\bmkfs\b',
        r'\bdd\s+.*of=/dev/[sh]d',
        r'>\s*/dev/[sh]d',
        r'\bformat\b.*[cC]:\\\\',
    ]
    for pat in BLOCKED:
        if re.search(pat, cmd):
            return False, "Bloqueado: patrón de comando potencialmente destructivo."
    return True, ""

# ── Runner ────────────────────────────────────────────────────────────────────
def run_command(job_id, cmd, cwd=None, env_extra=None):
    q = queue.Queue()
    job_queues[job_id] = q

    def worker():
        env = os.environ.copy()
        env['TERM'] = 'xterm-256color'
        env['FORCE_COLOR'] = '1'
        if env_extra:
            env.update(env_extra)
        try:
            proc = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                cwd=cwd, env=env, preexec_fn=os.setsid,
                bufsize=1, universal_newlines=True
            )
            with proc_lock:
                active_procs[job_id] = proc
            q.put({'type': 'start', 'pid': proc.pid, 'cmd': cmd})
            for line in iter(proc.stdout.readline, ''):
                q.put({'type': 'output', 'data': line})
            proc.stdout.close()
            proc.wait()
            q.put({'type': 'done', 'code': proc.returncode})
        except Exception as e:
            q.put({'type': 'error', 'data': str(e)})
            q.put({'type': 'done', 'code': -1})
        finally:
            with proc_lock:
                active_procs.pop(job_id, None)

    threading.Thread(target=worker, daemon=True).start()
    return q

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/run', methods=['POST'])
def api_run():
    data  = request.json or {}
    cmd   = data.get('cmd', '').strip()
    cwd   = data.get('cwd', '/tmp')
    if not cmd:
        return jsonify({'error': 'No command provided'}), 400
    ok, reason = sanitize_cmd(cmd)
    if not ok:
        return jsonify({'error': reason}), 403
    job_id = f"job_{int(time.time()*1000)}_{os.getpid()}"
    run_command(job_id, cmd, cwd=cwd)
    return jsonify({'job_id': job_id})

@app.route('/api/stream/<job_id>')
def api_stream(job_id):
    def generate():
        q = job_queues.get(job_id)
        if not q:
            time.sleep(0.15)
            q = job_queues.get(job_id)
        if not q:
            yield f"data: {json.dumps({'type':'error','data':'Job not found'})}\n\n"
            return
        while True:
            try:
                msg = q.get(timeout=30)
                yield f"data: {json.dumps(msg)}\n\n"
                if msg.get('type') == 'done':
                    job_queues.pop(job_id, None)
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'type':'keepalive'})}\n\n"
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control':'no-cache','X-Accel-Buffering':'no'}
    )

@app.route('/api/kill/<job_id>', methods=['POST'])
def api_kill(job_id):
    with proc_lock:
        proc = active_procs.get(job_id)
    if proc:
        try:
            pgid = os.getpgid(proc.pid)
            # SIGTERM first, then SIGKILL to handle sudo'd processes
            try: os.killpg(pgid, signal.SIGTERM)
            except OSError: pass
            time.sleep(0.3)
            try: os.killpg(pgid, signal.SIGKILL)
            except OSError: pass
            # also terminate the proc object itself
            try: proc.terminate()
            except Exception: pass
            try: proc.kill()
            except Exception: pass
            return jsonify({'status': 'killed'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Process not found'}), 404

@app.route('/api/jobs')
def api_jobs():
    with proc_lock:
        return jsonify({'active': list(active_procs.keys())})

@app.route('/api/check', methods=['POST'])
def api_check():
    tool = (request.json or {}).get('tool', '').split()[0]
    try:
        r = subprocess.run(['which', tool], capture_output=True, text=True, timeout=3)
        found = r.returncode == 0
        return jsonify({'tool': tool, 'found': found, 'path': r.stdout.strip() if found else ''})
    except Exception as e:
        return jsonify({'tool': tool, 'found': False, 'error': str(e)})

@app.route('/api/resolve/impacket', methods=['POST'])
def api_resolve_impacket():
    """Resolve real paths for impacket scripts."""
    scripts = (request.json or {}).get('scripts', IMPACKET_TOOLS)
    result  = {}
    for s in scripts:
        p = get_impacket(s)
        result[s] = {'path': p, 'found': p is not None}
    return jsonify(result)

@app.route('/api/john/format', methods=['POST'])
def api_john_format():
    fmt = (request.json or {}).get('format', '')
    return jsonify({'mapped': john_format(fmt)})

@app.route('/api/validate/file', methods=['POST'])
def api_validate_file():
    path = (request.json or {}).get('path', '')
    exists = os.path.isfile(path)
    return jsonify({'path': path, 'exists': exists,
                    'size': os.path.getsize(path) if exists else 0})

@app.route('/api/tools/status')
def api_tools_status():
    tools = [
        'nmap','gobuster','ffuf','sqlmap','hydra','john','hashcat',
        'msfvenom','msfconsole','searchsploit','wpscan','nikto',
        'subfinder','amass','whatweb','wafw00f','curl','wget',
        'crackmapexec','netexec','nxc','smbmap','smbclient','rpcclient',
        'enum4linux-ng','ldapdomaindump','ldapsearch',
        'kerbrute','bloodhound-python','responder','mitm6',
        'airmon-ng','airodump-ng','aireplay-ng','aircrack-ng',
        'impacket-psexec','evil-winrm','hashid','tcpdump',
        'medusa','wfuzz','dalfox','httpx','theharvester',
        'sherlock','holehe','dnsrecon','exiftool',
    ]
    status = {}
    for t in tools:
        r = subprocess.run(['which', t], capture_output=True, text=True, timeout=2)
        status[t] = r.returncode == 0
    # also resolve impacket scripts
    for s in IMPACKET_TOOLS:
        status[s] = get_impacket(s) is not None
    return jsonify(status)

@app.route('/api/files/list')
def api_files_list():
    dirs = ['/tmp', os.path.expanduser('~'), '/root']
    result = {}
    for d in dirs:
        if not os.path.isdir(d):
            continue
        try:
            files = []
            for f in sorted(os.listdir(d)):
                fp   = os.path.join(d, f)
                stat = os.stat(fp)
                files.append({'name': f, 'path': fp, 'size': stat.st_size,
                               'is_dir': os.path.isdir(fp)})
            result[d] = files
        except PermissionError:
            result[d] = []
    return jsonify(result)

@app.route('/api/files/read')
def api_files_read():
    path = request.args.get('path', '')
    if not path or not os.path.isfile(path):
        return jsonify({'error': 'Archivo no encontrado'}), 404
    try:
        with open(path, 'r', errors='replace') as f:
            content = f.read(500_000)
        return jsonify({'path': path, 'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/interfaces')
def api_interfaces():
    try:
        r = subprocess.run(['ip', '-o', 'link', 'show'],
                           capture_output=True, text=True, timeout=5)
        ifaces = re.findall(r'^\d+:\s+(\S+):', r.stdout, re.MULTILINE)
        ifaces = [i.rstrip(':') for i in ifaces if i not in ('lo',)]
        return jsonify({'interfaces': ifaces})
    except Exception as e:
        return jsonify({'interfaces': ['eth0', 'wlan0'], 'error': str(e)})

if __name__ == '__main__':
    banner = r"""
  _  _    ___  _  _  _  _  ___  ___  _ __      _  _     _
 | || |  / _ \| || |_( )/ _|/ _ \| __|\ V /    | || |__ (_)_
 | \| | | (_) | \/ / |/\__ \ (_) | _|  > <     | / / _|| | _|  
  \_,_|  \___/ \__/  |_||___/\___/|___/_/\_\    \_/\__||_|___|

  404x9-evil-kit  ·  by @xfraylin
  URL   → http://localhost:5000
  Press Ctrl+C to stop
"""
    print(banner)
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
