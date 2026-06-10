"""
Train Collaborative Filtering Model
"""

import pandas as pd
from pathlib import Path
from src.cf_model import CollaborativeFiltering

def main():
    print("\n" + "="*70)
    print("🤖 TRAINING COLLABORATIVE FILTERING MODEL")
    print("="*70 + "\n")
    
    # Paths
    data_dir = Path("data")
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Load data
    print("📂 Loading data...")
    ratings_df = pd.read_csv(data_dir / "user_ratings.csv")
    behavior_df = pd.read_csv(data_dir / "user_behavior.csv")
    
    print(f"   ✅ Ratings: {len(ratings_df)} records")
    print(f"   ✅ Behavior: {len(behavior_df)} records")
    
    # Initialize model
    model = CollaborativeFiltering(n_factors=50)
    
    # Train
    model.train(ratings_df, behavior_df)
    
    # Save
    model.save(models_dir / "cf_model.pkl")
    
    # Test predictions
    print("\n📊 Testing predictions...")
    test_users = ratings_df['user_id'].unique()[:5]
    
    for user_id in test_users:
        recs = model.recommend(user_id, k=5)
        print(f"\nUser {user_id} recommendations:")
        for product_id, score in recs[:3]:
            print(f"   Product {product_id}: {score:.3f}")
    
    # Test similar items
    print("\n🔍 Testing similar items...")
    test_product = ratings_df['product_id'].iloc[0]
    similar = model.get_similar_items(test_product, k=5)
    print(f"\nSimilar to Product {test_product}:")
    for product_id, similarity in similar[:3]:
        print(f"   Product {product_id}: {similarity:.3f}")
    
    print("\n" + "="*70)
    print("✅ COLLABORATIVE FILTERING TRAINING COMPLETED!")
    print("="*70)
    print(f"\n💾 Model saved to: {models_dir / 'cf_model.pkl'}")
    print(f"📊 Matrix size: {model.user_factors.shape[0]} users x {model.item_factors.shape[0]} items")
    print(f"🎯 Latent factors: {model.n_factors}")
    print()

if __name__ == "__main__":
    main()
