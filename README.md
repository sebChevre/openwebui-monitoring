# OpenWebUI Monitoring Integration

## Structure

- `monitoring.py` : Router FastAPI pour le monitoring
- `patch.py` : Script Python qui applique les modifications automatiquement
- `Dockerfile.monitoring` : Dockerfile custom qui applique les modifications
- `dev-docker-compose.yml` : Configuration docker-compose pour le stack monitoring
- `docs/` : Schémas d'architecture
- `MODIFICATIONS.md` : Documentation détaillée des modifications

## Utilisation

### Première fois
```bash
cd /Users/seb/OLLAMA/openwebui-monitoring
docker build -t open-webui-monitoring -f Dockerfile.monitoring .
docker compose -f dev-docker-compose.yml up -d
```

### Mettre à jour OpenWebUI
```bash
cd /Users/seb/OLLAMA/open-webui
git pull origin main  # Mettre à jour le repo officiel

# Puis rebuild
cd /Users/seb/OLLAMA/openwebui-monitoring
docker build -t open-webui-monitoring -f Dockerfile.monitoring .
docker compose -f dev-docker-compose.yml restart open-webui
```

## Fonctionnement automatique

Le `Dockerfile.monitoring` applique automatiquement:
1. Copie `monitoring.py` dans le bon dossier
2. Exécute `patch.py` pour injecter les modifications dans `main.py` et `index.html`
3. Aucune modification manuelle requise lors du build
