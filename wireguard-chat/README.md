> **Portfolio context:** CSC4026Z Network Security, UCT Honours (2026). Team project with Tadiwanashe Nyakonda and Jaylyn Bhula. Original repo: [TADIWABNYAKS/WireguardChat](https://github.com/TADIWABNYAKS/WireguardChat).
> **My contribution:** the asyncio + PyQt6 controller (integrating async network loops with the UI), local message stores for DMs and channels, and UI layout and bug fixes.
> Secrets (`.env`, keys) and the virtual environment are not included. See setup step 4 below.

# WireGuard Chat Client

A secure, multi-user, asynchronous chat client communicating with a remote server (`csc4026z.link`) over UDP. This project features a custom implementation of both a **Simplified** and an **Extended** WireGuard protocols, offering use through a PyQt6 Graphical User Interface (GUI).

---

##  Key Features

* **Custom WireGuard Stack**: Built from the ground up to support the Noise IK handshake, session key derivation, and the Extended WireGuard specification (cookie replies and MAC2 verification).
* **Asynchronous Design**: Integrates the PyQt6 event loop with Python's native `asyncio` using `qasync` to handle concurrent socket operations, heartbeats, and UI rendering without blocking.
* **Channel & User Management**: Features support for creating/joining rooms, listing online users, direct messaging, and WHOIS lookups.

---

---

##  Setup & Installation

### Prerequisites
* Python 3.10 or higher
* Pip (Python package manager)

### 1. Clone & Navigate to the Project
```bash
git clone <repository-url>
cd WireguardChat
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment to manage dependencies locally:
```bash
# Create the environment
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries specified in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory of the project to store your cryptographic keys.
```bash
touch .env
```
Open `.env` and add your base64-encoded client private key and the server's public key in the following format:
```env
USER_KEY="your_base64_encoded_private_key_here"
SERVER_KEY="server_base64_encoded_public_key_here"
```

---

## Running the Application

Ensure your virtual environment is active (`source .venv/bin/activate`) before running the client.

To launch the application:
```bash
python mainUI.py
```

## Running Tests

Unit tests are included to verify key derivations, packet formatting, and cryptographic calculations. 

To run the test suite:
```bash
pytest
```
Or for verbose output:
```bash
pytest -v
```

---

## Project Directory Structure

```text
WireguardChat/
├── encryption/                   # Custom Cryptographic Stack
│   ├── crypto_math.py            # Custom wrappers, KDFs, nonces, timestamps
│   ├── encryption_protocol.py    # WireGuard/Noise state machine
│   ├── SecureSocket.py           # Message serialization and UDP wrapper
│   └── tests/                    # Cryptographic unit tests
│       ├── test_crypto_math.py
│       └── test_encryption.py
├── messages/                     # Chat protocol handlers (Session, Channels, Users)
├── ui/                           # PyQt6 User Interface components
├── mainUI.py                     # PyQt6 GUI application entry point
├── requirements.txt              # Project dependencies
└── .env                          # Local configuration keys (ignored by git)
```
