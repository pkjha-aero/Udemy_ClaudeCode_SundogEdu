#!/bin/bash
# Build script for Radio Calico Docker images

set -e

VERSION=${1:-latest}
REGISTRY=${2:-localhost}

echo "Building Radio Calico Docker images..."
echo "Version: $VERSION"
echo "Registry: $REGISTRY"

# Build development image
echo ""
echo "📦 Building development image..."
docker build \
  --target=dev \
  --tag "$REGISTRY/radiocalico:dev" \
  --tag "$REGISTRY/radiocalico:dev-$VERSION" \
  .

# Build production image
echo ""
echo "📦 Building production image..."
docker build \
  --target=prod \
  --tag "$REGISTRY/radiocalico:prod" \
  --tag "$REGISTRY/radiocalico:latest" \
  --tag "$REGISTRY/radiocalico:$VERSION" \
  .

echo ""
echo "✅ Build complete!"
echo ""
echo "Images created:"
docker images | grep radiocalico || true

echo ""
echo "Usage:"
echo "  Development:  docker run -it -p 5000:5000 $REGISTRY/radiocalico:dev"
echo "  Production:   docker run -d -p 5000:5000 $REGISTRY/radiocalico:prod"
echo "  Compose dev:  docker compose up"
echo "  Compose prod: docker compose -f docker-compose.prod.yml up -d"
