# 💾 Hướng dẫn Tối ưu hóa Memory

**Your System:** 14GB RAM, hiện đang dùng 9.3GB (66%)

---

## 📊 Phân tích hiện tại

```
Total Memory:     14GB
Used:             9.3GB (66%)
Free:             1.8GB (13%)
Available:        5.5GB (39%)
Swap:             590MB used / 4.0GB total
```

**Đánh giá:** ⚠️ Moderate - Có thể chạy Docker nhưng nên tối ưu

---

## 🎯 Memory Requirements

### Docker Deployment
```
Minimum:          6GB available
Recommended:      8GB available
Your Available:   5.5GB ⚠️
```

### Service Memory Usage (ước tính)
```
MySQL databases (3):        ~300MB each = 900MB
PostgreSQL databases (4):   ~200MB each = 800MB
Neo4j:                      ~1GB
Django services (6):        ~200MB each = 1.2GB
FastAPI (AI Service):       ~2-4GB (with ML models)
Nginx:                      ~50MB
Frontend:                   ~200MB
───────────────────────────────────────────
Total:                      ~7-9GB
```

---

## 🧹 Quick Cleanup (Trước khi chạy Docker)

### Option 1: Sử dụng script tự động
```bash
cd /home/trung/Documents/TieuluanS.A&D
./cleanup_memory.sh
```

### Option 2: Manual cleanup
```bash
# 1. Clear caches
sync
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# 2. Clear journal logs
sudo journalctl --vacuum-time=3d

# 3. Clean Docker (if installed)
docker system prune -f

# 4. Check result
free -h
```

---

## 🔍 Tìm và đóng ứng dụng tốn RAM

### Xem top processes
```bash
# Show top 20 memory-consuming processes
ps aux --sort=-%mem | head -21

# Or use htop (more visual)
htop
# Press F6, chọn PERCENT_MEM, press Enter
# Press F9 to kill process
```

### Common culprits
```bash
# Check Chrome/Firefox tabs
ps aux | grep -E "chrome|firefox" | wc -l

# Check VS Code/IDEs
ps aux | grep -E "code|pycharm|intellij"

# Check Electron apps (Slack, Discord, etc.)
ps aux | grep -i electron
```

### Đóng các ứng dụng không cần thiết
```bash
# Chrome/Chromium
killall chrome chromium-browser

# VS Code
killall code

# Slack
killall slack

# Discord
killall discord
```

---

## ⚙️ Tối ưu hóa Docker Deployment

### 1. Giới hạn memory cho containers

**Tạo file docker-compose.override.yml:**
```yaml
version: '3.8'

services:
  # Limit memory for each service
  user-service:
    mem_limit: 512m
    mem_reservation: 256m
  
  product-service:
    mem_limit: 512m
    mem_reservation: 256m
  
  cart-service:
    mem_limit: 512m
    mem_reservation: 256m
  
  order-service:
    mem_limit: 512m
    mem_reservation: 256m
  
  payment-service:
    mem_limit: 512m
    mem_reservation: 256m
  
  shipping-service:
    mem_limit: 512m
    mem_reservation: 256m
  
  frontend-service:
    mem_limit: 512m
    mem_reservation: 256m
  
  ai-service:
    mem_limit: 4g
    mem_reservation: 2g
  
  neo4j:
    mem_limit: 2g
    mem_reservation: 1g
    environment:
      - NEO4J_server_memory_heap_initial__size=512m
      - NEO4J_server_memory_heap_max__size=1G
      - NEO4J_server_memory_pagecache_size=512m
  
  # Databases
  user-db:
    mem_limit: 256m
    mem_reservation: 128m
  
  product-db:
    mem_limit: 256m
    mem_reservation: 128m
  
  cart-db:
    mem_limit: 256m
    mem_reservation: 128m
  
  order-db:
    mem_limit: 256m
    mem_reservation: 128m
  
  payment-db:
    mem_limit: 256m
    mem_reservation: 128m
  
  shipping-db:
    mem_limit: 256m
    mem_reservation: 128m
  
  frontend-db:
    mem_limit: 256m
    mem_reservation: 128m
```

**Sử dụng:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

---

### 2. Deployment có chọn lọc

**Option A: Chỉ chạy services cần thiết**
```bash
# Start core services only
docker-compose up -d \
  api-gateway \
  user-db user-service \
  product-db product-service \
  cart-db cart-service \
  order-db order-service \
  frontend-db frontend-service

# AI Service có thể start sau nếu cần
docker-compose up -d neo4j ai-service
```

**Option B: Chạy AI Service standalone**
```bash
# Chỉ chạy AI Service + Neo4j
cd services/ai-service
docker-compose -f docker-compose.ai.yml up -d
```

---

### 3. Monitoring memory usage

**Real-time monitoring:**
```bash
# Watch all containers
docker stats

# Watch specific service
docker stats ai-service

# Check memory usage once
docker stats --no-stream
```

**Set up alerts:**
```bash
# Check if any container exceeds 1GB
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}" | \
  awk '{if ($2 ~ /[0-9]+GiB/ && $2+0 > 1) print}'
```

---

## 🚨 Khi gặp Out of Memory

### Dấu hiệu
- Container restart liên tục
- Services không response
- System freeze/lag
- Swap usage tăng cao (>2GB)

### Giải pháp khẩn cấp

**1. Stop services ngay:**
```bash
docker-compose down
```

**2. Free memory:**
```bash
./cleanup_memory.sh
# Or manual:
sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
```

**3. Restart with limits:**
```bash
# Use override file
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

**4. Monitor closely:**
```bash
watch -n 5 'free -h && echo "" && docker stats --no-stream'
```

---

## 📈 Long-term Solutions

### 1. Tăng RAM (Hardware)
- **Current:** 14GB
- **Recommended:** 16GB+ cho development
- **Ideal:** 32GB cho comfortable development

### 2. Tăng Swap
```bash
# Check current swap
swapon --show

# Create additional swap file (4GB)
sudo fallocate -l 4G /swapfile2
sudo chmod 600 /swapfile2
sudo mkswap /swapfile2
sudo swapon /swapfile2

# Make permanent
echo '/swapfile2 none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 3. Optimize system services
```bash
# Disable unused services
sudo systemctl disable bluetooth
sudo systemctl disable cups
sudo systemctl disable avahi-daemon

# Limit journal size
sudo journalctl --vacuum-size=100M
```

### 4. Use lighter alternatives
- **Browser:** Use Firefox/Chrome with fewer tabs
- **Editor:** Use VS Code with fewer extensions
- **Terminal:** Use lightweight terminal (kitty, alacritty)

---

## 📊 Memory Budget Planning

### Recommended allocation
```
System & Desktop:           2GB
Browser (10 tabs):          2GB
IDE/Editor:                 1GB
Docker Services:            7-8GB
Buffer:                     1-2GB
─────────────────────────────
Total needed:               13-15GB
```

### Your current situation
```
Used (non-Docker):          9.3GB
Docker will need:           ~7-8GB
Total needed:               ~16-17GB
Your total:                 14GB
─────────────────────────────
Shortage:                   2-3GB ⚠️
```

**Recommendation:**
- Close 5-10 browser tabs → Save 1GB
- Close unused apps → Save 1-2GB
- Use memory limits → Save 1-2GB
= Should be OK! ✅

---

## ✅ Pre-Docker Checklist

Trước khi chạy `docker-compose up -d`:

- [ ] Run `./cleanup_memory.sh`
- [ ] Close unnecessary browser tabs
- [ ] Close unused applications
- [ ] Check `free -h` shows >6GB available
- [ ] Consider using docker-compose.override.yml
- [ ] Plan to monitor `docker stats`

---

## 🔧 Troubleshooting

### "Cannot allocate memory" error
```bash
# 1. Stop Docker
docker-compose down

# 2. Clean everything
docker system prune -a --volumes

# 3. Clear caches
./cleanup_memory.sh

# 4. Restart with limits
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Container keeps restarting
```bash
# Check memory usage
docker stats container-name

# Check logs
docker logs container-name | tail -50

# If OOM (Out of Memory), increase limit
# Edit docker-compose.override.yml
```

### System freezing
```bash
# Emergency: Switch to TTY
# Press Ctrl+Alt+F3

# Kill Docker
sudo killall dockerd

# Free memory
sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# Switch back
# Press Ctrl+Alt+F2
```

---

## 📚 Additional Resources

- [Docker Memory Limits](https://docs.docker.com/config/containers/resource_constraints/)
- [Linux Memory Management](https://www.kernel.org/doc/html/latest/admin-guide/mm/index.html)
- [Monitoring Docker](https://docs.docker.com/config/containers/runmetrics/)

---

## 🎯 TL;DR - Quick Start

**Nếu RAM đang ở mức 66% (9.3GB/14GB):**

1. **Close apps:** Browser tabs, IDE, Slack, Discord
2. **Clean memory:** `./cleanup_memory.sh`
3. **Check:** `free -h` should show >6GB available
4. **Deploy:** `docker-compose up -d`
5. **Monitor:** `docker stats`

**Nếu vẫn thiếu RAM:**
- Use `docker-compose.override.yml` with memory limits
- Deploy services incrementally
- Consider increasing swap

---

**Status:** ⚠️ Need optimization before Docker deployment  
**Action:** Run cleanup script and close unused apps  
**Goal:** Get 6GB+ available memory
