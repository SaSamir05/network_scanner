# Network Scanner

A professional Python-based network scanner built for discovering, analyzing, and managing active devices on local networks. The application combines powerful network scanning capabilities with a modern CustomTkinter interface, making it suitable for students, network administrators, and cybersecurity enthusiasts.

## Features

### Network Discovery

* Discover active devices on local networks
* Fast ARP-based host detection
* Real-time scan progress updates

### Device Information

* IP Address Detection
* MAC Address Detection
* Hostname Resolution
* Vendor Identification (when available)

### Data Export

* Export scan results to CSV
* Export scan results to JSON

### Modern GUI

* Responsive CustomTkinter interface
* Easy-to-use dashboard
* Organized device listing

## Technologies Used

* Python
* Scapy
* CustomTkinter
* Threading
* Socket Programming

## Installation

### 1. Install Npcap (Windows)

Npcap is recommended for reliable ARP-based device discovery.

Download from:
https://npcap.com/#download

During installation:

* Run as Administrator
* Enable **WinPcap API-Compatible Mode**
* Complete installation and restart the terminal

### 2. Clone Repository

```bash
git clone https://github.com/SaSamir05/network_scanner.git
cd network_scanner
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Run Application

```bash
python main.py
```

## Project Structure

```text
network_scanner/
├── scanner/
├── utils/
├── exports/
├── assets/
├── requirements.txt
├── main.py
└── README.md
```

## Use Cases

* Network Monitoring
* Asset Discovery
* Device Inventory Management
* Cybersecurity Learning
* Home Lab Administration
* Network Troubleshooting

## Future Improvements

* Port Scanning
* Operating System Detection
* Device History Tracking
* PDF Report Export
* Dark Mode Dashboard
* Multi-Subnet Scanning

## Disclaimer

This project is intended solely for educational purposes and authorized network administration. Always obtain permission before scanning networks that you do not own or manage.

## Author

**Md. Shahriyar Alam (Samir)**

Computer Science & Engineering Student
Daffodil International University
