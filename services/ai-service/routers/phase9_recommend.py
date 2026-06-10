"""
Phase 9 Multi-Model Recommendations
New endpoints for 3-model ensemble (LSTM + CF + RF)
DOES NOT affect existing endpoints
"""
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from pathlib import Path

router = APIRouter()

# Pydantic schemas for Phase 9
class Phase9RecommendRequest(BaseModel):
    """Request for Phase 9 multi-model recommendations"""
    user_id: int = Field(..., ge=1, description="User ID")
    k: int = Field(10, ge=1, le=50, description="Number of recommendations")
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Custom weights for models (lstm, cf, rf)"
    )
    filter_available: bool = Field(
        True,
        description="Only recommend products in stock"
    )

class ModelScore(BaseModel):
    """Individual model scores"""
    lstm: float = Field(..., description="LSTM model score")
    cf: float = Field(..., description="Collaborative Filtering score")
    rf: float = Field(..., description="Random Forest score")

class Phase9Recommendation(BaseModel):
    """Single Phase 9 recommendation"""
    product_id: int
    score: float = Field(..., description="Ensemble score")
    model_scores: ModelScore
    confidence: float = Field(..., description="Prediction confidence (0-1)")
    product_name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None

class Phase9RecommendResponse(BaseModel):
    """Response for Phase 9 recommendations"""
    recommendations: List[Phase9Recommendation]
    total: int
    weights_used: Dict[str, float]
    method: str = "ensemble"

class ModelComparisonRequest(BaseModel):
    """Request for comparing model predictions"""
    user_id: int = Field(..., ge=1)
    product_id: int = Field(..., ge=1)

class ModelComparisonResponse(BaseModel):
    """Response comparing model predictions"""
    user_id: int
    product_id: int
    lstm_score: float
    cf_score: float
    rf_score: float
    ensemble_score: float
    confidence: float
    recommendation: str  # high, medium, low
    model_agreement: Dict

# Lazy load Phase 9 models
_phase9_ensemble = None
_phase9_models_loaded = False

def get_phase9_ensemble():
    """Lazy load Phase 9 ensemble"""
    global _phase9_ensemble, _phase9_models_loaded
    
    if _phase9_models_loaded:
        return _phase9_ensemble
    
    try:
        from src.ensemble import EnsembleRecommender
        from src.cf_model import CollaborativeFiltering
        from src.rf_model import RandomForestRecommender
        
        models_dir = Path("models")
        
        # Load models
        cf_model = CollaborativeFiltering.load(models_dir / "cf_model.pkl")
        rf_model = RandomForestRecommender.load(models_dir / "rf_model.pkl")
        
        # Create ensemble
        ensemble = EnsembleRecommender(method='weighted')
        ensemble.set_models(
            lstm_model=None,  # Will integrate later
            cf_model=cf_model,
            rf_model=rf_model
        )
        
        # Load saved weights if available
        weights_path = models_dir / "ensemble_weights.pkl"
        if weights_path.exists():
            saved_ensemble = EnsembleRecommender.load(weights_path)
            ensemble.weights = saved_ensemble.weights
        
        _phase9_ensemble = ensemble
        _phase9_models_loaded = True
        
        print("✅ Phase 9 ensemble loaded successfully")
        return ensemble
        
    except Exception as e:
        print(f"⚠️  Failed to load Phase 9 ensemble: {e}")
        return None

@router.post("/phase9/recommend", response_model=Phase9RecommendResponse)
async def phase9_recommend(
    request: Request,
    req: Phase9RecommendRequest
):
    """
    Phase 9 Multi-Model Recommendations
    Uses ensemble of CF + RF models (LSTM integration pending)
    
    This endpoint does NOT affect existing recommendation endpoints.
    """
    ensemble = get_phase9_ensemble()
    
    if not ensemble:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Phase 9 models not available. Please train models first."
        )
    
    try:
        # Update weights if provided
        if req.weights:
            ensemble.set_weights(
                lstm_weight=req.weights.get('lstm', 0.40),
                cf_weight=req.weights.get('cf', 0.35),
                rf_weight=req.weights.get('rf', 0.25)
            )
        
        # Get candidate products (simplified - in production, fetch from product service)
        import pandas as pd
        product_features_df = pd.read_csv("data/product_features.csv")
        candidate_products = product_features_df.to_dict('records')
        
        # Filter by stock if requested
        if req.filter_available:
            candidate_products = [p for p in candidate_products if p.get('stock', 0) > 0]
        
        # Get recommendations
        recommendations = ensemble.recommend(
            user_id=req.user_id,
            candidate_products=candidate_products,
            k=req.k
        )
        
        # Format response
        formatted_recs = []
        for rec in recommendations:
            formatted_recs.append(
                Phase9Recommendation(
                    product_id=rec['product_id'],
                    score=rec['score'],
                    model_scores=ModelScore(
                        lstm=rec['model_scores']['lstm'],
                        cf=rec['model_scores']['cf'],
                        rf=rec['model_scores']['rf']
                    ),
                    confidence=rec['confidence'],
                    product_name=rec['product'].get('name'),
                    category=rec['product'].get('category'),
                    price=rec['product'].get('price')
                )
            )
        
        return Phase9RecommendResponse(
            recommendations=formatted_recs,
            total=len(formatted_recs),
            weights_used=ensemble.weights,
            method="ensemble"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Phase 9 recommendations: {str(e)}"
        )

@router.post("/phase9/compare", response_model=ModelComparisonResponse)
async def phase9_compare_models(
    request: Request,
    req: ModelComparisonRequest
):
    """
    Compare predictions from all Phase 9 models
    Useful for understanding how different models view a product
    """
    ensemble = get_phase9_ensemble()
    
    if not ensemble:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Phase 9 models not available"
        )
    
    try:
        # Get product features
        import pandas as pd
        product_features_df = pd.read_csv("data/product_features.csv")
        product = product_features_df[
            product_features_df['product_id'] == req.product_id
        ].to_dict('records')
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {req.product_id} not found"
            )
        
        product_features = product[0]
        
        # Get comparison
        comparison = ensemble.get_model_comparison(
            user_id=req.user_id,
            product_id=req.product_id,
            product_features=product_features
        )
        
        return ModelComparisonResponse(**comparison)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing models: {str(e)}"
        )

@router.get("/phase9/health")
async def phase9_health():
    """
    Health check for Phase 9 models
    """
    ensemble = get_phase9_ensemble()
    
    models_dir = Path("models")
    
    status = {
        "phase9_enabled": ensemble is not None,
        "models": {
            "cf": (models_dir / "cf_model.pkl").exists(),
            "rf": (models_dir / "rf_model.pkl").exists(),
            "ensemble_config": (models_dir / "ensemble_weights.pkl").exists()
        },
        "weights": ensemble.weights if ensemble else None,
        "method": ensemble.method if ensemble else None
    }
    
    return status

@router.get("/phase9/stats")
async def phase9_stats():
    """
    Get Phase 9 system statistics
    """
    ensemble = get_phase9_ensemble()
    
    if not ensemble:
        return {
            "status": "not_loaded",
            "message": "Phase 9 models not available"
        }
    
    import pandas as pd
    
    # Load data stats
    behavior_df = pd.read_csv("data/user_behavior.csv")
    product_features_df = pd.read_csv("data/product_features.csv")
    interactions_df = pd.read_csv("data/product_interactions.csv")
    ratings_df = pd.read_csv("data/user_ratings.csv")
    category_trends_df = pd.read_csv("data/category_trends.csv")
    
    return {
        "status": "loaded",
        "datasets": {
            "user_behavior": len(behavior_df),
            "product_features": len(product_features_df),
            "interactions": len(interactions_df),
            "ratings": len(ratings_df),
            "category_trends": len(category_trends_df)
        },
        "models": {
            "cf": {
                "type": "Collaborative Filtering",
                "n_users": ensemble.cf_model.n_users if ensemble.cf_model else 0,
                "n_items": ensemble.cf_model.n_items if ensemble.cf_model else 0,
                "n_factors": ensemble.cf_model.n_factors if ensemble.cf_model else 0
            },
            "rf": {
                "type": "Random Forest",
                "n_estimators": ensemble.rf_model.model.n_estimators if ensemble.rf_model else 0,
                "n_features": len(ensemble.rf_model.feature_names) if ensemble.rf_model else 0
            }
        },
        "ensemble": {
            "method": ensemble.method,
            "weights": ensemble.weights
        }
    }
