"""
Run Phase 2: LSTM Model Training
This script trains the LSTM recommendation model
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from train_lstm import train_lstm_model

def main():
    print("=" * 70)
    print("📌 PHASE 2 — LSTM MODEL (PyTorch)")
    print("=" * 70)
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Train model
    recommender, trainer = train_lstm_model(
        X_path='data/X_train.npy',
        y_path='data/y_train.npy',
        mappings_path='data/mappings.pkl',
        batch_size=32,
        num_epochs=20,
        learning_rate=0.001,
        val_split=0.2,
        random_state=42
    )
    
    # Test inference
    print("\n" + "=" * 70)
    print("🧪 Testing Inference")
    print("=" * 70)
    
    # Test with sample sequence
    test_sequences = [
        [1, 2, 3, 4, 5],
        [10, 11, 12],
        [20, 21, 22, 23, 24, 25]
    ]
    
    for i, seq in enumerate(test_sequences, 1):
        print(f"\nTest {i}:")
        print(f"   Input sequence: {seq}")
        
        recommendations = recommender.recommend(seq, k=5, exclude_seen=True)
        
        print(f"   Top-5 recommendations:")
        for rank, (product_id, score) in enumerate(recommendations, 1):
            print(f"      {rank}. Product {product_id} (score: {score:.4f})")
    
    print("\n" + "=" * 70)
    print("✅ PHASE 2 COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print("   📄 models/lstm_model.pth - Final trained model")
    print("   📄 models/lstm_model_best.pth - Best model checkpoint")
    print("\nModel is ready for:")
    print("   - Phase 5: Hybrid Recommendation")
    print("   - Phase 6: FastAPI Service Integration")

if __name__ == '__main__':
    main()
