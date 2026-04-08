# ChangeMappers API Documentation

## Overview

The ChangeMappers API provides programmatic access to a comprehensive database of social change actors, organizations, initiatives, causes, patterns, and stories. The API follows RESTful principles and returns JSON responses.

**Base URL:** `https://api.changemappers.org/v1`

**API Version:** 1.0.0

**Content-Type:** `application/json`

---

## Authentication

All API requests require authentication using one of the following methods:

### API Key Authentication

Include your API key in the request header:

```http
Authorization: Bearer YOUR_API_KEY
```

### OAuth 2.0

For applications requiring user-specific access, use OAuth 2.0:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Obtaining an API Key

1. Register at https://changemappers.org/developers
2. Create a new application
3. Generate an API key with appropriate scopes

**API Key Scopes:**
- `read:public` - Read access to public data
- `read:private` - Read access to private data (requires approval)
- `write` - Write access (requires approval)
- `admin` - Administrative access (internal use only)

---

## Rate Limiting

API requests are rate limited to ensure fair usage:

| Plan | Requests/hour | Requests/minute | Burst Limit |
|------|---------------|-----------------|-------------|
| Free | 100 | 30 | 10 |
| Basic | 1,000 | 100 | 50 |
| Professional | 10,000 | 500 | 100 |
| Enterprise | Unlimited | 1,000 | 500 |

### Rate Limit Headers

All responses include rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
```

### Rate Limit Exceeded

When rate limits are exceeded, the API returns:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Retry after 60 seconds.",
    "retry_after": 60
  }
}
```

---

## Response Format

All responses are returned in JSON format with consistent structure:

### Success Response

```json
{
  "data": { ... },
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 OK | Successful GET request |
| 201 Created | Successful POST request |
| 204 No Content | Successful DELETE request |
| 400 Bad Request | Invalid request parameters |
| 401 Unauthorized | Authentication required |
| 403 Forbidden | Insufficient permissions |
| 404 Not Found | Resource not found |
| 409 Conflict | Resource conflict (e.g., duplicate) |
| 422 Unprocessable Entity | Validation error |
| 429 Too Many Requests | Rate limit exceeded |
| 500 Internal Server Error | Server error |
| 503 Service Unavailable | Service temporarily unavailable |

### Error Codes

Common error codes returned by the API:

| Code | Description |
|------|-------------|
| `BAD_REQUEST` | Invalid request parameters or body |
| `UNAUTHORIZED` | Missing or invalid authentication |
| `FORBIDDEN` | Insufficient permissions |
| `NOT_FOUND` | Requested resource not found |
| `CONFLICT` | Resource already exists or conflict |
| `UNPROCESSABLE_ENTITY` | Validation failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_SERVER_ERROR` | Server-side error |

---

## Pagination

List endpoints support pagination using `limit` and `offset` parameters:

**Request:**
```http
GET /v1/organizations?limit=20&offset=0
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "total": 234,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

### Pagination Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `limit` | integer | 20 | 100 | Number of results per page |
| `offset` | integer | 0 | - | Pagination offset |

---

## Filtering and Sorting

### Filtering

Most endpoints support filtering via query parameters:

```http
GET /v1/organizations?sector=environment&location=Germany
GET /v1/initiatives?status=active&type=campaign
GET /v1/causes?urgency=critical&category=environment
```

### Sorting

Control sorting with `sort` and `order` parameters:

```http
GET /v1/organizations?sort=name&order=asc
GET /v1/initiatives?sort=created_at&order=desc
```

### Search

Full-text search is available on searchable fields:

```http
GET /v1/search?q=climate&types=organizations,initiatives
```

---

## Endpoints

### Actors

Manage and query actors (individuals, groups, networks).

**Endpoint:** `/v1/actors`

| Method | Description |
|--------|-------------|
| GET | List actors with optional filters |
| POST | Create a new actor |
| PUT | Update an existing actor |
| DELETE | Delete an actor |

**Examples:**

```bash
# List all actors
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/actors?limit=10"

# Get specific actor
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/actors?id=actor_abc123"

# Create actor
curl -X POST -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"organization","name":"Climate Action Network","tags":["climate","activism"]}' \
  "https://api.changemappers.org/v1/actors"
```

```javascript
// JavaScript
const response = await fetch('https://api.changemappers.org/v1/actors?limit=10', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY'
  }
});
const data = await response.json();
```

```python
# Python
import requests

headers = {'Authorization': 'Bearer YOUR_API_KEY'}
response = requests.get(
    'https://api.changemappers.org/v1/actors',
    params={'limit': 10},
    headers=headers
)
data = response.json()
```

---

### Organizations

Manage and query organizations in the changemaking ecosystem.

**Endpoint:** `/v1/organizations`

| Method | Description |
|--------|-------------|
| GET | List organizations with filters |
| POST | Create a new organization |
| PUT | Update an organization |
| DELETE | Delete an organization |

**Examples:**

```bash
# List environmental organizations
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/organizations?sector=environment&limit=20"

# Search organizations by name
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/organizations?name=green"

# Create organization
curl -X POST -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Future Initiative",
    "type": "ngo",
    "sector": "environment",
    "location": {"city": "Berlin", "country": "Germany"},
    "tags": ["climate", "sustainability"]
  }' \
  "https://api.changemappers.org/v1/organizations"
```

```javascript
// JavaScript - Create organization
const response = await fetch('https://api.changemappers.org/v1/organizations', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Green Future Initiative',
    type: 'ngo',
    sector: 'environment',
    location: { city: 'Berlin', country: 'Germany' },
    tags: ['climate', 'sustainability']
  })
});
const organization = await response.json();
```

```python
# Python - Create organization
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}
data = {
    'name': 'Green Future Initiative',
    'type': 'ngo',
    'sector': 'environment',
    'location': {'city': 'Berlin', 'country': 'Germany'},
    'tags': ['climate', 'sustainability']
}
response = requests.post(
    'https://api.changemappers.org/v1/organizations',
    json=data,
    headers=headers
)
organization = response.json()
```

---

### Initiatives

Manage and query initiatives, projects, campaigns, and programs.

**Endpoint:** `/v1/initiatives`

| Method | Description |
|--------|-------------|
| GET | List initiatives with filters |
| POST | Create a new initiative |
| PUT | Update an initiative |
| DELETE | Delete an initiative |

**Examples:**

```bash
# List active initiatives
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/initiatives?status=active&limit=20"

# Get initiatives by organization
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/initiatives?organization_id=org_abc123"

# Filter by date range
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/initiatives?start_date=2024-01-01&end_date=2024-12-31"
```

```javascript
// JavaScript - List initiatives
const response = await fetch(
  'https://api.changemappers.org/v1/initiatives?status=active&limit=20',
  {
    headers: { 'Authorization': 'Bearer YOUR_API_KEY' }
  }
);
const initiatives = await response.json();

// Create initiative
const createResponse = await fetch('https://api.changemappers.org/v1/initiatives', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Urban Gardening Project',
    type: 'project',
    status: 'planning',
    organization_id: 'org_abc123',
    start_date: '2024-06-01',
    tags: ['urban', 'gardening']
  })
});
```

```python
# Python
import requests

headers = {'Authorization': 'Bearer YOUR_API_KEY'}

# List initiatives
response = requests.get(
    'https://api.changemappers.org/v1/initiatives',
    params={'status': 'active', 'limit': 20},
    headers=headers
)
initiatives = response.json()

# Create initiative
data = {
    'name': 'Urban Gardening Project',
    'type': 'project',
    'status': 'planning',
    'organization_id': 'org_abc123',
    'start_date': '2024-06-01',
    'tags': ['urban', 'gardening']
}
response = requests.post(
    'https://api.changemappers.org/v1/initiatives',
    json=data,
    headers=headers
)
```

---

### Causes

Manage and query social and environmental causes.

**Endpoint:** `/v1/causes`

| Method | Description |
|--------|-------------|
| GET | List causes with filters |
| POST | Create a new cause |
| PUT | Update a cause |
| DELETE | Delete a cause |

**Examples:**

```bash
# List critical causes
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/causes?urgency=critical"

# Filter by SDG
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/causes?sdg=SDG13"

# Get hierarchical causes
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/causes?parent_id=cause_abc123&include_children=true"
```

```javascript
// JavaScript
const response = await fetch(
  'https://api.changemappers.org/v1/causes?urgency=critical&category=environment',
  { headers: { 'Authorization': 'Bearer YOUR_API_KEY' } }
);
const causes = await response.json();
```

```python
# Python
import requests

headers = {'Authorization': 'Bearer YOUR_API_KEY'}
response = requests.get(
    'https://api.changemappers.org/v1/causes',
    params={'urgency': 'critical', 'category': 'environment'},
    headers=headers
)
causes = response.json()
```

---

### Patterns

Manage and query reusable change patterns and strategies.

**Endpoint:** `/v1/patterns`

| Method | Description |
|--------|-------------|
| GET | List patterns with filters |
| POST | Create a new pattern |
| PUT | Update a pattern |
| DELETE | Delete a pattern |

**Examples:**

```bash
# List proven patterns
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/patterns?effectiveness=proven&limit=20"

# Filter by category
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/patterns?category=mobilization"

# Search patterns
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/patterns?name=community"
```

```javascript
// JavaScript
const response = await fetch(
  'https://api.changemappers.org/v1/patterns?effectiveness=proven',
  { headers: { 'Authorization': 'Bearer YOUR_API_KEY' } }
);
const patterns = await response.json();
```

```python
# Python
import requests

headers = {'Authorization': 'Bearer YOUR_API_KEY'}
response = requests.get(
    'https://api.changemappers.org/v1/patterns',
    params={'effectiveness': 'proven'},
    headers=headers
)
patterns = response.json()
```

---

### Stories

Manage and query narratives documenting change efforts.

**Endpoint:** `/v1/stories`

| Method | Description |
|--------|-------------|
| GET | List stories with filters |
| POST | Create a new story |
| PUT | Update a story |
| DELETE | Delete a story |

**Examples:**

```bash
# List featured stories
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/stories?featured=true&limit=10"

# Get case studies
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/stories?type=case_study"

# Filter by organization
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/stories?organization_id=org_abc123"
```

```javascript
// JavaScript
const response = await fetch(
  'https://api.changemappers.org/v1/stories?featured=true&type=case_study',
  { headers: { 'Authorization': 'Bearer YOUR_API_KEY' } }
);
const stories = await response.json();
```

```python
# Python
import requests

headers = {'Authorization': 'Bearer YOUR_API_KEY'}
response = requests.get(
    'https://api.changemappers.org/v1/stories',
    params={'featured': 'true', 'type': 'case_study'},
    headers=headers
)
stories = response.json()
```

---

### Search

Full-text search across all entity types.

**Endpoint:** `/v1/search`

| Method | Description |
|--------|-------------|
| GET | Search across entities |

**Examples:**

```bash
# Basic search
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/search?q=climate"

# Search specific types
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/search?q=climate&types=organizations,initiatives"

# Search with filters
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/search?q=climate&filters[location]=Germany&filters[tags]=activism"
```

```javascript
// JavaScript
const response = await fetch(
  'https://api.changemappers.org/v1/search?q=climate&types=organizations,initiatives',
  { headers: { 'Authorization': 'Bearer YOUR_API_KEY' } }
);
const results = await response.json();
```

```python
# Python
import requests

headers = {'Authorization': 'Bearer YOUR_API_KEY'}
response = requests.get(
    'https://api.changemappers.org/v1/search',
    params={'q': 'climate', 'types': 'organizations,initiatives'},
    headers=headers
)
results = response.json()
```

---

### Graph

Graph traversal and relationship queries.

**Endpoint:** `/v1/graph`

| Method | Description |
|--------|-------------|
| GET | Traverse graph from a starting node |
| POST | Complex graph queries |

**Examples:**

```bash
# Get neighbors of an organization
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/graph?start_node=org_abc123&start_type=organization&depth=2"

# Filter by relationship type
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/graph?start_node=org_abc123&start_type=organization&relationship_types=PARTNER_OF,MEMBER_OF"

# Find shortest path
curl -X POST -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "shortest_path",
    "start_nodes": [{"id": "org_abc123", "type": "organization"}],
    "end_nodes": [{"id": "org_xyz789", "type": "organization"}]
  }' \
  "https://api.changemappers.org/v1/graph"
```

```javascript
// JavaScript - Graph traversal
const response = await fetch(
  'https://api.changemappers.org/v1/graph?start_node=org_abc123&start_type=organization&depth=2',
  { headers: { 'Authorization': 'Bearer YOUR_API_KEY' } }
);
const graph = await response.json();

// Complex graph query
const queryResponse = await fetch('https://api.changemappers.org/v1/graph', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query_type: 'shortest_path',
    start_nodes: [{ id: 'org_abc123', type: 'organization' }],
    end_nodes: [{ id: 'org_xyz789', type: 'organization' }]
  })
});
const path = await queryResponse.json();
```

```python
# Python
import requests

headers = {'Authorization': 'Bearer YOUR_API_KEY'}

# Graph traversal
response = requests.get(
    'https://api.changemappers.org/v1/graph',
    params={
        'start_node': 'org_abc123',
        'start_type': 'organization',
        'depth': 2
    },
    headers=headers
)
graph = response.json()

# Complex query
data = {
    'query_type': 'shortest_path',
    'start_nodes': [{'id': 'org_abc123', 'type': 'organization'}],
    'end_nodes': [{'id': 'org_xyz789', 'type': 'organization'}]
}
response = requests.post(
    'https://api.changemappers.org/v1/graph',
    json=data,
    headers=headers
)
path = response.json()
```

---

### Taxonomies

Lookup taxonomy values and controlled vocabularies.

**Endpoint:** `/v1/taxonomies`

| Method | Description |
|--------|-------------|
| GET | List taxonomy values |

**Examples:**

```bash
# Get all taxonomies
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/taxonomies"

# Get specific taxonomy
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/taxonomies?name=sectors"

# Get with usage counts
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/taxonomies?include_counts=true"
```

```javascript
// JavaScript
const response = await fetch(
  'https://api.changemappers.org/v1/taxonomies?name=sectors&include_counts=true',
  { headers: { 'Authorization': 'Bearer YOUR_API_KEY' } }
);
const taxonomies = await response.json();
```

```python
# Python
import requests

headers = {'Authorization': 'Bearer YOUR_API_KEY'}
response = requests.get(
    'https://api.changemappers.org/v1/taxonomies',
    params={'name': 'sectors', 'include_counts': 'true'},
    headers=headers
)
taxonomies = response.json()
```

---

### Relationships

Manage relationships between entities.

**Endpoint:** `/v1/relationships`

| Method | Description |
|--------|-------------|
| GET | List relationships with filters |
| POST | Create a new relationship |
| PUT | Update a relationship |
| DELETE | Delete a relationship |

**Examples:**

```bash
# List relationships by source
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/relationships?source_id=org_abc123&source_type=organization"

# Filter by relationship type
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.changemappers.org/v1/relationships?type=PARTNER_OF&status=active"

# Create relationship
curl -X POST -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "org_abc123",
    "source_type": "organization",
    "target_id": "org_xyz789",
    "target_type": "organization",
    "type": "PARTNER_OF",
    "description": "Strategic partnership"
  }' \
  "https://api.changemappers.org/v1/relationships"
```

```javascript
// JavaScript - Create relationship
const response = await fetch('https://api.changemappers.org/v1/relationships', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    source_id: 'org_abc123',
    source_type: 'organization',
    target_id: 'org_xyz789',
    target_type: 'organization',
    type: 'PARTNER_OF',
    description: 'Strategic partnership'
  })
});
const relationship = await response.json();
```

```python
# Python
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

# Create relationship
data = {
    'source_id': 'org_abc123',
    'source_type': 'organization',
    'target_id': 'org_xyz789',
    'target_type': 'organization',
    'type': 'PARTNER_OF',
    'description': 'Strategic partnership'
}
response = requests.post(
    'https://api.changemappers.org/v1/relationships',
    json=data,
    headers=headers
)
relationship = response.json()
```

---

## SDK Examples

### JavaScript/Node.js

```javascript
// Installation: npm install @changemappers/sdk

const { ChangeMappersClient } = require('@changemappers/sdk');

const client = new ChangeMappersClient({
  apiKey: process.env.CHANGEMAPPERS_API_KEY
});

// List organizations
const organizations = await client.organizations.list({
  sector: 'environment',
  limit: 20
});

// Create initiative
const initiative = await client.initiatives.create({
  name: 'Urban Gardening Project',
  type: 'project',
  organization_id: 'org_abc123'
});

// Search
const results = await client.search({
  q: 'climate',
  types: ['organizations', 'initiatives']
});

// Graph traversal
const graph = await client.graph.traverse({
  start_node: 'org_abc123',
  start_type: 'organization',
  depth: 2
});
```

### Python

```python
# Installation: pip install changemappers

from changemappers import Client

client = Client(api_key='YOUR_API_KEY')

# List organizations
organizations = client.organizations.list(
    sector='environment',
    limit=20
)

# Create initiative
initiative = client.initiatives.create(
    name='Urban Gardening Project',
    type='project',
    organization_id='org_abc123'
)

# Search
results = client.search(
    q='climate',
    types=['organizations', 'initiatives']
)

# Graph traversal
graph = client.graph.traverse(
    start_node='org_abc123',
    start_type='organization',
    depth=2
)
```

### cURL Script

```bash
#!/bin/bash

API_KEY="YOUR_API_KEY"
BASE_URL="https://api.changemappers.org/v1"

# Function to make API calls
api_call() {
  curl -s -H "Authorization: Bearer $API_KEY" "$BASE_URL$1"
}

# Get organizations
api_call "/organizations?sector=environment&limit=10"

# Search
api_call "/search?q=climate&types=organizations,initiatives"

# Get graph
api_call "/graph?start_node=org_abc123&start_type=organization&depth=2"
```

---

## Webhooks

Webhooks are available for real-time notifications of data changes.

### Webhook Events

| Event | Description |
|-------|-------------|
| `organization.created` | New organization created |
| `organization.updated` | Organization updated |
| `initiative.created` | New initiative created |
| `initiative.status_changed` | Initiative status changed |
| `relationship.created` | New relationship created |
| `story.published` | Story published |

### Webhook Payload

```json
{
  "event": "organization.created",
  "timestamp": "2024-06-20T12:00:00Z",
  "data": {
    "id": "org_abc123",
    "name": "Green Future Initiative",
    "type": "ngo",
    "sector": "environment"
  }
}
```

---

## Support

- **Documentation:** https://docs.changemappers.org
- **API Status:** https://status.changemappers.org
- **Support Email:** api-support@changemappers.org
- **GitHub:** https://github.com/changemappers/api

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-01 | Initial release |
| 1.1.0 | 2024-03-15 | Added graph traversal endpoint |
| 1.2.0 | 2024-06-01 | Added webhooks support |

---

## License

This API documentation is licensed under CC BY 4.0. API access is subject to the ChangeMappers Terms of Service.
