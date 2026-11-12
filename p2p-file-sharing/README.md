> **Portfolio context:** CSC3002F Networks assignment, UCT (2025). Team project (3 members) built in a shared GitHub repo. The project report is in `ReportNetworks1.pdf`.

> **⚠️ Known issues (code kept as submitted):** the tracker → seeder → leecher flow works, but downloads are not correct for real files.
> - `SeederClass.py` registers every file with a hardcoded size of 5 bytes (`self.SeederUDPClient('test.txt', 5)`), so the leecher only requests the first few bytes: a 20 KB file downloads as 6 bytes.
> - The seeder serves `test.txt` and the leecher writes to `output/`; neither is in the repo, so create both before running.
> - `TrackerClass.py`, `SeederClass.py` and `LeecherClass.py` have no entry point, so running them directly (steps 1–3 below) does nothing. Start everything through `python TorrentUI.py`, which launches the tracker and two seeders itself.
> - The clone command below points at the original team repository.

# P2P File Sharing System

## Overview
This project is a **Peer-to-Peer (P2P) File Sharing System** implemented using Python socket programming. It allows users to share and download files in a decentralized manner, similar to BitTorrent, using a **Tracker**, **Seeder**, and **Leecher** system.

## Features
- **Tracker (UDP Server):** Maintains a list of active Seeders.
- **Seeder (TCP Server):** Hosts and provides file chunks for download.
- **Leecher (TCP Client):** Requests and downloads file chunks from multiple Seeders.
- **Message Formatting:** A dedicated `MsgFormatter.py` module to standardize communication.
- **Basic UI:** A basic UI to handle functionality
- **Future Enhancements:** File integrity checks, and automatic re-seeding.

## Project Structure
```
NETWORKS1/
│── LeecherClass.py      # Handles downloading files from Seeders
│── MsgFormatter.py      # Formats and parses messages for communication
│── SeederClass.py       # Acts as a file provider (Seeder)
│── TorrentUI.py         # Creates a basic UI
│── TrackerClass.py      # Keeps track of Seeders and manages requests
│── .gitattributes       # Git configuration file
```

## Installation & Setup
### Prerequisites
- Python 3.x
- Basic understanding of networking and socket programming

### Installation
1. **Clone the Repository:**
   ```sh
   git clone https://github.com/MRSSAR011/Networks1.git
   cd Networks1
   ```
2. **Ensure Python is Installed:**
   ```sh
   python --version
   ```

## Running the System
### Start the UI file
Run the UI to begin the application
'''sh
python TorrentUI.py
'''

### 1. Start the Tracker
Run the Tracker to manage Seeder and Leecher communication.
```sh
python TrackerClass.py
```

### 2. Start the Seeder
Run the Seeder to register with the Tracker and provide files for download.
```sh
python SeederClass.py
```

### 3. Start the Leecher
Run the Leecher to request and download files from the Seeder.
```sh
python LeecherClass.py
```

## Communication Flow
1. **Seeder Registers with Tracker**: Seeder informs the Tracker about available files.
2. **Leecher Requests File**: Leecher queries the Tracker for Seeders.
3. **Tracker Responds with Seeder Info**: Tracker provides available Seeder details.
4. **Leecher Downloads from Seeder**: Leecher connects via TCP and downloads the file.

## Future Enhancements
- ✅ **File Integrity Verification:** SHA-256 hash check for downloaded chunks.
- ✅ **Re-Seeding:** Leechers can become Seeders automatically.

## Contributors
- **Matome Mbowene**  
- **Daniel Schlesinger**  
- **Sarah-Jane Marais**  

