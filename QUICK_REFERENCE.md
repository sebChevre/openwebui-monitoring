# Quick Reference: Monitoring Integration

## 📁 Directory Structure

```
openwebui-monitoring/
├── README.md                 # Overview et utilisation
├── MODIFICATIONS.md          # Changes détaillées ligne par ligne
├── QUICK_REFERENCE.md        # Ce fichier
├── patch.py                  # Script de patch automatisé
├── monitoring.py             # Router FastAPI pour le monitoring
├── Dockerfile.monitoring     # Docker build avec modifications
├── dev-docker-compose.yml    # Configuration docker-compose
├── update.sh                 # Script de mise à jour automatisée
└── docs/
    └── architecture.drawio   # Schémas d'architecture
```

## 🚀 Commandes Rapides

### Mise à jour OpenWebUI (après git pull)
```bash
cd /Users/seb/OLLAMA/openwebui-monitoring
./update.sh
```

### Rebuild Docker avec modifications
```bash
cd /Users/seb/OLLAMA/openwebui-monitoring
docker build -t open-webui-monitoring -f Dockerfile.monitoring .
docker compose -f dev-docker-compose.yml down
docker compose -f dev-docker-compose.yml up -d
```

### Vérifier les logs
```bash
docker logs open-webui -f          # Logs en temps réel
docker logs open-webui | tail -50  # Dernières 50 lignes
```

### Réinitialiser (si quelque chose casse)
```bash
# Option 1: Reconstruire complètement
./update.sh

# Option 2: Redémarrer seulement
docker compose -f dev-docker-compose.yml restart open-webui
```

## 📊 Endpoints Disponibles

Tous les endpoints sont sous `/api/admin/monitoring/`:

| Endpoint | Méthode | Retour |
|----------|---------|--------|
| `/health` | GET | `{"status": "healthy"}` |
| `/stats` | GET | Total requests + par model |
| `/stats/model/{name}` | GET | Stats pour un model spécifique |
| `/history` | GET | Historique des requêtes |
| `/dashboard` | GET | HTML dashboard avec Chart.js |
| `/inject-sidebar.js` | GET | JavaScript d'injection |
| `/reset` | POST | Réinitialiser les stats |

## 🔍 Dashboard

Accès direct: http://localhost:8080/api/admin/monitoring/dashboard

Où tu verras:
- Graphique du nombre de requêtes par model
- Nombre total de requêtes
- Modèles utilisés
- Tokens comptabilisés

## 🔧 Troubleshooting

### "Je ne vois pas le lien Monitoring dans le menu"
1. Ouvre la console (F12)
2. Regarde pour des erreurs JavaScript
3. Vérifie les logs: `docker logs open-webui | grep monitoring`
4. Rebuild au besoin: `docker build -t open-webui-monitoring -f openwebui-monitoring/Dockerfile.monitoring .`

### "Les modifications ont disparu après mise à jour"
1. Les fichiers sont dans openwebui-monitoring/MODIFICATIONS.md
2. Rebuild automatiquement avec le Dockerfile
3. Ou utilise: `./update.sh`

### "Dockerfile ne build pas"
1. Vérifie la version d'OpenWebUI: `grep FROM openwebui-monitoring/Dockerfile.monitoring`
2. Compare avec la version officielle actuellement running
3. Ajuste les chemins de fichiers si OpenWebUI structure a changé

## 📝 Maintenance Automatisée

Tout est maintenant **automatisé** par le `Dockerfile.monitoring` et `patch.py`:

1. **monitoring.py** - Cloné dans le bon dossier
2. **main.py** - Modifications appliquées automatiquement par `patch.py`
3. **index.html** - Script injecté automatiquement par `patch.py`

Lors d'une mise à jour majeure d'OpenWebUI, il suffira de rebuildler le Dockerfile. Si des erreurs surviennent, consulte MODIFICATIONS.md pour adapter manuellement.

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
