# CrossRef API Configuration

The `CrossRefLocalEngine` in scitex package supports both internal and external CrossRef APIs, automatically detecting the format and adjusting endpoints accordingly.

## API Types

### Internal API (Recommended for NAS/Docker)
- **Fast**: Direct database access, no rate limiting
- **Private**: Only accessible within Docker network or VPN
- **Large**: Requires 1.2TB database storage

### External API (Recommended for Development/Remote)
- **Accessible**: Works from anywhere over internet
- **Rate-limited**: 100 requests/hour per IP
- **Cached**: 1-hour Redis cache for faster responses

## Environment Variable Configuration

### Option 1: Internal API (NAS Docker Network)

```bash
export SCITEX_SCHOLAR_CROSSREF_API_URL=http://crossref:3333
```

**Use when:**
- Running inside NAS Docker network
- Need maximum speed (no rate limits)
- Have access to local CrossRef database

**Endpoints generated:**
- Search: `http://crossref:3333/api/search/`
- Health: `http://crossref:3333/api/health/`
- Stats: `http://crossref:3333/api/stats/`

### Option 2: Internal API (NAS IP via VPN)

```bash
export SCITEX_SCHOLAR_CROSSREF_API_URL=http://169.254.11.50:3333
```

**Use when:**
- Connected to NAS via VPN/local network
- Running on laptop but want internal speed
- Testing from development machine

**Endpoints generated:**
- Search: `http://169.254.11.50:3333/api/search/`
- Health: `http://169.254.11.50:3333/api/health/`
- Stats: `http://169.254.11.50:3333/api/stats/`

### Option 3: External API (Public Internet)

```bash
export SCITEX_SCHOLAR_CROSSREF_API_URL=https://scitex.ai/scholar/api/crossref
```

**Use when:**
- Working remotely without VPN
- Testing from anywhere
- Don't need high request rates

**Endpoints generated:**
- Search: `https://scitex.ai/scholar/api/crossref/search/`
- Health: `https://scitex.ai/scholar/api/crossref/health/`
- Stats: `https://scitex.ai/scholar/api/crossref/stats/`

**Rate limits:**
- 100 requests/hour per IP address
- Health and stats endpoints not rate-limited

## Configuration Files

### For Development (.env.dev)

```bash
# Internal API when on VPN
SCITEX_SCHOLAR_CROSSREF_API_URL_DEV=http://169.254.11.50:3333

# External API when remote
# SCITEX_SCHOLAR_CROSSREF_API_URL_DEV=https://scitex.ai/scholar/api/crossref

# Active configuration
SCITEX_SCHOLAR_CROSSREF_API_URL=${SCITEX_SCHOLAR_CROSSREF_API_URL_DEV}
```

### For Production (.env.nas)

```bash
# Internal API (Docker network)
SCITEX_SCHOLAR_CROSSREF_API_URL_NAS=http://crossref:3333

# External API fallback
SCITEX_SCHOLAR_CROSSREF_API_URL_DEV=https://scitex.ai/scholar/api/crossref

# Active configuration
SCITEX_SCHOLAR_CROSSREF_API_URL=${SCITEX_SCHOLAR_CROSSREF_API_URL_NAS}
```

## Testing Configuration

### Quick Test (Python)

```python
from scitex.scholar.metadata_engines.individual import CrossRefLocalEngine

# Test with your configuration
engine = CrossRefLocalEngine("your@email.com")
print(f"API URL: {engine.api_url}")
print(f"Is External: {engine._is_external_api}")
print(f"Search endpoint: {engine._build_endpoint_url('search')}")

# Test search
result = engine.search(doi="10.1038/nature12373")
if result:
    print(f"Title: {result.get('basic', {}).get('title')}")
    print(f"Success! API is working.")
```

### Quick Test (Shell)

```bash
# Internal API test
curl "http://crossref:3333/api/health/"

# External API test
curl "https://scitex.ai/scholar/api/crossref/health/"
```

## Automatic Detection

The engine automatically detects API type:

```python
# Detection logic
is_external = "/api/crossref" in api_url or "scitex.ai" in api_url

if is_external:
    # External: https://scitex.ai/scholar/api/crossref/search/
    url = f"{api_url}/{endpoint}/"
else:
    # Internal: http://crossref:3333/api/search/
    url = f"{api_url}/api/{endpoint}/"
```

## Database Information

- **Total papers**: 167,008,748
- **Database size**: 1.2TB (1,197,367 MB)
- **Format**: local database with indexed fields
- **Source**: CrossRef official database

## Best Practices

1. **Use internal API when possible** for speed and no rate limits
2. **Use external API for remote work** when VPN not available
3. **Set environment variables** rather than hardcoding URLs
4. **Test configuration** before running large batch jobs
5. **Respect rate limits** on external API (100/hour)

## Troubleshooting

### Connection Refused (Internal API)

```
CrossRef Local server not available at http://crossref:3333 (connection refused)
```

**Solutions:**
- Check if CrossRef service is running: `docker ps | grep crossref`
- Verify you're inside Docker network or VPN
- Try external API instead: `export SCITEX_SCHOLAR_CROSSREF_API_URL=https://scitex.ai/scholar/api/crossref`

### Rate Limited (External API)

```
HTTP 429 Too Many Requests
```

**Solutions:**
- Wait 1 hour for rate limit to reset
- Use internal API if available
- Reduce request frequency
- Implement caching in your application

## See Also

- [CrossRef API Proxy Implementation](../apps/scholar_app/api/crossref_proxy.py)
- [CrossRef Local Server](../deployment/docker/crossref_local/server.py)
- [Environment Variables Guide](../SECRETS/README.md)
