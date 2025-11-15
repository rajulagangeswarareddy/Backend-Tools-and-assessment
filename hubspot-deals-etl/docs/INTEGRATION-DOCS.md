# 📋 HubSpot Deals - Integration with HubSpot CRM API v3

This document explains the HubSpot REST API endpoints required by the HubSpot Deals Data Extraction Service to extract deal data from HubSpot CRM instances.

---

## 📋 Overview

The HubSpot Deals Data Extraction Service integrates with HubSpot CRM API v3 endpoints to extract deal information. Below are the required and optional endpoints:

### ✅ **Required Endpoint (Essential)**
| **API Endpoint**                    | **Purpose**                          | **Version** | **Required Permissions** | **Usage**    |
|-------------------------------------|--------------------------------------|-------------|--------------------------|--------------|
| `/crm/v3/objects/deals`             | Search and list deals                | v3          | `crm.objects.deals.read` | **Required** |

### 🔧 **Optional Endpoints (Advanced Features)**
| **API Endpoint**                    | **Purpose**                          | **Version** | **Required Permissions** | **Usage**    |
|-------------------------------------|--------------------------------------|-------------|--------------------------|--------------|
| `/crm/v3/objects/deals/{dealId}`    | Get detailed deal information        | v3          | `crm.objects.deals.read` | Optional     |
| `/crm/v4/associations/deals/contacts` | Get deal-contact associations      | v4          | `crm.objects.deals.read` | Optional     |
| `/crm/v3/pipelines/deals`           | Get deal pipeline configuration      | v3          | `crm.objects.deals.read` | Optional     |
| `/crm/v3/objects/deals/search`      | Search deals with filters            | v3          | `crm.objects.deals.read` | Optional     |

### 🎯 **Recommendation**
**Start with only the required endpoint.** The `/crm/v3/objects/deals` endpoint provides all essential deal data needed for basic deal analytics and extraction.

---

## 🔐 Authentication Requirements

### **Private App Access Token Authentication**

HubSpot uses Private App Access Tokens for API authentication. The token must be included in the `Authorization` header as a Bearer token.

**Authentication Header:**
```
Authorization: Bearer <PRIVATE_APP_ACCESS_TOKEN>
Content-Type: application/json
```

**Token Format:**
- Private App Access Tokens start with `pat-na1-` for US accounts or `pat-eu1-` for EU accounts
- Example: `pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### **Required Permissions**

The HubSpot Private App must have the following scopes:
- **`crm.objects.deals.read`**: Read access to deals objects (required for deal extraction)

### **Creating a Private App**

1. Log into HubSpot account
2. Navigate to **Settings** → **Integrations** → **Private Apps**
3. Create a new private app
4. Grant the `crm.objects.deals.read` scope
5. Copy the Private App Access Token (only shown once)

### **Security Best Practices**

- Store tokens securely (encrypted in database)
- Never commit tokens to version control
- Rotate tokens regularly
- Use environment variables or secure vaults in production

---

## 🌐 HubSpot CRM API v3 Endpoints

### 🎯 **PRIMARY ENDPOINT (Required for Basic Deal Extraction)**

### 1. **List Deals** - `/crm/v3/objects/deals` ✅ **REQUIRED**

**Purpose**: Get paginated list of all deals - **THIS IS ALL YOU NEED FOR BASIC DEAL EXTRACTION**

**Method**: `GET`

**Base URL**: `https://api.hubapi.com`

**Full Endpoint**: `https://api.hubapi.com/crm/v3/objects/deals`

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 100 | Number of deals to return (max 100) |
| `after` | string | No | - | Pagination cursor from previous response |
| `properties` | string | No | All properties | Comma-separated list of deal properties to return |
| `archived` | boolean | No | false | Whether to include archived deals |
| `associations` | string | No | - | Comma-separated list of association types (e.g., "contacts") |

**Example Request**:
```http
GET https://api.hubapi.com/crm/v3/objects/deals?limit=100&properties=dealname,amount,dealstage,createdate,closedate,pipeline&archived=false
Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Content-Type: application/json
```

**Response Structure**:
```json
{
  "results": [
    {
      "id": "1234567890",
      "properties": {
        "dealname": "Q1 Enterprise Deal",
        "amount": "50000",
        "dealstage": "appointmentscheduled",
        "pipeline": "default",
        "createdate": "2024-01-15T10:00:00.000Z",
        "closedate": null,
        "dealtype": "newbusiness",
        "hubspot_owner_id": "12345678",
        "hs_deal_amount_calculation_preference": "deal_amount"
      },
      "createdAt": "2024-01-15T10:00:00.000Z",
      "updatedAt": "2024-01-15T12:30:00.000Z",
      "archived": false
    },
    {
      "id": "0987654321",
      "properties": {
        "dealname": "Enterprise Renewal",
        "amount": "75000",
        "dealstage": "closedwon",
        "pipeline": "default",
        "createdate": "2024-01-10T08:00:00.000Z",
        "closedate": "2024-02-01T17:00:00.000Z",
        "dealtype": "existingbusiness"
      },
      "createdAt": "2024-01-10T08:00:00.000Z",
      "updatedAt": "2024-02-01T17:00:00.000Z",
      "archived": false
    }
  ],
  "paging": {
    "next": {
      "after": "0987654321",
      "link": "?after=0987654321&limit=100"
    }
  }
}
```

**✅ This endpoint provides ALL essential deal fields:**
- Deal ID, name, amount, stage, pipeline
- Creation and close dates
- Deal type, owner information
- Custom properties (if requested)
- Association data (if requested)

**Rate Limits**:
- **100 requests per 10 seconds** per Private App
- **40,000 requests per day** per Private App
- Burst limit: 100 requests in a single burst

---

## 🔧 **OPTIONAL ENDPOINTS (Advanced Features Only)**

> **⚠️ Note**: These endpoints are NOT required for basic [object] extraction. Only implement if you need advanced [object] analytics like [feature 1], [feature 2], or [feature 3].

### 2. **Get [Object] Details** - `/[api_path]/[endpoint_1]/{objectId}` 🔧 **OPTIONAL**

**Purpose**: Get detailed information for a specific [/crm/v3/objects/deals/{dealId}]

**When to use**: Only if you need additional [object] metadata not available in search

**Method**: `GET`

**URL**: `https://{baseUrl}/[api_path]/[endpoint_1]/{objectId}`

**Request Example**:
```http
GET https://[your_instance].[platform_domain]/[api_path]/[endpoint_1]/[sample_id]
[AUTH_HEADER]: [AUTH_VALUE]
Content-Type: application/json
```

**Response Structure**:
```json
{
  "[field_id]": "[sample_id]",
  "[field_url]": "https://[your_instance].[platform_domain]/[api_path]/[endpoint_1]/[sample_id]",
  "[field_name]": "[Sample Object Name]",
  "[field_type]": "[object_type]",
  "[additional_field_1]": {
    "[sub_field_1]": [
      {
        "[property_1]": "[value_1]",
        "[property_2]": "[value_2]",
        "[property_3]": true
      }
    ],
    "[sub_field_2]": [
      {
        "[property_4]": "[value_4]",
        "[property_5]": "[value_5]"
      }
    ]
  },
  "[nested_object]": {
    "[nested_field_1]": "[value_1]",
    "[nested_field_2]": "[value_2]",
    "[nested_field_3]": "[value_3]",
    "[nested_field_4]": "[value_4]",
    "[nested_field_5]": "[value_5]"
  },
  "[boolean_field_1]": true,
  "[boolean_field_2]": false,
  "[boolean_field_3]": false
}
```

---

### 3. **Get [Object] [Related Data]** - `/[api_path]/[endpoint_2]/{objectId}/[related_endpoint]` 🔧 **OPTIONAL**

**Purpose**: Get [related data] associated with a [object]

**When to use**: Only if you need [related data] analysis and [specific metrics]

**Method**: `GET`

**URL**: `https://{baseUrl}/[api_path]/[endpoint_2]/{objectId}/[related_endpoint]`

**Query Parameters**:
```
?[param1]=[value]&[param2]=[value]&[filter_param]=[filter_value]
```

**Request Example**:
```http
GET https://[your_instance].[platform_domain]/[api_path]/[endpoint_2]/[sample_id]/[related_endpoint]?[param2]=[value]
[AUTH_HEADER]: [AUTH_VALUE]
Content-Type: application/json
```

**Response Structure**:
```json
{
  "[pagination_start]": 0,
  "[pagination_size]": 50,
  "[pagination_total]": 25,
  "[pagination_last]": false,
  "[data_array]": [
    {
      "[related_id]": 1,
      "[related_url]": "https://[your_instance].[platform_domain]/[api_path]/[related_endpoint]/1",
      "[related_status]": "[status_1]",
      "[related_name]": "[Related Item 1]",
      "[date_start]": "[date_format]",
      "[date_end]": "[date_format]",
      "[date_complete]": "[date_format]",
      "[date_created]": "[date_format]",
      "[origin_field]": "[sample_id]",
      "[description_field]": "[Description text]"
    },
    {
      "[related_id]": 2,
      "[related_url]": "https://[your_instance].[platform_domain]/[api_path]/[related_endpoint]/2",
      "[related_status]": "[status_2]", 
      "[related_name]": "[Related Item 2]",
      "[date_start]": "[date_format]",
      "[date_end]": "[date_format]",
      "[date_created]": "[date_format]",
      "[origin_field]": "[sample_id]",
      "[description_field]": "[Description text]"
    }
  ]
}
```

---

### 4. **Get [Object] Configuration** - `/[api_path]/[endpoint_3]/{objectId}/[config_endpoint]` 🔧 **OPTIONAL**

**Purpose**: Get [object] configuration details ([config_type_1], [config_type_2], [config_type_3])

**When to use**: Only if you need [workflow type] and [object] setup analysis

**Method**: `GET`

**URL**: `https://{baseUrl}/[api_path]/[endpoint_3]/{objectId}/[config_endpoint]`

**Request Example**:
```http
GET https://[your_instance].[platform_domain]/[api_path]/[endpoint_3]/[sample_id]/[config_endpoint]
[AUTH_HEADER]: [AUTH_VALUE]
Content-Type: application/json
```

**Response Structure**:
```json
{
  "[field_id]": "[sample_id]",
  "[field_name]": "[Sample Object Name]",
  "[field_type]": "[object_type]",
  "[field_url]": "https://[your_instance].[platform_domain]/[api_path]/[endpoint_3]/[sample_id]/[config_endpoint]",
  "[location_field]": {
    "[location_type]": "[location_value]",
    "[location_identifier]": "[identifier]"
  },
  "[filter_field]": {
    "[filter_id]": "[filter_value]",
    "[filter_url]": "https://[your_instance].[platform_domain]/[api_path]/[filter_endpoint]/[filter_value]"
  },
  "[config_object]": {
    "[config_array]": [
      {
        "[config_name]": "[Config Item 1]",
        "[config_values]": [
          {
            "[config_id]": "[id_1]",
            "[config_url]": "https://[your_instance].[platform_domain]/[api_path]/[status_endpoint]/[id_1]"
          }
        ]
      },
      {
        "[config_name]": "[Config Item 2]",
        "[config_values]": [
          {
            "[config_id]": "[id_2]",
            "[config_url]": "https://[your_instance].[platform_domain]/[api_path]/[status_endpoint]/[id_2]"
          }
        ]
      },
      {
        "[config_name]": "[Config Item 3]",
        "[config_values]": [
          {
            "[config_id]": "[id_3]",
            "[config_url]": "https://[your_instance].[platform_domain]/[api_path]/[status_endpoint]/[id_3]"
          }
        ]
      }
    ],
    "[constraint_type]": "[constraint_value]"
  },
  "[estimation_field]": {
    "[estimation_type]": "[estimation_value]",
    "[estimation_details]": {
      "[detail_id]": "[detail_value]",
      "[detail_name]": "[Detail Display Name]"
    }
  }
}
```

---

### 5. **Get [Object] [Additional Data]** - `/[api_path]/[endpoint_4]/{objectId}/[additional_endpoint]` 🔧 **OPTIONAL**

**Purpose**: Get [additional data] for a [object]

**When to use**: Only if you need [additional data] analysis and [specific functionality]

**Method**: `GET`

**URL**: `https://{baseUrl}/[api_path]/[endpoint_4]/{objectId}/[additional_endpoint]`

**Query Parameters**:
```
?[param1]=[value]&[param2]=[value]&[query_param]=[query_value]&[validation_param]=[validation_value]&[fields_param]=[field1],[field2],[field3],[field4]
```

**Request Example**:
```http
GET https://[your_instance].[platform_domain]/[api_path]/[endpoint_4]/[sample_id]/[additional_endpoint]?[param2]=[value]
[AUTH_HEADER]: [AUTH_VALUE]
Content-Type: application/json
```

**Response Structure**:
```json
{
  "[pagination_start]": 0,
  "[pagination_size]": 50,
  "[pagination_total]": 120,
  "[data_key]": [
    {
      "[item_id]": "[item_id_value]",
      "[item_key]": "[ITEM-123]",
      "[item_url]": "https://[your_instance].[platform_domain]/[api_path]/[item_endpoint]/[item_id_value]",
      "[item_fields]": {
        "[summary_field]": "[Item summary text]",
        "[status_field]": {
          "[status_id]": "[status_id_value]",
          "[status_name]": "[Status Name]",
          "[status_category]": {
            "[category_id]": 2,
            "[category_key]": "[category_key]",
            "[category_color]": "[color-name]"
          }
        },
        "[assignee_field]": {
          "[assignee_id]": "[assignee_account_id]",
          "[assignee_name]": "[Assignee Name]"
        },
        "[priority_field]": {
          "[priority_id]": "[priority_id_value]",
          "[priority_name]": "[Priority Level]"
        }
      }
    }
  ]
}
```

---

## 📊 Data Extraction Flow

### 🎯 **SIMPLE FLOW (Recommended - Using Only Required Endpoint)**

### **Single Endpoint Approach - `/crm/v3/objects/deals` Only**

This is the recommended approach for extracting all deal data. It requires only one API endpoint and provides all essential deal information.

```python
import requests
from typing import List, Dict, Any, Optional

def extract_all_deals(
    access_token: str,
    properties: Optional[List[str]] = None,
    include_archived: bool = False,
    max_deals: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Extract all deals from HubSpot CRM using pagination.
    
    Args:
        access_token: HubSpot Private App Access Token
        properties: Optional list of properties to retrieve (default: all)
        include_archived: Whether to include archived deals
        max_deals: Maximum number of deals to extract (None = all)
    
    Returns:
        List of deal objects
    """
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    all_deals = []
    after = None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    while True:
        params = {
            "limit": 100,  # Maximum allowed by HubSpot API
            "archived": str(include_archived).lower()
        }
        
        if after:
            params["after"] = after
        
        if properties:
            params["properties"] = ",".join(properties)
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            deals = data.get("results", [])
            all_deals.extend(deals)
            
            # Check if we've reached max_deals limit
            if max_deals and len(all_deals) >= max_deals:
                all_deals = all_deals[:max_deals]
                break
            
            # Check for pagination
            paging = data.get("paging", {})
            if "next" not in paging:
                break
            
            after = paging["next"].get("after")
            
            # Rate limit handling
            if response.headers.get("X-HubSpot-RateLimit-Second-Remaining") == "0":
                retry_after = int(response.headers.get("Retry-After", 10))
                time.sleep(retry_after)
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching deals: {e}")
            raise
    
    return all_deals


# Example usage
access_token = "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Extract all deals with specific properties
deals = extract_all_deals(
    access_token=access_token,
    properties=["dealname", "amount", "dealstage", "pipeline", "createdate", "closedate"],
    include_archived=False
)

print(f"Extracted {len(deals)} deals")

# This gives you ALL essential deal data:
# - Deal ID, name, amount, stage, pipeline
# - Creation and close dates
# - Deal type, owner information
# - Custom properties (if requested)
```

### **Deal Properties in Response**

Each deal object contains:
- `id`: Unique deal ID (string)
- `properties`: Object containing deal properties (dealname, amount, dealstage, etc.)
- `createdAt`: Creation timestamp (ISO 8601)
- `updatedAt`: Last update timestamp (ISO 8601)
- `archived`: Boolean indicating if deal is archived

---

### 🔧 **ADVANCED FLOW (Optional - Multiple Endpoints)**

> **⚠️ Only use this if you need [related_data], [configuration], or [additional_data] data**

### **Step 1: Batch [Object] Retrieval**
```python
# Get [objects] in batches of 50
for start_at in range(0, total_objects, 50):
    response = requests.get(
        f"{base_url}/[api_path]/[primary_endpoint]",
        params={
            "[pagination_param]": start_at,
            "[size_param]": 50
        },
        headers=auth_headers
    )
    objects_data = response.json()
    objects = objects_data.get("[data_array]", [])
```

### **Step 2: Enhanced [Object] Details (Optional)**
```python
# Get detailed information for each [object]
for obj in objects:
    response = requests.get(
        f"{base_url}/[api_path]/[endpoint_1]/{obj['[field_id]']}",
        headers=auth_headers
    )
    detailed_object = response.json()
```

### **Step 3: [Object] [Related Data] (Optional)**
```python
# Get [related data] for each [specific type] [object]
for obj in objects:
    if obj['[field_type]'] == '[specific_type]':
        response = requests.get(
            f"{base_url}/[api_path]/[endpoint_2]/{obj['[field_id]']}/[related_endpoint]",
            params={"[param2]": 50},
            headers=auth_headers
        )
        object_related_data = response.json()
```

### **Step 4: [Object] Configuration (Optional)**
```python
# Get configuration for each [object]
for obj in objects:
    response = requests.get(
        f"{base_url}/[api_path]/[endpoint_3]/{obj['[field_id]']}/[config_endpoint]",
        headers=auth_headers
    )
    object_config = response.json()
```

---

## 📋 Available Deal Properties

HubSpot deals have many built-in and custom properties. Here are the most commonly used standard properties:

### **Standard Deal Properties**

| Property Name | Type | Description |
|---------------|------|-------------|
| `dealname` | String | Deal name |
| `amount` | Number | Deal amount (as string) |
| `dealstage` | String | Deal stage ID |
| `pipeline` | String | Pipeline ID |
| `createdate` | DateTime | Creation date (ISO 8601) |
| `closedate` | DateTime | Close date (ISO 8601, nullable) |
| `dealtype` | String | Deal type (newbusiness, existingbusiness, etc.) |
| `hubspot_owner_id` | String | Owner user ID |
| `description` | String | Deal description |
| `deal_currency_code` | String | Currency code (e.g., "USD") |
| `hs_deal_amount_calculation_preference` | String | Amount calculation preference |
| `hs_next_step` | String | Next step |
| `hs_priority` | String | Deal priority |

### **Custom Properties**

Custom properties can be created in HubSpot and accessed via the API. They follow the format `hs_custom_field_name` or `custom_field_name`.

**To list all available properties:**
```http
GET https://api.hubapi.com/crm/v3/properties/deals
Authorization: Bearer <token>
```

---

## ⚡ Performance Considerations

### **Rate Limiting**

HubSpot API enforces strict rate limits:

- **100 requests per 10 seconds** per Private App
- **40,000 requests per day** per Private App
- **Burst Limit**: Up to 100 requests in rapid succession

**Rate Limit Headers in Response:**
```
X-HubSpot-RateLimit-Daily: 40000
X-HubSpot-RateLimit-Daily-Remaining: 38500
X-HubSpot-RateLimit-Second: 100
X-HubSpot-RateLimit-Second-Remaining: 95
```

**Best Practices:**
- Implement exponential backoff on 429 responses
- Monitor rate limit headers
- Batch requests efficiently (use max limit of 100)
- Use pagination cursors (`after` parameter) for large datasets

### **Batch Processing**

- **Recommended Batch Size**: 100 deals per request (API maximum)
- **Concurrent Requests**: Max 100 requests per 10-second window
- **Request Interval**: Monitor rate limit headers to avoid exceeding limits
- **Pagination**: Use `after` cursor for efficient pagination

### **Error Handling**

HubSpot API returns standard HTTP status codes:

```http
# Rate limit exceeded
HTTP/429 Too Many Requests
Retry-After: 10
X-HubSpot-RateLimit-Second-Remaining: 0

# Authentication failed  
HTTP/401 Unauthorized
{
  "status": "error",
  "message": "Invalid access token"
}

# Insufficient permissions
HTTP/403 Forbidden
{
  "status": "error",
  "message": "Permission denied"
}

# Deal not found
HTTP/404 Not Found
{
  "status": "error",
  "message": "Deal not found"
}

# Invalid request
HTTP/400 Bad Request
{
  "status": "error",
  "message": "Invalid property name",
  "correlationId": "abc123"
}
```

**Error Response Format:**
```json
{
  "status": "error",
  "message": "Error description",
  "correlationId": "unique-correlation-id",
  "category": "VALIDATION_ERROR"
}
```

---

## 🔒 Security Requirements

### **API Token Permissions**

#### ✅ **Required (Minimum Permissions)**
```
Required Scopes:
- [scope_1] (for basic [object] information)
```

#### 🔧 **Optional (Advanced Features)**
```
Additional Scopes (only if using optional endpoints):
- [scope_2] (for [related data] information)
- [scope_3] (for [object] configuration)
```

### **User Permissions**

#### ✅ **Required (Minimum)**
The API token user must have:
- **[Permission_1]** global permission
- **[Permission_2]** permission

#### 🔧 **Optional (Advanced Features)**
Additional permissions (only if using optional endpoints):
- **[Permission_3]** permission (for [object] configuration details)
- **[Permission_4]** (for [additional data] access)

---

## 📈 Monitoring & Debugging

### **Request Headers for Debugging**
```http
[AUTH_HEADER]: [AUTH_VALUE]
Content-Type: application/json
User-Agent: [ServiceName]/1.0
X-Request-ID: [object]-scan-001-batch-1
```

### **Response Validation**
```python
def validate_object_response(object_data):
    required_fields = ["[field_id]", "[field_name]", "[field_type]", "[nested_object]"]
    for field in required_fields:
        if field not in object_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate [object] type
    if object_data["[field_type]"] not in ["[type_1]", "[type_2]"]:
        raise ValueError(f"Invalid [object] type: {object_data['[field_type]']}")
```

### **API Usage Metrics**
- Track requests per [time period]
- Monitor response times
- Log rate limit headers
- Track authentication failures

---

## 🧪 Testing API Integration

### **Test Authentication**
```bash
curl -X GET \
  "https://api.hubapi.com/crm/v3/objects/deals?limit=1" \
  -H "Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  -H "Content-Type: application/json"
```

### **Test Deal Listing**
```bash
curl -X GET \
  "https://api.hubapi.com/crm/v3/objects/deals?limit=5&properties=dealname,amount,dealstage" \
  -H "Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  -H "Content-Type: application/json"
```

### **Test Deal Details**
```bash
curl -X GET \
  "https://api.hubapi.com/crm/v3/objects/deals/1234567890" \
  -H "Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  -H "Content-Type: application/json"
```

### **Test Pagination**
```bash
# First page
curl -X GET \
  "https://api.hubapi.com/crm/v3/objects/deals?limit=10" \
  -H "Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Second page (using 'after' from first response)
curl -X GET \
  "https://api.hubapi.com/crm/v3/objects/deals?limit=10&after=0987654321" \
  -H "Authorization: Bearer pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

---

## 🚨 Common Issues & Solutions

### **Issue**: 401 Unauthorized
**Solution**: Verify Private App Access Token is valid and correctly formatted
```bash
# Verify token format (should start with pat-na1- or pat-eu1-)
# Token must be included in Authorization header as Bearer token
curl -X GET \
  "https://api.hubapi.com/crm/v3/objects/deals?limit=1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Common Causes:**
- Token expired or revoked
- Token not included in request
- Token format incorrect (must include "Bearer" prefix)
- Token belongs to different HubSpot account

### **Issue**: 403 Forbidden
**Solution**: Check Private App has `crm.objects.deals.read` scope enabled
- Go to HubSpot Settings → Integrations → Private Apps
- Select your private app
- Ensure "Read deals" permission is enabled

### **Issue**: 429 Rate Limited
**Solution**: Implement retry with exponential backoff
```python
import time
import random
import requests

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', 10))
                wait_time = retry_after + (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise
        else:
            return
    raise Exception("Max retries exceeded")
```

### **Issue**: Empty Deal List
**Solution**: Check if:
- Deals exist in HubSpot account
- `archived=false` is correctly set (default)
- Property filters are not too restrictive
- Private App has access to the deals

### **Issue**: Invalid Property Names
**Solution**: Use correct HubSpot property internal names
- Standard properties: `dealname`, `amount`, `dealstage`, etc.
- Custom properties: Check exact name in HubSpot settings
- List all properties: `GET https://api.hubapi.com/crm/v3/properties/deals`

---

## 💡 **Implementation Recommendations**

### 🎯 **Phase 1: Start Simple (Recommended)**
1. Implement only `/crm/v3/objects/deals` endpoint
2. Extract basic deal data (dealname, amount, dealstage, pipeline, dates)
3. This covers 90% of deal analytics needs

### 🔧 **Phase 2: Add Advanced Features (If Needed)**
1. Add `/crm/v3/objects/deals/{dealId}` for detailed deal information
2. Add `/crm/v4/associations/deals/contacts` for deal-contact associations  
3. Add `/crm/v3/pipelines/deals` for pipeline configuration analysis
4. Add `/crm/v3/objects/deals/search` for filtered searches

### ⚡ **Performance Tip**
- **Simple approach**: 1 API call per 100 deals (max batch size)
- **Advanced approach**: 1 + N API calls (N = number of deals for details)
- Start simple to minimize API usage and stay within rate limits!

### **Recommended Properties to Extract**

**Essential Properties:**
- `dealname` - Deal name
- `amount` - Deal amount
- `dealstage` - Current deal stage
- `pipeline` - Pipeline ID
- `createdate` - Creation date
- `closedate` - Close date (if closed)

**Recommended Additional Properties:**
- `dealtype` - Deal type (new/existing business)
- `hubspot_owner_id` - Owner user ID
- `description` - Deal description
- `deal_currency_code` - Currency
- `hs_next_step` - Next step
- `hs_priority` - Priority level

---

## 📞 Support Resources

- **HubSpot API Documentation**: https://developers.hubspot.com/docs/api/crm/deals
- **HubSpot Rate Limiting Guide**: https://developers.hubspot.com/docs/api/working-with-apis/rate-limits
- **HubSpot Private Apps Guide**: https://developers.hubspot.com/docs/api/working-with-apis/private-apps
- **HubSpot Deals Properties Reference**: https://developers.hubspot.com/docs/api/crm/properties
- **HubSpot CRM API Overview**: https://developers.hubspot.com/docs/api/crm/understanding-the-crm