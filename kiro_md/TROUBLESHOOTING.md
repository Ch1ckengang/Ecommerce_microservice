# 🔧 Troubleshooting Guide

Hướng dẫn xử lý các lỗi thường gặp khi deploy Docker.

---

## 🐛 Issue 1: Docker DNS Error

### Triệu chứng
```
failed to resolve source metadata for docker.io/library/python:3.11-slim
lookup registry-1.docker.io on 127.0.0.53:53: server misbehaving
```

### Nguyên nhân
Docker không thể resolve DNS của Docker Hub registry.

### Giải pháp

#### Quick Fix (Recommended)
```bash
cd /home/trung/Documents/TieuluanS.A&D
./fix_docker_dns.sh
```

#### Manual Fix
```bash
# 1. Create Docker daemon config
sudo mkdir -p /etc/docker

# 2. Add DNS configuration
sudo tee /etc/docker/daemon.json <<EOF
{
  "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]
}
EOF

# 3. Restart Docker
sudo systemctl restart docker

# 4. Test
docker run --rm alpine ping -c 3 google.com

# 5. Retry build
docker-compose build
docker-compose up -d
```

#### Alternative DNS servers
If Google DNS doesn't work, try:
```json
{
  "dns": ["1.1.1.1", "1.0.0.1"]  // Cloudflare
}
```

Or use your system DNS:
```bash
# Check your DNS
cat /etc/resolv.conf | grep nameserver

# Use that DNS in daemon.json
```

---

## 🐛 Issue 2: Product Service 500 Error

### Triệu chứng
```
500 Server Error: Internal Server Error
URL: http://product-service:8000/products/?page=1&category=...
```

### Nguyên nhân có thể
1. Database chưa migrate
2. Service chưa ready
3. Database connection error
4. Category name encoding issue

### Giải pháp

#### Step 1: Check service logs
```bash
docker logs product-service
```

#### Step 2: Check database connection
```bash
# Check if product-db is healthy
docker ps | grep product-db

# Check product-db logs
docker logs product-db
```

#### Step 3: Run migrations
```bash
# Enter product-service container
docker exec -it product-service bash

# Run migrations
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser

# Exit
exit
```

#### Step 4: Check URL encoding
The error shows URL-encoded category: `%C4%90i%E1%BB%87n+tho%E1%BA%A1i`

This is "Điện thoại & Tablet" encoded.

Check if category exists:
```bash
docker exec -it product-service python manage.py shell

# In Python shell:
from products.models import Category
print(Category.objects.all())
# Should show categories including "Điện thoại & Tablet"
```

#### Step 5: Restart service
```bash
docker-compose restart product-service
```

---

## 🐛 Issue 3: Out of Memory (OOM)

### Triệu chứng
- Containers restart repeatedly
- System freeze/lag
- Docker logs show "OOMKilled"

### Giải pháp

#### Check memory usage
```bash
# System memory
free -h

# Docker memory
docker stats

# Check which container is OOM
docker ps -a | grep -i restart
```

#### Free memory
```bash
./cleanup_memory.sh
```

#### Add memory limits
Create `docker-compose.override.yml`:
```yaml
version: '3.8'

services:
  ai-service:
    mem_limit: 4g
    mem_reservation: 2g
  
  neo4j:
    mem_limit: 2g
    mem_reservation: 1g
```

Deploy with limits:
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

---

## 🐛 Issue 4: Port Already in Use

### Triệu chứng
```
Error: Bind for 0.0.0.0:8001 failed: port is already allocated
```

### Giải pháp

#### Find what's using the port
```bash
# Check port 8001
sudo lsof -i :8001

# Or using netstat
sudo netstat -tulpn | grep :8001
```

#### Kill the process
```bash
# Get PID from above command
sudo kill -9 <PID>
```

#### Or change port
Edit `.env` file:
```bash
PRODUCT_SERVICE_PORT=8011  # Changed from 8001
```

Then restart:
```bash
docker-compose up -d
```

---

## 🐛 Issue 5: Permission Denied

### Triệu chứng
```
Permission denied: '/app/data'
```

### Giải pháp

#### Fix directory permissions
```bash
# For AI Service data
sudo chown -R $USER:$USER services/ai-service/data
sudo chmod -R 755 services/ai-service/data

# For all services
sudo chown -R $USER:$USER services/
```

#### Run Docker without sudo
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
# Or run:
newgrp docker
```

---

## 🐛 Issue 6: Container Won't Start

### Triệu chứng
Container status shows "Restarting" or "Exited"

### Giải pháp

#### Check logs
```bash
docker logs <container-name>
docker logs <container-name> --tail 100
```

#### Check health status
```bash
docker inspect <container-name> | grep -A 10 Health
```

#### Common causes

**Missing environment variables:**
```bash
# Check .env file exists
cat .env

# Verify variables
docker-compose config
```

**Database not ready:**
```bash
# Check database logs
docker logs product-db
docker logs user-db

# Wait longer for DB to start
# Edit docker-compose.yml:
depends_on:
  product-db:
    condition: service_healthy
```

**Migration needed:**
```bash
docker exec -it <service-name> python manage.py migrate
```

---

## 🐛 Issue 7: Network Issues

### Triệu chứng
Services can't communicate with each other

### Giải pháp

#### Check networks
```bash
# List networks
docker network ls

# Inspect network
docker network inspect tieuluansad_default
```

#### Check DNS
```bash
# From one service to another
docker exec -it frontend-service ping product-service

# Should resolve to internal IP
```

#### Recreate networks
```bash
docker-compose down
docker network prune
docker-compose up -d
```

---

## 🐛 Issue 8: Image Build Failed

### Triệu chứng
```
ERROR: failed to solve: process "/bin/sh -c pip install ..." did not complete
```

### Giải pháp

#### Clear build cache
```bash
docker builder prune -a
```

#### Rebuild without cache
```bash
docker-compose build --no-cache
```

#### Check Dockerfile
- Verify base image exists
- Check requirements.txt is valid
- Ensure proper syntax

---

## 🐛 Issue 9: Volume Issues

### Triệu chứng
Data not persisting or old data showing

### Giải pháp

#### List volumes
```bash
docker volume ls
```

#### Remove old volumes
```bash
# Stop containers first
docker-compose down

# Remove volumes
docker volume rm tieuluansad_user_db_data

# Or remove all unused
docker volume prune
```

#### Backup before removing
```bash
# Example: Backup MySQL
docker exec user-db mysqldump -u user -p user_db > backup.sql
```

---

## 🐛 Issue 10: Slow Performance

### Triệu chứng
Services respond slowly, high CPU/memory usage

### Giải pháp

#### Monitor resources
```bash
# Real-time monitoring
docker stats

# System resources
htop
```

#### Optimize Docker
```bash
# Limit resources in docker-compose.override.yml
services:
  service-name:
    cpus: '2'
    mem_limit: 1g
```

#### Check database
```bash
# Check slow queries
docker exec -it product-db psql -U postgres

# Analyze queries
EXPLAIN ANALYZE SELECT ...;
```

#### Clear unused resources
```bash
docker system prune -a
```

---

## 📋 General Debugging Workflow

```
1. Identify the problem
   ↓
2. Check logs: docker logs <service>
   ↓
3. Check status: docker ps -a
   ↓
4. Check resources: docker stats
   ↓
5. Check network: docker network inspect
   ↓
6. Try restart: docker-compose restart <service>
   ↓
7. If still fails, check specific issue above
   ↓
8. Last resort: docker-compose down && docker-compose up -d
```

---

## 🆘 Emergency Commands

### Stop everything
```bash
docker-compose down
docker stop $(docker ps -aq)
```

### Clean everything
```bash
docker-compose down -v
docker system prune -a --volumes
```

### Fresh start
```bash
# 1. Stop and remove everything
docker-compose down -v
docker system prune -a --volumes

# 2. Rebuild
docker-compose build --no-cache

# 3. Start
docker-compose up -d

# 4. Check logs
docker-compose logs -f
```

---

## 📞 Getting Help

### Check documentation
- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- Project README files

### Useful commands for debugging
```bash
# Service logs
docker-compose logs <service-name>

# Follow logs
docker-compose logs -f <service-name>

# All logs
docker-compose logs -f

# Container shell
docker exec -it <container> bash

# Container processes
docker top <container>

# Container details
docker inspect <container>
```

---

## 🔍 Diagnostic Script

Create `diagnose.sh`:
```bash
#!/bin/bash

echo "=== Docker Info ==="
docker version
docker-compose version

echo ""
echo "=== Running Containers ==="
docker ps

echo ""
echo "=== Resource Usage ==="
docker stats --no-stream

echo ""
echo "=== Networks ==="
docker network ls

echo ""
echo "=== Volumes ==="
docker volume ls

echo ""
echo "=== System Info ==="
free -h
df -h | grep -E '^Filesystem|/$'
```

Run it:
```bash
chmod +x diagnose.sh
./diagnose.sh
```

---

**Need more help?** Check:
- Project logs in `docker-compose logs`
- Service-specific docs in `services/*/README.md`
- System docs in `kiro_md/`
