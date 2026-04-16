#!/bin/bash
# ============================================================
#  404x9-evil-kit — Instalador / Actualizador
#  by @xfraylin
#
#  Instalación inicial:
#    sudo bash install.sh
#
#  Actualización (después de git pull):
#    sudo bash install.sh
#
#  Forzar reinstalación completa:
#    sudo bash install.sh --force
#
#  Una línea (instala desde cero):
#    sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/xFraylin/404x9-evil-kit/main/install.sh)"
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[0;90m'
NC='\033[0m'

REPO_URL="https://github.com/xFraylin/404x9-evil-kit.git"
INSTALL_DIR="/opt/x9-evilkit"
VENV_DIR="${INSTALL_DIR}/venv"
REQ_HASH_FILE="${INSTALL_DIR}/.req_hash"

# ── Argument parsing ──────────────────────────────────────
FORCE=false
for arg in "$@"; do [ "$arg" = "--force" ] && FORCE=true; done

# ── Root check ────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Ejecutar como root: sudo bash install.sh${NC}"
  exit 1
fi

# ── Bootstrap desde curl ──────────────────────────────────
# Este bloque corre ANTES del banner para que el exec no duplique
# la salida. Si no hay server.py en el CWD, clona el repo y
# re-ejecuta este mismo script desde la copia fresca.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)"
if [ ! -f "${SCRIPT_DIR}/server.py" ]; then
  echo -e "${CYAN}[*] Descargando 404x9-evil-kit...${NC}"
  apt-get install -y git -qq
  TMP_DIR="$(mktemp -d)"
  git clone --depth=1 "${REPO_URL}" "${TMP_DIR}/repo" -q
  exec bash "${TMP_DIR}/repo/install.sh" "$@"
fi

# ── Banner ────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   404x9-evil-kit — by @xfraylin         ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Detección de sistema operativo ───────────────────────
OS_ID=""
OS_VERSION_ID=""
OS_PRETTY=""
if [ -f /etc/os-release ]; then
  OS_ID=$(grep -oP '(?<=^ID=)[^\n]+' /etc/os-release | tr -d '"' | tr '[:upper:]' '[:lower:]')
  OS_VERSION_ID=$(grep -oP '(?<=^VERSION_ID=)[^\n]+' /etc/os-release | tr -d '"')
  OS_PRETTY=$(grep -oP '(?<=^PRETTY_NAME=)[^\n]+' /etc/os-release | tr -d '"')
fi
OS_ID_LIKE=$(grep -oP '(?<=^ID_LIKE=)[^\n]+' /etc/os-release 2>/dev/null | tr -d '"' | tr '[:upper:]' '[:lower:]')

case "$OS_ID" in
  kali)
    OS_STATUS="ok"; OS_NOTE="Compatibilidad total — entorno recomendado" ;;
  parrot)
    OS_STATUS="ok"; OS_NOTE="Compatibilidad total" ;;
  ubuntu)
    case "$OS_VERSION_ID" in
      20.04|22.04|24.04|24.10) OS_STATUS="ok"; OS_NOTE="Compatibilidad total" ;;
      *) OS_STATUS="warn"; OS_NOTE="Versión no probada — puede funcionar" ;;
    esac ;;
  debian)
    case "$OS_VERSION_ID" in
      11|12|13) OS_STATUS="ok"; OS_NOTE="Compatible" ;;
      *) OS_STATUS="warn"; OS_NOTE="Versión no probada — puede funcionar" ;;
    esac ;;
  linuxmint|zorin|pop)
    OS_STATUS="ok"; OS_NOTE="Basado en Ubuntu/Debian — compatible" ;;
  *)
    if echo "$OS_ID_LIKE" | grep -qE 'debian|ubuntu'; then
      OS_STATUS="warn"; OS_NOTE="Derivado Debian/Ubuntu — probablemente compatible"
    else
      OS_STATUS="fail"; OS_NOTE="No soportado — el toolkit requiere apt (Debian/Ubuntu)"
    fi ;;
esac

DETECTED_NAME="${OS_PRETTY:-${OS_ID} ${OS_VERSION_ID}}"
case "$OS_STATUS" in
  ok)
    echo -e "  ${GREEN}[✓] Sistema:${NC} ${DETECTED_NAME}"
    echo -e "      ${DIM}${OS_NOTE}${NC}"
    ;;
  warn)
    echo -e "  ${YELLOW}[~] Sistema:${NC} ${DETECTED_NAME}"
    echo -e "      ${YELLOW}${OS_NOTE}${NC}"
    echo -e "      ${DIM}Continúa bajo tu propio riesgo.${NC}"
    ;;
  fail)
    echo -e "  ${RED}[✗] Sistema:${NC} ${DETECTED_NAME}"
    echo -e "      ${RED}${OS_NOTE}${NC}"
    echo ""
    echo -e "  ${YELLOW}Sistemas compatibles:${NC}"
    echo -e "    ${DIM}• Kali Linux (recomendado)${NC}"
    echo -e "    ${DIM}• Parrot OS${NC}"
    echo -e "    ${DIM}• Ubuntu 20.04 / 22.04 / 24.04${NC}"
    echo -e "    ${DIM}• Debian 11 / 12${NC}"
    echo -e "    ${DIM}• Cualquier derivado con apt${NC}"
    echo ""
    read -rp "  Continuar de todas formas? [s/N] " _confirm
    [[ "$_confirm" =~ ^[sS]$ ]] || exit 1
    ;;
esac
echo ""

# ── Detectar modo: update vs fresh install ────────────────
IS_UPDATE=false
if [ -d "${VENV_DIR}" ] && [ -f "${VENV_DIR}/bin/python3" ]; then
  IS_UPDATE=true
fi
if [ "$FORCE" = true ]; then
  IS_UPDATE=false
  echo -e "${YELLOW}[!] --force: se realizará instalación completa${NC}"
  echo ""
fi

if [ "$IS_UPDATE" = true ]; then
  echo -e "${CYAN}[~] Instalación existente detectada → modo actualización${NC}"
else
  echo -e "${CYAN}[*] Instalación nueva${NC}"
fi
echo ""

# ── 1. Herramientas de sistema ────────────────────────────
if [ "$IS_UPDATE" = false ]; then
  echo -e "${CYAN}[*] Instalando herramientas de sistema...${NC}"
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
else
  echo -e "${DIM}[~] Herramientas de sistema → omitidas (ya instaladas)${NC}"
  echo -e "${DIM}    Usa --force para reinstalar si falta alguna${NC}"
fi
echo ""

# ── 2. Copiar archivos del proyecto ──────────────────────
echo -e "${CYAN}[*] Sincronizando archivos...${NC}"
mkdir -p "${INSTALL_DIR}/templates" "${INSTALL_DIR}/static"
cp "${SCRIPT_DIR}/server.py"            "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/requirements.txt"     "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/templates/index.html" "${INSTALL_DIR}/templates/"
[ -d "${SCRIPT_DIR}/static" ] && cp -r "${SCRIPT_DIR}/static/." "${INSTALL_DIR}/static/"
echo -e "${GREEN}[✓] Archivos sincronizados${NC}"
echo ""

# ── 3. Entorno virtual ────────────────────────────────────
if [ ! -d "${VENV_DIR}" ] || [ ! -f "${VENV_DIR}/bin/python3" ]; then
  echo -e "${CYAN}[*] Creando entorno virtual...${NC}"
  python3 -m venv "${VENV_DIR}"
  echo -e "${GREEN}[✓] Venv creado en ${VENV_DIR}${NC}"
else
  echo -e "${DIM}[~] Venv existente → reutilizando${NC}"
fi
echo ""

# ── 4. Dependencias Python ────────────────────────────────
CURRENT_HASH=$(md5sum "${INSTALL_DIR}/requirements.txt" | awk '{print $1}')
STORED_HASH=$(cat "${REQ_HASH_FILE}" 2>/dev/null || echo "")

if [ "$CURRENT_HASH" != "$STORED_HASH" ] || [ "$FORCE" = true ]; then
  echo -e "${CYAN}[*] Instalando dependencias Python...${NC}"
  source "${VENV_DIR}/bin/activate"
  pip install --upgrade pip -q
  pip install -r "${INSTALL_DIR}/requirements.txt" -q
  deactivate
  echo "$CURRENT_HASH" > "${REQ_HASH_FILE}"
  echo -e "${GREEN}[✓] Dependencias Python listas${NC}"
else
  echo -e "${DIM}[~] requirements.txt sin cambios → pip install omitido${NC}"
fi
echo ""

# ── 5. Lanzador del sistema ───────────────────────────────
cat > /usr/local/bin/404x9-evil-kit << EOF
#!/bin/bash
cd ${INSTALL_DIR}
source ${VENV_DIR}/bin/activate
(sleep 1.5 && xdg-open http://localhost:5000 2>/dev/null &)
python3 server.py
EOF
chmod +x /usr/local/bin/404x9-evil-kit
ln -sf /usr/local/bin/404x9-evil-kit /usr/local/bin/x9-evilkit 2>/dev/null

# ── 6. Acceso directo en el escritorio ───────────────────
REAL_HOME=$(getent passwd "${SUDO_USER:-$USER}" | cut -d: -f6)
mkdir -p "${REAL_HOME}/Desktop"
cat > "${REAL_HOME}/Desktop/x9-evilkit.desktop" << 'DEOF'
[Desktop Entry]
Name=x9 Evil Kit
Comment=Pentesting Web Toolkit
Exec=bash -c '404x9-evil-kit'
Icon=kali-menu
Terminal=true
Type=Application
Categories=Security;
DEOF
chmod +x "${REAL_HOME}/Desktop/x9-evilkit.desktop" 2>/dev/null

# ── Resultado ─────────────────────────────────────────────
echo ""
if [ "$IS_UPDATE" = true ]; then
  echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║   [✓] Actualización completada!         ║${NC}"
  echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
else
  echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║   [✓] Instalación completada!           ║${NC}"
  echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
fi
echo ""
echo -e "  ${YELLOW}Para iniciar:${NC}      ${CYAN}404x9-evil-kit${NC}"
echo -e "  ${YELLOW}Para actualizar:${NC}   ${DIM}git pull && sudo bash install.sh${NC}"
echo -e "  ${YELLOW}Reinstalación:${NC}     ${DIM}sudo bash install.sh --force${NC}"
echo ""
