#!/bin/bash

# Memory Cleanup Script for Docker Deployment
# Run this before starting docker-compose if memory is low

echo "═══════════════════════════════════════════════════════════"
echo "🧹 MEMORY CLEANUP TOOL"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check current memory
echo "💾 CURRENT MEMORY STATUS:"
free -h
echo ""

# Show top memory consumers
echo "📊 TOP 10 MEMORY-CONSUMING PROCESSES:"
echo "─────────────────────────────────────────────────────────"
ps aux --sort=-%mem | awk 'NR<=11 {printf "%-20s %6s %6s %s\n", $11, $4"%", $6, $12}' | column -t
echo ""

# Ask for confirmation
read -p "Do you want to clean up memory? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled."
    exit 0
fi

echo "🧹 Cleaning up memory..."

# 1. Clear PageCache, dentries and inodes
echo "  → Dropping caches..."
sync
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' 2>/dev/null || {
    echo "  ⚠️  Need sudo permission to drop caches"
}

# 2. Clear systemd journal logs (optional)
echo "  → Cleaning journal logs..."
sudo journalctl --vacuum-time=3d 2>/dev/null || true

# 3. Remove old Docker data (if Docker is running)
if command -v docker &> /dev/null; then
    echo "  → Cleaning Docker..."
    docker system prune -f 2>/dev/null || true
fi

echo ""
echo "✅ Cleanup completed!"
echo ""

# Show updated memory
echo "💾 MEMORY STATUS AFTER CLEANUP:"
free -h
echo ""

# Calculate available memory
AVAILABLE=$(free -m | awk 'NR==2 {print $7}')
if [ $AVAILABLE -lt 6000 ]; then
    echo "⚠️  WARNING: Available memory is ${AVAILABLE}MB"
    echo "   Docker deployment needs at least 6GB available."
    echo "   Consider closing some applications."
else
    echo "✅ Available memory: ${AVAILABLE}MB - Good for Docker deployment!"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
