#!/usr/bin/env bash
set -euo pipefail

# -------- Colors --------
BLUE='\033[38;5;33m'
CYAN='\033[38;5;44m'
GRAY='\033[38;5;245m'
GREEN='\033[38;5;42m'
RED='\033[38;5;196m'
YELLOW='\033[38;5;220m'
NC='\033[0m'

# -------- Ensure project root --------
cd "$(dirname "$0")" || exit 1

# -------- Dependency Check --------
check_deps() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: python3 is not installed.${NC}"
        exit 1
    fi

    # Check for psutil
    if ! python3 -c "import psutil" &> /dev/null; then
        echo -e "${YELLOW}Missing dependencies. Installing...${NC}"
        pip install -r requirements.txt
    fi
}

# -------- Banner --------
show_banner() {
    clear
    echo -e "${BLUE}"
    echo "   ███████╗██╗   ██╗███████╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗ "
    echo "   ██╔════╝╚██╗ ██╔╝██╔════╝██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗"
    echo "   ███████╗ ╚████╔╝ ███████╗██║  ███╗██║   ██║███████║██████╔╝██║  ██║"
    echo "   ╚════██║  ╚██╔╝  ╚════██║██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║"
    echo "   ███████║   ██║   ███████║╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝"
    echo "   ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ "
    echo -e "${NC}"
    echo -e "         ${CYAN}Advanced System Health & Auto-Fix Tool${NC}"
    echo -e "         ${GRAY}Built for speed, reliability, and automation${NC}"
    echo -e "${GRAY}-------------------------------------------------------------------${NC}"
    echo ""
}

# -------- Logic --------
check_deps
show_banner

while true; do
    echo -e "${GREEN}Main Menu:${NC}"
    echo -e "  ${CYAN}1)${NC} System Snapshot  ${GRAY}(Quick health check)${NC}"
    echo -e "  ${CYAN}2)${NC} Live Monitor     ${GRAY}(Real-time terminal UI)${NC}"
    echo -e "  ${CYAN}3)${NC} Web Dashboard    ${GRAY}(FastAPI + WebSocket)${NC}"
    echo -e "  ${CYAN}4)${NC} Process Top      ${GRAY}(Identify resource hogs)${NC}"
    echo -e "  ${CYAN}5)${NC} Alert History    ${GRAY}(View past incidents)${NC}"
    echo -e "  ${CYAN}6)${NC} View Config      ${GRAY}(Thresholds & Rules)${NC}"
    echo -e "  ${CYAN}0)${NC} Exit"
    echo ""

    read -rp "SysGuard ▶ " choice
    echo ""

    case "$choice" in
        1)
            python3 run.py status
            echo ""
            read -rp "Press Enter to return to menu..."
            show_banner
            ;;
        2)
            python3 run.py monitor --watch
            show_banner
            ;;
        3)
            echo -e "${YELLOW}Launching Web Dashboard on http://localhost:8000...${NC}"
            echo -e "${GRAY}Press Ctrl+C to stop the server and return here.${NC}"
            echo ""
            python3 run.py web
            show_banner
            ;;
        4)
            python3 run.py top
            echo ""
            read -rp "Press Enter to return to menu..."
            show_banner
            ;;
        5)
            python3 run.py history
            echo ""
            read -rp "Press Enter to return to menu..."
            show_banner
            ;;
        6)
            echo -e "${BLUE}Current Configuration:${NC}"
            cat config/sysguard.yaml
            echo ""
            read -rp "Press Enter to return to menu..."
            show_banner
            ;;
        0|q|exit)
            echo -e "${CYAN}Stopping SysGuard. Stay secure!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option '${choice}'. Please select 0-6.${NC}"
            sleep 1
            show_banner
            ;;
    esac
done