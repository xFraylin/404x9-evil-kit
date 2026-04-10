#!/bin/bash
# ============================================================
#  404x9-evil-kit — Instalador
#  by @xfraylin
#  Ejecutar como root: bash install.sh
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

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

echo -e "${CYAN}[*] Instalando python3-venv...${NC}"
apt-get install -y python3 python3-venv 2>/dev/null

# Copy files
echo -e "${CYAN}[*] Copiando archivos a ${INSTALL_DIR}...${NC}"
mkdir -p "${INSTALL_DIR}/templates"
mkdir -p "${INSTALL_DIR}/static"
cp server.py "${INSTALL_DIR}/"
cp requirements.txt "${INSTALL_DIR}/"
cp templates/index.html "${INSTALL_DIR}/templates/"
[ -d static ] && cp -r static/. "${INSTALL_DIR}/static/"

# Create virtual environment
echo -e "${CYAN}[*] Creando entorno virtual en ${VENV_DIR}...${NC}"
python3 -m venv "${VENV_DIR}"

# Install dependencies inside venv
echo -e "${CYAN}[*] Instalando dependencias en el entorno virtual...${NC}"
"${VENV_DIR}/bin/pip" install --upgrade pip -q
"${VENV_DIR}/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" -q

# Create launcher script
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
# Keep backward compat alias
ln -sf /usr/local/bin/404x9-evil-kit /usr/local/bin/kali-toolkit 2>/dev/null || true

# Create desktop shortcut
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
echo -e "${GREEN}[✓] Instalación completada!${NC}"
echo ""
echo -e "  ${YELLOW}Para iniciar:${NC}"
echo -e "  ${CYAN}404x9-evil-kit${NC}"
echo ""
echo -e "  ${YELLOW}O manualmente:${NC}"
echo -e "  ${CYAN}cd ${INSTALL_DIR} && ${VENV_DIR}/bin/python3 server.py${NC}"
echo -e "  ${CYAN}Luego abre: http://localhost:5000${NC}"
echo ""
