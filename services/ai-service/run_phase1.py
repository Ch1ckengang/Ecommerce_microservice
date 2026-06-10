"""
Run Phase 1: Data Preparation
This script executes all tasks in Phase 1
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generate_data import generate_user_behavior, save_to_csv
from data_preprocessing import preprocess_pipeline

def main():
    print("=" * 70)
    print("📌 PHASE 1 — DATA PREPARATION")
    print("=" * 70)
    
    # Task 1.1: Create dataset
    print("\n" + "=" * 70)
    print("Task 1.1: Create Dataset")
    print("=" * 70)
    
    behaviors = generate_user_behavior()
    save_to_csv(behaviors, 'data/user_behavior.csv')
    
    # Task 1.2 & 1.3: Preprocess and create training samples
    print("\n" + "=" * 70)
    print("Task 1.2 & 1.3: Preprocess Data and Create Training Samples")
    print("=" * 70)
    
    X, y, preprocessor = preprocess_pipeline('data/user_behavior.csv')
    
    # Save numpy arrays
    import numpy as np
    np.save('data/X_train.npy', X)
    np.save('data/y_train.npy', y)
    print("\n💾 Saved training data:")
    print("   📄 data/X_train.npy")
    print("   📄 data/y_train.npy")
    
    print("\n" + "=" * 70)
    print("✅ PHASE 1 COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print("   📄 data/user_behavior.csv - Raw user behavior data")
    print("   📄 data/mappings.pkl - Product ID mappings")
    print("   📄 data/X_train.npy - Training input sequences")
    print("   📄 data/y_train.npy - Training target products")
    print("\nReady for Phase 2: LSTM Model Training")

if __name__ == '__main__':
    main()
