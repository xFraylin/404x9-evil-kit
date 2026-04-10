# 404x9-evil-kit

**A local web-based pentesting toolkit for Kali Linux.**  
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
- Scalable wordlist picker — file browser modal + custom path input
- Isolated Python venv — zero system Python pollution
- Kill switch for any running process (including sudo'd tools)

---

## Modules & Tools

### Recon
| Tool | Description |
|---|---|
| **Nmap** | Network scanner. Discovers open ports, services, OS versions and runs NSE scripts for vulnerability detection. |
| **Subfinder** | Passive subdomain enumeration using public sources (DNS, APIs, certificates). |
| **Amass** | In-depth attack surface mapping — subdomains, ASNs, IPs and relationships. |
| **WhatWeb** | Web technology fingerprinting — CMS, frameworks, server versions, analytics platforms. |
| **WafW00f** | Detects and identifies Web Application Firewalls (WAF) protecting a target. |

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
| **Gobuster** | Directory, file and subdomain brute force using wordlists. Fast multi-threaded scanner. |
| **FFUF** | Highly flexible web fuzzer — supports multiple wordlist positions, filters by size/status/words. |
| **WFuzz** | Web application fuzzer focused on parameter tampering, LFI, SQLi and XSS fuzzing. |
| **WPScan** | WordPress-specific scanner — enumerates users, plugins, themes and known vulnerabilities. |
| **Nikto** | Web server scanner that detects dangerous files, outdated software and misconfigurations. |
| **DalFox** | XSS (Cross-Site Scripting) scanner with parameter analysis and PoC generation. |
| **HTTPX** | Fast HTTP toolkit — probes URLs for status, title, tech stack, CDNs and redirect chains. |
| **theHarvester** | Gathers emails, names, subdomains and IPs from public sources (Google, Bing, Shodan, etc.). |

### Injection
| Tool | Description |
|---|---|
| **SQLMap** | Automated SQL injection detection and exploitation — supports all major database backends. |

### Brute Force
| Tool | Description |
|---|---|
| **Hydra** | Network login brute forcer — supports SSH, FTP, HTTP, RDP, SMB, and 50+ protocols. |
| **Medusa** | Parallel network login auditor — similar to Hydra, optimized for speed and modularity. |
| **WFuzz** | Also used for brute forcing web parameters, forms and hidden endpoints. |

### Hash Cracking
| Tool | Description |
|---|---|
| **John the Ripper** | CPU-based password cracker — supports hundreds of hash formats, wordlist + rules modes. |
| **Hashcat** | GPU-accelerated hash cracker — fastest available, supports dictionary, brute force and hybrid attacks. |
| **HashID** | Identifies unknown hash types by analyzing the format and length of the hash. |

### Exploit
| Tool | Description |
|---|---|
| **MSFVenom** | Payload generator from the Metasploit Framework — creates shellcode, executables and reverse shells for any platform. |
| **SearchSploit** | Offline search engine for Exploit-DB — finds public exploits for software versions without internet. |

### Active Directory
| Tool | Description |
|---|---|
| **NetExec / CrackMapExec** | Swiss army knife for Active Directory — SMB/LDAP/WinRM enumeration, credential spraying, lateral movement. |
| **SMBMap** | Enumerates SMB shares, permissions and files across a network. |
| **SMBClient** | Command-line SMB client to browse shares, upload/download files. |
| **RPCClient** | Queries Windows RPC endpoints — user enumeration, domain info, SID lookups. |
| **Enum4linux-ng** | Enumerates Windows/Samba hosts — users, groups, shares, password policies via SMB/RPC. |
| **LDAPDomainDump** | Dumps Active Directory information over LDAP and saves it as HTML/JSON/CSV reports. |
| **LDAPSearch** | Raw LDAP queries against directory services for users, groups, GPOs and more. |
| **Kerbrute** | Kerberos-based username enumeration and password spraying without triggering LDAP lockouts. |
| **BloodHound Python** | Collects AD data (users, groups, ACLs, sessions) to feed into BloodHound for attack path analysis. |
| **Responder** | LLMNR/NBT-NS/MDNS poisoner — captures NTLMv2 hashes from network broadcast traffic. |
| **Mitm6** | IPv6-based man-in-the-middle attack that exploits Windows DHCPv6 to capture credentials. |
| **Evil-WinRM** | WinRM shell for Windows remote management — uploads, downloads, PowerShell bypass and more. |
| **Impacket suite** | Collection of Python scripts: `psexec`, `wmiexec`, `smbexec`, `secretsdump`, `ntlmrelayx`, `GetUserSPNs`, `GetNPUsers` and more. |

### Wireless
| Tool | Description |
|---|---|
| **Airmon-ng** | Puts wireless interfaces into monitor mode, required for all wireless attacks. |
| **Airodump-ng** | Captures 802.11 frames — shows nearby APs, clients, BSSIDs, channels and signal strength. |
| **Aireplay-ng** | Injects wireless frames — used for deauthentication attacks and WEP/WPA handshake capture. |
| **Aircrack-ng** | Cracks WEP keys and WPA/WPA2 handshakes using dictionary attacks. |
| **WiFi Disconnect** | Automated deauth workflow built into the UI — monitor mode → scan → deauth → crack, all in one flow. |

### Misc
| Tool | Description |
|---|---|
| **TCPDump** | Command-line packet capture — filters and inspects live network traffic. |
| **cURL** | HTTP client for crafting and sending custom requests, useful for API testing and exploitation. |
| **Wget** | Recursive file downloader — useful for mirroring sites or downloading exploit files. |

---

## Instalación rápida (una sola línea)

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/xFraylin/404x9-evil-kit/main/install.sh)"
```

El script clona el repo, instala las herramientas necesarias, crea el venv e instala todas las dependencias Python adentro.

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
# 1. Activate the venv
source /opt/x9-evilkit/venv/bin/activate

# 2. Run the server
cd /opt/x9-evilkit
python3 server.py
```

### Virtual environment reference

```bash
# Activate
source /opt/x9-evilkit/venv/bin/activate

# Verify it's active (should show venv path)
which python
# → /opt/x9-evilkit/venv/bin/python

# Deactivate when done
deactivate
```

> **Note:** `source /opt/x9-evilkit/venv` is **wrong** and does nothing.  
> Always use `source /opt/x9-evilkit/venv/bin/activate`.

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
