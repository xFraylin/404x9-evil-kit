# 404x9-evil-kit

**A local web-based pentesting toolkit for Kali Linux, Parrot OS, Ubuntu and Debian.**  
Built by [@xFraylin](https://github.com/xFraylin)

---

![404x9-evil-kit preview](static/preview.svg)

---

> **Aviso legal / Disclaimer**  
> Este toolkit es únicamente para uso en entornos autorizados: laboratorios propios, CTFs, pruebas de penetración con permiso explícito del propietario del sistema.  
> **Todo uso es bajo tu exclusiva responsabilidad.** El autor no se hace responsable de ningún uso indebido, ilegal o dañino de esta herramienta.  
> Using this tool against systems you do not own or have explicit permission to test is illegal and unethical.

---

## Features

- Browser-based GUI — no extra GUI frameworks needed
- Live streaming output via Server-Sent Events (SSE)
- Smart parsed output for every tool (clean tables, no ANSI clutter)
- **Interactive ADCS parsed view** — certipy results as clickable pills that expand/collapse per section, with live JSON enrichment
- **AD Enumeration action picker** — choose tool + action, get a syntactically correct command with dependency hints
- **COERCION dynamic path resolution** — locates `coercer`, `PetitPotam.py`, `dfscoerce.py` at runtime after install, no hardcoded paths
- **Tickets inline help** — contextual docs inside getTGT / getST / ticketer tabs: inputs, expected output, common errors
- Scalable wordlist picker — file browser modal + custom path input
- Isolated Python venv — zero system Python pollution; venv is injected into PATH for all subprocesses automatically
- Kill switch for any running process (including sudo'd tools)
- **State persistence** — all sessions, campaigns, credentials and config survive server restarts (`data/state.json`)

---

## Modules & Tools

### Recon
| Tool | Description |
|---|---|
| **Nmap** | Network scanner — open ports, services, OS detection, NSE vulnerability scripts. |
| **Subfinder** | Passive subdomain enumeration using public sources (DNS, APIs, certificates). |
| **Amass** | In-depth attack surface mapping — subdomains, ASNs, IPs and relationships. |
| **theHarvester** | Gathers emails, names, subdomains and IPs from public sources (Google, Bing, Shodan, etc.). |
| **WhatWeb / WAFW00F** | Web technology fingerprinting (WhatWeb) and WAF/protection detection (WAFW00F). |
| **WPScan** | WordPress-specific scanner — enumerates users, plugins, themes and known vulnerabilities. |

### OSINT
| Tool | Description |
|---|---|
| **Sherlock** | Searches hundreds of social networks by username to find accounts linked to a person. |
| **Holehe** | Checks if an email address is registered on popular websites without sending emails. |
| **DNSRecon** | DNS enumeration — zone transfers, brute force subdomains, SRV records, DNSSEC info. |
| **Exiftool** | Extracts metadata from files (images, PDFs, docs) — GPS, author, device, timestamps. |

### Web
| Tool | Description |
|---|---|
| **FFUF** | Highly flexible web fuzzer — multiple wordlist positions, filters by size/status/words. |
| **Gobuster** | Directory, file and subdomain brute force using wordlists. Fast multi-threaded scanner. |
| **Nikto** | Web server scanner that detects dangerous files, outdated software and misconfigurations. |
| **WFuzz** | Web application fuzzer focused on parameter tampering, LFI, SQLi and XSS fuzzing. |
| **DalFox** | XSS scanner with parameter analysis and PoC generation. |

### Injection
| Tool | Description |
|---|---|
| **SQLMap** | Automated SQL injection detection and exploitation — supports all major database backends. |

### Cracking
| Tool | Description |
|---|---|
| **John the Ripper** | CPU-based password cracker — hundreds of hash formats, wordlist + rules modes. |
| **Hashcat** | GPU-accelerated hash cracker — dictionary, brute force and hybrid attacks. |
| **HashID** | Identifies unknown hash types by analyzing format and length. |

### Brute Force
| Tool | Description |
|---|---|
| **Hydra** | Network login brute forcer — SSH, FTP, HTTP, RDP, SMB, and 50+ protocols. |
| **Medusa** | Parallel network login auditor — optimized for speed and modularity. |

### Exploit
| Tool | Description |
|---|---|
| **MSFVenom** | Payload generator from Metasploit — shellcode, executables and reverse shells for any platform. |
| **SearchSploit** | Offline search engine for Exploit-DB — finds public exploits without internet. |

### Active Directory
| Panel | Tools inside | Description |
|---|---|---|
| **Enumeration** | ldapdomaindump, enum4linux-ng, rpcclient, smbclient, ldapsearch, ldeep, adidnsdump, windapsearch | Full domain enumeration — users, groups, shares, GPOs, password policies, AD-integrated DNS. Action-based UX: pick a tool and an action, get a ready-to-run command. |
| **SMB Access** | smbmap, crackmapexec, netexec, nxc | Share enumeration, permission mapping, credential spraying. |
| **Kerberos** | kerbrute, GetUserSPNs.py, GetNPUsers.py | Username enumeration, Kerberoasting and AS-REP Roasting. |
| **Tickets** | getTGT.py, getST.py, ticketer.py | Kerberos ticket operations — request TGTs, obtain impersonation service tickets (S4U2Self/S4U2Proxy), and forge Silver/Golden tickets. Inline contextual help per tab. |
| **Execution** | psexec.py, wmiexec.py, smbexec.py, atexec.py, dcomexec.py | Remote command execution via Impacket. |
| **Credentials** | secretsdump.py | Dumps SAM hashes, NTDS domain hashes and LSA plaintext credentials. |
| **ADCS** | certipy-ad | AD Certificate Services attacks (ESC1–ESC9). Interactive parsed output: counters are clickable pills that expand/collapse detailed sections; JSON enrichment pulls live data from certipy's output file. |
| **ACL / Attacks** | bloodyad, dacledit.py, owneredit.py | ACL-based privilege escalation — GenericAll, RBCD, shadow credentials, ownership changes. |
| **Coercion** | coercer, PetitPotam.py, dfscoerce.py | Authentication coercion attacks (PrinterBug, PetitPotam, DFSCoerce). Dynamic path resolution: locates binaries at runtime via `/api/tools/find-script` after install. |
| **BloodHound** | bloodhound-python, rusthound | AD data collection for attack path analysis. Built-in Neo4j and BloodHound launchers. |
| **MITM** | responder, mitm6, ntlmrelayx.py | LLMNR/NBT-NS/DHCPv6 poisoning and NTLM relay attacks. |

### Network
| Tool | Description |
|---|---|
| **TCPDump** | Packet capture with BPF filters — inspects live traffic, saves to .pcap. |

### Wireless
| Panel | Tools inside | Description |
|---|---|---|
| **Aircrack-NG** | airmon-ng, airodump-ng, aireplay-ng, aircrack-ng | Full WPA attack suite — monitor → scan → handshake → deauth → crack. |
| **WiFi Disconnect** | airmon-ng, airodump-ng, aireplay-ng | Automated deauth workflow with live AP table. |

---

### Mobile Attack Platform (Phishing)

> All features are intended for authorized penetration testing and lab environments only.

A full mobile-focused phishing and credential harvesting platform, accessible from the **Phishing** section of the Spyware module.

#### Templates — Fake Login Pages (12 mobile-optimized)

| Template | Real redirect |
|---|---|
| WhatsApp, Instagram, Facebook, Google, Apple ID | Respective official sites |
| TikTok, Snapchat, Netflix, Twitter/X, Telegram | Respective official sites |
| PayPal, Spotify | Respective official sites |

#### Templates — Social Engineering (12 realistic lures)

| Template | Scenario |
|---|---|
| **Google Survey / SurveyMonkey** | Fake satisfaction survey — collects name, email, phone, DOB |
| **Reddit Forum** | Fake Reddit login with convincing posts about "security breach" |
| **Community Forum** | Generic dark forum login |
| **Amazon Checkout** | Fake cart with item — collects full card details |
| **Shopify Store** | Fake clothing store checkout |
| **News Paywall** | Leaked documents article behind a paywall login |
| **Job Application** | Collects name, DOB, SSN, CV upload |
| **Giveaway / Prize** | Countdown timer, collects name, address, DOB, card |
| **Crypto Wallet (MetaMask)** | Wallet recovery — collects seed phrase + password |
| **Bank Verify** | Fake bank identity check — collects SSN, card, PIN, password |
| **Parcel Tracking (FedEx)** | Failed delivery + $2.99 re-delivery fee — collects card + address |

#### Steal Payloads (JS, inject into any page)

| Payload | What it captures |
|---|---|
| **Cookie Steal** | All cookies via `document.cookie` + image beacon fallback |
| **Session/Storage** | localStorage, sessionStorage, IndexedDB keys |
| **Form Hijacker** | Intercepts all form submits, captures every field |
| **Keylogger** | Buffered keystrokes with active field name |
| **Camera Capture** | Silent photo via `getUserMedia` (640×480 JPEG → C2) |
| **Mic Record** | 15s audio recording → base64 → C2 |
| **FULL Payload** | All of the above combined + geolocation |
| **Clickjacking** | Logs every click (XY, element, text), form submits, focus/blur |
| **Permission Reuse** | Checks `navigator.permissions.query` — captures silently if camera/mic/geo already granted |
| **XSS Probe** | 5 ready-to-paste variants: reflected, onerror, SVG, eval(atob), full stored |
| **Obfuscated** | base64+eval wrapper, anti-bot gate, self-deletes from DOM, viewport check |
| **Anti-Detect** | Headless browser kill, right-click block, F12 trap, console wipe, URL/title spoof |

#### Exfil Config

- **C2 Local** — LHOST + PORT (default `localhost:5000`)
- **Custom URL** — full endpoint, e.g. `https://xxxx.ngrok.io/api/phish/capture`
- **Telegram Exfil** — bot token + chat ID stored server-side; all captures forwarded automatically via Telegram Bot API. Token is never exposed in the JS payload delivered to the victim.

#### Deploy System

- **DEPLOY TO C2** — saves HTML to server, returns a clean public URL (`/p/<id>`)
- **Auto-inject FULL payload** — injects the steal script before `</body>` automatically on deploy
- **Redirect URL** — auto-filled per template (Instagram → instagram.com, Amazon → amazon.com, etc.); editable manually. Victim is redirected to the real site after submitting — no error shown.
- **Deployed Sites panel** — live status (ACTIVE / STOPPED) with STOP / RESTART / LOAD / ⎘ URL buttons; persists across restarts

#### APK Builder

Generates `msfvenom android/meterpreter/reverse_tcp` command with feature flags:

| Feature | Meterpreter post command |
|---|---|
| SMS exfil | `dump_sms` |
| Contacts | `dump_contacts` |
| GPS | `geolocate` |
| Camera | `webcam_snap` |
| Microphone | `record_mic -d 30` |
| File access | `download /sdcard` |
| Persistence | `run app_install` |

#### Termux Beacon Generator

Python beacon for Android (via Termux) — checks in to C2, runs `termux-sms-list`, `termux-contact-list`, `termux-location`, `termux-camera-photo`, `termux-microphone-record` based on selected features.

#### Campaigns, Tracker & Logs

- **Campaigns** — create campaigns with name, template, redirect URL, targets (email / phone); start/stop per campaign
- **Tracker** — per-target status: pending → sent → opened → clicked → captured
- **Logs** — real-time log of all hits, submits and captures with IP, UA, timestamp and data

#### GUIDE Tab

Step-by-step usage guide for every attack technique — Clickjacking setup, Permission Reuse with ngrok, XSS injection types, Obfuscation payload generation, Anti-forensics combos, APK delivery + Meterpreter post-exploitation, full campaign flow.

---

### Spyware (Post-Exploitation C2)

| Panel | Description |
|---|---|
| **Payload Builder** | Generates Python HTTP beacons, MSFVenom stagers, PowerShell download cradles / AMSI bypasses. |
| **C2 Server** | Built-in HTTP C2. Sessions table with alive/dead status, command console with result polling, full session history. |

**How the C2 works:**
1. Generate a Python beacon from **Payload Builder → HTTP Beacon**
2. Deploy it on the target (`python3 beacon.py`)
3. Session appears in **C2 Server → Sessions** within seconds
4. Send commands from the **Console** tab — results arrive on next check-in

---

### Priv Esc
| Panel | Description |
|---|---|
| **Priv Esc** | Cheatsheet — Linux (SUID/SGID, cron, writable paths, shadow) / Windows (registry, services, stored creds) / GTFOBins / TTY Upgrade. |
| **Rev Shells** | Reverse shell one-liners — Bash, Python, Netcat, PHP/Perl, Windows/PowerShell, Listeners. |
| **LINPEAS / WINPEAS** | Download + run commands for PEASS-ng scripts + built-in HTTP server to serve them. |

### Utils
| Tool | Description |
|---|---|
| **cURL** | Advanced HTTP client — custom headers, methods, body, auth, proxy, cookies. |
| **Wget** | Recursive file downloader — mirror sites, download files from targets. |
| **HTTPX** | Fast HTTP toolkit — probes URLs for status, title, tech, CDNs and redirect chains. |
| **Encoder** | Client-side encode/decode chain — URL, HTML, Base64, Hex, Unicode, JSON, ROT13, MD5, SHA1/256. |

### System
| Panel | Description |
|---|---|
| **Herramientas** | Visual status grid of installed tools with one-click install shortcuts. |
| **Archivos** | File browser for `/tmp` and `/root`. |
| **Historial** | Session command history with clear option. |
| **Evidencia** | Reports panel — full list of all past executions with search, export and delete. |

---

## Reports / Evidencia

Every command execution auto-generates a structured report and injects action buttons directly into the tool's output toolbar.

### Toolbar (after execution)

```
LIVE OUTPUT — NETEXEC    [RAW] [PARSED] [REPORT] [PDF] [WORD] [JSON] [⎘ COPY] [CLEAR]
```

- **REPORT** — opens a full-screen modal with the cyberpunk dark theme: metadata cards, findings, indicators, errors, evidence, parsed output, and raw output (collapsible sections).
- **PDF** — downloads a real `.pdf` file (generated server-side with WeasyPrint). Parsed output is rendered as actual HTML (tables stay tables, lists stay lists). Uses a clean light theme for print.
- **WORD** — downloads a `.docx` file (python-docx). HTML tables are converted to native Word tables; lists to `List Bullet` style paragraphs.
- **JSON** — downloads the parsed output as `.json`.

For **NetExec** specifically, the buttons are integrated statically into the `LIVE OUTPUT — NETEXEC` panel header and are disabled until a command completes. Once the job finishes and the output is parsed, they enable automatically with the correct `reportId`.

### Report content

| Field | Description |
|---|---|
| Tool | Tool name extracted from the command |
| Target | IP / domain auto-extracted from arguments |
| Command | Full command run, with passwords and hashes masked |
| Credentials used | Auth type (password / NTLM hash / Kerberos) — values never stored |
| Summary | Auto-generated one-line summary |
| Findings | Lines matching `[+]`, `Pwn3d!`, `ADMIN`, `VULNERABLE`, etc. |
| Indicators | SMB signing disabled, null auth, ASREP, open ports, DC/domain, etc. |
| Errors | Timeout, refused, traceback, authentication failures |
| Evidence | IPs, hashes, certificate thumbprints, SPN strings |
| Parsed output | Full rendered HTML from the tool's parsed panel |
| Raw output | Complete terminal output |

### Persistence

All reports are saved to `data/reports.json` and survive server restarts.

### Backend routes

| Route | Description |
|---|---|
| `GET /api/reports` | List all reports |
| `POST /api/reports/save` | Save new report |
| `GET /api/reports/<rid>` | Get report JSON |
| `DELETE /api/reports/<rid>` | Delete one report |
| `DELETE /api/reports` | Clear all reports |
| `GET /api/reports/<rid>/view` | HTML report page (dark cyberpunk theme) |
| `GET /api/reports/<rid>/export/pdf` | Download PDF (WeasyPrint) |
| `GET /api/reports/<rid>/export/docx` | Download Word document |
| `GET /api/reports/<rid>/raw` | Download raw output as `.txt` |
| `GET /api/reports/<rid>/parsed` | Download parsed output as `.json` |

### Python dependencies added

`python-docx` (Word export), `weasyprint` (PDF generation)

---

## State Persistence

All mutable data is automatically saved to `data/state.json` after every mutation and restored on server startup:

| Data | Persists |
|---|---|
| Campaigns, targets, stats | ✓ |
| Captured credentials (logs) | ✓ |
| Deployed pages + active/stopped state | ✓ |
| Telegram config (token, chat ID, enabled) | ✓ |
| Cloned sites metadata | ✓ |
| Phishing tracking IDs | ✓ |

Saves are atomic (write to `.tmp` → `os.replace`) — no corruption on crash.

---

## Instalación rápida (una sola línea)

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/xFraylin/404x9-evil-kit/main/install.sh)"
```

El script clona el repo, instala las herramientas necesarias, crea el venv e instala todas las dependencias Python adentro.

---

## Sistemas operativos compatibles

| Sistema | Versión | Estado |
|---|---|---|
| **Kali Linux** | Rolling | ✅ Recomendado — entorno nativo |
| **Parrot OS** | 5.x / 6.x | ✅ Compatible |
| **Ubuntu** | 20.04 / 22.04 / 24.04 | ✅ Compatible |
| **Debian** | 11 (Bullseye) / 12 (Bookworm) | ✅ Compatible |
| **Linux Mint** | 21.x / 22.x | ✅ Compatible (base Ubuntu) |
| **Zorin OS** | 16 / 17 | ✅ Compatible (base Ubuntu) |
| **Pop!\_OS** | 22.04 | ✅ Compatible |
| Otro derivado Debian/Ubuntu | — | ⚠️ Probablemente compatible |
| Arch / Fedora / openSUSE / etc. | — | ❌ No soportado (requiere `apt`) |

## Requirements

- Sistema Debian/Ubuntu (ver tabla arriba)
- Python 3.10+
- Root access para la instalación

### Python dependencies (auto-installed in venv)

`flask`, `flask-cors`, `sqlmap`, `impacket`, `dnsrecon`, `holehe`, `theharvester`, `sherlock-project`, `bloodhound`, `ldapdomaindump`, `mitm6`, `certipy-ad`, `bloodyad`, `coercer`, `adidnsdump`, `ldeep`, `ldap3`, `gssapi`

---

## Installation (manual)

```bash
git clone https://github.com/xFraylin/404x9-evil-kit.git
cd 404x9-evil-kit
sudo bash install.sh
```

The installer will:
1. Clone the repo automatically if run via `curl`
2. Install system binaries via `apt` (skips already installed tools)
3. Copy all files to `/opt/x9-evilkit/`
4. Create an isolated venv at `/opt/x9-evilkit/venv/`
5. Activate the venv and install all Python dependencies from `requirements.txt`
6. Create the `/usr/local/bin/404x9-evil-kit` launcher
7. Create a desktop shortcut

---

## Usage

```bash
404x9-evil-kit
```

The launcher activates the venv automatically and opens `http://localhost:5000` in your browser.

### Manual start

```bash
source /opt/x9-evilkit/venv/bin/activate
cd /opt/x9-evilkit
python3 server.py
```

---

## Project Structure

```
404x9-evil-kit/
├── server.py           # Flask backend — SSE streaming, phishing engine, C2, persistence
├── requirements.txt    # Python dependencies (installed inside venv)
├── install.sh          # Installer — one-liner compatible
├── run.sh              # Quick launcher (activates venv + starts server)
├── data/
│   └── state.json      # Persistent state (auto-created on first run)
├── templates/
│   └── index.html      # Full single-page frontend
└── static/
    └── favicon.ico     # Skull favicon
```

---

## How It Works

1. **Frontend** (`index.html`) sends commands to the Flask backend via POST to `/api/run`
2. **Backend** spawns the process and streams output line-by-line via `/api/stream/<job_id>` (SSE)
3. **Frontend** buffers all output and runs tool-specific parsers on completion to render clean tables
4. **Kill** — `/api/kill/<job_id>` sends SIGTERM + SIGKILL to the entire process group
5. **Phishing** — deployed pages served at `/p/<id>`; form submits captured server-side and forwarded to Telegram if configured

---

## License

MIT — do whatever you want with it.
