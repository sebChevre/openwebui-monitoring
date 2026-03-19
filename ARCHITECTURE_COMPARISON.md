# Architecture Comparison

## Ancien Setup (JavaScript Injection)

```
┌─────────────────────────────────────┐
│  ghcr.io/open-webui:0.8.10          │
│  (prebuilt, compiled)               │
└────────────────┬──────────────────────┘
                 │
                 ├─> patch.py injects:
                 │   - Add router to main.py
                 │   - Add script tag to index.html
                 │
                 └─> index.html
                     ├─ <script> inject-sidebar.js
                     └─ Runtime: DOM mutation to add link
                        (Fragile! Depends on selectors)
```

**Problèmes:**
- ❌ Link appears at runtime (after page load)
- ❌ Depends on specific DOM structure (brittle)
- ❌ MutationObserver overhead
- ❌ May break if OpenWebUI DOM changes

---

## Nouveau Setup (Component Source)

```
┌─────────────────────────────────────┐
│  open-webui repo (source)           │
│  src/lib/components/layout/         │
│    └─ Sidebar.svelte ← MODIFIED     │
└────────────────┬──────────────────────┘
                 │
   build.sh      │
                 v
┌─────────────────────────────────────┐
│  Dockerfile.monitoring              │
│  Stage 1: Node.js builder           │
│    ├─ npm ci                        │
│    ├─ npm run build                 │
│    └─ Output: compiled JS bundle    │
└────────────────┬──────────────────────┘
                 │
                 ├─> Sidebar component compiled
                 │   └─ Monitoring link baked in
                 │
                 └─> /app/build/ (all JS/CSS)
                     └─ No runtime injection needed!
```

**Avantages:**
- ✅ Link is part of component source code
- ✅ Present in final bundle (like all other UI)
- ✅ No runtime DOM manipulation
- ✅ Version-independent approach
- ✅ Same method as modifying any Svelte component

---

## File Flow

### Build Process

```
open-webui/
└── src/lib/components/layout/
    └── Sidebar.svelte ← Local modifications
            │
            │ (user edits)
            │
            v
openwebui-monitoring/
├── build.sh
│   ├── cp ../open-webui/Sidebar.svelte .
│   └── docker-compose build open-webui
│
├── Dockerfile.monitoring
│   ├── Stage builder (Node):
│   │   ├── git clone v0.8.10
│   │   ├── COPY Sidebar.svelte → /build/src/...
│   │   ├── npm run build
│   │   └── Output: /build/build/
│   │
│   └── Stage runtime (OpenWebUI image):
│       ├── COPY --from=builder /build/build /app/build
│       ├── COPY monitoring.py
│       ├── RUN patch.py
│       └── Final: open-webui with monitoring
│
└── Final volume mount in docker-compose.yml
    └── Accessible at http://localhost:8080/api/admin/monitoring/dashboard
```

### Component Location in Runtime

```
Container open-webui:
├── /app/build/                    (compiled output)
│   ├── index.html                 (includes bundled JS)
│   ├── _app-[hash].js            (app bundle with compiled Sidebar)
│   └── _layout-[hash].js          (layout with monitoring link)
│
├── /app/backend/
│   └── open_webui/routers/
│       └── monitoring.py          (FastAPI router)
│
└── /app/backend/open_webui/
    └── main.py                    (patched with monitoring.router)
```

The monitoring link is inside the JavaScript bundles - it's part of the Svelte component compilation output!

---

## Development Workflow

### Modify Sidebar
```
1. Edit: /Users/seb/OLLAMA/open-webui/src/lib/components/layout/Sidebar.svelte
2. Run: cd openwebui-monitoring && ./build.sh
3. Test: docker-compose up, check http://localhost:8080
4. Commit: git add Sidebar.svelte, git commit
```

### Maintain
```
When OpenWebUI updates:
  - git pull in /Users/seb/OLLAMA/open-webui
  - ./build.sh (rebuilds everything)
  - Test & deploy
```

### Version Safety
```
Changes are:
- In source control (Sidebar.svelte)
- Not dependent on HTML structure
- Compiled into final bundle
- Same as any other component change
```
