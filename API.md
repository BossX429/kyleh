# API Documentation

> REST API reference for Security Monitor backend

## 🌐 Overview

The Security Monitor provides a REST API for programmatic access to system metrics, security findings, and control operations.

**Base URL:** `http://localhost:5000/api/v1`  
**Protocol:** HTTP  
**Data Format:** JSON

## 🔐 Authentication

Currently, the API is localhost-only and does not require authentication. Future versions may add API key support.

## 📡 Endpoints

### System Metrics

#### GET /metrics

Get current system performance metrics.

**Response:**

```json
{
  "timestamp": "2025-10-24T10:30:00",
  "cpu": {
    "percent": 45.2,
    "cores": 12,
    "frequency_mhz": 3600
  },
  "memory": {
    "total_mb": 32768,
    "used_mb": 16384,
    "percent": 50.0
  },
  "gpu": {
    "name": "AMD Radeon RX 7900 XTX",
    "load_percent": 75.5,
    "memory_used_mb": 12288,
    "memory_total_mb": 24576,
    "temperature_c": 68
  },
  "disk": {
    "read_mb_s": 150.5,
    "write_mb_s": 75.2
  },
  "network": {
    "latency_ms": 15.3,
    "jitter_ms": 2.1
  }
}
```

**Status Codes:**

- `200 OK` - Success
- `500 Internal Server Error` - Metrics collection failed

---

#### GET /metrics/history

Get historical metrics over time.

**Query Parameters:**

- `duration` (optional) - Time range in seconds (default: 300)
- `interval` (optional) - Data point interval in seconds (default: 5)

**Example:**

```
GET /metrics/history?duration=600&interval=10
```

**Response:**

```json
{
  "duration_seconds": 600,
  "interval_seconds": 10,
  "data_points": 60,
  "metrics": [
    {
      "timestamp": "2025-10-24T10:20:00",
      "cpu_percent": 42.1,
      "ram_percent": 48.5,
      "gpu_percent": 70.2
    },
    {
      "timestamp": "2025-10-24T10:20:10",
      "cpu_percent": 45.3,
      "ram_percent": 49.1,
      "gpu_percent": 72.5
    }
    // ... more data points
  ]
}
```

---

### Security & Privacy

#### GET /findings

Get recent security and privacy findings.

**Response:**

```json
{
  "timestamp": "2025-10-24T10:30:00",
  "total_findings": 3,
  "findings": [
    {
      "id": "SEC-001",
      "severity": "warning",
      "category": "process",
      "title": "Suspicious process detected",
      "description": "Unknown process 'malware.exe' started",
      "timestamp": "2025-10-24T10:25:15",
      "recommended_action": "Investigate and quarantine if malicious"
    },
    {
      "id": "PRIV-002",
      "severity": "info",
      "category": "network",
      "title": "New network connection",
      "description": "Connection to 192.168.1.100:443",
      "timestamp": "2025-10-24T10:28:30",
      "recommended_action": "Review connection legitimacy"
    }
  ]
}
```

**Status Codes:**

- `200 OK` - Success
- `500 Internal Server Error` - Query failed

---

#### GET /findings/:id

Get details for a specific finding.

**URL Parameters:**

- `id` - Finding ID (e.g., "SEC-001")

**Response:**

```json
{
  "id": "SEC-001",
  "severity": "warning",
  "category": "process",
  "title": "Suspicious process detected",
  "description": "Unknown process 'malware.exe' started",
  "timestamp": "2025-10-24T10:25:15",
  "details": {
    "process_name": "malware.exe",
    "pid": 12345,
    "path": "C:\\Temp\\malware.exe",
    "parent_process": "explorer.exe",
    "command_line": "malware.exe --stealth"
  },
  "recommended_action": "Investigate and quarantine if malicious",
  "status": "active"
}
```

**Status Codes:**

- `200 OK` - Success
- `404 Not Found` - Finding ID not found
- `500 Internal Server Error` - Query failed

---

### Optimization

#### POST /optimize

Trigger system optimization.

**Request Body:**

```json
{
  "actions": [
    "close_background_apps",
    "boost_priority",
    "clear_ram"
  ],
  "aggressive": false
}
```

**Parameters:**

- `actions` (optional) - Array of optimization actions
  - `close_background_apps` - Close non-essential processes
  - `boost_priority` - Boost foreground app priority
  - `clear_ram` - Clear RAM cache (Windows)
  - `all` - Run all optimizations
- `aggressive` (optional) - Use aggressive optimizations (default: false)

**Response:**

```json
{
  "success": true,
  "optimizations_applied": [
    "close_background_apps",
    "boost_priority"
  ],
  "metrics_before": {
    "cpu_percent": 65.5,
    "ram_percent": 78.2
  },
  "metrics_after": {
    "cpu_percent": 45.2,
    "ram_percent": 62.1
  },
  "improvement": {
    "cpu_reduction": 20.3,
    "ram_freed_mb": 5120
  }
}
```

**Status Codes:**

- `200 OK` - Optimization completed
- `400 Bad Request` - Invalid request body
- `500 Internal Server Error` - Optimization failed

---

### Plugins

#### GET /plugins

List all loaded plugins and their status.

**Response:**

```json
{
  "total_plugins": 2,
  "plugins": [
    {
      "name": "Valorant Monitor",
      "version": "1.0.0",
      "enabled": true,
      "status": "active",
      "metrics": {
        "running": true,
        "cpu_percent": 45.2,
        "memory_mb": 2048
      }
    },
    {
      "name": "GPU Advanced",
      "version": "2.1.0",
      "enabled": true,
      "status": "active",
      "metrics": {
        "gpu_temperature": 68,
        "fan_speed_rpm": 1500
      }
    }
  ]
}
```

**Status Codes:**

- `200 OK` - Success
- `500 Internal Server Error` - Plugin query failed

---

#### GET /plugins/:name

Get detailed information for a specific plugin.

**URL Parameters:**

- `name` - Plugin name (URL encoded)

**Response:**

```json
{
  "name": "Valorant Monitor",
  "version": "1.0.0",
  "description": "Monitors Valorant game performance",
  "enabled": true,
  "status": "active",
  "metrics": {
    "running": true,
    "cpu_percent": 45.2,
    "memory_mb": 2048,
    "threads": 64,
    "fps": 144
  },
  "history": {
    "cpu_avg": 42.5,
    "memory_avg_mb": 1950,
    "sessions": 15
  }
}
```

**Status Codes:**

- `200 OK` - Success
- `404 Not Found` - Plugin not found
- `500 Internal Server Error` - Query failed

---

### Automation

#### GET /automation

Get current automation status and configured tasks.

**Response:**

```json
{
  "enabled": true,
  "active_tasks": 3,
  "tasks": [
    {
      "id": "auto-optimize-1",
      "name": "Auto-optimize on high CPU",
      "trigger": {
        "condition": "cpu_percent > 80",
        "duration_seconds": 30
      },
      "action": "optimize",
      "enabled": true,
      "last_triggered": "2025-10-24T09:15:00"
    },
    {
      "id": "close-chrome-2",
      "name": "Close Chrome when gaming",
      "trigger": {
        "condition": "game_running == true",
        "game": "Valorant"
      },
      "action": "close_process",
      "target": "chrome.exe",
      "enabled": true,
      "last_triggered": "2025-10-24T08:30:00"
    }
  ]
}
```

**Status Codes:**

- `200 OK` - Success
- `500 Internal Server Error` - Query failed

---

#### POST /automation/run

Manually trigger an automation task.

**Request Body:**

```json
{
  "task_id": "auto-optimize-1"
}
```

**Response:**

```json
{
  "success": true,
  "task_id": "auto-optimize-1",
  "result": "Optimization completed",
  "execution_time_ms": 1250
}
```

**Status Codes:**

- `200 OK` - Task executed successfully
- `400 Bad Request` - Invalid task_id
- `404 Not Found` - Task not found
- `500 Internal Server Error` - Execution failed

---

### System State

#### GET /state

Get overall system state and monitor status.

**Response:**

```json
{
  "running": true,
  "version": "0.1.0",
  "uptime_seconds": 3600,
  "monitoring": {
    "cpu": true,
    "ram": true,
    "gpu": true,
    "disk": true,
    "network": true,
    "processes": true
  },
  "plugins_loaded": 2,
  "automation_enabled": true,
  "last_optimization": "2025-10-24T09:15:00",
  "warnings": [],
  "errors": []
}
```

**Status Codes:**

- `200 OK` - Success
- `500 Internal Server Error` - State query failed

---

#### POST /state/pause

Pause monitoring temporarily.

**Response:**

```json
{
  "success": true,
  "monitoring_paused": true
}
```

**Status Codes:**

- `200 OK` - Monitoring paused
- `500 Internal Server Error` - Failed to pause

---

#### POST /state/resume

Resume monitoring after pause.

**Response:**

```json
{
  "success": true,
  "monitoring_paused": false
}
```

**Status Codes:**

- `200 OK` - Monitoring resumed
- `500 Internal Server Error` - Failed to resume

---

## 🔄 WebSocket Support (Future)

Real-time metric streaming via WebSocket will be available in v0.2.0:

```javascript
const ws = new WebSocket('ws://localhost:5000/ws/metrics');

ws.onmessage = (event) => {
  const metrics = JSON.parse(event.data);
  console.log('CPU:', metrics.cpu.percent + '%');
};
```

## 📊 Rate Limiting

**Current:** No rate limiting (localhost only)  
**Future:** 100 requests/minute per IP

## 🛠️ Client Examples

### Python

```python
import requests

# Get metrics
response = requests.get('http://localhost:5000/api/v1/metrics')
metrics = response.json()
print(f"CPU: {metrics['cpu']['percent']}%")

# Trigger optimization
response = requests.post('http://localhost:5000/api/v1/optimize', json={
    'actions': ['close_background_apps', 'boost_priority']
})
result = response.json()
print(f"Optimization success: {result['success']}")
```

### PowerShell

```powershell
# Get metrics
$metrics = Invoke-RestMethod -Uri 'http://localhost:5000/api/v1/metrics'
Write-Host "CPU: $($metrics.cpu.percent)%"

# Trigger optimization
$body = @{
    actions = @('close_background_apps', 'boost_priority')
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri 'http://localhost:5000/api/v1/optimize' -Method Post -Body $body -ContentType 'application/json'
Write-Host "Success: $($result.success)"
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

// Get metrics
axios.get('http://localhost:5000/api/v1/metrics')
  .then(response => {
    console.log(`CPU: ${response.data.cpu.percent}%`);
  });

// Trigger optimization
axios.post('http://localhost:5000/api/v1/optimize', {
  actions: ['close_background_apps', 'boost_priority']
})
  .then(response => {
    console.log(`Success: ${response.data.success}`);
  });
```

## 🐛 Error Handling

All endpoints return errors in consistent format:

```json
{
  "error": true,
  "code": "METRIC_COLLECTION_FAILED",
  "message": "Failed to collect GPU metrics",
  "details": "GPUtil library not installed",
  "timestamp": "2025-10-24T10:30:00"
}
```

**Common Error Codes:**

- `INVALID_REQUEST` - Malformed request body
- `NOT_FOUND` - Resource not found
- `METRIC_COLLECTION_FAILED` - Failed to collect metrics
- `OPTIMIZATION_FAILED` - Optimization action failed
- `PLUGIN_NOT_LOADED` - Requested plugin not loaded
- `INTERNAL_ERROR` - Unexpected server error

## 📚 Related Documentation

- [Plugin Development Guide](PLUGIN_DEVELOPMENT.md) - Create custom plugins
- [Main README](README.md) - Project overview
- [Backend Architecture](backend_frontend_mapping.md) - System design

---

**API Version:** 1.0  
**Last Updated:** October 2025
