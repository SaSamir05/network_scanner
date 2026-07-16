# Network Scanner

A professional Python-based network scanner designed to discover and analyze active devices on a local network. The application provides real-time network visibility through a modern graphical interface built with CustomTkinter.

## Features

### Network Discovery

* Detect active devices on the local network
* Fast and efficient host scanning

### Device Information

* IP Address Detection
* MAC Address Detection
* Hostname Resolution
* Vendor Identification (if available)

### Data Export

* Export scan results to CSV format
* Export scan results to JSON format

### Modern User Interface

* Clean and responsive CustomTkinter GUI
* Real-time scan progress updates
* User-friendly device management

## Technologies Used

* Python
* Scapy
* CustomTkinter
* Threading
* Socket Programming


## Installation

### 1. Install Npcap (Windows)

Npcap is recommended for fast and reliable ARP-based network discovery.

Download Npcap:

https://npcap.com/#download

During installation:

* Run the installer as Administrator
* Enable **"Install Npcap in WinPcap API-Compatible Mode"**
* Complete the installation and restart your computer (or terminal)

### 2. Clone the Repository

```bash
git clone https://github.com/SaSamir05/network_scanner.git
cd network_scanner
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

## Use Cases

* Network Monitoring
* Device Inventory Management
* Home Lab Administration
* Cybersecurity Learning
* Network Troubleshooting

## License

This project is intended for educational and authorized network administration purposes only.
