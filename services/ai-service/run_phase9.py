"""
Phase 9: Complete Multi-Model AI System Setup
Chạy tất cả các bước training
"""

import subprocess
import sys
from pathlib import Path
import time

def run_command(command, description):
    """Run a command and print status"""
    print("\n" + "="*70)
    print(f"🚀 {description}")
    print("="*70)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        
        elapsed = time.time() - start_time
        print(f"\n✅ {description} - Completed in {elapsed:.1f}s")
        return True
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"\n❌ {description} - Failed after {elapsed:.1f}s")
        print(f"Error: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n" + "="*70)
    print("🔍 CHECKING DEPENDENCIES")
    print("="*70)
    
    required_packages = [
        'pandas',
        'numpy',
        'scipy',
        'sklearn',
        'torch'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\nInstall with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("\n✅ All dependencies installed!")
    return True

def check_files():
    """Check if data files exist"""
    print("\n" + "="*70)
    print("🔍 CHECKING DATA FILES")
    print("="*70)
    
    data_dir = Path("data")
    required_files = [
        "product_features.csv",
        "user_behavior.csv",
        "user_ratings.csv",
        "product_interactions.csv",
        "category_trends.csv"
    ]
    
    missing = []
    for file in required_files:
        filepath = data_dir / file
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"   ✅ {file} ({size_kb:.1f} KB)")
        else:
            print(f"   ❌ {file} - NOT FOUND")
            missing.append(file)
    
    if missing:
        print(f"\n⚠️  Missing files: {', '.join(missing)}")
        return False
    
    print("\n✅ All data files exist!")
    return True

def main():
    print("\n" + "="*70)
    print("🎯 PHASE 9: MULTI-MODEL AI SYSTEM SETUP")
    print("="*70)
    print("\nThis will:")
    print("  1. Generate 5 datasets")
    print("  2. Train Collaborative Filtering model")
    print("  3. Train Random Forest model")
    print("  4. Train Ensemble system")
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first!")
        sys.exit(1)
    
    # Step 1: Generate data (if not exists)
    if not check_files():
        print("\n📊 Generating data files...")
        if not run_command("python src/data_generator.py", "Step 1: Generate Data"):
            print("❌ Data generation failed!")
            sys.exit(1)
    else:
        print("\n✅ Data files already exist, skipping generation...")
    
    # Step 2: Train Collaborative Filtering
    if not run_command("python train_cf.py", "Step 2: Train Collaborative Filtering"):
        print("❌ CF training failed!")
        sys.exit(1)
    
    # Step 3: Train Random Forest
    if not run_command("python train_rf.py", "Step 3: Train Random Forest"):
        print("❌ RF training failed!")
        sys.exit(1)
    
    # Step 4: Train Ensemble
    if not run_command("python train_ensemble.py", "Step 4: Train Ensemble"):
        print("❌ Ensemble training failed!")
        sys.exit(1)
    
    # Final summary
    print("\n" + "="*70)
    print("🎉 PHASE 9 SETUP COMPLETED SUCCESSFULLY!")
    print("="*70)
    
    models_dir = Path("models")
    print("\n📦 Models created:")
    print(f"   ✅ {models_dir / 'cf_model.pkl'}")
    print(f"   ✅ {models_dir / 'rf_model.pkl'}")
    print(f"   ✅ {models_dir / 'ensemble_weights.pkl'}")
    
    print("\n📊 Data files:")
    data_dir = Path("data")
    for file in ["product_features.csv", "user_behavior.csv", "user_ratings.csv", 
                 "product_interactions.csv", "category_trends.csv"]:
        filepath = data_dir / file
        if filepath.exists():
            print(f"   ✅ {file}")
    
    print("\n🚀 Next steps:")
    print("   1. Test the models:")
    print("      python -c \"from src.cf_model import CollaborativeFiltering; cf = CollaborativeFiltering.load('models/cf_model.pkl'); print(cf.recommend(1, 5))\"")
    print()
    print("   2. Start AI service:")
    print("      docker-compose up ai-service")
    print()
    print("   3. Test API endpoints:")
    print("      curl http://localhost:8008/api/v1/health")
    print()

if __name__ == "__main__":
    main()
