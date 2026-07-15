# 🛰 Network Scanner

A modern, dark-mode desktop network scanner built with **Python** and
**CustomTkinter**. Discovers every active device on your local network via
ARP, enriches the results with hostname and vendor information, and lets
you export or inspect them from a professional dashboard UI.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **Automatic ARP scan** of the detected local subnet
- **Device details**: IP, MAC, hostname, vendor, status
- **Multithreaded enrichment** (fast even with 100+ hosts)
- **Modern dark dashboard** with stat cards, sortable table, live progress
- **Search & filter** across every column
- **Sort** by any column with a single click
- **Ping** a selected device, **copy** IP/MAC to clipboard
- **Gateway detection** and local host info
- **Export** results to CSV or JSON
- **Scan history** saved automatically to `data/history/`
- **Logging** to `data/network_scanner.log`

## 📁 Project Structure

```
network_scanner/
├── main.py
├── scanner/
│   ├── network_scanner.py
│   ├── arp_scanner.py
│   └── device_info.py
├── ui/
│   ├── dashboard.py
│   └── components.py
├── utils/
│   ├── exporter.py
│   ├── logger.py
│   └── helpers.py
├── data/
│   └── history/
├── requirements.txt
├── README.md
└── .gitignore
```

## 🚀 Installation

Requires **Python 3.9+**.

```bash
git clone <your-repo-url>
cd network_scanner
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Platform prerequisites

| OS      | Requirement                                                             |
| ------- | ----------------------------------------------------------------------- |
| Windows | Install [Npcap](https://npcap.com/) (WinPcap-compatible mode). Run as Administrator. |
| Linux   | Run with `sudo`, or grant CAP_NET_RAW: `sudo setcap cap_net_raw,cap_net_admin=eip $(which python)` |
| macOS   | Run with `sudo` (ARP requires raw sockets)                              |

## 🖥 Usage

```bash
# Windows (Administrator PowerShell)
python main.py

# macOS / Linux
sudo python main.py
```

1. Click **Scan** — the app auto-detects your subnet and scans it.
2. Wait for the progress bar; results stream in as they resolve.
3. Use the **search box** to filter, click any **column header** to sort.
4. Select a row to **Ping** or **Copy IP/MAC**.
5. Click **Export** to save results as CSV or JSON.

Scan history is saved as JSON under `data/history/` after every scan.

## 🧪 Troubleshooting

- **`PermissionError` / empty results** — re-run with administrator/root privileges.
- **`Npcap not found` on Windows** — install Npcap in "WinPcap API-compatible mode".
- **Vendor shows `Unknown`** — first run downloads the OUI database; ensure internet access once.
- **No devices found** — check your subnet in the dashboard header; a VPN can hide LAN peers.

## 🛠 Tech Stack

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — modern Tk UI
- [Scapy](https://scapy.net/) — ARP packet crafting
- [mac-vendor-lookup](https://pypi.org/project/mac-vendor-lookup/) — OUI vendor database

## 📄 License

MIT — free to use, learn from, and extend.
