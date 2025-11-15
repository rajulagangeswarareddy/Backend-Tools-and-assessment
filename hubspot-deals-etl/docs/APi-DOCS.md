# HubSpot Deals Data Extraction Service - API Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URLs](#base-urls)
4. [Common Response Formats](#common-response-formats)
5. [API Endpoints](#api-endpoints)
6. [Health & Stats Endpoints](#health--stats-endpoints)
7. [Error Handling](#error-handling)
8. [Examples](#examples)
9. [Rate Limiting](#rate-limiting)
10. [Changelog](#changelog)

## 🔍 Overview

The HubSpot Deals Data Extraction Service is a REST API service that extracts deal data from HubSpot CRM and loads it into a PostgreSQL database using DLT (data load tool). The service provides endpoints to start, monitor, and retrieve deal extraction scans.

### API Version
- **Version**: 1.0.0
- **Base Path**: `/api/v1`
- **Content Type**: `application/json`
- **Documentation**: Available at `/docs` (Swagger UI)

### Key Features
- **Deal Extraction**: Extract deals from HubSpot CRM with configurable filters and date ranges
- **Background Processing**: Asynchronous scan processing with status monitoring
- **Checkpoint Support**: Resume interrupted scans from the last checkpoint
- **Pagination**: Retrieve results with configurable pagination limits
- **Multiple Tables**: Access extracted data through multiple database tables
- **Maintenance Operations**: Cleanup old scans and detect crashed jobs

## 🔐 Authentication

This service uses HubSpot Private App Access Token authentication. The access token must be provided in each scan request configuration.

### Required Credentials
- **accessToken**: HubSpot Private App Access Token (required, minimum 10 characters)
- **tennantUrl**: HubSpot tenant URL (optional, must be valid URL format if provided)

### Required Permissions
The HubSpot Private App must have the following scopes:
- `crm.objects.deals.read` - Read access to deals objects (required)

### Authentication in Requests
Authentication credentials are provided in the scan request body, not as HTTP headers:

```json
{
  "config": {
    "auth": {
      "accessToken": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "tennantUrl": "https://app.hubspot.com"  // Optional
    }
  }
}
```

### Security Notes
- Access tokens are encrypted before storage in the database
- Never share or log access tokens
- Rotate tokens regularly for security
- Use environment variables or secure vaults to store tokens in production

## 🌐 Base URLs

### Development
```
http://localhost:5000
```

### Staging
```
https://staging-api.your-domain.com
```

### Production
```
https://api.your-domain.com
```

### Swagger Documentation
```
http://localhost:5000/api/v1/docs
```

All API endpoints are prefixed with `/api/v1`. For example:
- Start scan: `POST /api/v1/scan/start`
- Get status: `GET /api/v1/scan/{scan_id}/status`
- Get results: `GET /api/v1/results/{scan_id}/result`

## 📊 Common Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response (Validation)
```json
{
  "status": "error",
  "message": "Input validation failed",
  "errors": {
    "[field_name]": "Field is required"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response (Application Logic)
```json
{
  "status": "error",
  "error_code": "RESOURCE_NOT_FOUND",
  "message": "The requested resource was not found",
  "details": {},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Pagination Response
```json
{
  "pagination": {
    "current_page": 1,
    "page_size": 50,
    "total_items": 150,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false,
    "next_page": 2,
    "previous_page": null
  }
}
```

## 🔍 API Endpoints

### Scan Operations

#### 1. Start Deal Extraction Scan

**POST** `/api/v1/scan/start`

Initiates a new deal extraction scan from HubSpot CRM. The scan runs asynchronously in the background.

#### Request Body
```json
{
  "config": {
    "scanId": "hubspot-deals-scan-2025-001",
    "organizationId": "org-12345",
    "type": ["user"],
    "auth": {
      "accessToken": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "tennantUrl": "https://app.hubspot.com"
    },
    "filters": {
      "properties": [
        "dealname",
        "amount",
        "dealstage",
        "pipeline",
        "createdate",
        "closedate"
      ],
      "includeArchived": false,
      "dateRange": {
        "startDate": "2024-01-01",
        "endDate": "2024-12-31"
      }
    }
  }
}
```

#### Request Schema
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config.scanId` | string | Yes | Unique identifier for the scan (alphanumeric, hyphens, underscores only, 1-255 chars) |
| `config.organizationId` | string | Yes | Organization identifier (1-255 chars) |
| `config.type` | array | Yes | Scan type (must be `["user"]`) |
| `config.auth.accessToken` | string | Yes | HubSpot Private App Access Token (minimum 10 characters) |
| `config.auth.tennantUrl` | string | No | HubSpot tenant URL (optional, must be valid URL format) |
| `config.filters.properties` | array | No | List of deal properties to extract (e.g., `["dealname", "amount"]`) |
| `config.filters.includeArchived` | boolean | No | Include archived deals (default: `false`) |
| `config.filters.dateRange.startDate` | string | No | Start date for deal filtering (YYYY-MM-DD format) |
| `config.filters.dateRange.endDate` | string | No | End date for deal filtering (YYYY-MM-DD format) |

#### Response
```json
{
  "success": true,
  "message": "Scan initialization accepted and is now processing in the background."
}
```

#### Status Codes
- **202**: Scan started successfully (processing in background)
- **400**: Invalid request data (validation errors)
- **409**: Scan with this ID already exists
- **500**: Internal server error

#### Example Request
```bash
curl -X POST "http://localhost:5000/api/v1/scan/start" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "scanId": "hubspot-deals-scan-2025-001",
      "organizationId": "org-12345",
      "type": ["user"],
      "auth": {
        "accessToken": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      },
      "filters": {
        "properties": ["dealname", "amount", "dealstage"],
        "dateRange": {
          "startDate": "2024-01-01",
          "endDate": "2024-12-31"
        }
      }
    }
  }'
```

#### 2. Get Scan Status

**GET** `/api/v1/scan/{scan_id}/status`

Retrieves the current status and progress of a deal extraction scan.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scan_id` | string | Yes | Unique scan identifier |

#### Response Schema
```json
{
  "success": true,
  "data": {
    "scanId": "hubspot-deals-scan-2025-001",
    "organizationId": "org-12345",
    "type": "user",
    "status": "running",
    "startTime": "2024-01-15T10:30:00Z",
    "endTime": null,
    "lastHeartbeat": "2024-01-15T10:35:00Z",
    "recordsExtracted": 1250,
    "duration": 300.5,
    "errorMessage": null,
    "metadata": {},
    "config": {
      "scanId": "hubspot-deals-scan-2025-001",
      "organizationId": "org-12345",
      "type": ["user"],
      "filters": {
        "properties": ["dealname", "amount", "dealstage"]
      }
    },
    "checkpointInfo": {
      "latestCheckpoint": {},
      "progress": 45.5,
      "lastCheckpointAt": "2024-01-15T10:35:00Z"
    }
  }
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `scanId` | string | Unique scan identifier |
| `organizationId` | string | Organization identifier |
| `status` | string | Current scan status (see Status Values below) |
| `startTime` | string | Scan start time (ISO 8601 format) |
| `endTime` | string | Scan end time (ISO 8601 format, null if not completed) |
| `lastHeartbeat` | string | Last heartbeat timestamp |
| `recordsExtracted` | integer | Number of deals extracted so far |
| `duration` | float | Scan duration in seconds |
| `errorMessage` | string | Error message if failed (null otherwise) |
| `checkpointInfo` | object | Checkpoint information for resume capability |

#### Status Values
- **pending**: Scan queued but not started
- **running**: Scan in progress
- **completed**: Scan finished successfully
- **failed**: Scan failed with error
- **cancelled**: Scan cancelled by user
- **crashed**: Scan crashed (detected by timeout)
- **resuming**: Scan resuming from checkpoint

#### Status Codes
- **200**: Status retrieved successfully
- **404**: Scan not found
- **500**: Internal server error

#### Example Request
```bash
curl "http://localhost:5000/api/v1/scan/hubspot-deals-scan-2025-001/status"
```

#### 3. Cancel Scan

**POST** `/api/v1/scan/{scan_id}/cancel`

Cancels an ongoing or pending scan. Cannot cancel completed or failed scans.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scan_id` | string | Yes | Unique scan identifier |

#### Response
```json
{
  "success": true,
  "message": "Scan cancelled successfully",
  "data": {
    "scanId": "hubspot-deals-scan-2025-001",
    "status": "cancelled"
  }
}
```

#### Status Codes
- **200**: Scan cancelled successfully
- **400**: Cannot cancel scan (scan already completed/failed/cancelled)
- **404**: Scan not found
- **500**: Internal server error

#### Example Request
```bash
curl -X POST "http://localhost:5000/api/v1/scan/hubspot-deals-scan-2025-001/cancel"
```

---

#### 4. Pause Scan

**POST** `/api/v1/scan/{scan_id}/pause`

Pauses a running scan. The scan can be resumed later from the last checkpoint.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scan_id` | string | Yes | Unique scan identifier |

#### Response
```json
{
  "success": true,
  "message": "Scan paused successfully",
  "data": {
    "scanId": "hubspot-deals-scan-2025-001",
    "status": "paused"
  }
}
```

#### Status Codes
- **200**: Scan paused successfully
- **400**: Cannot pause scan
- **404**: Scan not found
- **500**: Internal server error

---

#### 5. List Scans

**GET** `/api/v1/scan/list`

Lists all scans with optional filtering and pagination.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `organizationId` | string | No | - | Filter by organization ID |
| `limit` | integer | No | 20 | Number of scans per page (max 100) |
| `offset` | integer | No | 0 | Number of scans to skip |

#### Response
```json
{
  "success": true,
  "data": {
    "scans": [
      {
        "scanId": "hubspot-deals-scan-2025-001",
        "organizationId": "org-12345",
        "status": "completed",
        "startTime": "2024-01-15T10:30:00Z",
        "endTime": "2024-01-15T10:45:00Z",
        "recordsExtracted": 2500
      }
    ],
    "pagination": {
      "total": 50,
      "limit": 20,
      "offset": 0,
      "hasMore": true,
      "returned": 20
    }
  }
}
```

#### Status Codes
- **200**: Scans retrieved successfully
- **400**: Invalid pagination parameters
- **500**: Internal server error

#### Example Request
```bash
curl "http://localhost:5000/api/v1/scan/list?organizationId=org-12345&limit=10&offset=0"
```

---

#### 6. Remove Scan

**DELETE** `/api/v1/scan/{scan_id}/remove`

Removes a scan and all associated data from the database. Can only remove completed, failed, or cancelled scans.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scan_id` | string | Yes | Unique scan identifier |

#### Response
```json
{
  "success": true,
  "message": "Scan removed successfully",
  "data": {
    "scanId": "hubspot-deals-scan-2025-001",
    "recordsDeleted": 2500
  }
}
```

#### Status Codes
- **200**: Scan removed successfully
- **400**: Cannot remove scan (scan is still running or pending)
- **404**: Scan not found
- **500**: Internal server error

#### Example Request
```bash
curl -X DELETE "http://localhost:5000/api/v1/scan/hubspot-deals-scan-2025-001/remove"
```

---

### Results Operations

#### 7. Get Available Tables

**GET** `/api/v1/results/{scan_id}/tables`

Returns a list of available database tables for a completed scan.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scan_id` | string | Yes | Unique scan identifier |

#### Response
```json
{
  "success": true,
  "data": {
    "scanId": "hubspot-deals-scan-2025-001",
    "datasetName": "hubspot_deals_extraction",
    "tables": [
      {
        "name": "users",
        "rowCount": 2500,
        "extractedCount": 2500
      },
      {
        "name": "deals",
        "rowCount": 5000,
        "extractedCount": 5000
      }
    ],
    "totalTables": 2
  }
}
```

#### Status Codes
- **200**: Tables retrieved successfully
- **400**: Scan not completed yet
- **404**: Scan not found
- **500**: Internal server error

#### Example Request
```bash
curl "http://localhost:5000/api/v1/results/hubspot-deals-scan-2025-001/tables"
```

---

#### 8. Get Scan Results

**GET** `/api/v1/results/{scan_id}/result`

Retrieves paginated results from a specific table for a completed scan.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scan_id` | string | Yes | Unique scan identifier |

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tableName` | string | No | "users" | Name of the table to query |
| `limit` | integer | No | 100 | Number of records per page (max 500) |
| `offset` | integer | No | 0 | Number of records to skip |

#### Response
```json
{
  "success": true,
  "data": {
    "scanId": "hubspot-deals-scan-2025-001",
    "tableName": "deals",
    "records": [
      {
        "id": "12345",
        "dealname": "Q1 Enterprise Deal",
        "amount": "50000",
        "dealstage": "appointmentscheduled",
        "pipeline": "default",
        "createdate": "2024-01-15T10:00:00Z",
        "closedate": null
      }
    ],
    "pagination": {
      "total": 5000,
      "limit": 100,
      "offset": 0,
      "hasMore": true,
      "returned": 100
    },
    "availableTables": ["users", "deals"],
    "columns": ["id", "dealname", "amount", "dealstage", "pipeline", "createdate", "closedate"]
  }
}
```

#### Status Codes
- **200**: Results retrieved successfully
- **400**: Scan not completed or invalid parameters
- **404**: Scan not found
- **500**: Internal server error

#### Example Request
```bash
curl "http://localhost:5000/api/v1/results/hubspot-deals-scan-2025-001/result?tableName=deals&limit=50&offset=0"
```

### Pipeline Operations

#### 9. Get Pipeline Info

**GET** `/api/v1/pipeline/info`

Returns information about the DLT pipeline configuration and status.

#### Response
```json
{
  "success": true,
  "data": {
    "pipeline_name": "hubspot_deals_extraction",
    "destination_type": "postgres",
    "working_dir": ".dlt",
    "dataset_name": "hubspot_deals_extraction",
    "is_active": true,
    "source_type": "hubspot_deals",
    "uses_api_service": true,
    "configuration_method": "config_file",
    "database_health": true,
    "supports_checkpoints": true,
    "error": null
  }
}
```

#### Status Codes
- **200**: Pipeline info retrieved successfully
- **500**: Internal server error

#### Example Request
```bash
curl "http://localhost:5000/api/v1/pipeline/info"
```

---

### Maintenance Operations

#### 10. Cleanup Old Scans

**POST** `/api/v1/maintenance/cleanup`

Removes old scan results from the database based on age threshold.

#### Request Body
```json
{
  "daysOld": 7
}
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `daysOld` | integer | No | 7 | Remove scans older than this many days (1-365) |

#### Response
```json
{
  "success": true,
  "message": "Successfully cleaned up 15 old scan results",
  "data": {
    "cleanedCount": 15,
    "daysOld": 7
  }
}
```

#### Status Codes
- **200**: Cleanup completed successfully
- **400**: Invalid request data
- **500**: Internal server error

#### Example Request
```bash
curl -X POST "http://localhost:5000/api/v1/maintenance/cleanup" \
  -H "Content-Type: application/json" \
  -d '{"daysOld": 30}'
```

---

#### 11. Detect Crashed Jobs

**POST** `/api/v1/maintenance/detect-crashed`

Detects and marks jobs that have exceeded the timeout threshold as crashed.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `timeoutMinutes` | integer | No | 10 | Timeout in minutes for crash detection (1-1440) |

#### Response
```json
{
  "success": true,
  "message": "Detected 2 crashed jobs",
  "data": {
    "crashedJobIds": ["job-001", "job-002"],
    "crashedCount": 2,
    "timeoutMinutes": 10
  }
}
```

#### Status Codes
- **200**: Detection completed successfully
- **400**: Invalid timeout parameter
- **500**: Internal server error

#### Example Request
```bash
curl -X POST "http://localhost:5000/api/v1/maintenance/detect-crashed?timeoutMinutes=30"
```

---

## 🏥 Health & Stats Endpoints

### 12. Health Check

**GET** `/api/v1/health`

Returns the overall health status of the service and its dependencies.

#### Response (Healthy)
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "hubspot_deals_extraction",
  "pipeline": {
    "pipeline_name": "hubspot_deals_extraction",
    "database_health": true,
    "supports_checkpoints": true
  }
}
```

#### Response (Unhealthy)
```json
{
  "status": "unhealthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "hubspot_deals_extraction",
  "error": "Database connection failed"
}
```

#### Status Codes
- **200**: Service is healthy
- **500**: Service is unhealthy

#### Example Request
```bash
curl "http://localhost:5000/api/v1/health"
```

---

### 13. Service Statistics

**GET** `/api/v1/stats`

Returns comprehensive service statistics including scan counts and performance metrics.

#### Response
```json
{
  "success": true,
  "data": {
    "total_jobs": 150,
    "status_breakdown": {
      "completed": 120,
      "running": 5,
      "failed": 15,
      "cancelled": 10
    },
    "recent_jobs_7_days": 45,
    "total_records_extracted": 250000,
    "organization_filter": null,
    "generated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Status Codes
- **200**: Statistics retrieved successfully
- **500**: Internal server error

#### Example Request
```bash
curl "http://localhost:5000/api/v1/stats"
```

---

## ⚠️ Error Handling

All error responses follow a consistent format with a `success: false` indicator and an `error` or `message` field describing the issue.

### Error Response Format

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error information",
  "validation_errors": {}  // Only present for validation errors
}
```

### Error Status Codes

#### 400 Bad Request - Validation Errors
Returned when request validation fails:

```json
{
  "success": false,
  "message": "Configuration validation failed: {'config': {'scanId': ['Scan ID is required']}}",
  "error": "Configuration validation failed: {'config': {'scanId': ['Scan ID is required']}}",
  "validation_errors": {
    "config": {
      "scanId": ["Scan ID is required"],
      "auth": {
        "accessToken": ["Access token is required"]
      }
    }
  }
}
```

**Common validation errors:**
- Missing required fields (scanId, organizationId, auth.accessToken)
- Invalid scan ID format (must be alphanumeric with hyphens/underscores, 1-255 chars)
- Invalid date format (must be YYYY-MM-DD)
- Invalid pagination parameters (limit must be 1-1000, offset must be >= 0)
- Invalid timeout values

#### 404 Not Found
Returned when a requested resource doesn't exist:

```json
{
  "success": false,
  "message": "No scan found with ID: hubspot-deals-scan-2025-001",
  "error": "No scan found with ID: hubspot-deals-scan-2025-001"
}
```

#### 409 Conflict
Returned when attempting to create a resource that already exists:

```json
{
  "success": false,
  "message": "A scan with ID 'hubspot-deals-scan-2025-001' already exists",
  "error": "A scan with ID 'hubspot-deals-scan-2025-001' already exists"
}
```

#### 500 Internal Server Error
Returned for unexpected server errors:

```json
{
  "success": false,
  "message": "An unexpected error occurred: Database connection timeout",
  "error": "Database connection timeout"
}
```

### HTTP Status Code Summary

| Status Code | Description | When It Occurs |
|-------------|-------------|----------------|
| **200** | OK | Request succeeded |
| **202** | Accepted | Scan started successfully (processing in background) |
| **400** | Bad Request | Invalid request data or validation errors |
| **404** | Not Found | Scan or resource not found |
| **409** | Conflict | Scan with same ID already exists |
| **500** | Internal Server Error | Unexpected server error |
| **503** | Service Unavailable | Service unhealthy (health check endpoint) |

### Error Handling Best Practices

1. **Always check the `success` field** in responses
2. **Handle validation errors** by checking `validation_errors` field
3. **Retry on 500 errors** with exponential backoff
4. **Check scan status** before retrieving results (scan must be completed)
5. **Validate pagination parameters** before making requests
6. **Handle rate limiting** if implemented (429 status code)

---

## 📚 Examples

### Complete Deal Extraction Workflow

This section provides comprehensive examples for starting scans and getting results using curl, Python, and PowerShell.

#### 1. Start Deal Extraction Scan

**Using curl:**
```bash
curl -X POST "http://localhost:5000/api/v1/scan/start" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "scanId": "hubspot-deals-scan-2025-001",
      "organizationId": "org-12345",
      "type": ["user"],
      "auth": {
        "accessToken": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      },
      "filters": {
        "properties": [
          "dealname",
          "amount",
          "dealstage",
          "pipeline",
          "createdate",
          "closedate"
        ],
        "dateRange": {
          "startDate": "2024-01-01",
          "endDate": "2024-12-31"
        },
        "includeArchived": false
      }
    }
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Scan initialization accepted and is now processing in the background."
}
```

#### 2. Monitor Scan Progress

**Using curl:**
```bash
curl "http://localhost:5000/api/v1/scan/hubspot-deals-scan-2025-001/status"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "scanId": "hubspot-deals-scan-2025-001",
    "status": "running",
    "startTime": "2024-01-15T10:30:00Z",
    "recordsExtracted": 1250,
    "checkpointInfo": {
      "progress": 45.5,
      "lastCheckpointAt": "2024-01-15T10:35:00Z"
    }
  }
}
```

#### 3. Get Available Tables (after scan completes)

**Using curl:**
```bash
curl "http://localhost:5000/api/v1/results/hubspot-deals-scan-2025-001/tables"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "scanId": "hubspot-deals-scan-2025-001",
    "tables": [
      {
        "name": "deals",
        "rowCount": 5000,
        "extractedCount": 5000
      }
    ],
    "totalTables": 1
  }
}
```

#### 4. Get Scan Results

**Using curl:**
```bash
curl "http://localhost:5000/api/v1/results/hubspot-deals-scan-2025-001/result?tableName=deals&limit=50&offset=0"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "scanId": "hubspot-deals-scan-2025-001",
    "tableName": "deals",
    "records": [
      {
        "id": "12345",
        "dealname": "Q1 Enterprise Deal",
        "amount": "50000",
        "dealstage": "appointmentscheduled",
        "pipeline": "default",
        "createdate": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "total": 5000,
      "limit": 50,
      "offset": 0,
      "hasMore": true,
      "returned": 50
    }
  }
}
```

#### 5. Cancel Scan (if needed)

**Using curl:**
```bash
curl -X POST "http://localhost:5000/api/v1/scan/hubspot-deals-scan-2025-001/cancel"
```

#### 6. Remove Scan (cleanup)

**Using curl:**
```bash
curl -X DELETE "http://localhost:5000/api/v1/scan/hubspot-deals-scan-2025-001/remove"
```

### PowerShell Examples

#### Start Deal Extraction Scan
```powershell
$body = @{
  config = @{
    scanId = "hubspot-deals-scan-2025-001"
    organizationId = "org-12345"
    type = @("user")
    auth = @{
      accessToken = "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
    filters = @{
      properties = @("dealname", "amount", "dealstage", "pipeline")
      dateRange = @{
        startDate = "2024-01-01"
        endDate = "2024-12-31"
      }
      includeArchived = $false
    }
  }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:5000/api/v1/scan/start" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

#### Get Scan Status
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/v1/scan/hubspot-deals-scan-2025-001/status"
Write-Host "Scan Status: $($response.data.status)"
Write-Host "Records Extracted: $($response.data.recordsExtracted)"
```

#### Get Scan Results
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/v1/results/hubspot-deals-scan-2025-001/result?tableName=deals&limit=50"
$response.data.records | Format-Table
```

### Python Examples

#### Start Deal Extraction Scan
```python
import requests

BASE_URL = "http://localhost:5000/api/v1"

# Start scan
payload = {
    "config": {
        "scanId": "hubspot-deals-scan-2025-001",
        "organizationId": "org-12345",
        "type": ["user"],
        "auth": {
            "accessToken": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        },
        "filters": {
            "properties": [
                "dealname",
                "amount",
                "dealstage",
                "pipeline",
                "createdate",
                "closedate"
            ],
            "dateRange": {
                "startDate": "2024-01-01",
                "endDate": "2024-12-31"
            },
            "includeArchived": False
        }
    }
}

response = requests.post(f"{BASE_URL}/scan/start", json=payload)
if response.status_code == 202:
    print("Scan started successfully!")
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

#### Monitor Scan Progress
```python
import requests
import time

BASE_URL = "http://localhost:5000/api/v1"
scan_id = "hubspot-deals-scan-2025-001"

while True:
    response = requests.get(f"{BASE_URL}/scan/{scan_id}/status")
    
    if response.status_code == 200:
        data = response.json()
        status = data['data']['status']
        records = data['data'].get('recordsExtracted', 0)
        
        print(f"Status: {status}, Records Extracted: {records}")
        
        if status in ['completed', 'failed', 'cancelled', 'crashed']:
            break
    else:
        print(f"Error: {response.status_code}")
        break
    
    time.sleep(10)  # Check every 10 seconds
```

#### Get Paginated Results
```python
import requests

BASE_URL = "http://localhost:5000/api/v1"
scan_id = "hubspot-deals-scan-2025-001"
table_name = "deals"
limit = 100
offset = 0
all_records = []

while True:
    url = f"{BASE_URL}/results/{scan_id}/result"
    params = {
        "tableName": table_name,
        "limit": limit,
        "offset": offset
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        records = data['data']['records']
        all_records.extend(records)
        pagination = data['data']['pagination']
        
        print(f"Retrieved {len(records)} records (offset: {offset})")
        
        if not pagination.get('hasMore', False):
            break
        
        offset += limit
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        break

print(f"\nTotal records retrieved: {len(all_records)}")
```

#### Complete Workflow Example
```python
import requests
import time

BASE_URL = "http://localhost:5000/api/v1"

def start_scan(scan_id, access_token, start_date, end_date):
    """Start a new deal extraction scan"""
    payload = {
        "config": {
            "scanId": scan_id,
            "organizationId": "org-12345",
            "type": ["user"],
            "auth": {"accessToken": access_token},
            "filters": {
                "properties": ["dealname", "amount", "dealstage"],
                "dateRange": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/scan/start", json=payload)
    return response.json() if response.status_code == 202 else None

def wait_for_completion(scan_id, max_wait_minutes=60):
    """Wait for scan to complete"""
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while time.time() - start_time < max_wait_seconds:
        response = requests.get(f"{BASE_URL}/scan/{scan_id}/status")
        if response.status_code == 200:
            data = response.json()
            status = data['data']['status']
            
            if status == 'completed':
                return True, data['data']
            elif status in ['failed', 'cancelled', 'crashed']:
                return False, data['data']
        
        time.sleep(10)
    
    return False, {"error": "Timeout waiting for scan to complete"}

def get_results(scan_id, table_name="deals", limit=100):
    """Get all results from a completed scan"""
    offset = 0
    all_records = []
    
    while True:
        params = {"tableName": table_name, "limit": limit, "offset": offset}
        response = requests.get(f"{BASE_URL}/results/{scan_id}/result", params=params)
        
        if response.status_code != 200:
            break
        
        data = response.json()
        records = data['data']['records']
        all_records.extend(records)
        
        if not data['data']['pagination'].get('hasMore', False):
            break
        
        offset += limit
    
    return all_records

# Usage
scan_id = "hubspot-deals-scan-2025-001"
access_token = "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Start scan
print("Starting scan...")
result = start_scan(scan_id, access_token, "2024-01-01", "2024-12-31")
if result:
    print(f"Scan started: {scan_id}")

# Wait for completion
print("Waiting for scan to complete...")
success, status_data = wait_for_completion(scan_id)
if success:
    print(f"Scan completed! Extracted {status_data.get('recordsExtracted', 0)} records")
    
    # Get results
    print("Retrieving results...")
    deals = get_results(scan_id)
    print(f"Retrieved {len(deals)} deals")
else:
    print(f"Scan failed or was cancelled: {status_data}")

#### Error Handling
```python
import requests

BASE_URL = "http://localhost:5000/api/v1"

def safe_request(method, endpoint, **kwargs):
    """Make a request with error handling"""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_data = e.response.json() if e.response.content else {}
        print(f"HTTP Error {e.response.status_code}: {error_data.get('message', 'Unknown error')}")
        if 'validation_errors' in error_data:
            print(f"Validation errors: {error_data['validation_errors']}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

# Example usage
result = safe_request('POST', '/scan/start', json={
    "config": {
        "scanId": "test-scan",
        "organizationId": "org-12345",
        "type": ["user"],
        "auth": {"accessToken": "invalid-token"}
    }
})
```

---

## ⚡ Rate Limiting

The API implements rate limiting to ensure fair usage and system stability. Rate limits may vary by environment and endpoint.

### Rate Limit Headers

When rate limits are approached or exceeded, the API includes the following headers in responses:

- `X-RateLimit-Limit`: Maximum number of requests allowed per window
- `X-RateLimit-Remaining`: Number of requests remaining in the current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit window resets

### Rate Limit Response

When rate limit is exceeded, the API returns a **429 Too Many Requests** status code:

```json
{
  "success": false,
  "message": "Rate limit exceeded. Please retry after 60 seconds.",
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

### Rate Limit Best Practices

1. **Implement exponential backoff** when receiving 429 responses
2. **Respect the `Retry-After` header** value (in seconds)
3. **Monitor rate limit headers** to avoid hitting limits
4. **Batch requests** when possible to reduce API calls
5. **Use pagination** efficiently to minimize requests

### Default Rate Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Scan Operations | 100 requests | Per hour |
| Results Operations | 1000 requests | Per hour |
| Maintenance Operations | 10 requests | Per hour |
| Health/Stats | 60 requests | Per minute |

*Note: Rate limits may vary by environment and can be configured. Check with your administrator for specific limits.*

---

## 📝 Changelog

### Version 1.0.0 (2025-01-15)

**Initial Release**

#### Features
- ✅ Deal extraction from HubSpot CRM
- ✅ Asynchronous scan processing with background jobs
- ✅ Scan status monitoring and progress tracking
- ✅ Checkpoint support for resume capability
- ✅ Paginated results retrieval
- ✅ Multiple table access for extracted data
- ✅ Scan management (cancel, pause, remove)
- ✅ Maintenance operations (cleanup, crash detection)
- ✅ Health check and statistics endpoints
- ✅ Comprehensive error handling
- ✅ Swagger API documentation at `/api/v1/docs`

#### API Endpoints
- `POST /api/v1/scan/start` - Start deal extraction scan
- `GET /api/v1/scan/{scan_id}/status` - Get scan status
- `POST /api/v1/scan/{scan_id}/cancel` - Cancel scan
- `POST /api/v1/scan/{scan_id}/pause` - Pause scan
- `GET /api/v1/scan/list` - List all scans
- `DELETE /api/v1/scan/{scan_id}/remove` - Remove scan
- `GET /api/v1/results/{scan_id}/tables` - Get available tables
- `GET /api/v1/results/{scan_id}/result` - Get scan results
- `GET /api/v1/pipeline/info` - Get pipeline information
- `POST /api/v1/maintenance/cleanup` - Cleanup old scans
- `POST /api/v1/maintenance/detect-crashed` - Detect crashed jobs
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - Service statistics

#### Authentication
- HubSpot Private App Access Token authentication
- Encrypted token storage
- Token validation on scan start

#### Data Format
- Request/Response: JSON
- Date format: YYYY-MM-DD (ISO 8601)
- Timestamps: ISO 8601 format

---

## 📖 Additional Resources

- **Swagger Documentation**: `http://localhost:5000/api/v1/docs`
- **Integration Documentation**: See `INTEGRATION-DOCS.md`
- **Database Design**: See `DATABASE-DESIGN-DOCS.md`
- **Extraction Documentation**: See `EXTRACTION-DOCS.md`

---

## 💡 Support

For questions, issues, or feature requests, please contact the development team or refer to the project repository.