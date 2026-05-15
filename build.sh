#!/bin/bash
set -e
echo "→ Build du frontend React..."
cd frontend
npm install
npm run build
cd ..
echo "→ Copie du build dans backend/static..."
mkdir -p backend/static
cp -r frontend/dist/* backend/static/
echo "✓ Build terminé"
