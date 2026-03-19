# Modifications à OpenWebUI pour le Monitoring

## Fichier 1: `backend/open_webui/main.py`

### Import (ligne ~74)
Ajouter `monitoring` à la liste des imports des routers :

```python
from open_webui.routers import (
    analytics,
    audio,
    images,
    monitoring,  # ← AJOUTER CETTE LIGNE
    ollama,
    ...
)
```

### Enregistrement du router (vers la fin du fichier, ~ligne 1568)
Ajouter cette ligne parmi les autres `app.include_router` :

```python
app.include_router(monitoring.router, prefix="/api/admin/monitoring", tags=["monitoring"])
```

---

## Fichier 2: `build/index.html`

Ajouter cette ligne avant la fermeture de `</html>` :

```html
<script async src="/api/admin/monitoring/inject-sidebar.js"></script>
```

---

## Fichier 3: `backend/open_webui/routers/monitoring.py`

Ce fichier est **entièrement nouveau**. Copier le fichier `monitoring.py` de ce dossier vers :

```
backend/open_webui/routers/monitoring.py
```

---

## Procédure de mise à jour

1. **Récupère la dernière version d'OpenWebUI :**
   ```bash
   cd /Users/seb/OLLAMA/open-webui
   git pull origin main
   ```

2. **Vérifie si `main.py` a changé** (cherche les lignes d'import et d'enregistrement)

3. **S'il a changé :**
   - Ouvre `main.py` et applique les modifications selon les lignes ci-dessus
   - Adapte les numéros de lignes si nécessaire

4. **Copie les fichiers :**
   ```bash
   cp monitoring.py /path/to/project/backend/open_webui/routers/
   ```

5. **Rebuild l'image Docker :**
   ```bash
   docker build -t open-webui-monitoring -f openwebui-monitoring/Dockerfile.monitoring .
   docker compose restart open-webui
   ```

---

## Conseils

- Les modifications dans `main.py` sont **minimales** (2 petites additions)
- Le fichier `monitoring.py` est **indépendant**, facile à copier
- Si les lignes exact ont changé mais la structure est la même, adapte juste les numéros

