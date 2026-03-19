# Testing Guide - New Build Strategy

## ✅ Pre-Check

All files in place:
```
openwebui-monitoring/
├── ✅ Sidebar.svelte (42 KB - modified with monitoring link)
├── ✅ build.sh (executable)
├── ✅ Dockerfile.monitoring (multi-stage)
├── ✅ monitoring.py (FastAPI router)
├── ✅ patch.py (main.py patcher)
├── ✅ dev-docker-compose.yml
├── ✅ README.md
├── ✅ QUICK_REFERENCE.md
├── ✅ ARCHITECTURE_COMPARISON.md
└── ✅ CHANGELOG_MONITORING_STRATEGY.md
```

---

## 🧪 Test Steps

### Step 1: Build (takes 5-10 minutes first time)
```bash
cd /Users/seb/OLLAMA/openwebui-monitoring
./build.sh

# What happens:
# 1. Copies Sidebar.svelte from ../open-webui/
# 2. Runs: docker-compose -f dev-docker-compose.yml build open-webui
# 3. Docker multi-stage build:
#    a) Stage 1 (builder): Node.js clones OpenWebUI, compiles with your Sidebar.svelte
#    b) Stage 2 (runtime): Uses official image, copies compiled bundle, adds monitoring.py, runs patch.py
```

### Step 2: Start Services
```bash
docker-compose -f dev-docker-compose.yml up -d

# Verify all services started:
docker-compose -f dev-docker-compose.yml ps
```

Expected output:
```
NAME              STATUS
ollama            Up 2 minutes (11434)
ollama-proxy      Up 2 minutes (3000)
ollama-monitoring Up 2 minutes (3333)
open-webui        Up 2 minutes (8080)
```

### Step 3: Test OpenWebUI Access
```bash
# Open browser
open http://localhost:8080

# You should see:
# ✅ OpenWebUI login page (or chat if auto-logged)
# ✅ Left sidebar with menu items
# ✅ NEW: "Monitoring" link with chart icon
```

### Step 4: Test Monitoring Dashboard
```bash
# Click "Monitoring" in sidebar (or direct URL)
open http://localhost:8080/api/admin/monitoring/dashboard

# Should show:
# ✅ Chart with request statistics
# ✅ Token count
# ✅ Model usage
```

### Step 5: Check Docker Logs
```bash
# Build logs (if something failed)
docker-compose -f dev-docker-compose.yml logs open-webui | tail -100

# Should show:
# ✅ No Python errors
# ✅ monitoring router registered
# ✅ Server listening on 0.0.0.0:8080
```

---

## 🔍 If Monitoring Link Doesn't Appear

### Why might this happen?

**Most likely (99%): Browser cache**
```bash
# Try:
1. Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
2. Or clear cookies: DevTools → Application → Clear storage
3. Or: curl -s http://localhost:8080/api/version | jq .version
```

**Check build succeeded:**
```bash
# Did the build complete successfully?
docker image ls | grep open-webui

# Should show image with recent creation time
```

**Verify Sidebar.svelte was included:**
```bash
# Check that file exists in build context
ls -lh /Users/seb/OLLAMA/openwebui-monitoring/Sidebar.svelte

# Verify container has monitoring.py
docker exec open-webui ls -la /app/backend/open_webui/routers/monitoring.py
```

**Check if compilation succeeded:**
```bash
# Look for build artifacts
docker exec open-webui ls -la /app/build/ | head -20

# Should show JavaScript files (index.html, _app-*.js, etc)
```

---

## 📊 What Changed in Deployment

### Before Build (Old way)
```
Container image: ghcr.io/open-webui:0.8.10
├── pre-compiled bundle (no Sidebar.svelte modifications)
└── At runtime: patch.py injects main.py + index.html script tag
    → Performance hit: DOM manipulation + MutationObserver
    → Risk: selectors might break in newer versions
```

### After Build (New way)
```
Container image: locally built
├── Sidebar.svelte compiled WITH monitoring link included
├── Link is part of the bundle (like all other UI)
└── No runtime injection needed
    ✅ Performance: no DOM manipulation
    ✅ Reliability: no selector dependencies
    ✅ Maintainability: change = modify Svelte file
```

---

## 🚀 Normal Development Workflow

```
1. Modify: open-webui/src/lib/components/layout/Sidebar.svelte
   (like you did - added the monitoring link in the footer section)

2. Build: cd openwebui-monitoring && ./build.sh
   (copies your changes and rebuilds)

3. Test: docker-compose up
   (run the new image)

4. Verify: http://localhost:8080
   (check monitoring link appears)

5. Commit: 
   - git add open-webui/src/lib/components/layout/Sidebar.svelte
   - git commit "Add monitoring link to sidebar"
```

---

## 📝 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Build takes very long | Normal (npm install + compilation). First build: 5-10 min. Second: 2-3 min. |
| Docker runs out of disk | `docker system prune -a` |
| Can't connect to service | Check `docker-compose ps` - all should be Up |
| Link doesn't appear | Hard refresh browser + check cache |
| Build fails with git error | Check internet + check v0.8.10 still exists on GitHub |

---

## ✨ Success Indicators

After `docker-compose up`:
- [ ] All services show "Up" in `docker-compose ps`
- [ ] Can access http://localhost:8080
- [ ] "Monitoring" link visible in left sidebar
- [ ] Can click Monitoring → dashboard loads
- [ ] No JavaScript errors in browser console

If all green ✅ - you're done!
