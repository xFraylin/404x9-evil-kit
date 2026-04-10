#!/bin/bash
# ============================================================
#  404x9-evil-kit — Instalador
#  by @xfraylin
#
#  Una sola línea:
#    sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/xFraylin/404x9-evil-kit/main/install.sh)"
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO_URL="https://github.com/xFraylin/404x9-evil-kit.git"
INSTALL_DIR="/opt/x9-evilkit"
VENV_DIR="${INSTALL_DIR}/venv"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   404x9-evil-kit — by @xfraylin         ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Ejecutar como root: sudo bash install.sh${NC}"
  exit 1
fi

# ── 1. Clonar si se ejecuta desde curl ───────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)"
if [ ! -f "${SCRIPT_DIR}/server.py" ]; then
  echo -e "${CYAN}[*] Clonando repositorio...${NC}"
  apt-get install -y git -qq
  TMP_DIR="$(mktemp -d)"
  git clone --depth=1 "${REPO_URL}" "${TMP_DIR}/repo" 2>&1 | tail -2
  SCRIPT_DIR="${TMP_DIR}/repo"
fi

# ── 2. Instalar herramientas de sistema (apt ignora las ya instaladas) ────────
echo -e "${CYAN}[*] Instalando herramientas necesarias...${NC}"
apt-get update -qq 2>/dev/null
apt-get install -y -qq \
  python3 python3-venv \
  nmap gobuster ffuf whatweb wafw00f amass \
  wpscan nikto curl wget \
  hydra medusa wfuzz \
  john hashcat hashid \
  exploitdb \
  netexec smbmap smbclient enum4linux-ng ldap-utils responder \
  aircrack-ng \
  exiftool \
  tcpdump netcat-openbsd 2>/dev/null
echo -e "${GREEN}[✓] Herramientas de sistema listas${NC}"

# ── 3. Copiar archivos ────────────────────────────────────────────────────────
echo -e "${CYAN}[*] Copiando archivos a ${INSTALL_DIR}...${NC}"
mkdir -p "${INSTALL_DIR}/templates" "${INSTALL_DIR}/static"
cp "${SCRIPT_DIR}/server.py"            "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/requirements.txt"     "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/templates/index.html" "${INSTALL_DIR}/templates/"
[ -d "${SCRIPT_DIR}/static" ] && cp -r "${SCRIPT_DIR}/static/." "${INSTALL_DIR}/static/"

# ── 4. Crear entorno virtual ──────────────────────────────────────────────────
echo -e "${CYAN}[*] Creando entorno virtual...${NC}"
python3 -m venv "${VENV_DIR}"

# ── 5. Entrar al venv e instalar requirements ─────────────────────────────────
echo -e "${CYAN}[*] Instalando dependencias Python en el venv...${NC}"
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip -q
pip install -r "${INSTALL_DIR}/requirements.txt"
deactivate
echo -e "${GREEN}[✓] Venv listo${NC}"

# ── 6. Crear lanzador ─────────────────────────────────────────────────────────
cat > /usr/local/bin/404x9-evil-kit << EOF
#!/bin/bash
cd ${INSTALL_DIR}
source ${VENV_DIR}/bin/activate
(sleep 1.5 && xdg-open http://localhost:5000 2>/dev/null &)
python3 server.py
EOF
chmod +x /usr/local/bin/404x9-evil-kit
ln -sf /usr/local/bin/404x9-evil-kit /usr/local/bin/x9-evilkit 2>/dev/null

# ── 7. Acceso directo en el escritorio ────────────────────────────────────────
REAL_HOME=$(getent passwd "${SUDO_USER:-$USER}" | cut -d: -f6)
mkdir -p "${REAL_HOME}/Desktop"
cat > "${REAL_HOME}/Desktop/x9-evilkit.desktop" << 'EOF'
[Desktop Entry]
Name=x9 Evil Kit
Comment=Pentesting Web Toolkit
Exec=bash -c '404x9-evil-kit'
Icon=kali-menu
Terminal=true
Type=Application
Categories=Security;
EOF
chmod +x "${REAL_HOME}/Desktop/x9-evilkit.desktop" 2>/dev/null

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   [✓] Instalación completada!           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${YELLOW}Para iniciar:${NC} ${CYAN}404x9-evil-kit${NC}"
echo ""
