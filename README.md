# Secure IoT OTA Firmware Update System (ESP32 Backend)

A secure, lightweight, and production-ready Over-The-Air (OTA) firmware update server built using Python 3, Flask, and SQLite. Designed for managing secure wireless firmware distribution to ESP32 IoT microcontrollers.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [What is OTA?](#what-is-ota)
3. [Architecture & System Flow](#architecture--system-flow)
4. [Technologies Used](#technologies-used)
5. [Folder Structure](#folder-structure)
6. [Installation & Setup](#installation--setup)
7. [Environment Variables](#environment-variables)
8. [Database Schema](#database-schema)
9. [Running the Server](#running-the-server)
10. [API Endpoints Summary](#api-endpoints-summary)
11. [Testing with Curl / Postman](#testing-with-curl--postman)
12. [ESP32 Communication Flow](#esp32-communication-flow)
13. [Security Implementation](#security-implementation)
14. [Security Limitations](#security-limitations)
15. [Future Enhancements](#future-enhancements)

---

## Project Overview
In modern Internet of Things (IoT) deployments, microcontrollers like the ESP32 are often deployed in remote or hard-to-reach locations. Manually connecting a USB cable to update device code is impractical.

This project implements a **local, secure OTA update backend** that allows administrators to upload compiled ESP32 firmware binaries (`.bin` files) and enables registered ESP32 devices to securely check for, download, and report firmware updates over Wi-Fi.

---

## What is OTA?
**OTA** stands for **Over-The-Air**. It refers to the wireless transmission of new software or firmware updates to embedded devices over Wi-Fi, Cellular, or Bluetooth networks. 

When an ESP32 performs an OTA update:
1. It connects to the update server via HTTP/HTTPS.
2. It compares its current firmware version with the latest version on the server.
3. If a newer version exists, it downloads the binary data directly into the ESP32's secondary flash memory partition (e.g., `ota_1`).
4. It verifies the payload integrity (via SHA-256 hash matching).
5. It switches its boot partition to the new code and reboots.

---

## Architecture & System Flow

```
+-------------------+              +-----------------------+              +------------------------+
|                   |              |                       |              |                        |
|  Administrator    | -- Upload -> |   Flask OTA Backend   | <-- Check -- |     ESP32 IoT Node     |
| (Postman/Curl/UI) |   (.bin)     |  (REST API + SQLite)  |   Download   |  (Wi-Fi / HTTP Client) |
|                   |              |                       |   Report ->  |                        |
+-------------------+              +-----------------------+              +------------------------+
                                              |
                                     +-----------------+
                                     |  SQLite Database|
                                     | (Devices, FW,   |
                                     |  Update Logs)   |
                                     +-----------------+
```

---

## Technologies Used
- **Python 3.10+**: Core programming language.
- **Flask 3.x**: Lightweight Web framework for handling RESTful APIs.
- **SQLite 3**: Embedded, file-based relational database for device, firmware, and update audit logs.
- **Werkzeug**: Secure filename handling and security utilities.
- **hashlib**: Built-in Python library for token hashing and SHA-256 binary hash generation.
- **python-dotenv**: Environment variable management.
- **Flask-CORS**: Cross-Origin Resource Sharing support for future web dashboard integration.
- **packaging**: Semantic version parsing and comparison (`packaging.version`).

---

## Folder Structure

```
secure-iot-ota/
└── backend/
    ├── app.py                      # Application factory, CORS, error handling
    ├── config.py                   # Environment configuration loader
    ├── database.py                 # SQLite initialization & thread-safe connection management
    ├── models.py                   # Data layer models (Devices, Firmware, Update Logs)
    ├── requirements.txt            # Python dependencies
    ├── .env.example                # Template for environment configuration
    ├── .env                        # Local secrets (git-ignored)
    ├── .gitignore                  # Git ignore rules
    ├── README.md                   # System documentation
    │
    ├── routes/                     # Modular API route blueprints
    │   ├── __init__.py
    │   ├── auth_middleware.py      # Device & Admin authentication decorators
    │   ├── device_routes.py        # Registration, device lookup, heartbeat
    │   ├── firmware_routes.py      # Upload, list, update check, download
    │   └── update_routes.py        # Status report logging and history lookup
    │
    ├── firmware/                   # Directory storing uploaded .bin binary files
    ├── logs/                       # Server audit logs (ota_system.log)
    └── tests/                      # Automated unit test suite
        └── test_api.py
```

---

## Installation & Setup

### Prerequisites
- Python 3.8+ installed on Windows, Linux, or macOS.

### 1. Open Terminal & Navigate to Project Directory
```powershell
cd secure-iot-ota/backend
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
```

### 3. Activate Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## Environment Variables

Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```

Default `.env` contents:
```env
FLASK_ENV=development
FLASK_PORT=5000
SECRET_KEY=dev-secret-key-987654321
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin_secret_pass
DATABASE_PATH=ota_database.db
FIRMWARE_DIR=firmware
LOG_DIR=logs
```

---

## Database Schema

The SQLite database (`ota_database.db`) consists of three tables:

### 1. `DEVICES`
| Field | Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique row ID |
| `device_id` | TEXT | UNIQUE, NOT NULL | Hardware device identifier (e.g. ESP32-001) |
| `device_name` | TEXT | NOT NULL | Human readable device name |
| `current_firmware_version` | TEXT | NOT NULL | Firmware currently running on device |
| `api_token_hash` | TEXT | NOT NULL | SHA-256 hash of device authentication token |
| `status` | TEXT | NOT NULL | Status ('online' or 'offline') |
| `last_seen` | TEXT | NULLABLE | Timestamp of last heartbeat |
| `created_at` | TEXT | NOT NULL | Device registration timestamp |

### 2. `FIRMWARE`
| Field | Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique row ID |
| `version` | TEXT | UNIQUE, NOT NULL | Semantic version (e.g., 1.1.0) |
| `filename` | TEXT | NOT NULL | Sanitized filename on server disk |
| `file_path` | TEXT | NOT NULL | Server filesystem location |
| `sha256_hash` | TEXT | NOT NULL | Calculated SHA-256 checksum of firmware file |
| `file_size` | INTEGER | NOT NULL | Size of `.bin` file in bytes |
| `uploaded_at` | TEXT | NOT NULL | Upload timestamp |
| `is_latest` | INTEGER | NOT NULL DEFAULT 0 | Flag indicating if this is the newest version |

### 3. `UPDATE_LOGS`
| Field | Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique row ID |
| `device_id` | TEXT | NOT NULL | Target device ID |
| `old_version` | TEXT | NOT NULL | Firmware version before update attempt |
| `new_version` | TEXT | NOT NULL | Firmware version attempted |
| `status` | TEXT | NOT NULL | Update outcome ('success' or 'failed') |
| `message` | TEXT | NULLABLE | Detailed status message / error description |
| `timestamp` | TEXT | NOT NULL | Log record timestamp |

---

## Running the Server

Start the Flask server:
```powershell
python app.py
```
The server will run on `http://127.0.0.1:5000`.

---

## API Endpoints Summary

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/devices/register` | None | Register new ESP32 device & receive raw token |
| `GET` | `/api/devices` | None | List registered devices (omits secrets) |
| `GET` | `/api/devices/<device_id>` | None | Get specific device details |
| `POST` | `/api/devices/<device_id>/heartbeat` | Device Bearer | Record heartbeat ping |
| `POST` | `/api/firmware/upload` | Admin | Upload new firmware binary (`.bin`) |
| `GET` | `/api/firmware` | None | List available firmware versions |
| `GET` | `/api/firmware/check/<device_id>` | Device Bearer | Check if firmware update is available |
| `GET` | `/api/firmware/download/<version>` | Device Bearer | Download firmware `.bin` binary |
| `POST` | `/api/updates/report` | Device Bearer | Report update outcome ('success' or 'failed') |
| `GET` | `/api/updates` | None | List complete update audit log history |
| `GET` | `/api/updates/<device_id>` | None | List update audit logs for single device |

---

## Testing with Curl / Postman

### 1. Register a New ESP32 Device
```bash
curl -X POST http://127.0.0.1:5000/api/devices/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32-001",
    "device_name": "Living Room ESP32",
    "firmware_version": "1.0.0"
  }'
```
*Response returns `"api_token"`. Save this token for subsequent device calls.*

### 2. Device Heartbeat
```bash
curl -X POST http://127.0.0.1:5000/api/devices/ESP32-001/heartbeat \
  -H "Authorization: Bearer YOUR_DEVICE_API_TOKEN"
```

### 3. Upload Firmware (Admin Only)
```bash
curl -X POST http://127.0.0.1:5000/api/firmware/upload \
  -u admin:admin_secret_pass \
  -F "file=@sample_firmware_v1.1.0.bin" \
  -F "version=1.1.0"
```

### 4. Check for Update
```bash
curl -X GET http://127.0.0.1:5000/api/firmware/check/ESP32-001 \
  -H "Authorization: Bearer YOUR_DEVICE_API_TOKEN"
```

### 5. Download Firmware
```bash
curl -X GET http://127.0.0.1:5000/api/firmware/download/1.1.0 \
  -H "Authorization: Bearer YOUR_DEVICE_API_TOKEN" \
  --output downloaded_firmware.bin
```

### 6. Report Update Status
```bash
curl -X POST http://127.0.0.1:5000/api/updates/report \
  -H "Authorization: Bearer YOUR_DEVICE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32-001",
    "old_version": "1.0.0",
    "new_version": "1.1.0",
    "status": "success",
    "message": "Update flashed successfully"
  }'
```

---

## ESP32 Communication Flow

When integrating an actual ESP32 device later using Arduino C++ or ESP-IDF:

1. **Bootup & Registration**: The ESP32 connects to Wi-Fi. On initial boot (or first setup), it sends a POST request to `/api/devices/register` and securely stores the returned `api_token` in ESP32 NVS (Non-Volatile Storage).
2. **Periodic Check**: Every $N$ minutes, the ESP32 issues `GET /api/firmware/check/ESP32-001` with `Authorization: Bearer <token>`.
3. **Download**: If `update_available` is `true`, the ESP32 initiates `HTTPUpdate` or `esp_https_ota` to download the binary stream from `/api/firmware/download/1.1.0`.
4. **Verification**: During stream download, the ESP32 accumulates the incoming byte stream, calculates the SHA-256 hash, and compares it against the `sha256` value provided in the update check.
5. **Flash & Reboot**: Upon verification match, the ESP32 marks the new partition as active, reboots, and sends a POST to `/api/updates/report` confirming `status: success`.

---

## Security Implementation

- **Token Hashing**: Device API tokens are generated using cryptographically secure random bytes (`secrets.token_hex(32)`). The raw token is returned once during registration. Only the SHA-256 hash of the token is saved in SQLite.
- **Path Traversal Protection**: Uploaded filenames are sanitized using `werkzeug.utils.secure_filename`. Path bounds checking ensures files can only be accessed inside `firmware/`.
- **Server-side Hash Calculation**: SHA-256 integrity hashes are computed directly from the saved file on disk by the server, preventing clients from supplying fake hash values.
- **Sanitized API Responses**: Sensitive internal server paths and database token hashes are stripped from all API outputs.
- **Input Validation**: All incoming JSON inputs and version numbers undergo strict validation and semantic version parsing.

---

## Security Limitations

> [!IMPORTANT]
> - **SHA-256 Checksum vs Digital Signature**: SHA-256 provides file **integrity** (protecting against transmission errors or accidental corruption), but does NOT guarantee **authenticity** or **non-repudiation** (proving the file originated from an authorized developer).
> - **Transport Layer Security (TLS)**: In local development, HTTP is used. For production deployments over public networks, HTTPS (TLS/SSL) must be enabled to encrypt token headers and binary traffic against Eavesdropping and Man-in-the-Middle (MitM) attacks.

---

## Future Enhancements
1. **Asymmetric Digital Signatures (ECDSA / RSA)**: Sign firmware binaries with an admin private key so the ESP32 can verify the signature using an embedded public key (Hardware Root of Trust).
2. **Flash Encryption & Secure Boot**: Enable ESP32 hardware Secure Boot V2 and Flash Encryption.
3. **Rollback Safeguards**: Auto-rollback to previous partition if newly updated firmware fails heartbeat check within 60 seconds of reboot.
