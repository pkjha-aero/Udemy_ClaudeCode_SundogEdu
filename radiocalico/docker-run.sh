#!/bin/bash
# Run script for Radio Calico Docker containers

set -e

MODE=${1:-dev}

case $MODE in
  dev)
    echo "🚀 Starting Radio Calico in DEVELOPMENT mode..."
    echo "   - Flask debug enabled"
    echo "   - Hot reload on file changes"
    echo "   - Accessible at http://localhost:5000"
    echo ""
    docker compose up
    ;;

  prod)
    echo "🚀 Starting Radio Calico in PRODUCTION mode..."
    echo "   - Gunicorn with 4 workers"
    echo "   - Nginx reverse proxy"
    echo "   - Health checks enabled"
    echo "   - Accessible at http://localhost (or https://localhost)"
    echo ""
    docker compose -f docker-compose.prod.yml up -d
    echo ""
    echo "✅ Services running in background"
    echo "   View logs: docker compose -f docker-compose.prod.yml logs -f"
    echo "   Stop:      docker compose -f docker-compose.prod.yml down"
    ;;

  stop)
    echo "⏹️  Stopping Radio Calico containers..."
    if [ -f docker-compose.prod.yml ]; then
      docker compose -f docker-compose.prod.yml down
    else
      docker compose down
    fi
    echo "✅ Stopped"
    ;;

  logs)
    COMPOSE_FILE=${2:-docker-compose.yml}
    echo "📋 Showing logs..."
    docker compose -f "$COMPOSE_FILE" logs -f
    ;;

  *)
    echo "Usage: $0 {dev|prod|stop|logs [compose_file]}"
    echo ""
    echo "Examples:"
    echo "  $0 dev          # Start in development mode"
    echo "  $0 prod         # Start in production mode"
    echo "  $0 stop         # Stop containers"
    echo "  $0 logs         # Show dev logs"
    echo "  $0 logs docker-compose.prod.yml  # Show prod logs"
    exit 1
    ;;
esac
