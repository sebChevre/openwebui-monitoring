# OpenWebUI Monitoring Integration

## Overview

This project integrates a monitoring dashboard into OpenWebUI by:
1. **Building OpenWebUI from source** with a modified `Sidebar.svelte` component
2. **Adding a FastAPI monitoring router** for statistics and dashboard endpoints
3. **Patching main.py** to register the monitoring router

The monitoring link appears directly in the sidebar (compiled into the JavaScript bundle).

## Requirements

- **Node.js 20+** (for building OpenWebUI)
- **Docker** with multi-stage build support
- **Python 3.6+** (for patch.py)

## Quick Start

### 1. Build
```bash
cd /Users/seb/OLLAMA/openwebui-monitoring

# Copies Sidebar.svelte and builds Docker image
./build.sh
```

### 2. Run
```bash
docker-compose -f dev-docker-compose.yml up -d
```

### 3. Access
- OpenWebUI: http://localhost:8080
- Monitoring Dashboard: http://localhost:8080/api/admin/monitoring/dashboard

## File Structure

```
openwebui-monitoring/
├── Sidebar.svelte             # Modified OpenWebUI sidebar component
├── monitoring.py              # FastAPI router for monitoring endpoints
├── patch.py                   # Patches main.py to register router
├── Dockerfile.monitoring      # Multi-stage build (Node.js → Runtime)
├── build.sh                   # Build automation script
├── dev-docker-compose.yml     # Docker Compose configuration
├── README.md                  # This file
├── QUICK_REFERENCE.md         # Common commands
└── TESTING_GUIDE.md           # Testing procedures
```

## How It Works

### Build Pipeline

```
1. build.sh
   └─> Copies Sidebar.svelte from ../open-webui/

2. Dockerfile.monitoring (Stage 1: Node.js builder)
   ├─ Clones OpenWebUI v0.8.10 source
   ├─ Copies your modified Sidebar.svelte
   ├─ npm ci --legacy-peer-deps --force
   ├─ npm run build
   └─> Output: compiled JavaScript bundles with monitoring link

3. Dockerfile.monitoring (Stage 2: Runtime)
   ├─ Copies compiled bundles from Stage 1
   ├─ Adds monitoring.py
   ├─ Runs patch.py (registers router in main.py)
   └─> Final Image: full OpenWebUI with monitoring

4. Docker-compose up
   └─> Container starts with all monitoring features
```

### Key Implementation Details

**Monitoring Link**: 
- Added to `Sidebar.svelte` in the footer section
- Automatically compiled into the JavaScript bundle during Stage 1
- **No runtime injection** required (unlike the old approach)
- Always present and version-independent

**Backend**:
- `monitoring.py` provides:
  - `/api/admin/monitoring/stats` - token statistics
  - `/api/admin/monitoring/dashboard` - HTML dashboard with charts
  - `/api/admin/monitoring/history` - request history
- `patch.py` registers the router in FastAPI's `main.py`

## Development Workflow

### Modify Sidebar
```bash
# Edit the component
vim /Users/seb/OLLAMA/open-webui/src/lib/components/layout/Sidebar.svelte

# Rebuild OpenWebUI
cd /Users/seb/OLLAMA/openwebui-monitoring
./build.sh

# Test
docker-compose -f dev-docker-compose.yml restart open-webui

# Check browser
open http://localhost:8080
```

### Update OpenWebUI
```bash
# Fetch latest from OpenWebUI
cd /Users/seb/OLLAMA/open-webui
git pull origin main

# Rebuild with new sources
cd /Users/seb/OLLAMA/openwebui-monitoring
./build.sh
docker-compose -f dev-docker-compose.yml restart open-webui
```

## Troubleshooting

### Build fails with Node engine error
```
npm error Required: {"node":">=20"}
npm error Actual: {"npm":"x.x.x","node":"vX.X.X"}
```
**Solution**: The Dockerfile now uses `node:20-alpine`. Ensure you're using the latest version of this repo.

### npm dependency conflicts with --legacy-peer-deps
This is expected for OpenWebUI 0.8.10. The `--force` flag helps resolve most conflicts.

### Monitoring link not appearing
1. Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
2. Clear browser cache
3. Check logs: `docker logs open-webui | tail -50`
4. Verify build completed: `docker images | grep open-webui`

## API Endpoints

All under `/api/admin/monitoring/`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/stats` | GET | Overall statistics |
| `/stats/model/{name}` | GET | Model-specific stats |
| `/history` | GET | Request history |
| `/dashboard` | GET | HTML dashboard |
| `/health` | GET | Service health check |
| `/reset` | POST | Reset statistics |

## Performance Notes

- **First build**: 5-10 minutes (includes Node.js dependencies compilation)
- **Subsequent builds**: 2-3 minutes (uses Docker cache)
- **Runtime overhead**: Minimal (monitoring link is just a Svelte component, no runtime injection)

## Maintenance

The setup is designed to be maintainable across OpenWebUI updates:
- Sidebar.svelte modifications are version-controlled
- Build process is fully automated
- No fragile JavaScript injection
- Same approach as any component customization
