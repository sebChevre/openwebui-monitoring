# Quick Reference - OpenWebUI Monitoring

## ⚙️ Requirements

- Docker Desktop (or Docker Engine)
- Docker Compose v2+
- **Node.js 20+** (only for local builds outside Docker)

## 🚀 Quick Commands

### Build & Start
```bash
cd /Users/seb/OLLAMA/openwebui-monitoring

# One-liner: build + start
./build.sh && docker-compose -f dev-docker-compose.yml up -d

# Or separate:
./build.sh                                          # Build image
docker-compose -f dev-docker-compose.yml up -d     # Start all services
```

### Access Services
```bash
# OpenWebUI
open http://localhost:8080

# Monitoring Dashboard
open http://localhost:8080/api/admin/monitoring/dashboard

# Check all services running
docker-compose -f dev-docker-compose.yml ps
```

### View Logs
```bash
# All services
docker-compose -f dev-docker-compose.yml logs -f

# OpenWebUI only
docker-compose -f dev-docker-compose.yml logs -f open-webui

# Last 50 lines
docker logs open-webui | tail -50
```

### Restart Services
```bash
# Restart OpenWebUI only
docker-compose -f dev-docker-compose.yml restart open-webui

# Restart all services
docker-compose -f dev-docker-compose.yml restart
```

### Stop Everything
```bash
docker-compose -f dev-docker-compose.yml down -v  # Add -v to clean volumes
```

## 🔄 Development Workflow

### After Modifying Sidebar.svelte
```bash
# 1. Update local copy (if editing in open-webui repo)
cp ../open-webui/src/lib/components/layout/Sidebar.svelte ./Sidebar.svelte

# 2. Rebuild with build.sh (includes copy + docker build)
./build.sh

# 3. Restart container
docker-compose -f dev-docker-compose.yml restart open-webui

# 4. Test in browser (hard refresh!)
open http://localhost:8080
```

### After OpenWebUI Source Updates
```bash
cd /Users/seb/OLLAMA/open-webui
git pull origin main

cd /Users/seb/OLLAMA/openwebui-monitoring
./build.sh  # Auto-copies Sidebar.svelte + rebuilds everything
docker-compose -f dev-docker-compose.yml restart open-webui
```

## 📊 Monitoring API

**Base URL:** `http://localhost:8080/api/admin/monitoring/`

```bash
# Get stats
curl http://localhost:8080/api/admin/monitoring/stats | jq

# Get model stats
curl http://localhost:8080/api/admin/monitoring/stats/model/llama2 | jq

# Check health
curl http://localhost:8080/api/admin/monitoring/health | jq

# Reset stats (POST)
curl -X POST http://localhost:8080/api/admin/monitoring/reset
```

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Service health check |
| `/stats` | GET | Overall statistics |
| `/stats/model/{name}` | GET | Model-specific stats |
| `/history` | GET | Request history |
| `/dashboard` | GET | HTML dashboard |
| `/reset` | POST | Reset all statistics |

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails with `EBADENGINE` | Docker uses `node:20-alpine`. Only issue if building outside Docker. |
| npm dependency conflicts | Expected - build uses `--legacy-peer-deps --force` flags. Safe. |
| Monitoring link doesn't appear | Hard refresh browser (Cmd+Shift+R on macOS) |
| Services won't start | Check `docker-compose -f dev-docker-compose.yml ps` - all Up? |
| Port 8080 already in use | Change port in `dev-docker-compose.yml` or stop conflicting app |
| Container exited | Check logs: `docker-compose logs open-webui` |

## 📦 Docker Cache & Performance

```bash
# Build from cache (fastest, ~1-2 min)
./build.sh

# Rebuild without cache (longest, ~5-10 min)
docker-compose -f dev-docker-compose.yml build open-webui --no-cache

# Clear all Docker artifacts
docker system prune -a
```

## 📂 Build Context

The Dockerfile.monitoring multi-stage build:

1. **Stage 1 (Builder)**: `node:20-alpine`
   - Clones OpenWebUI v0.8.10
   - Copies custom Sidebar.svelte
   - Runs `npm ci --legacy-peer-deps --force`
   - Builds with `npm run build`

2. **Stage 2 (Runtime)**: `ghcr.io/open-webui:0.8.10`
   - Copies compiled bundle from builder
   - Adds monitoring.py + patch.py
   - Patches main.py to register monitoring router

## 📁 Key Files

```
openwebui-monitoring/
├── Dockerfile.monitoring  # Multi-stage build (Node 20 + compiler + runtime)
├── build.sh              # Copies Sidebar.svelte + runs docker build
├── monitoring.py         # FastAPI router (/api/admin/monitoring/*)
├── patch.py              # Registers monitoring router in main.py
├── Sidebar.svelte        # Custom sidebar (auto-copied by build.sh)
├── dev-docker-compose.yml
└── README.md             # Full documentation
```

## 💡 Quick Tips

- **First build**: Takes 5-10 minutes (normal - compiling Node.js + web app)
- **Subsequent builds**: 1-2 minutes thanks to Docker cache
- **Browser hard refresh**: Cmd+Shift+R (clears local cache)
- **Docker logs**: Always first troubleshooting step
- **Volume cleanup**: Use `docker-compose down -v` to reset data

## ✅ Build Process

**What build.sh does:**
1. Copies Sidebar.svelte from `../open-webui/`
2. Runs Docker multi-stage build:
   - Stage 1: Node.js clone OpenWebUI, copy modified Sidebar.svelte, build
   - Stage 2: Use official image, copy compiled bundle, add monitoring
3. Final image has: built Open WebUI + monitoring integration + patched main.py

## 🎯 Cas d'Utilisation Courants

### Désactiver temporairement le monitoring
```bash
# Commente la ligne dans index.html via Dockerfile
# Puis redémarre
docker compose -f /Users/seb/OLLAMA/openwebui-monitoring/dev-docker-compose.yml restart open-webui
```

### Exporter les stats
```bash
curl http://localhost:8080/api/admin/monitoring/stats > monitoring_stats.json
```

### Réinitialiser les stats
```bash
curl -X POST http://localhost:8080/api/admin/monitoring/reset
```

### Vérifier version OpenWebUI
```bash
curl http://localhost:8080/api/version
```

## ✅ Checklist Post-Mise à Jour

After running `./update.sh`:

- [ ] Service redémarré sans erreurs
- [ ] Lien "Monitoring" visible dans le menu d'OpenWebUI
- [ ] Dashboard accessible et charge les données
- [ ] Pas d'erreurs dans la console (F12)

---

**Voir aussi**: README.md (overview) et MODIFICATIONS.md (détails techniques)  
**Maintenance par**: OpenWebUI Monitoring Integration
