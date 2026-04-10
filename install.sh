#!/bin/bash
# ============================================================
#  404x9-evil-kit — Instalador
#  by @xfraylin
#
#  Uso rápido (una sola línea):
#    sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/xFraylin/404x9-evil-kit/main/install.sh)"
#
#  O clona y ejecuta:
#    git clone https://github.com/xFraylin/404x9-evil-kit.git && sudo bash 404x9-evil-kit/install.sh
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO_URL="https://github.com/xFraylin/404x9-evil-kit.git"
INSTALL_DIR="/opt/kali-toolkit"
VENV_DIR="${INSTALL_DIR}/venv"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   404x9-evil-kit — by @xfraylin         ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Ejecutar como root: sudo bash install.sh${NC}"
  exit 1
fi

# ── Auto-clone si los archivos fuente no están presentes ─────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)"
if [ ! -f "${SCRIPT_DIR}/server.py" ]; then
  echo -e "${CYAN}[*] Descargando 404x9-evil-kit desde GitHub...${NC}"
  apt-get install -y git 2>/dev/null | tail -1
  TMP_DIR="$(mktemp -d)"
  git clone --depth=1 "${REPO_URL}" "${TMP_DIR}/404x9-evil-kit" 2>&1 | tail -3
  SCRIPT_DIR="${TMP_DIR}/404x9-evil-kit"
fi

# ── Dependencias del sistema ──────────────────────────────────────────────────
echo -e "${CYAN}[*] Instalando python3-venv...${NC}"
apt-get install -y python3 python3-venv 2>/dev/null | tail -1

# ── Copiar archivos ───────────────────────────────────────────────────────────
echo -e "${CYAN}[*] Copiando archivos a ${INSTALL_DIR}...${NC}"
mkdir -p "${INSTALL_DIR}/templates"
mkdir -p "${INSTALL_DIR}/static"
cp "${SCRIPT_DIR}/server.py"              "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/requirements.txt"       "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/templates/index.html"   "${INSTALL_DIR}/templates/"
[ -d "${SCRIPT_DIR}/static" ] && cp -r "${SCRIPT_DIR}/static/." "${INSTALL_DIR}/static/"

# ── Entorno virtual ───────────────────────────────────────────────────────────
echo -e "${CYAN}[*] Creando entorno virtual en ${VENV_DIR}...${NC}"
python3 -m venv "${VENV_DIR}"

echo -e "${CYAN}[*] Instalando dependencias Python (flask, flask-cors)...${NC}"
"${VENV_DIR}/bin/pip" install --upgrade pip -q
"${VENV_DIR}/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" -q

# ── Lanzador ──────────────────────────────────────────────────────────────────
cat > /usr/local/bin/404x9-evil-kit << EOF
#!/bin/bash
cd ${INSTALL_DIR}
echo ""
echo "  404x9-evil-kit · by @xfraylin"
echo "  Abriendo http://localhost:5000 ..."
echo "  Ctrl+C para detener"
echo ""
(sleep 1.5 && xdg-open http://localhost:5000 2>/dev/null || firefox http://localhost:5000 2>/dev/null &) &
${VENV_DIR}/bin/python3 server.py
EOF
chmod +x /usr/local/bin/404x9-evil-kit
ln -sf /usr/local/bin/404x9-evil-kit /usr/local/bin/kali-toolkit 2>/dev/null || true

# ── Acceso directo escritorio ─────────────────────────────────────────────────
cat > /root/Desktop/kali-toolkit.desktop 2>/dev/null << 'EOF'
[Desktop Entry]
Name=Kali Toolkit
Comment=Pentesting Web Toolkit
Exec=bash -c 'kali-toolkit'
Icon=kali-menu
Terminal=true
Type=Application
Categories=Security;
EOF
chmod +x /root/Desktop/kali-toolkit.desktop 2>/dev/null

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   [✓] Instalación completada!           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${YELLOW}Para iniciar escribe:${NC}"
echo -e "  ${CYAN}  404x9-evil-kit${NC}"
echo ""
