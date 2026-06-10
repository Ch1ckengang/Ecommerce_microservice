# 🚀 PHASE 9 QUICK START GUIDE

## Tổng Quan
Phase 9 nâng cấp AI service với:
- **3 mô hình ML:** LSTM + Collaborative Filtering + Random Forest
- **5 tệp dữ liệu:** user_behavior, product_features, user_ratings, product_interactions, category_trends
- **Ensemble system:** Kết hợp predictions từ 3 mô hình

---

## ⚡ QUICK START (5 Bước)

### Bước 1: Generate Data (5 phút)
```bash
cd services/ai-service
python src/data_generator.py
```

**Output:**
```
✅ product_features.csv     (100 products)
✅ user_behavior.csv        (10,000+ records)
✅ user_ratings.csv         (3,000 ratings)
✅ product_interactions.csv (15,000 interactions)
✅ category_trends.csv      (900 trend records)
```

### Bước 2: Train Collaborative Filtering (2 phút)
```bash
python train_cf.py
```

**Output:**
```
💾 models/cf_model.pkl
📊 User-Item matrix: 500 users x 100 products
```

### Bước 3: Train Random Forest (3 phút)
```bash
python train_rf.py
```

**Output:**
```
💾 models/rf_model.pkl
📊 Features: 26
📊 Accuracy: ~85%
```

### Bước 4: Retrain LSTM với Enhanced Features (5 phút)
```bash
python train_lstm.py --enhanced
```

**Output:**
```
💾 models/lstm_model_enhanced.pth
📊 Validation Loss: < 0.3
```

### Bước 5: Train Ensemble (1 phút)
```bash
python train_ensemble.py
```

**Output:**
```
💾 models/ensemble_weights.pkl
📊 Optimal weights: LSTM=0.40, CF=0.35, RF=0.25
```

---

## 📊 KIỂM TRA KẾT QUẢ

### Test Individual Models
```python
python << EOF
from src.cf_model import CollaborativeFiltering
from src.rf_model import RandomForestRecommender

# Test CF
cf = CollaborativeFiltering.load('models/cf_model.pkl')
recs = cf.recommend(user_id=1, k=5)
print("CF Recommendations:", recs)

# Test RF
rf = RandomForestRecommender.load('models/rf_model.pkl')
print("RF Model loaded successfully")
EOF
```

### Test Ensemble
```python
python << EOF
from src.ensemble import EnsembleRecommender
from src.cf_model import CollaborativeFiltering
from src.rf_model import RandomForestRecommender

# Load models
cf = CollaborativeFiltering.load('models/cf_model.pkl')
rf = RandomForestRecommender.load('models/rf_model.pkl')

# Create ensemble
ensemble = EnsembleRecommender(method='weighted')
ensemble.set_models(None, cf, rf)

# Get comparison
comparison = ensemble.get_model_comparison(
    user_id=1,
    product_id=10,
    product_features={'price': 1000000, 'rating': 4.5, 'category': 'Electronics'}
)
print(comparison)
EOF
```

---

## 🔌 API ENDPOINTS MỚI

### 1. Multi-Model Recommendation
```bash
curl -X POST http://localhost:8008/api/v1/recommend/multi-model \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "k": 10,
    "model": "ensemble"
  }'
```

**Response:**
```json
{
  "recommendations": [
    {
      "product_id": 101,
      "score": 0.92,
      "model_scores": {
        "lstm": 0.95,
        "cf": 0.88,
        "rf": 0.93
      },
      "confidence": 0.91
    }
  ]
}
```

### 2. Model Comparison
```bash
curl "http://localhost:8008/api/v1/compare-models?user_id=1&product_id=101"
```

**Response:**
```json
{
  "lstm_score": 0.85,
  "cf_score": 0.78,
  "rf_score": 0.82,
  "ensemble_score": 0.83,
  "confidence": 0.88,
  "recommendation": "high"
}
```

### 3. CF Similar Items
```bash
curl "http://localhost:8008/api/v1/cf/similar-items?product_id=101&k=5"
```

### 4. CF Similar Users
```bash
curl "http://localhost:8008/api/v1/cf/similar-users?user_id=1&k=5"
```

---

## 📁 CẤU TRÚC FILES

```
services/ai-service/
├── data/
│   ├── product_features.csv       ← Generated
│   ├── user_behavior.csv          ← Generated
│   ├── user_ratings.csv           ← Generated
│   ├── product_interactions.csv   ← Generated
│   └── category_trends.csv        ← Generated
│
├── models/
│   ├── lstm_model.pth             ← Existing
│   ├── cf_model.pkl               ← New
│   ├── rf_model.pkl               ← New
│   └── ensemble_weights.pkl       ← New
│
├── src/
│   ├── lstm_model.py              ← Existing
│   ├── cf_model.py                ← New
│   ├── rf_model.py                ← New
│   ├── ensemble.py                ← New
│   └── data_generator.py          ← New
│
├── train_cf.py                    ← New
├── train_rf.py                    ← New
├── train_ensemble.py              ← New
└── README_PHASE9.md               ← New
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] 5 CSV files created in `data/`
- [ ] `cf_model.pkl` trained and saved
- [ ] `rf_model.pkl` trained and saved
- [ ] `ensemble_weights.pkl` saved
- [ ] API endpoints responding
- [ ] Model comparison returning scores
- [ ] Recommendations quality is good

---

## 🎯 EXPECTED PERFORMANCE

| Model | Precision@10 | Recall@10 | NDCG@10 |
|-------|--------------|-----------|---------|
| LSTM | 0.35 | 0.42 | 0.68 |
| CF | 0.38 | 0.45 | 0.71 |
| RF | 0.33 | 0.40 | 0.65 |
| **Ensemble** | **0.42** | **0.50** | **0.75** |

---

## 🐛 TROUBLESHOOTING

### Error: "No module named 'sklearn'"
```bash
pip install scikit-learn
```

### Error: "No module named 'scipy'"
```bash
pip install scipy
```

### Memory Error during training
```bash
# Reduce dataset size in data_generator.py
self.num_interactions = 5000  # Instead of 10000
```

### CF Model prediction error
```bash
# Check if user/product exists in training data
# Cold start: model returns popular items
```

---

## 📚 NEXT STEPS

1. ✅ Integrate with existing AI service
2. ✅ Update API endpoints
3. ✅ Add tests for new models
4. ✅ Update documentation
5. ⏳ A/B testing với existing LSTM
6. ⏳ Monitor performance metrics
7. ⏳ Optimize ensemble weights với real data

---

**Status:** READY TO IMPLEMENT  
**Estimated Time:** 20-30 minutes (all steps)  
**Dependencies:** scipy, scikit-learn, pandas, numpy
