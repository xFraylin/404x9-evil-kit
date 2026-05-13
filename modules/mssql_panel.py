"""
mssql_panel.py — SQLCMD / SQL Server command builder, query runner, and helpers
for the 404x9-evil-kit server.
"""

import os
import re
import shlex
import socket
import subprocess

# ── sqlcmd resolver ───────────────────────────────────────────────────────────

_SQLCMD_SEARCH_DIRS = [
    '/opt/mssql-tools18/bin',
    '/opt/mssql-tools/bin',
    '/usr/local/bin',
    '/usr/bin',
    '/usr/local/mssql-tools/bin',
]

_sqlcmd_path_cache: str | None = None


def _find_sqlcmd() -> str:
    global _sqlcmd_path_cache
    if _sqlcmd_path_cache:
        return _sqlcmd_path_cache
    # Check PATH
    r = subprocess.run(['which', 'sqlcmd'], capture_output=True, text=True, timeout=3)
    if r.returncode == 0 and r.stdout.strip():
        _sqlcmd_path_cache = r.stdout.strip()
        return _sqlcmd_path_cache
    # Fallback: well-known install dirs
    for d in _SQLCMD_SEARCH_DIRS:
        p = os.path.join(d, 'sqlcmd')
        if os.path.isfile(p) and os.access(p, os.X_OK):
            _sqlcmd_path_cache = p
            return p
    return 'sqlcmd'  # will surface a clear FileNotFoundError


def _mssql_env_path() -> str:
    """Return a PATH string that includes mssql-tools dirs."""
    extra = ':'.join(_SQLCMD_SEARCH_DIRS)
    return extra + ':' + os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')


# ── SQL query library ─────────────────────────────────────────────────────────

SQL = {
    'server_version': "SELECT @@VERSION AS version;",
    'current_user': (
        "SELECT SYSTEM_USER AS system_user, USER_NAME() AS database_user;"
    ),
    'current_database': "SELECT DB_NAME() AS current_database;",
    'server_time': "SELECT GETDATE() AS server_time;",
    'list_databases': "SELECT name FROM sys.databases ORDER BY name;",
    'show_schemas': "SELECT name FROM sys.schemas ORDER BY name;",
    'list_tables': (
        "SELECT TABLE_SCHEMA, TABLE_NAME "
        "FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_TYPE = 'BASE TABLE' "
        "ORDER BY TABLE_SCHEMA, TABLE_NAME;"
    ),
    'db_size': (
        "SELECT f.name AS logical_name, "
        "ROUND(f.size * 8.0 / 1024, 2) AS size_mb, "
        "DB_NAME(f.database_id) AS db_name "
        "FROM sys.master_files f "
        "WHERE f.type_desc = 'ROWS' "
        "ORDER BY size_mb DESC;"
    ),
    'active_db': "SELECT DB_NAME() AS active_database;",
    'active_connections': (
        "SELECT DB_NAME(database_id) AS database_name, COUNT(*) AS connections "
        "FROM sys.dm_exec_sessions "
        "WHERE is_user_process = 1 "
        "GROUP BY database_id "
        "ORDER BY connections DESC;"
    ),
    'running_queries': (
        "SELECT r.session_id, r.status, r.command, "
        "r.cpu_time, r.total_elapsed_time, "
        "SUBSTRING(t.text, 1, 300) AS sql_text "
        "FROM sys.dm_exec_requests r "
        "CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t "
        "WHERE r.session_id <> @@SPID;"
    ),
    'sessions': (
        "SELECT session_id, login_name, host_name, program_name, status, "
        "CONVERT(varchar(20), login_time, 120) AS login_time "
        "FROM sys.dm_exec_sessions "
        "WHERE is_user_process = 1 "
        "ORDER BY login_time DESC;"
    ),
    'locks': (
        "SELECT request_session_id, resource_type, "
        "DB_NAME(resource_database_id) AS database_name, "
        "request_mode, request_status "
        "FROM sys.dm_tran_locks "
        "WHERE request_session_id <> @@SPID "
        "ORDER BY request_session_id;"
    ),
    'db_users': (
        "SELECT name, type_desc, "
        "CONVERT(varchar(20), create_date, 120) AS create_date "
        "FROM sys.database_principals "
        "WHERE type NOT IN ('R', 'A') "
        "ORDER BY name;"
    ),
    'permissions': (
        "SELECT USER_NAME(grantee_principal_id) AS grantee, "
        "class_desc, permission_name, state_desc "
        "FROM sys.database_permissions "
        "ORDER BY grantee, class_desc, permission_name;"
    ),
    'timeout_test': (
        "SELECT GETDATE() AS before_wait; "
        "WAITFOR DELAY '00:00:03'; "
        "SELECT GETDATE() AS after_wait;"
    ),
}

# ── Validation ────────────────────────────────────────────────────────────────

_HOST_RE  = re.compile(r'^[a-zA-Z0-9._\-\\]+$')
_PORT_RE  = re.compile(r'^\d{1,5}$')
_DB_RE    = re.compile(r'^[a-zA-Z0-9_\-. #]+$')
_USER_RE  = re.compile(r'^[a-zA-Z0-9_\-\\.@]+$')
_NAME_RE  = re.compile(r'^[a-zA-Z0-9_#@ ]+$')
_DIGIT_RE = re.compile(r'^\d+$')

_DANGEROUS = re.compile(
    r'\b(DROP\s+TABLE|DROP\s+DATABASE|TRUNCATE\s+TABLE|FORMAT\s*\()'
    r'|DELETE\s+FROM\s+\S+'
    r'|UPDATE\s+\S+\s+SET'
    r'|\bKILL\b',
    re.I,
)


def validate_conn(conn: dict) -> None:
    host = str(conn.get('host', '')).strip()
    port = str(conn.get('port', '1433')).strip()
    user = str(conn.get('username', '')).strip()

    if not host:
        raise ValueError("Host requerido")
    if not _HOST_RE.match(host):
        raise ValueError(f"Host invalido: {host!r}")
    if not _PORT_RE.match(port) or not (1 <= int(port) <= 65535):
        raise ValueError(f"Puerto invalido: {port!r}")
    if not user:
        raise ValueError("Usuario requerido")
    if not _USER_RE.match(user):
        raise ValueError(f"Usuario invalido: {user!r}")
    db = str(conn.get('database', '')).strip()
    if db and not _DB_RE.match(db):
        raise ValueError(f"Base de datos invalida: {db!r}")


def _sql_bracket(name: str) -> str:
    name = name.strip()
    if not _NAME_RE.match(name):
        raise ValueError(f"Nombre de objeto invalido: {name!r}")
    return '[' + name.replace(']', ']]') + ']'


def _sql_str(value: str) -> str:
    return "N'" + value.replace("'", "''") + "'"


def is_dangerous(sql: str) -> bool:
    return bool(_DANGEROUS.search(sql))


# ── Parameterized query builders ──────────────────────────────────────────────

def build_query(action: str, params: dict = None) -> str:
    params = params or {}

    if action in SQL:
        return SQL[action]

    schema = params.get('schema', 'dbo').strip()
    table  = params.get('table', '').strip()
    limit  = min(abs(int(params.get('limit', 10) or 10)), 5000)
    col    = params.get('column', '').strip()
    search = params.get('search', '').strip()
    sid    = params.get('session_id', '').strip()
    page   = max(1, int(params.get('page', 1) or 1))
    offset = (page - 1) * limit

    if action == 'show_columns':
        if not table:
            raise ValueError("Tabla requerida")
        return (
            f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, "
            f"CHARACTER_MAXIMUM_LENGTH, COLUMN_DEFAULT "
            f"FROM INFORMATION_SCHEMA.COLUMNS "
            f"WHERE TABLE_SCHEMA = {_sql_str(schema)} "
            f"AND TABLE_NAME = {_sql_str(table)} "
            f"ORDER BY ORDINAL_POSITION;"
        )
    elif action == 'describe_table':
        if not table:
            raise ValueError("Tabla requerida")
        return (
            f"SELECT c.COLUMN_NAME, c.DATA_TYPE, c.IS_NULLABLE, "
            f"c.CHARACTER_MAXIMUM_LENGTH, c.COLUMN_DEFAULT, "
            f"COLUMNPROPERTY(OBJECT_ID({_sql_str(schema + '.' + table)}), "
            f"c.COLUMN_NAME, 'IsIdentity') AS is_identity "
            f"FROM INFORMATION_SCHEMA.COLUMNS c "
            f"WHERE c.TABLE_SCHEMA = {_sql_str(schema)} "
            f"AND c.TABLE_NAME = {_sql_str(table)} "
            f"ORDER BY c.ORDINAL_POSITION;"
        )
    elif action == 'primary_keys':
        if not table:
            raise ValueError("Tabla requerida")
        return (
            f"SELECT KU.COLUMN_NAME, KU.ORDINAL_POSITION "
            f"FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS TC "
            f"JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KU "
            f"ON TC.CONSTRAINT_NAME = KU.CONSTRAINT_NAME "
            f"WHERE TC.CONSTRAINT_TYPE = 'PRIMARY KEY' "
            f"AND KU.TABLE_SCHEMA = {_sql_str(schema)} "
            f"AND KU.TABLE_NAME = {_sql_str(table)} "
            f"ORDER BY KU.ORDINAL_POSITION;"
        )
    elif action == 'foreign_keys':
        if not table:
            raise ValueError("Tabla requerida")
        return (
            f"SELECT fk.name AS foreign_key, "
            f"COL_NAME(fc.parent_object_id, fc.parent_column_id) AS column_name, "
            f"OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS ref_schema, "
            f"OBJECT_NAME(fk.referenced_object_id) AS ref_table, "
            f"COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS ref_column "
            f"FROM sys.foreign_keys fk "
            f"JOIN sys.foreign_key_columns fc "
            f"ON fk.object_id = fc.constraint_object_id "
            f"WHERE OBJECT_SCHEMA_NAME(fk.parent_object_id) = {_sql_str(schema)} "
            f"AND OBJECT_NAME(fk.parent_object_id) = {_sql_str(table)};"
        )
    elif action == 'indexes':
        if not table:
            raise ValueError("Tabla requerida")
        return (
            f"SELECT i.name AS index_name, i.type_desc, "
            f"c.name AS column_name, i.is_unique, i.is_primary_key "
            f"FROM sys.indexes i "
            f"JOIN sys.index_columns ic "
            f"ON i.object_id = ic.object_id AND i.index_id = ic.index_id "
            f"JOIN sys.columns c "
            f"ON ic.object_id = c.object_id AND ic.column_id = c.column_id "
            f"WHERE OBJECT_SCHEMA_NAME(i.object_id) = {_sql_str(schema)} "
            f"AND OBJECT_NAME(i.object_id) = {_sql_str(table)} "
            f"ORDER BY i.name, ic.key_ordinal;"
        )
    elif action == 'count_rows':
        if not table:
            raise ValueError("Tabla requerida")
        return (
            f"SELECT COUNT(*) AS total_rows "
            f"FROM {_sql_bracket(schema)}.{_sql_bracket(table)};"
        )
    elif action in ('preview', 'select_top_n'):
        if not table:
            raise ValueError("Tabla requerida")
        return (
            f"SELECT TOP {limit} * "
            f"FROM {_sql_bracket(schema)}.{_sql_bracket(table)};"
        )
    elif action == 'paginated':
        if not table:
            raise ValueError("Tabla requerida")
        return (
            f"SELECT * FROM {_sql_bracket(schema)}.{_sql_bracket(table)} "
            f"ORDER BY (SELECT NULL) "
            f"OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY;"
        )
    elif action == 'list_tables_by_schema':
        return (
            f"SELECT TABLE_SCHEMA, TABLE_NAME "
            f"FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_TYPE = 'BASE TABLE' "
            f"AND TABLE_SCHEMA = {_sql_str(schema)} "
            f"ORDER BY TABLE_NAME;"
        )
    elif action == 'search_table_name':
        return (
            f"SELECT TABLE_SCHEMA, TABLE_NAME "
            f"FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_TYPE = 'BASE TABLE' "
            f"AND TABLE_NAME LIKE {_sql_str('%' + search + '%')} "
            f"ORDER BY TABLE_SCHEMA, TABLE_NAME;"
        )
    elif action == 'search_text_in_table':
        if not table:
            raise ValueError("Tabla requerida")
        if not col:
            raise ValueError("Columna requerida para busqueda de texto")
        return (
            f"SELECT * FROM {_sql_bracket(schema)}.{_sql_bracket(table)} "
            f"WHERE CAST({_sql_bracket(col)} AS NVARCHAR(MAX)) "
            f"LIKE {_sql_str('%' + search + '%')};"
        )
    elif action == 'kill_session':
        if not sid or not _DIGIT_RE.match(sid):
            raise ValueError(f"Session ID invalido: {sid!r}")
        return f"KILL {int(sid)};"
    elif action == 'use_database':
        db = params.get('database', '').strip()
        if not db or not _DB_RE.match(db):
            raise ValueError(f"Base de datos invalida: {db!r}")
        return f"USE {_sql_bracket(db)};"
    elif action == 'export_table_csv':
        if not table:
            raise ValueError("Tabla requerida")
        return f"SELECT * FROM {_sql_bracket(schema)}.{_sql_bracket(table)};"

    elif action == 'search_all_text':
        term = (params.get('term') or '').strip()
        if not term:
            raise ValueError("Término de búsqueda requerido")
        term_esc = term.replace("'", "''")
        return (
            f"DECLARE @term NVARCHAR(200) = N'%{term_esc}%';\n"
            "DECLARE @sql NVARCHAR(MAX) = N'';\n"
            "SELECT @sql = @sql + N' UNION ALL SELECT TOP 5 ''' + TABLE_SCHEMA + N'.' + TABLE_NAME + N''' AS [table], ''' + COLUMN_NAME + N''' AS [column], CAST(' + QUOTENAME(COLUMN_NAME) + N' AS NVARCHAR(200)) AS [value] FROM ' + QUOTENAME(TABLE_SCHEMA) + N'.' + QUOTENAME(TABLE_NAME) + N' WHERE CAST(' + QUOTENAME(COLUMN_NAME) + N' AS NVARCHAR(MAX)) LIKE @t'\n"
            "FROM INFORMATION_SCHEMA.COLUMNS\n"
            "WHERE DATA_TYPE IN ('char','varchar','nchar','nvarchar','text','ntext')\n"
            "  AND TABLE_SCHEMA NOT IN ('sys','INFORMATION_SCHEMA');\n"
            "IF LEN(@sql) > 0 BEGIN\n"
            "    SET @sql = STUFF(@sql, 1, 11, '');\n"
            "    EXEC sp_executesql @sql, N'@t NVARCHAR(200)', @t = @term;\n"
            "END ELSE SELECT 'Sin columnas de texto en esta DB' AS info;"
        )

    raise ValueError(f"Accion desconocida: {action!r}")


# ── Command builder ───────────────────────────────────────────────────────────

def build_sqlcmd_cmd(conn: dict, sql: str, output_file: str = None) -> tuple:
    """
    Build sqlcmd argv and env dict.
    Password is passed via SQLCMDPASSWORD env var — never on the command line.
    Returns (display_cmd_str, argv_list, env_dict).
    """
    validate_conn(conn)

    host = str(conn['host']).strip()
    port = str(conn.get('port', '1433')).strip() or '1433'
    db   = str(conn.get('database', '')).strip()
    user = str(conn['username']).strip()
    pwd  = conn.get('password', '')

    server   = f"{host},{port}"
    sqlcmd   = _find_sqlcmd()
    argv     = [sqlcmd, '-S', server, '-U', user, '-C', '-W', '-s', '|', '-r', '1']
    if db:
        argv += ['-d', db]
    if output_file:
        argv += ['-o', output_file]
    argv += ['-Q', sql.strip()]

    # Password via env var only — never on the command line.
    # PATH not overridden here: argv[0] is already a resolved absolute path,
    # so the shell / subprocess will find it regardless of $PATH.
    env     = {'SQLCMDPASSWORD': pwd}
    display = ' '.join(shlex.quote(a) for a in argv)
    return display, argv, env


# ── Synchronous query runner (for dropdowns / auto-load) ──────────────────────

def run_query_sync(conn: dict, sql: str, timeout: int = 12) -> dict:
    """Run a SQL query synchronously. Returns {ok, rows, headers, error}."""
    try:
        _, argv, env = build_sqlcmd_cmd(conn, sql)
    except ValueError as e:
        return {'ok': False, 'error': str(e), 'rows': [], 'headers': []}

    env_full = os.environ.copy()
    env_full['PATH'] = _mssql_env_path()
    env_full.update(env)   # SQLCMDPASSWORD on top

    try:
        r = subprocess.run(
            argv, capture_output=True, text=True,
            timeout=timeout, env=env_full,
        )
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': 'Timeout al conectar', 'rows': [], 'headers': []}
    except FileNotFoundError:
        return {
            'ok': False,
            'error': (
                'sqlcmd no encontrado.\n'
                'Instala: apt-get install -y mssql-tools18 unixodbc-dev\n'
                'Luego agrega a PATH: export PATH=$PATH:/opt/mssql-tools18/bin'
            ),
            'rows': [], 'headers': [],
        }
    except Exception as e:
        return {'ok': False, 'error': str(e), 'rows': [], 'headers': []}

    stderr = (r.stderr or '').strip()
    stdout = (r.stdout or '').strip()

    if r.returncode != 0:
        err = stderr or stdout or 'Error desconocido'
        return {'ok': False, 'error': err, 'rows': [], 'headers': []}

    rows, headers = _parse_pipe_output(stdout)
    return {'ok': True, 'rows': rows, 'headers': headers, 'raw': stdout}


def _parse_pipe_output(raw: str) -> tuple:
    """Parse sqlcmd pipe-delimited output into (rows_list, headers_list)."""
    lines = []
    for ln in raw.splitlines():
        stripped = ln.strip()
        if not stripped:
            continue
        if re.match(r'^-+(\|-+)*$', stripped):
            continue
        if re.match(r'^\(\d+\s+rows?\s+affected\)', stripped, re.I):
            continue
        lines.append(stripped)

    if not lines:
        return [], []

    headers = [h.strip() for h in lines[0].split('|')]
    rows = []
    for line in lines[1:]:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) == len(headers):
            rows.append(dict(zip(headers, parts)))
        elif parts and any(p for p in parts):
            rows.append({'_raw': '|'.join(parts)})
    return rows, headers


# ── Tool / environment checks ─────────────────────────────────────────────────

def check_sqlcmd_installed() -> dict:
    global _sqlcmd_path_cache
    _sqlcmd_path_cache = None  # bust cache so we always re-probe
    path  = _find_sqlcmd()
    found = path != 'sqlcmd' and os.path.isfile(path)
    version = None
    if found:
        env_full = os.environ.copy()
        env_full['PATH'] = _mssql_env_path()
        vr = subprocess.run([path, '-?'], capture_output=True, text=True, timeout=3, env=env_full)
        m  = re.search(r'(?:Sqlcmd|Version)\s*[:\s]+([\d.]+)', vr.stdout + vr.stderr, re.I)
        if m:
            version = m.group(1)
    return {'found': found, 'path': path if found else '', 'version': version}


def check_odbc_drivers() -> dict:
    drivers = []
    r = subprocess.run(['odbcinst', '-q', '-d'], capture_output=True, text=True, timeout=3)
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            m = re.match(r'^\[(.+)\]$', line.strip())
            if m and m.group(1) not in drivers:
                drivers.append(m.group(1))
    try:
        import pyodbc
        for d in pyodbc.drivers():
            if d not in drivers:
                drivers.append(d)
    except Exception:
        pass
    return {'found': bool(drivers), 'drivers': drivers}


def check_tcp_port(host: str, port: int, timeout: float = 3.0) -> dict:
    try:
        if not _HOST_RE.match(str(host).strip()):
            raise ValueError(f"Host invalido: {host!r}")
        with socket.create_connection((str(host).strip(), int(port)), timeout=timeout):
            return {'open': True, 'host': host, 'port': port}
    except Exception as e:
        return {'open': False, 'host': host, 'port': port, 'error': str(e)}
