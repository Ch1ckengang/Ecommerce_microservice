#!/bin/bash

# E-commerce Microservices Demo Setup Script
# This script sets up the entire system with demo data

set -e

echo "=========================================="
echo "E-commerce Microservices Demo Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Build and start services
echo -e "${BLUE}Step 1: Building and starting all services...${NC}"
docker compose down -v
docker compose build
docker compose up -d

echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Step 2: Wait for services to be healthy
echo -e "${BLUE}Step 2: Waiting for services to be healthy...${NC}"
echo "This may take 1-2 minutes..."

max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker compose ps | grep -q "unhealthy"; then
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    else
        all_healthy=true
        for service in product-service user-service cart-service order-service payment-service shipping-service api-gateway; do
            if ! docker compose ps $service | grep -q "healthy"; then
                all_healthy=false
                break
            fi
        done
        
        if [ "$all_healthy" = true ]; then
            echo ""
            echo -e "${GREEN}✓ All services are healthy${NC}"
            break
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo ""
    echo -e "${YELLOW}Warning: Some services may not be fully healthy yet${NC}"
fi

echo ""

# Step 3: Run migrations
echo -e "${BLUE}Step 3: Running database migrations...${NC}"

docker compose exec -T product-service python manage.py migrate --noinput
docker compose exec -T user-service python manage.py migrate --noinput
docker compose exec -T cart-service python manage.py migrate --noinput
docker compose exec -T order-service python manage.py migrate --noinput
docker compose exec -T payment-service python manage.py migrate --noinput
docker compose exec -T shipping-service python manage.py migrate --noinput

echo -e "${GREEN}✓ Migrations completed${NC}"
echo ""

# Step 4: Seed demo data
echo -e "${BLUE}Step 4: Seeding demo data...${NC}"

docker compose exec -T product-service python manage.py seed_demo_data

echo -e "${GREEN}✓ Demo data seeded${NC}"
echo ""

# Step 5: Create demo users
echo -e "${BLUE}Step 5: Creating demo users...${NC}"

# Create demo user via API
curl -s -X POST http://localhost:8080/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "Demo123!@#",
    "first_name": "Demo",
    "last_name": "User"
  }' > /dev/null

curl -s -X POST http://localhost:8080/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin123!@#",
    "first_name": "Admin",
    "last_name": "User"
  }' > /dev/null

echo -e "${GREEN}✓ Demo users created${NC}"
echo ""

# Step 6: Display summary
echo "=========================================="
echo -e "${GREEN}Demo Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Services are running at:"
echo "  • API Gateway:        http://localhost:8080"
echo "  • Product Service:    http://localhost:8001"
echo "  • User Service:       http://localhost:8002"
echo "  • Cart Service:       http://localhost:8003"
echo "  • Order Service:      http://localhost:8004"
echo "  • Payment Service:    http://localhost:8005"
echo "  • Shipping Service:   http://localhost:8006"
echo ""
echo "API Documentation (Swagger):"
echo "  • Product Service:    http://localhost:8001/api/docs/"
echo "  • User Service:       http://localhost:8002/api/docs/"
echo "  • Cart Service:       http://localhost:8003/api/docs/"
echo "  • Order Service:      http://localhost:8004/api/docs/"
echo "  • Payment Service:    http://localhost:8005/api/docs/"
echo "  • Shipping Service:   http://localhost:8006/api/docs/"
echo ""
echo "Demo Users:"
echo "  • Email: demo@example.com"
echo "    Password: Demo123!@#"
echo ""
echo "  • Email: admin@example.com"
echo "    Password: Admin123!@#"
echo ""
echo "Quick Test Commands:"
echo "  # Get JWT token"
echo "  curl -X POST http://localhost:8080/users/token/ \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"email\":\"demo@example.com\",\"password\":\"Demo123!@#\"}'"
echo ""
echo "  # List products"
echo "  curl http://localhost:8080/products/"
echo ""
echo "To view logs:"
echo "  docker compose logs -f [service-name]"
echo ""
echo "To stop all services:"
echo "  docker compose down"
echo ""
