#!/bin/bash
# Build script for OpenWebUI with custom Sidebar

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENWEBUI_DIR="$SCRIPT_DIR/../open-webui"
OPENWEBUI_MONITORING_DIR="$SCRIPT_DIR"

echo "📋 Copie du Sidebar.svelte modifié..."
cp "$OPENWEBUI_DIR/src/lib/components/layout/Sidebar.svelte" "$OPENWEBUI_MONITORING_DIR/Sidebar.svelte"

echo "🔨 Build du Docker image avec Sidebar.svelte modifié..."
docker-compose -f dev-docker-compose.yml build --no-cache open-webui

echo "✅ Build terminé ! Lancer avec: docker-compose -f dev-docker-compose.yml up"
