"""
Run Phase 8: Deployment Testing
This script tests the Docker deployment
"""
import subprocess
import time
import requests
import json

def run_command(cmd, cwd="."):
    """Run shell command"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_docker_installed():
    """Test if Docker is installed"""
    print("\n" + "=" * 70)
    print("Test 1: Docker Installation")
    print("=" * 70)
    
    success, stdout, stderr = run_command("docker --version")
    
    if success:
        print(f"✅ Docker is installed: {stdout.strip()}")
        return True
    else:
        print(f"❌ Docker is not installed")
        return False

def test_docker_compose_installed():
    """Test if Docker Compose is installed"""
    print("\n" + "=" * 70)
    print("Test 2: Docker Compose Installation")
    print("=" * 70)
    
    success, stdout, stderr = run_command("docker compose version")
    
    if success:
        print(f"✅ Docker Compose is installed: {stdout.strip()}")
        return True
    else:
        print(f"❌ Docker Compose is not installed")
        return False

def test_required_files():
    """Test if all required files exist"""
    print("\n" + "=" * 70)
    print("Test 3: Required Files")
    print("=" * 70)
    
    import os
    
    required_files = [
        "Dockerfile",
        ".dockerignore",
        "docker-compose.ai.yml",
        ".env.example",
        "deploy.sh",
        "requirements.txt",
        "main.py",
        "data/user_behavior.csv",
        "data/mappings.pkl",
        "data/faiss_index.bin",
        "data/rag_metadata.pkl",
        "models/lstm_model_best.pth"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_exist = False
    
    return all_exist

def test_docker_build():
    """Test Docker image build"""
    print("\n" + "=" * 70)
    print("Test 4: Docker Image Build")
    print("=" * 70)
    
    print("Building Docker image (this may take a few minutes)...")
    success, stdout, stderr = run_command("docker build -t ai-service:test .")
    
    if success:
        print("✅ Docker image built successfully")
        
        # Check image size
        success2, stdout2, stderr2 = run_command(
            "docker images ai-service:test --format '{{.Size}}'"
        )
        if success2:
            print(f"   Image size: {stdout2.strip()}")
        
        return True
    else:
        print(f"❌ Docker build failed")
        print(f"Error: {stderr[:500]}")
        return False

def test_docker_compose_config():
    """Test docker-compose configuration"""
    print("\n" + "=" * 70)
    print("Test 5: Docker Compose Configuration")
    print("=" * 70)
    
    success, stdout, stderr = run_command("docker compose -f docker-compose.ai.yml config")
    
    if success:
        print("✅ Docker Compose configuration is valid")
        return True
    else:
        print(f"❌ Docker Compose configuration is invalid")
        print(f"Error: {stderr[:500]}")
        return False

def test_deployment_script():
    """Test deployment script"""
    print("\n" + "=" * 70)
    print("Test 6: Deployment Script")
    print("=" * 70)
    
    import os
    
    if os.path.exists("deploy.sh"):
        print("✅ deploy.sh exists")
        
        # Check if executable
        if os.access("deploy.sh", os.X_OK):
            print("✅ deploy.sh is executable")
            return True
        else:
            print("⚠️  deploy.sh is not executable")
            print("   Run: chmod +x deploy.sh")
            return True
    else:
        print("❌ deploy.sh not found")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("\n" + "=" * 70)
    print("Test 7: Environment Variables")
    print("=" * 70)
    
    import os
    
    if os.path.exists(".env.example"):
        print("✅ .env.example exists")
        
        with open(".env.example", "r") as f:
            content = f.read()
            
        required_vars = [
            "PRODUCT_SERVICE_URL",
            "ORDER_SERVICE_URL",
            "USER_SERVICE_URL",
            "NEO4J_URI",
            "NEO4J_USER",
            "NEO4J_PASSWORD"
        ]
        
        all_found = True
        for var in required_vars:
            if var in content:
                print(f"✅ {var}")
            else:
                print(f"❌ {var} - MISSING")
                all_found = False
        
        return all_found
    else:
        print("❌ .env.example not found")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("📌 GIAI ĐOẠN 8 — KIỂM THỬ DEPLOYMENT")
    print("=" * 70)
    
    tests = [
        ("Docker Installation", test_docker_installed),
        ("Docker Compose Installation", test_docker_compose_installed),
        ("Required Files", test_required_files),
        ("Docker Image Build", test_docker_build),
        ("Docker Compose Config", test_docker_compose_config),
        ("Deployment Script", test_deployment_script),
        ("Environment Variables", test_environment_variables)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 KẾT QUẢ KIỂM THỬ")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTổng kết: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("✅ GIAI ĐOẠN 8 HOÀN THÀNH!")
        print("=" * 70)
        
        print("\nDeployment artifacts created:")
        print("   ✅ Dockerfile")
        print("   ✅ .dockerignore")
        print("   ✅ docker-compose.ai.yml")
        print("   ✅ .env.example")
        print("   ✅ deploy.sh")
        
        print("\nTo deploy:")
        print("   1. Run: ./deploy.sh")
        print("   2. Or: docker-compose -f docker-compose.ai.yml up -d")
        
        print("\nTo deploy with full system:")
        print("   docker-compose up -d")
        
        print("\nService will be available at:")
        print("   - API: http://localhost:8008")
        print("   - Docs: http://localhost:8008/docs")
        print("   - Health: http://localhost:8008/api/v1/health")
        
        print("\n🎉 AI Service is ready for production deployment!")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before deployment.")

if __name__ == "__main__":
    main()
