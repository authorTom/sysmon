#!/bin/bash

# sysmon installer script
# Installs sysmon system performance monitor

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

REPO_URL="https://github.com/YOUR_USERNAME/sysmon.git"
INSTALL_DIR="/opt/sysmon"
VENV_DIR="$INSTALL_DIR/venv"
BIN_LINK="/usr/local/bin/sysmon"

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_dependencies() {
    print_status "Checking dependencies..."

    # Check Python version
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        echo "Install with: sudo apt install python3 python3-venv python3-pip"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8 ]]; then
        print_error "Python 3.8+ is required (found $PYTHON_VERSION)"
        exit 1
    fi
    print_status "Found Python $PYTHON_VERSION"

    # Check for venv module
    if ! python3 -m venv --help &> /dev/null; then
        print_warning "python3-venv not found, installing..."
        apt-get update && apt-get install -y python3-venv
    fi

    # Check for git (only needed for git install method)
    if ! command -v git &> /dev/null; then
        print_warning "git not found, installing..."
        apt-get update && apt-get install -y git
    fi
}

install_from_local() {
    local source_dir="$1"

    print_status "Installing from local directory: $source_dir"

    # Create install directory
    mkdir -p "$INSTALL_DIR"

    # Copy source files
    cp -r "$source_dir"/* "$INSTALL_DIR/"

    # Create virtual environment
    print_status "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"

    # Install the package
    print_status "Installing sysmon and dependencies..."
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install "$INSTALL_DIR"

    # Create symlink
    create_symlink
}

install_from_git() {
    print_status "Installing from git repository..."

    # Clone repository
    if [[ -d "$INSTALL_DIR" ]]; then
        print_warning "Removing existing installation..."
        rm -rf "$INSTALL_DIR"
    fi

    git clone "$REPO_URL" "$INSTALL_DIR"

    # Create virtual environment
    print_status "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"

    # Install the package
    print_status "Installing sysmon and dependencies..."
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install "$INSTALL_DIR"

    # Create symlink
    create_symlink
}

create_symlink() {
    print_status "Creating command symlink..."

    # Create wrapper script
    cat > "$INSTALL_DIR/sysmon-wrapper.sh" << 'EOF'
#!/bin/bash
/opt/sysmon/venv/bin/python -m sysmon "$@"
EOF

    chmod +x "$INSTALL_DIR/sysmon-wrapper.sh"

    # Remove old symlink if exists
    [[ -L "$BIN_LINK" ]] && rm "$BIN_LINK"

    # Create new symlink
    ln -s "$INSTALL_DIR/sysmon-wrapper.sh" "$BIN_LINK"
}

uninstall() {
    print_status "Uninstalling sysmon..."

    [[ -L "$BIN_LINK" ]] && rm "$BIN_LINK"
    [[ -d "$INSTALL_DIR" ]] && rm -rf "$INSTALL_DIR"

    print_status "sysmon has been uninstalled"
}

show_help() {
    echo "sysmon installer"
    echo ""
    echo "Usage: sudo ./install.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  --local DIR    Install from local directory"
    echo "  --git          Install from git repository"
    echo "  --uninstall    Remove sysmon"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  sudo ./install.sh --local .       # Install from current directory"
    echo "  sudo ./install.sh --local /path   # Install from specific path"
    echo "  sudo ./install.sh --git           # Install from GitHub"
    echo "  sudo ./install.sh --uninstall     # Remove sysmon"
}

main() {
    echo ""
    echo "================================"
    echo "  sysmon Installer v1.0.0"
    echo "================================"
    echo ""

    case "${1:-}" in
        --local)
            check_root
            check_dependencies
            if [[ -z "${2:-}" ]]; then
                print_error "Please specify source directory"
                echo "Usage: sudo ./install.sh --local /path/to/sysmon"
                exit 1
            fi
            SOURCE_DIR="$(cd "$2" && pwd)"
            install_from_local "$SOURCE_DIR"
            ;;
        --git)
            check_root
            check_dependencies
            install_from_git
            ;;
        --uninstall)
            check_root
            uninstall
            exit 0
            ;;
        --help|-h|"")
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac

    echo ""
    print_status "Installation complete!"
    echo ""
    echo "You can now run 'sysmon' from anywhere."
    echo "Try: sysmon --help"
    echo ""
    echo "To uninstall: sudo ./install.sh --uninstall"
    echo ""
}

main "$@"
