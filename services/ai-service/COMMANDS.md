# AI Service - Command Reference

Tổng hợp tất cả các lệnh hữu ích để làm việc với AI Service.

---

## 📦 Deployment Commands

### Standalone Deployment
```bash
# Deploy AI Service + Neo4j
cd services/ai-service
./deploy.sh

# Or using docker-compose
docker-compose -f docker-compose.ai.yml up -d

# Stop
docker-compose -f docker-compose.ai.yml down

# Stop and remove volumes
docker-compose -f docker-compose.ai.yml down -v
```

### Full System Deployment
```bash
# From root directory
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart all services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build
```

### Manual Deployment
```bash
# Build image
docker build -t ai-service:latest services/ai-service/

# Run Neo4j
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:5.15.0

# Run AI Service
docker run -d \
  --name ai-service \
  -p 8008:8000 \
  -e NEO4J_URI=bolt://neo4j:7687 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  ai-service:latest
```

---

## 🔍 Monitoring Commands

### Check Status
```bash
# List all containers
docker ps

# List all containers (including stopped)
docker ps -a

# Check specific service
docker ps | grep ai-service

# Check resource usage
docker stats ai-service

# Check resource usage (all services)
docker stats
```

### View Logs
```bash
# AI Service logs (follow)
docker logs -f ai-service

# AI Service logs (last 100 lines)
docker logs --tail 100 ai-service

# Neo4j logs
docker logs -f neo4j

# All services logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f ai-service
```

### Health Checks
```bash
# Check AI Service health
curl http://localhost:8008/api/v1/health

# Check with formatted output
curl -s http://localhost:8008/api/v1/health | jq

# Check Neo4j health
docker exec neo4j cypher-shell -u neo4j -p password123 "RETURN 1"

# Check all services health
docker-compose ps
```

---

## 🧪 Testing Commands

### Run Phase Tests
```bash
cd services/ai-service

# Phase 1: Data Preparation
python3 run_phase1.py

# Phase 2: LSTM Model
python3 run_phase2.py

# Phase 3: Knowledge Graph
python3 run_phase3.py

# Phase 4: RAG System
python3 run_phase4.py

# Phase 5: Hybrid Recommendation
python3 run_phase5.py

# Phase 6: FastAPI Service
python3 run_phase6.py

# Phase 7: Microservices Integration
python3 run_phase7.py

# Phase 8: Deployment
python3 run_phase8.py
```

### API Testing
```bash
# Health check
curl http://localhost:8008/api/v1/health

# Get statistics
curl http://localhost:8008/api/v1/stats

# User recommendations
curl -X POST http://localhost:8008/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "k": 10}'

# Query recommendations
curl -X POST http://localhost:8008/api/v1/recommend/query \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop gaming", "k": 10}'

# Similar products
curl http://localhost:8008/api/v1/similar/1

# Chatbot
curl -X POST http://localhost:8008/api/v1/chatbot \
  -H "Content-Type: application/json" \
  -d '{"query": "Tôi muốn mua laptop"}'

# Smart recommendations
curl -X POST http://localhost:8008/api/v1/smart-recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "k": 10, "filter_available": true}'

# User context
curl http://localhost:8008/api/v1/user/1/context

# Custom weights
curl -X POST http://localhost:8008/api/v1/recommend/custom-weights \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "k": 10, "weights": {"lstm": 0.5, "graph": 0.3, "rag": 0.2}}'
```

---

## 🔧 Management Commands

### Container Management
```bash
# Start service
docker start ai-service

# Stop service
docker stop ai-service

# Restart service
docker restart ai-service

# Remove container
docker rm ai-service

# Remove container (force)
docker rm -f ai-service
```

### Image Management
```bash
# List images
docker images | grep ai-service

# Remove image
docker rmi ai-service:latest

# Remove unused images
docker image prune

# Remove all unused images
docker image prune -a
```

### Volume Management
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect ai-service_neo4j_data

# Remove volume
docker volume rm ai-service_neo4j_data

# Remove unused volumes
docker volume prune
```

### Network Management
```bash
# List networks
docker network ls

# Inspect network
docker network inspect ai-service_ai-network

# Remove network
docker network rm ai-service_ai-network

# Remove unused networks
docker network prune
```

---

## 🐛 Debugging Commands

### Enter Container
```bash
# Enter AI Service container
docker exec -it ai-service bash

# Enter as root
docker exec -it -u root ai-service bash

# Enter Neo4j container
docker exec -it neo4j bash
```

### Inspect Container
```bash
# Inspect AI Service
docker inspect ai-service

# Get IP address
docker inspect ai-service | grep IPAddress

# Get environment variables
docker inspect ai-service | grep -A 20 Env

# Get health status
docker inspect ai-service | grep Health -A 10
```

### File Operations
```bash
# Copy file from container
docker cp ai-service:/app/logs/app.log ./logs/

# Copy file to container
docker cp ./config.json ai-service:/app/config.json

# List files in container
docker exec ai-service ls -la /app

# View file in container
docker exec ai-service cat /app/main.py
```

### Process Management
```bash
# List processes in container
docker exec ai-service ps aux

# Check Python processes
docker exec ai-service ps aux | grep python

# Kill process in container
docker exec ai-service kill -9 <PID>
```

---

## 🗄️ Database Commands

### Neo4j Commands
```bash
# Enter Cypher shell
docker exec -it neo4j cypher-shell -u neo4j -p password123

# Run query from command line
docker exec neo4j cypher-shell -u neo4j -p password123 "MATCH (n) RETURN count(n)"

# Export database
docker exec neo4j neo4j-admin dump --to=/tmp/backup.dump

# Import database
docker exec neo4j neo4j-admin load --from=/tmp/backup.dump

# Clear database
docker exec neo4j cypher-shell -u neo4j -p password123 "MATCH (n) DETACH DELETE n"
```

### Cypher Queries
```cypher
# Count all nodes
MATCH (n) RETURN count(n)

# Count all relationships
MATCH ()-[r]->() RETURN count(r)

# Get all users
MATCH (u:User) RETURN u LIMIT 10

# Get all products
MATCH (p:Product) RETURN p LIMIT 10

# Get user purchases
MATCH (u:User {id: 1})-[:PURCHASED]->(p:Product)
RETURN u.name, p.name

# Get similar products
MATCH (p:Product {id: 1})-[:SIMILAR_TO]->(similar:Product)
RETURN p.name, similar.name

# Get product recommendations
MATCH (u:User {id: 1})-[:PURCHASED]->(:Product)-[:SIMILAR_TO]->(rec:Product)
WHERE NOT (u)-[:PURCHASED]->(rec)
RETURN rec.name, count(*) as score
ORDER BY score DESC
LIMIT 10
```

---

## 📊 Performance Commands

### Resource Monitoring
```bash
# Monitor CPU and memory
docker stats ai-service

# Monitor all services
docker stats

# Get container resource limits
docker inspect ai-service | grep -A 10 Resources

# Check disk usage
docker system df

# Check detailed disk usage
docker system df -v
```

### Performance Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8008/api/v1/health

# Test recommendation endpoint
ab -n 100 -c 5 -p request.json -T application/json \
  http://localhost:8008/api/v1/recommend

# Install wrk
sudo apt-get install wrk

# Load test
wrk -t4 -c100 -d30s http://localhost:8008/api/v1/health
```

---

## 🔐 Security Commands

### Environment Variables
```bash
# View environment variables
docker exec ai-service env

# Set environment variable
docker exec -e NEW_VAR=value ai-service env

# Load from .env file
docker-compose --env-file .env up -d
```

### Secrets Management
```bash
# Create secret
echo "password123" | docker secret create neo4j_password -

# List secrets
docker secret ls

# Inspect secret
docker secret inspect neo4j_password

# Remove secret
docker secret rm neo4j_password
```

---

## 🔄 Backup & Restore Commands

### Backup Data
```bash
# Backup data directory
docker cp ai-service:/app/data ./backup/data

# Backup models directory
docker cp ai-service:/app/models ./backup/models

# Backup Neo4j database
docker exec neo4j neo4j-admin dump --to=/tmp/backup.dump
docker cp neo4j:/tmp/backup.dump ./backup/neo4j.dump

# Backup all volumes
docker run --rm \
  -v ai-service_neo4j_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/neo4j_data.tar.gz /data
```

### Restore Data
```bash
# Restore data directory
docker cp ./backup/data ai-service:/app/data

# Restore models directory
docker cp ./backup/models ai-service:/app/models

# Restore Neo4j database
docker cp ./backup/neo4j.dump neo4j:/tmp/backup.dump
docker exec neo4j neo4j-admin load --from=/tmp/backup.dump --force

# Restore volume
docker run --rm \
  -v ai-service_neo4j_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/neo4j_data.tar.gz -C /
```

---

## 🚀 Scaling Commands

### Horizontal Scaling
```bash
# Scale AI Service to 3 instances
docker-compose up -d --scale ai-service=3

# Check scaled instances
docker ps | grep ai-service

# Scale down to 1 instance
docker-compose up -d --scale ai-service=1
```

### Resource Limits
```bash
# Run with memory limit
docker run -d \
  --name ai-service \
  --memory="4g" \
  --cpus="2" \
  ai-service:latest

# Update resource limits
docker update --memory="8g" --cpus="4" ai-service
```

---

## 🧹 Cleanup Commands

### Remove Containers
```bash
# Stop and remove AI Service
docker stop ai-service && docker rm ai-service

# Stop and remove all containers
docker stop $(docker ps -aq) && docker rm $(docker ps -aq)

# Remove exited containers
docker container prune
```

### Remove Images
```bash
# Remove AI Service image
docker rmi ai-service:latest

# Remove dangling images
docker image prune

# Remove all unused images
docker image prune -a
```

### Remove Volumes
```bash
# Remove specific volume
docker volume rm ai-service_neo4j_data

# Remove all unused volumes
docker volume prune
```

### Complete Cleanup
```bash
# Remove everything (containers, images, volumes, networks)
docker system prune -a --volumes

# Remove only stopped containers and unused images
docker system prune
```

---

## 📝 Development Commands

### Local Development
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with specific workers
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Sort imports
isort .
```

---

## 🔗 Useful Aliases

Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
# AI Service aliases
alias ai-logs='docker logs -f ai-service'
alias ai-restart='docker-compose restart ai-service'
alias ai-health='curl -s http://localhost:8008/api/v1/health | jq'
alias ai-stats='curl -s http://localhost:8008/api/v1/stats | jq'
alias ai-shell='docker exec -it ai-service bash'

# Neo4j aliases
alias neo4j-logs='docker logs -f neo4j'
alias neo4j-shell='docker exec -it neo4j cypher-shell -u neo4j -p password123'
alias neo4j-restart='docker-compose restart neo4j'

# Docker Compose aliases
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcp='docker-compose ps'
```

---

## 📚 Reference

### Documentation
- [Quick Start Guide](QUICK_START.md)
- [AI Service Status](AI_SERVICE_STATUS.md)
- [Development Progress](AI_SERVICE_PROGRESS.md)
- [Phase 1-8 READMEs](README_PHASE*.md)

### URLs
- **AI Service**: http://localhost:8008
- **API Docs**: http://localhost:8008/docs
- **ReDoc**: http://localhost:8008/redoc
- **Neo4j Browser**: http://localhost:7474
- **Neo4j Bolt**: bolt://localhost:7687

### Credentials
- **Neo4j**: neo4j / password123

---

**💡 Tip**: Bookmark this file for quick reference!
