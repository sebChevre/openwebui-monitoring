#!/bin/bash

# Script pour mettre à jour OpenWebUI avec les modifications de monitoring

set -e

REPO_DIR="/Users/seb/OLLAMA/open-webui"
CUSTOM_DIR="/Users/seb/OLLAMA/openwebui-monitoring"
DOCKER_COMPOSE_FILE="/Users/seb/OLLAMA/global/dev-docker-compose.yml"

echo "🔄 Mise à jour d'OpenWebUI..."

# Arrêter le container
echo "Arrêt des containers..."
cd /Users/seb/OLLAMA/global
docker compose -f "$DOCKER_COMPOSE_FILE" down

# Mettre à jour le repo OpenWebUI
echo "Téléchargement des modifications d'OpenWebUI..."
cd "$REPO_DIR"
git pull origin main || echo "⚠️  Attention: pas de repo git"

# Rebuild l'image Docker avec les modifications
echo "Rebuild de l'image Docker..."
cd /Users/seb/OLLAMA
docker build -t open-webui-monitoring -f "$CUSTOM_DIR/Dockerfile.monitoring" .

# Redémarrer les containers
echo "Démarrage des containers..."
cd /Users/seb/OLLAMA/global
docker compose -f "$DOCKER_COMPOSE_FILE" up -d

# Attendre que le service soit prêt
echo "Attente du démarrage... (10s)"
sleep 10

# Vérifier que ça marche
echo "Vérification de la santé du service..."
if curl -s http://localhost:8080/api/version > /dev/null; then
    echo "✅ Service OpenWebUI est opérationnel!"
    echo "✅ Accès: http://localhost:8080"
else
    echo "❌ Erreur: le service n'a pas démarré"
    exit 1
fi

echo "✅ Mise à jour terminée!"
echo ""
echo "💡 Prochaines étapes si tu vois des erreurs:"
echo "  1. Consulte les logs: docker logs open-webui"
echo "  2. Edit les modifications dans MODIFICATIONS.md si main.py a trop changé"
echo "  3. Contacte l'équipe OpenWebUI si c'est un vraiment un vrai problème"
