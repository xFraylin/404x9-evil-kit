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

## Requirements

- Kali Linux (or any Debian-based distro with pentesting tools installed)
- Python 3.10+
- Root access for installation

---

## Installation

```bash
git clone https://github.com/xFraylin/404x9-evil-kit.git
cd 404x9-evil-kit
sudo bash install.sh
```

The installer will:
1. Install `python3-venv` via apt
2. Copy all files to `/opt/kali-toolkit/`
3. Create an isolated venv at `/opt/kali-toolkit/venv/`
4. Install Python dependencies (`flask`, `flask-cors`) inside the venv
5. Create the `/usr/local/bin/404x9-evil-kit` launcher
6. Create a desktop shortcut at `/root/Desktop/kali-toolkit.desktop`

---

## Usage

```bash
404x9-evil-kit
```

Then open your browser at `http://localhost:5000`

The launcher auto-opens the browser after 1.5 seconds.

### Manual start

```bash
cd /opt/kali-toolkit
/opt/kali-toolkit/venv/bin/python3 server.py
```

---

## Project Structure

```
404x9-evil-kit/
├── server.py           # Flask backend — SSE streaming, process manager
├── requirements.txt    # Python dependencies (flask, flask-cors)
├── install.sh          # Installer script
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
