"""
Train Random Forest Model
"""

import pandas as pd
from pathlib import Path
from src.rf_model import RandomForestRecommender

def main():
    print("\n" + "="*70)
    print("🌲 TRAINING RANDOM FOREST MODEL")
    print("="*70 + "\n")
    
    # Paths
    data_dir = Path("data")
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Load data
    print("📂 Loading data...")
    behavior_df = pd.read_csv(data_dir / "user_behavior.csv")
    product_features_df = pd.read_csv(data_dir / "product_features.csv")
    interactions_df = pd.read_csv(data_dir / "product_interactions.csv")
    category_trends_df = pd.read_csv(data_dir / "category_trends.csv")
    
    print(f"   ✅ Behavior: {len(behavior_df)} records")
    print(f"   ✅ Product features: {len(product_features_df)} products")
    print(f"   ✅ Interactions: {len(interactions_df)} records")
    print(f"   ✅ Category trends: {len(category_trends_df)} records")
    
    # Initialize model
    model = RandomForestRecommender(n_estimators=100, max_depth=10)
    
    # Train
    model.train(
        behavior_df,
        product_features_df,
        interactions_df,
        category_trends_df
    )
    
    # Save
    model.save(models_dir / "rf_model.pkl")
    
    # Test predictions
    print("\n📊 Testing predictions...")
    
    # Get some test cases
    test_products = product_features_df.head(5).to_dict('records')
    user_id = 1
    
    print(f"\nPredictions for User {user_id}:")
    for product in test_products:
        proba = model.predict_proba(user_id, product['product_id'], product)
        print(f"   Product {product['product_id']} ({product['category']}): {proba:.3f}")
    
    print("\n" + "="*70)
    print("✅ RANDOM FOREST TRAINING COMPLETED!")
    print("="*70)
    print(f"\n💾 Model saved to: {models_dir / 'rf_model.pkl'}")
    print(f"📊 Trees: {model.model.n_estimators}")
    print(f"🎯 Features: {len(model.feature_names)}")
    print()

if __name__ == "__main__":
    main()
