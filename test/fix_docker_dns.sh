#!/bin/bash

# Fix Docker DNS Issue
# Run this script when you get "server misbehaving" DNS errors

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║              🔧 FIXING DOCKER DNS ISSUE                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

echo "Problem: Docker can't resolve registry-1.docker.io"
echo "Solution: Configure Docker to use public DNS servers"
echo ""

# Step 1: Create Docker config directory
echo "📁 Step 1: Creating Docker config directory..."
sudo mkdir -p /etc/docker

# Step 2: Configure Docker DNS
echo "🌐 Step 2: Configuring Docker DNS..."
cat << 'DOCKERDAEMON' | sudo tee /etc/docker/daemon.json
{
  "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
DOCKERDAEMON

echo ""
echo "✅ Docker DNS configured:"
echo "   - Primary DNS: 8.8.8.8 (Google)"
echo "   - Secondary DNS: 8.8.4.4 (Google)"
echo "   - Tertiary DNS: 1.1.1.1 (Cloudflare)"
echo ""

# Step 3: Restart Docker
echo "🔄 Step 3: Restarting Docker..."
sudo systemctl restart docker

# Wait for Docker to start
sleep 5

# Check if Docker is running
if sudo systemctl is-active --quiet docker; then
    echo "✅ Docker restarted successfully"
else
    echo "❌ Docker failed to restart"
    echo "Check logs: sudo journalctl -u docker -n 50"
    exit 1
fi

echo ""
echo "🧪 Step 4: Testing DNS resolution..."
echo "Testing connection to google.com..."

if docker run --rm alpine ping -c 3 google.com > /dev/null 2>&1; then
    echo "✅ DNS is working! Can reach internet."
else
    echo "⚠️  DNS test failed. Checking alternative solutions..."
    echo ""
    echo "Your system DNS:"
    cat /etc/resolv.conf | grep nameserver
    echo ""
    echo "Try manually editing /etc/docker/daemon.json with your system DNS"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ DNS FIX COMPLETED                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Run: docker-compose build"
echo "  2. Then: docker-compose up -d"
echo ""
