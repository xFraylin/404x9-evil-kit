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

echo -e "${CYAN}[*] Instalando dependencias Python...${NC}"
apt-get install -y python3 python3-pip python3-flask 2>/dev/null
pip3 install flask flask-cors --break-system-packages 2>/dev/null || \
  pip3 install flask flask-cors 2>/dev/null

# Copy files
echo -e "${CYAN}[*] Copiando archivos a ${INSTALL_DIR}...${NC}"
mkdir -p "${INSTALL_DIR}/templates"
cp server.py "${INSTALL_DIR}/"
cp templates/index.html "${INSTALL_DIR}/templates/"

# Create launcher script
cat > /usr/local/bin/404x9-evil-kit << 'EOF'
#!/bin/bash
cd /opt/kali-toolkit
echo ""
echo "  404x9-evil-kit · by @xfraylin"
echo "  Abriendo http://localhost:5000 ..."
echo "  Ctrl+C para detener"
echo ""
(sleep 1.5 && xdg-open http://localhost:5000 2>/dev/null || firefox http://localhost:5000 2>/dev/null &) &
python3 server.py
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
echo -e "  ${CYAN}cd /opt/kali-toolkit && python3 server.py${NC}"
echo -e "  ${CYAN}Luego abre: http://localhost:5000${NC}"
echo ""
