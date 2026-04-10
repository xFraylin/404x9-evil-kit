# 404x9-evil-kit

**A local web-based pentesting toolkit for Kali Linux.**  
Built by [@xFraylin](https://github.com/xFraylin)

---

## Features

- Browser-based GUI — no installation of extra GUI frameworks
- Live streaming output via Server-Sent Events (SSE)
- Smart parsed output for every tool (clean tables, no ANSI clutter)
- Isolated Python venv — zero system Python pollution
- Kill switch for any running process (including sudo'd tools)

---

## Included Modules

| Category | Tools |
|---|---|
| **Recon** | Nmap, Subfinder, Amass, WhatWeb, WafW00f |
| **OSINT** | Sherlock, Holehe, DNSRecon, Exiftool |
| **Web** | Gobuster, FFUF, WPScan, Nikto, DalFox, HTTPX, theHarvester |
| **Injection** | SQLMap |
| **Brute Force** | Hydra, Medusa, WFuzz |
| **Hash Cracking** | John the Ripper, Hashcat, HashID |
| **Exploit** | MSFVenom, SearchSploit |
| **Active Directory** | CrackMapExec / NetExec, SMBMap, SMBClient, RPCClient, Enum4linux-ng, LDAPDomainDump, LDAPSearch, Kerbrute, BloodHound-Python, Responder, Mitm6, Evil-WinRM, Impacket suite |
| **Wireless** | Airmon-ng, Airodump-ng, Aireplay-ng, Aircrack-ng — **WiFi Disconnect** automation |
| **Misc** | TCPDump, cURL, Wget |

---

## Instalación rápida (una sola línea)

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/xFraylin/404x9-evil-kit/main/install.sh)"
```

Eso es todo. El script clona el repo, instala las herramientas necesarias, crea el venv e instala todas las dependencias Python adentro.

---

## Requirements

- Kali Linux (or any Debian-based distro)
- Python 3.10+
- Root access for installation

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
3. Copy all files to `/opt/kali-toolkit/`
4. Create an isolated venv at `/opt/kali-toolkit/venv/`
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
# 1. Activate the venv
source /opt/kali-toolkit/venv/bin/activate

# 2. Run the server
cd /opt/kali-toolkit
python3 server.py
```

### Virtual environment reference

```bash
# Activate
source /opt/kali-toolkit/venv/bin/activate

# Verify it's active (should show venv path)
which python
# → /opt/kali-toolkit/venv/bin/python

# Deactivate when done
deactivate
```

> **Note:** `source /opt/kali-toolkit/venv` is **wrong** and does nothing.  
> Always use `source /opt/kali-toolkit/venv/bin/activate`.

---

## Project Structure

```
404x9-evil-kit/
├── server.py           # Flask backend — SSE streaming, process manager
├── requirements.txt    # Python dependencies (installed inside venv)
├── install.sh          # Installer — one-liner compatible
├── run.sh              # Quick launcher (activates venv + starts server)
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
4. **Kill** — `/api/kill/<job_id>` sends SIGTERM + SIGKILL to the entire process group (handles sudo'd tools)

---

## License

MIT — do whatever you want with it.
