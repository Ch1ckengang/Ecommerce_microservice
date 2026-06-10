#!/bin/bash

# AI Service Deployment Script

set -e

echo "========================================="
echo "AI Service Deployment"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: Please run this script from ai-service directory${NC}"
    exit 1
fi

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo ""
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi
print_status "Docker is installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi
print_status "Docker Compose is installed"

# Check required files
echo ""
echo "Checking required files..."

required_files=(
    "Dockerfile"
    "requirements.txt"
    "main.py"
    "data/user_behavior.csv"
    "data/X_train.npy"
    "data/y_train.npy"
    "data/mappings.pkl"
    "data/faiss_index.bin"
    "data/rag_metadata.pkl"
    "models/lstm_model_best.pth"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Missing required file: $file"
        print_warning "Please run all phases (1-7) before deployment"
        exit 1
    fi
    print_status "Found $file"
done

# Build Docker image
echo ""
echo "Building Docker image..."
docker build -t ai-service:latest . || {
    print_error "Docker build failed"
    exit 1
}
print_status "Docker image built successfully"

# Check if Neo4j is running
echo ""
echo "Checking Neo4j..."
if docker ps | grep -q neo4j; then
    print_status "Neo4j is already running"
else
    print_warning "Neo4j is not running. Starting Neo4j..."
    docker-compose -f docker-compose.neo4j.yml up -d neo4j
    echo "Waiting for Neo4j to be ready (30 seconds)..."
    sleep 30
    print_status "Neo4j started"
fi

# Start AI Service
echo ""
echo "Starting AI Service..."
docker-compose -f docker-compose.ai.yml up -d ai-service || {
    print_error "Failed to start AI Service"
    exit 1
}

# Wait for service to be healthy
echo ""
echo "Waiting for AI Service to be healthy..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8008/api/v1/health &> /dev/null; then
        print_status "AI Service is healthy!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    print_error "AI Service failed to become healthy"
    echo "Check logs with: docker logs ai-service"
    exit 1
fi

# Show service info
echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "AI Service is running at:"
echo "  - API: http://localhost:8008"
echo "  - Docs: http://localhost:8008/docs"
echo "  - Health: http://localhost:8008/api/v1/health"
echo ""
echo "Neo4j is running at:"
echo "  - Browser: http://localhost:7474"
echo "  - Bolt: bolt://localhost:7687"
echo "  - Credentials: neo4j/password123"
echo ""
echo "Useful commands:"
echo "  - View logs: docker logs -f ai-service"
echo "  - Stop service: docker-compose -f docker-compose.ai.yml down"
echo "  - Restart: docker-compose -f docker-compose.ai.yml restart ai-service"
echo ""
print_status "Deployment successful!"
