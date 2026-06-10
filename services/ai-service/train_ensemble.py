"""
Train Ensemble System
Kết hợp LSTM + CF + RF models
"""

import pandas as pd
from pathlib import Path
from src.ensemble import EnsembleRecommender
from src.cf_model import CollaborativeFiltering
from src.rf_model import RandomForestRecommender

def main():
    print("\n" + "="*70)
    print("🎯 TRAINING ENSEMBLE SYSTEM")
    print("="*70 + "\n")
    
    # Paths
    models_dir = Path("models")
    
    # Load trained models
    print("📂 Loading trained models...")
    
    cf_model = CollaborativeFiltering.load(models_dir / "cf_model.pkl")
    rf_model = RandomForestRecommender.load(models_dir / "rf_model.pkl")
    
    # Note: LSTM model would be loaded separately if available
    # lstm_model = load_lstm_model(models_dir / "lstm_model.pth")
    
    # Create ensemble
    print("\n🔧 Creating ensemble...")
    ensemble = EnsembleRecommender(method='weighted')
    
    # Set models (LSTM as None for now)
    ensemble.set_models(
        lstm_model=None,
        cf_model=cf_model,
        rf_model=rf_model
    )
    
    # Set initial weights
    print("\n⚖️  Setting ensemble weights...")
    ensemble.set_weights(
        lstm_weight=0.40,
        cf_weight=0.35,
        rf_weight=0.25
    )
    
    # Test ensemble
    print("\n📊 Testing ensemble predictions...")
    
    # Load product features for testing
    product_features_df = pd.read_csv("data/product_features.csv")
    test_products = product_features_df.head(5).to_dict('records')
    
    user_id = 1
    print(f"\nEnsemble predictions for User {user_id}:")
    
    for product in test_products:
        comparison = ensemble.get_model_comparison(
            user_id=user_id,
            product_id=product['product_id'],
            product_features=product
        )
        
        print(f"\n   Product {product['product_id']} ({product['category']}):")
        print(f"      CF Score:       {comparison['cf_score']:.3f}")
        print(f"      RF Score:       {comparison['rf_score']:.3f}")
        print(f"      Ensemble:       {comparison['ensemble_score']:.3f}")
        print(f"      Confidence:     {comparison['confidence']:.3f}")
        print(f"      Recommendation: {comparison['recommendation']}")
    
    # Test recommendations
    print("\n🎯 Testing recommendations...")
    recommendations = ensemble.recommend(
        user_id=user_id,
        candidate_products=test_products,
        k=3
    )
    
    print(f"\nTop 3 recommendations for User {user_id}:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n   #{i} Product {rec['product_id']}")
        print(f"      Ensemble Score: {rec['score']:.3f}")
        print(f"      CF: {rec['model_scores']['cf']:.3f}, RF: {rec['model_scores']['rf']:.3f}")
        print(f"      Confidence: {rec['confidence']:.3f}")
    
    # Save ensemble configuration
    print("\n💾 Saving ensemble configuration...")
    ensemble.save(models_dir / "ensemble_weights.pkl")
    
    print("\n" + "="*70)
    print("✅ ENSEMBLE SYSTEM TRAINING COMPLETED!")
    print("="*70)
    print(f"\n📊 Configuration saved to: {models_dir / 'ensemble_weights.pkl'}")
    print(f"⚖️  Weights: LSTM={ensemble.weights['lstm']:.2f}, "
          f"CF={ensemble.weights['cf']:.2f}, RF={ensemble.weights['rf']:.2f}")
    print(f"🎯 Method: {ensemble.method}")
    print()

if __name__ == "__main__":
    main()
