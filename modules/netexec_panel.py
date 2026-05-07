"""
netexec_panel.py — NXC command builder, module discovery, and output parser
for the 404x9-evil-kit server.
"""

import re
import shlex
import subprocess
import threading

# ── module discovery cache ────────────────────────────────────────────────────
_modules_cache: dict | None = None
_modules_lock = threading.Lock()


def discover_modules(refresh: bool = False) -> dict:
    global _modules_cache
    with _modules_lock:
        if _modules_cache is not None and not refresh:
            return _modules_cache
        result = _run_module_discovery()
        _modules_cache = result
        return result


def _run_module_discovery() -> dict:
    try:
        r = subprocess.run(
            ['nxc', 'smb', '-L'],
            capture_output=True, text=True, timeout=30,
        )
        output = r.stdout + r.stderr
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {'found': False, 'modules': []}

    modules = []
    # nxc smb -L format:
    #   [*] Module Name
    #       module_name   v0.x - Description text
    current_category = ''
    for line in output.splitlines():
        # category header e.g. "[*] smb" or "[*] POST"
        cat_m = re.match(r'^\[\*\]\s+(.+)', line)
        if cat_m:
            current_category = cat_m.group(1).strip()
            continue
        # module row: "  name   vX - description"
        mod_m = re.match(r'^\s{2,}(\S+)\s+v[\d.]+\S*\s+-\s+(.*)', line)
        if mod_m:
            modules.append({
                'name': mod_m.group(1).strip(),
                'description': mod_m.group(2).strip(),
                'category': current_category,
                'available': True,
            })
            continue
        # fallback: indented name without version
        alt_m = re.match(r'^\s{2,}(\S+)\s+(.*)', line)
        if alt_m and not alt_m.group(1).startswith('['):
            name = alt_m.group(1).strip()
            if name and not any(m['name'] == name for m in modules):
                modules.append({
                    'name': name,
                    'description': alt_m.group(2).strip(),
                    'category': current_category,
                    'available': True,
                })

    return {'found': bool(modules), 'modules': modules}


# ── command builder helpers ───────────────────────────────────────────────────

def _q(arg: str) -> str:
    """Shell-quote an argument if it contains special characters."""
    return shlex.quote(str(arg))


def _build_auth_args(argv: list, data: dict) -> None:
    auth_mode = data.get('auth_mode', 'password')
    domain = (data.get('domain') or '').strip()
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    hash_ = (data.get('hash') or '').strip()

    if domain:
        argv += ['-d', domain]

    if auth_mode == 'null':
        argv += ['-u', '', '-p', '']
    elif auth_mode == 'kcache':
        if username:
            argv += ['-u', username]
        argv.append('--use-kcache')
    elif auth_mode == 'kerberos':
        if username:
            argv += ['-u', username]
        if password:
            argv += ['-p', password]
        elif hash_:
            argv += ['-H', hash_]
        argv.append('--kerberos')
    elif auth_mode == 'hash':
        if username:
            argv += ['-u', username]
        if hash_:
            argv += ['-H', hash_]
    else:  # password
        if username:
            argv += ['-u', username]
        if password:
            argv += ['-p', password]

    if data.get('local_auth'):
        argv.append('--local-auth')
    if data.get('use_kcache') and auth_mode != 'kcache':
        argv.append('--use-kcache')
    if data.get('no_progress'):
        argv.append('--no-progress')


def _build_connection_args(argv: list, data: dict) -> None:
    if data.get('port'):
        argv += ['--port', str(data['port'])]
    if data.get('threads'):
        argv += ['-t', str(data['threads'])]
    if data.get('timeout'):
        argv += ['--timeout', str(data['timeout'])]
    if data.get('jitter'):
        argv += ['--jitter', str(data['jitter'])]
    if data.get('dns_server'):
        argv += ['--dns-server', data['dns_server']]
    if data.get('kdc_host'):
        argv += ['--kdcHost', data['kdc_host']]
    if data.get('aes_key'):
        argv += ['--aesKey', data['aes_key']]
    if data.get('log'):
        argv += ['--log', data['log']]
    if data.get('verbose'):
        argv.append('--verbose')
    if data.get('debug'):
        argv.append('--debug')


def _build_smb_args(argv: list, data: dict, actions: list) -> None:
    relay_out = (data.get('relay_output') or '/tmp/nxc_relayable.txt').strip()
    rid_max = (data.get('rid_max') or '').strip()

    smb_flag_map = {
        'shares': ['--shares'],
        'users': ['--users'],
        'groups': ['--groups'],
        'local-groups': ['--local-groups'],
        'loggedon-users': ['--loggedon-users'],
        'pass-pol': ['--pass-pol'],
        'sam': ['--sam'],
        'lsa': ['--lsa'],
        'ntds': ['--ntds'],
        'disks': ['--disks'],
        'interfaces': ['--interfaces'],
        'sessions': ['--sessions'],
    }
    for action in actions:
        if action in smb_flag_map:
            argv += smb_flag_map[action]
        elif action == 'rid-brute':
            argv.append('--rid-brute')
            if rid_max:
                argv += ['--rid-brute', rid_max]
                argv.pop(-3)  # remove the plain --rid-brute we just added
        elif action == 'gen-relay-list':
            argv += ['--gen-relay-list', relay_out]

    exec_type = (data.get('exec_type') or '').strip()
    exec_cmd = (data.get('exec_command') or '').strip()
    exec_method = (data.get('exec_method') or '').strip()

    if exec_method:
        argv += ['--exec-method', exec_method]
    if exec_type == 'cmd' and exec_cmd:
        argv += ['-x', exec_cmd]
    elif exec_type == 'powershell' and exec_cmd:
        argv += ['-X', exec_cmd]


def _build_winrm_args(argv: list, data: dict, actions: list) -> None:
    for action in actions:
        if action == 'check-https':
            argv += ['--port', '5986']
        elif action == 'sam':
            argv.append('--sam')
        elif action == 'lsa':
            argv.append('--lsa')
        elif action == 'dpapi':
            argv.append('--dpapi')

    exec_type = (data.get('exec_type') or '').strip()
    exec_cmd = (data.get('exec_command') or '').strip()
    if exec_type == 'cmd' and exec_cmd:
        argv += ['-x', exec_cmd]
    elif exec_type == 'powershell' and exec_cmd:
        argv += ['-X', exec_cmd]


def _build_ldap_args(argv: list, data: dict, actions: list) -> None:
    asrep_out = (data.get('asrep_out') or '/tmp/nxc_asrep_hashes.txt').strip()
    tgs_out = (data.get('tgs_out') or '/tmp/nxc_tgs_hashes.txt').strip()
    bh_collection = (data.get('bloodhound_collection') or 'All').strip()

    for action in actions:
        if action == 'users':
            argv.append('--users')
        elif action == 'groups':
            argv.append('--groups')
        elif action == 'asreproast':
            argv += ['--asreproast', asrep_out]
        elif action == 'kerberoast':
            argv += ['--kerberoast', tgs_out]
        elif action == 'laps':
            argv.append('--laps')
        elif action == 'maq':
            argv.append('--maq')
        elif action == 'gmsa':
            argv.append('--gmsa')
        elif action == 'delegation':
            argv.append('--delegation')
        elif action == 'bloodhound':
            argv += ['--bloodhound', '-c', bh_collection]
        elif action == 'pass-pol':
            argv.append('--pass-pol')
        elif action == 'dc-list':
            argv.append('--dc-list')
        elif action == 'get-sid':
            argv.append('--get-sid')


def _build_mssql_args(argv: list, data: dict, actions: list) -> None:
    database = (data.get('database') or '').strip()
    query = (data.get('query') or '').strip()

    if database:
        argv += ['--local-auth']  # mssql often needs --local-auth for DB access
        argv += ['--database', database] if '--database' in actions else []

    for action in actions:
        if action == 'database' and database:
            argv += ['--database', database]
        elif action == 'linked-servers':
            argv.append('--linked-servers')
        elif action == 'rid-brute':
            argv.append('--rid-brute')
        elif action == 'sam':
            argv.append('--sam')
        elif action == 'lsa':
            argv.append('--lsa')

    if query:
        argv += ['-q', query]

    exec_type = (data.get('exec_type') or '').strip()
    exec_cmd = (data.get('exec_command') or '').strip()
    if exec_type == 'cmd' and exec_cmd:
        argv += ['-x', exec_cmd]
    elif exec_type == 'powershell' and exec_cmd:
        argv += ['-X', exec_cmd]


def _build_wmi_args(argv: list, data: dict, actions: list) -> None:
    wmi_query = (data.get('wmi_query') or '').strip()
    wmi_ns = (data.get('wmi_namespace') or '').strip()
    exec_method = (data.get('exec_method') or '').strip()

    if wmi_ns:
        argv += ['--wmi-namespace', wmi_ns]
    if wmi_query:
        argv += ['--wmi', wmi_query]
    if exec_method:
        argv += ['--exec-method', exec_method]

    exec_type = (data.get('exec_type') or '').strip()
    exec_cmd = (data.get('exec_command') or '').strip()
    if exec_type == 'cmd' and exec_cmd:
        argv += ['-x', exec_cmd]
    elif exec_type == 'powershell' and exec_cmd:
        argv += ['-X', exec_cmd]


def _build_rdp_args(argv: list, data: dict, actions: list) -> None:
    screentime = (data.get('screentime') or '').strip()
    res = (data.get('res') or '').strip()
    clipboard_delay = (data.get('clipboard_delay') or '').strip()

    for action in actions:
        if action == 'check-nla':
            argv.append('--nla')
        elif action == 'screenshot':
            argv.append('--screenshot')
            if screentime:
                argv += ['--screentime', screentime]
            if res:
                argv += ['--res', res]
        elif action == 'nla-screenshot':
            argv.append('--nla-screenshot')
        elif action == 'clipboard':
            argv.append('--clipboard')
            if clipboard_delay:
                argv += ['--clipboard-delay', clipboard_delay]


# ── public API ────────────────────────────────────────────────────────────────

def build_netexec_command(data: dict) -> tuple:
    proto = (data.get('protocol') or 'smb').strip().lower()
    target = (data.get('target') or '').strip()
    if not target:
        raise ValueError('Target is required')

    argv = ['nxc', proto, target]

    _build_auth_args(argv, data)
    _build_connection_args(argv, data)

    actions = data.get('actions') or []

    if proto == 'smb':
        _build_smb_args(argv, data, actions)
    elif proto == 'winrm':
        _build_winrm_args(argv, data, actions)
    elif proto == 'ldap':
        _build_ldap_args(argv, data, actions)
    elif proto == 'mssql':
        _build_mssql_args(argv, data, actions)
    elif proto == 'wmi':
        _build_wmi_args(argv, data, actions)
    elif proto == 'rdp':
        _build_rdp_args(argv, data, actions)

    # Module
    module = (data.get('module') or '').strip()
    if module:
        argv += ['-M', module]
        for opt in (data.get('module_options') or []):
            if opt and '=' in opt:
                argv += ['-o', opt]

    # File transfer
    transfer_mode = (data.get('transfer_mode') or 'none').strip()
    src = (data.get('transfer_src') or '').strip()
    dst = (data.get('transfer_dst') or '').strip()
    if transfer_mode == 'upload' and src and dst:
        argv += ['--put-file', src, dst]
    elif transfer_mode == 'download' and src and dst:
        argv += ['--get-file', src, dst]

    cmd = ' '.join(_q(a) for a in argv)
    return cmd, argv


def build_evil_winrm_launcher(data: dict) -> str:
    """Build an evil-winrm command string from the NXC panel payload."""
    target = (data.get('target') or '').strip()
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    hash_ = (data.get('hash') or '').strip()
    domain = (data.get('domain') or '').strip()
    auth_mode = (data.get('auth_mode') or 'password').strip()

    if not target or not username:
        return 'evil-winrm -i <target> -u <user> -p <password>'

    argv = ['evil-winrm', '-i', target, '-u', username]

    if auth_mode == 'hash' and hash_:
        argv += ['-H', hash_]
    elif auth_mode == 'kcache':
        # evil-winrm uses --spnego-oid with kcache indirectly; just show -k
        argv.append('-k')
    elif auth_mode == 'kerberos':
        argv.append('-k')
        if password:
            argv += ['-p', password]
    else:
        if password:
            argv += ['-p', password]

    if domain:
        argv += ['-r', domain]

    actions = data.get('actions') or []
    if 'check-https' in actions:
        argv += ['-P', '5986', '-S']

    exec_type = (data.get('exec_type') or '').strip()
    exec_cmd = (data.get('exec_command') or '').strip()
    if exec_type and exec_cmd:
        argv += ['-c', exec_cmd] if exec_type == 'powershell' else ['-e', exec_cmd]

    return ' '.join(_q(a) for a in argv)


# ── output parser ─────────────────────────────────────────────────────────────

# NXC output line format examples:
# SMB  192.168.1.10  445  DC01  [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:corp.local) (signing:True) (SMBv1:False)
# SMB  192.168.1.10  445  DC01  [+] corp.local\admin:Password1! (Pwn3d!)
# SMB  192.168.1.10  445  DC01  [-] corp.local\guest:  STATUS_LOGON_FAILURE
# SMB  192.168.1.10  445  DC01  [*] Enumerated shares
# SMB  192.168.1.10  445  DC01  ADMIN$  READ,WRITE

_LINE_RE = re.compile(
    r'^(?P<proto>\w+)\s+'
    r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+'
    r'(?P<port>\d+)\s+'
    r'(?P<host>\S+)\s+'
    r'(?P<rest>.+)$'
)

_HOST_INFO_RE = re.compile(
    r'\[\*\].*\(name:(?P<name>[^)]+)\).*\(domain:(?P<domain>[^)]+)\)'
    r'.*\(signing:(?P<signing>[^)]+)\).*\(SMBv1:(?P<smbv1>[^)]+)\)'
)

_CRED_OK_RE = re.compile(
    r'\[\+\]\s+(?P<identity>\S+):(?P<secret>\S*)\s*(?P<admin>\(Pwn3d!\))?'
)

_SHARE_RE = re.compile(
    r'(?P<share>\S+)\s+(?P<perm>READ(?:,WRITE)?|WRITE|NO ACCESS)\s*(?P<comment>.*)'
)

_USER_RE = re.compile(r'\[\*\]\s+(?P<user>\S+@\S+|\S+\\[^\s]+|\S+)\s*(?P<detail>.*)')
_GROUP_RE = re.compile(r'\[\*\]\s+(?P<group>.+?)\s*(?:members|->|:)\s*(?P<detail>.*)', re.I)


def parse_netexec_output(raw: str) -> dict:
    result: dict = {
        'summary': {'hosts': 0, 'credentials': 0, 'admin': 0, 'shares': 0, 'errors': 0},
        'indicators': [],
        'credentials': [],
        'hosts': [],
        'shares': [],
        'users': [],
        'groups': [],
        'findings': [],
        'errors': [],
    }
    seen_hosts: set = set()

    for line in raw.splitlines():
        line = line.rstrip()
        if not line:
            continue

        m = _LINE_RE.match(line)
        if not m:
            # Non-standard line — capture as finding if it has signal
            if re.search(r'\[\+\]|\[!\]|Pwn3d', line):
                result['findings'].append({'line': line})
            continue

        proto = m.group('proto').upper()
        ip = m.group('ip')
        host = m.group('host')
        rest = m.group('rest').strip()

        # Host info line
        host_m = _HOST_INFO_RE.search(rest)
        if host_m and ip not in seen_hosts:
            seen_hosts.add(ip)
            result['hosts'].append({
                'protocol': proto,
                'ip': ip,
                'host': host,
                'name': host_m.group('name'),
                'domain': host_m.group('domain'),
                'signing': host_m.group('signing'),
                'smbv1': host_m.group('smbv1'),
            })
            result['summary']['hosts'] += 1
            # Indicator: SMBv1 enabled
            if host_m.group('smbv1').lower() == 'true':
                result['indicators'].append({
                    'label': 'SMBv1 enabled',
                    'host': ip,
                    'line': line,
                    'severity': 'warn',
                })
            # Indicator: signing disabled
            if host_m.group('signing').lower() == 'false':
                result['indicators'].append({
                    'label': 'Signing disabled (relay target)',
                    'host': ip,
                    'line': line,
                    'severity': 'crit',
                })
            continue

        # Credential success
        if rest.startswith('[+]'):
            cred_m = _CRED_OK_RE.search(rest)
            if cred_m:
                is_admin = bool(cred_m.group('admin'))
                result['credentials'].append({
                    'protocol': proto,
                    'host': ip,
                    'identity': cred_m.group('identity'),
                    'secret': cred_m.group('secret'),
                    'admin': is_admin,
                })
                result['summary']['credentials'] += 1
                if is_admin:
                    result['summary']['admin'] += 1
                    result['indicators'].append({
                        'label': 'Admin access',
                        'host': ip,
                        'line': line,
                        'severity': 'crit',
                    })
            else:
                result['findings'].append({'line': line})
            continue

        # Error lines
        if rest.startswith('[-]') or 'STATUS_' in rest:
            result['summary']['errors'] += 1
            result['errors'].append({'line': line})
            continue

        # Share enumeration
        share_m = _SHARE_RE.match(rest)
        if share_m:
            result['shares'].append({
                'host': ip,
                'share': share_m.group('share'),
                'permission': share_m.group('perm'),
                'comment': share_m.group('comment').strip(),
            })
            result['summary']['shares'] += 1
            if 'WRITE' in share_m.group('perm'):
                result['indicators'].append({
                    'label': f"Writable share: {share_m.group('share')}",
                    'host': ip,
                    'line': line,
                    'severity': 'crit',
                })
            continue

        # Info lines → findings
        if rest.startswith('[*]'):
            result['findings'].append({'line': line})

    return result
