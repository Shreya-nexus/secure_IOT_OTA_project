# Secure IoT OTA Firmware Update System - Frontend Dashboard

A modern, responsive, and clean web dashboard for the **Secure IoT OTA Firmware Update System Using ESP32**. Built specifically for B.Tech Cybersecurity & IoT college project demonstrations.

---

## 1. Purpose of Frontend

The web dashboard serves as the administrative control center for managing IoT devices, uploading compiled firmware binaries (`.bin`), monitoring real-time system status, checking firmware updates, and auditing immutable update history logs.

---

## 2. Technologies Used

- **HTML5**: Semantic web structure and accessible forms.
- **CSS3 (Vanilla)**: Modern cybersecurity dark theme, CSS Grid & Flexbox, custom responsive layout, glassmorphism cards, badges, and smooth modal overlays (Zero external CSS frameworks).
- **Vanilla JavaScript (ES6+)**: Modular client logic, async/await Fetch API integration, dynamic DOM manipulation.
- **Fetch API**: Standard browser-native HTTP communication with the Flask backend.

---

## 3. Folder Structure

```
frontend/
│
├── index.html          # Dashboard (Stats, System Status, Recent Activity, Architecture, Security Info)
├── devices.html        # Registered ESP32 Devices Management & OTA Update Checks
├── firmware.html       # Firmware Binaries Repository & Admin Upload Form
├── updates.html        # Complete OTA Update Audit History & Simulation Tool
│
├── css/
│   └── style.css       # Unified design system stylesheet & responsive rules
│
├── js/
│   ├── api.js          # Centralized REST API client & token storage manager
│   ├── dashboard.js    # Statistics aggregator & main view renderer
│   ├── devices.js      # Device registry, modal handlers & update check trigger
│   ├── firmware.js     # Binary upload form, .bin validation & version listing
│   └── updates.js      # Audit log listing, filters & report simulation
│
└── README.md           # Documentation guide
```

---

## 4. Backend URL & Configuration

The frontend connects directly to the local Flask REST API backend:

- **Backend Base URL**: `http://127.0.0.1:5000`
- Configured centrally in `frontend/js/api.js`:
  ```javascript
  const API_BASE_URL = "http://127.0.0.1:5000";
  ```

---

## 5. How to Run

### Step 1: Start the Flask Backend Server
Open a terminal, navigate to `secure-iot-ota/backend`, and run:

```powershell
# Windows
py app.py

# Linux / macOS
python3 app.py
```
*The Flask server will start at `http://127.0.0.1:5000`.*

### Step 2: Open the Frontend Dashboard
You can open `frontend/index.html` in any modern web browser (Chrome, Edge, Firefox, Safari):

- Simply double-click `frontend/index.html` or drag it into your browser.
- Alternatively, serve it via VS Code Live Server or Python HTTP server:
  ```powershell
  py -m http.server 8000 --directory frontend
  ```
  Then navigate to `http://127.0.0.1:8000`.

---

## 6. API Endpoints Used

| Method | Endpoint | Authorization | Description |
|---|---|---|---|
| `GET` | `/` | None | Backend health check & server status |
| `GET` | `/api/devices` | None | List all registered ESP32 devices |
| `GET` | `/api/devices/<device_id>` | None | Get details for single device |
| `POST` | `/api/devices/register` | None | Register new device & generate SHA-256 token |
| `GET` | `/api/firmware` | None | List uploaded firmware versions & SHA-256 hashes |
| `POST` | `/api/firmware/upload` | Admin Credentials | Upload `.bin` binary file with version |
| `GET` | `/api/firmware/check/<device_id>` | Device Bearer Token | Check if firmware update is available |
| `GET` | `/api/updates` | None | List complete OTA update audit log history |
| `POST` | `/api/updates/report` | Device Bearer Token | Report update outcome (`success` / `failed`) |

---

## 7. Key Dashboard Features

### 📊 Dashboard (`index.html`)
- **Live Server Status Indicator**: Displays `● Online` or `● Offline` with auto-reconnect polling every 15s.
- **6 Dynamic Metric Cards**: Backend Status, Total Devices, Online Devices, Firmware Versions, Successful Updates, Failed Updates.
- **Recent Devices & OTA Tables**: Quick view of latest registered devices and update events.
- **Visual System Architecture**: Visual workflow diagram (Admin -> Web Dashboard -> Flask -> SQLite -> Firmware -> ESP32 -> OTA).
- **Security Features Checklist**: Highlights token hashing, admin auth, `.bin` validation, server-side SHA-256 integrity, and path traversal protection.

### 📱 Devices Page (`devices.html`)
- **Device Management**: View registered ESP32 nodes with instant search and status filter.
- **Device Registration Modal**: Register new hardware node (`device_id`, `device_name`, `firmware_version`). Displays the returned raw API token with a one-click copy button and auto-saves token to browser local storage.
- **Device Details & Update Check Modal**: Inspect device attributes and click **Check for Update** to execute live backend check (`GET /api/firmware/check/<device_id>`).

### 📦 Firmware Page (`firmware.html`)
- **Firmware Repository Table**: Displays available versions, server-calculated SHA-256 integrity checksums, file sizes, uploaded timestamps, and "LATEST" status badges. Does NOT expose internal server file paths.
- **Admin Firmware Upload Section**: Allows uploading compiled `.bin` files with version strings. Requires administrator authentication (`X-Admin-Username` & `X-Admin-Password`). Includes strict `.bin` extension validation.

### 📜 Update History Page (`updates.html`)
- **Immutable Audit Logs**: View complete update logs with success/failed badges, old/new versions, and error message details.
- **Search & Filter**: Search logs by device ID, version, or description; filter by outcome status.
- **Report Outcome Simulator**: Interface to test reporting update outcomes (`success` or `failed`) with device token authorization.

---

## 8. Current ESP32 Physical Hardware Limitation

> [!NOTE]
> Currently, physical ESP32 microcontrollers are not connected to the network.
> 
> The dashboard operates directly against the live Flask REST API and SQLite database. When clicking "Check for Update" or "Upload Firmware", real HTTP API calls and database transactions are processed by the backend. Once physical ESP32 hardware is introduced in the next phase, it will communicate with these exact same API endpoints.
