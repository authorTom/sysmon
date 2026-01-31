# sysmon - System Performance Monitor

A modern CLI tool for real-time Linux system performance monitoring with a clean, colorful dashboard interface.

## Features

- **Real-time monitoring** - Updates every 2 seconds (configurable)
- **CPU metrics** - Overall usage, per-core breakdown, frequency
- **Memory metrics** - RAM and swap usage with detailed breakdown
- **System load** - 1, 5, and 15 minute load averages
- **Disk usage** - Per-partition space utilization
- **Docker containers** - Per-container CPU, memory, and network I/O
- **Top processes** - CPU and memory consuming processes
- **Historical graphs** - Sparkline graphs showing 2 minutes of history
- **Color-coded alerts** - Green (OK), Yellow (Warning), Red (Critical)

## Installation

### Quick Install (Recommended)

Use the included installer script for easy setup on Ubuntu/Debian systems:

```bash
# Clone the repository
git clone https://github.com/authorTom/sysmon.git
cd sysmon

# Run the installer
sudo ./install.sh --local .
```

After installation, `sysmon` will be available system-wide.

### Installer Options

| Command | Description |
|---------|-------------|
| `sudo ./install.sh --local .` | Install from current directory |
| `sudo ./install.sh --local /path/to/sysmon` | Install from specific path |
| `sudo ./install.sh --git` | Install directly from GitHub |
| `sudo ./install.sh --uninstall` | Remove sysmon |
| `./install.sh --help` | Show help message |

The installer will:
- Check for Python 3.8+ and install missing dependencies
- Create an isolated installation at `/opt/sysmon`
- Set up a virtual environment (avoids PEP 668 conflicts)
- Create a symlink so `sysmon` works from anywhere

### From Source (Manual)

```bash
# Clone the repository
git clone <repository-url>
cd sysmon

# Install with pip (in a virtual environment)
python3 -m venv venv
source venv/bin/activate
pip install .
```

### Using pipx

```bash
pipx install git+<repository-url>
```

### Requirements

- Python 3.8+
- Linux operating system (some features may work on macOS/Windows)
- Docker (optional) - for container monitoring, Docker must be installed and the user must have permission to access the Docker socket

## Usage

### Basic Usage

```bash
# Run with default settings (2 second refresh)
sysmon

# Or run as a module
python -m sysmon
```

### Command Line Options

```bash
sysmon [OPTIONS]

Options:
  -r, --refresh SECONDS   Refresh interval in seconds (default: 2.0)
  --no-processes          Hide the process list panel
  --no-docker             Hide Docker container metrics
  --docker-only           Show only Docker metrics (hide processes)
  --once                  Display metrics once and exit
  -v, --version          Show version and exit
  -h, --help             Show help message
```

### Examples

```bash
# Fast refresh (1 second)
sysmon -r 1

# Slow refresh (5 seconds)
sysmon -r 5

# Without process list (smaller display)
sysmon --no-processes

# Without Docker metrics
sysmon --no-docker

# Focus on Docker containers only
sysmon --docker-only

# Single snapshot (no live updates)
sysmon --once
```

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                      System Monitor                             │
│                    2024-01-15 14:30:00                          │
├──────────────────────────────┬──────────────────────────────────┤
│  CPU Usage              62%  │  Memory Usage             71%    │
│  ████████████░░░░░░░░        │  ██████████████░░░░░░           │
│  History: ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁    │  History: ▅▅▆▆▆▇▇▇▇▇▆▆▅▅       │
│  Core 0: 58%  Core 1: 65%    │  Used: 11.2 GB / 15.8 GB         │
├──────────────────────────────┼──────────────────────────────────┤
│  System Load                 │  Disk Usage                      │
│  1m: 2.15  5m: 1.87          │  /      ████████░░  80%          │
│  15m: 1.52                   │  /home  ██████░░░░  62%          │
├──────────────────────────────┴──────────────────────────────────┤
│  Docker Containers (3/5)                                        │
│  Container       Image              CPU%    Memory     MEM%     │
│  nginx-proxy     nginx:latest       2.3     125.4 MB   3.2      │
│  postgres-db     postgres:15        8.5     512.0 MB   13.1     │
│  redis-cache     redis:alpine       1.2     48.2 MB    1.2      │
├─────────────────────────────────────────────────────────────────┤
│  Top Processes by CPU                                           │
│  PID       NAME              CPU%      MEM%      STATUS         │
│  1234      firefox           12.3      8.5       running        │
│  5678      code              8.7       6.2       running        │
└─────────────────────────────────────────────────────────────────┘
```

## Color Coding

| Color  | Usage Range | Status   |
|--------|-------------|----------|
| Green  | 0-60%       | Healthy  |
| Yellow | 60-80%      | Warning  |
| Red    | 80-100%     | Critical |

## Keyboard Controls

- `Ctrl+C` - Exit the monitor

## Troubleshooting

### Docker not available error

If you see the error "Docker not available - Error while fetching server API version", your user likely doesn't have permission to access the Docker socket.

**Fix:** Add your user to the docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Alternatively, log out and log back in for the group change to take effect.

**To skip Docker monitoring entirely**, use the `--no-docker` flag:

```bash
sysmon --no-docker
```

## License

MIT License
