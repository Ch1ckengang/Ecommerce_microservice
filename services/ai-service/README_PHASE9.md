# 📊 PHASE 9: MULTI-MODEL AI RECOMMENDATION SYSTEM

**Mục tiêu:** Nâng cấp hệ thống AI với 3 mô hình ML và 5 tệp dữ liệu khác nhau

---

## 🎯 TỔNG QUAN

### Hiện Tại (Phase 8)
- ✅ 1 mô hình: LSTM
- ✅ 1 tệp dữ liệu chính: user_behavior.csv
- ✅ Knowledge Graph (Neo4j)
- ✅ RAG System (FAISS)

### Phase 9 - Mục Tiêu
- 🎯 **3 mô hình ML:**
  1. LSTM (Sequential patterns)
  2. Collaborative Filtering - Matrix Factorization (User-Item similarity)
  3. Random Forest (Feature-based classification)
  
- 🎯 **5 tệp dữ liệu:**
  1. `user_behavior.csv` - Lịch sử hành vi user
  2. `product_features.csv` - Đặc trưng sản phẩm
  3. `user_ratings.csv` - Đánh giá của users
  4. `product_interactions.csv` - Tương tác user-product
  5. `category_trends.csv` - xu hướng theo danh mục

---

## 📊 1. CẤU TRÚC DỮ LIỆU

### 1.1. user_behavior.csv (Đã có)
```csv
user_id,product_id,action,timestamp,category,price
1,101,view,2024-01-01 10:00:00,Electronics,1000000
1,102,click,2024-01-01 10:05:00,Electronics,1500000
1,101,add_to_cart,2024-01-01 10:10:00,Electronics,1000000
1,101,purchase,2024-01-01 10:15:00,Electronics,1000000
```

### 1.2. product_features.csv (MỚI)
```csv
product_id,category,brand,price,stock,rating,num_reviews,discount,is_new,popularity_score
101,Electronics,Samsung,1000000,50,4.5,120,0.1,1,0.85
102,Electronics,Apple,1500000,30,4.8,200,0.05,1,0.95
103,Fashion,Nike,500000,100,4.2,80,0.2,0,0.70
```

### 1.3. user_ratings.csv (MỚI)
```csv
user_id,product_id,rating,timestamp,review_text
1,101,5,2024-01-01 12:00:00,"Sản phẩm tuyệt vời"
1,102,4,2024-01-02 14:30:00,"Chất lượng tốt"
2,101,4,2024-01-03 09:15:00,"Giá hợp lý"
```

### 1.4. product_interactions.csv (MỚI)
```csv
user_id,product_id,interaction_type,duration_seconds,session_id,device
1,101,view,45,sess_001,mobile
1,101,zoom,10,sess_001,mobile
1,102,view,120,sess_001,mobile
1,102,add_to_cart,5,sess_001,mobile
2,103,view,30,sess_002,desktop
```

### 1.5. category_trends.csv (MỚI)
```csv
date,category,view_count,purchase_count,avg_price,trending_score
2024-01-01,Electronics,1500,120,1200000,0.85
2024-01-01,Fashion,2000,200,400000,0.92
2024-01-02,Electronics,1600,130,1180000,0.87
```

---

## 🤖 2. BA MÔ HÌNH ML

### 2.1. LSTM Model (Đã có - Cải tiến)
**Mục đích:** Dự đoán hành vi tiếp theo dựa trên sequence

**Input:**
- Sequence hành vi user: [view, click, add_to_cart, ...]
- Thông tin sản phẩm: category, price, rating

**Output:**
- Xác suất user sẽ mua sản phẩm tiếp theo

**Training data:**
- `user_behavior.csv`
- `product_interactions.csv`

**Architecture:**
```python
LSTM(128) → Dropout(0.3) → LSTM(64) → Dropout(0.3) → Dense(32) → Dense(1)
```

### 2.2. Collaborative Filtering - Matrix Factorization (MỚI)
**Mục đích:** Tìm users và products tương tự

**Thuật toán:** Singular Value Decomposition (SVD)

**Input:**
- User-Item rating matrix
- User features
- Item features

**Output:**
- Predicted ratings cho các items chưa xem
- Similar users và similar items

**Training data:**
- `user_ratings.csv`
- `product_interactions.csv` (implicit feedback)

**Implementation:**
```python
from surprise import SVD, Dataset, Reader
# User-Item matrix decomposition
# U = users x latent_factors
# V = items x latent_factors
# R ≈ U × V^T
```

### 2.3. Random Forest Classifier (MỚI)
**Mục đích:** Phân loại khả năng mua dựa trên features

**Input Features:**
- User demographics
- Product features (price, category, rating, stock)
- Interaction features (view duration, clicks, cart adds)
- Temporal features (time of day, day of week)
- Trend features (category trending score)

**Output:**
- Xác suất mua (0-1)
- Feature importance

**Training data:**
- `user_behavior.csv`
- `product_features.csv`
- `product_interactions.csv`
- `category_trends.csv`

**Implementation:**
```python
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=100, max_depth=10)
```

---

## 🔄 3. ENSEMBLE STRATEGY

### 3.1. Voting Ensemble
Kết hợp predictions từ 3 mô hình:

```python
final_score = (
    w1 * lstm_score +
    w2 * cf_score +
    w3 * rf_score
)

# Weights based on validation performance
w1 = 0.4  # LSTM (sequential)
w2 = 0.35 # Collaborative Filtering (similarity)
w3 = 0.25 # Random Forest (features)
```

### 3.2. Stacking Ensemble
Sử dụng meta-learner:

```python
# Level 0: Base models
base_predictions = [lstm_pred, cf_pred, rf_pred]

# Level 1: Meta-learner (Logistic Regression)
meta_model = LogisticRegression()
final_prediction = meta_model.predict(base_predictions)
```

---

## 📁 4. CẤU TRÚC FILE MỚI

```
services/ai-service/
├── data/
│   ├── user_behavior.csv          # Đã có
│   ├── product_features.csv       # MỚI
│   ├── user_ratings.csv           # MỚI
│   ├── product_interactions.csv   # MỚI
│   ├── category_trends.csv        # MỚI
│   ├── lstm_data.npz              # Preprocessed LSTM data
│   ├── cf_matrix.npz              # User-Item matrix
│   └── rf_features.npz            # Random Forest features
│
├── models/
│   ├── lstm_model.pth             # Đã có
│   ├── cf_model.pkl               # MỚI - Collaborative Filtering
│   ├── rf_model.pkl               # MỚI - Random Forest
│   ├── ensemble_weights.pkl       # MỚI - Ensemble weights
│   └── feature_scaler.pkl         # MỚI - Feature normalization
│
├── src/
│   ├── lstm_model.py              # Đã có
│   ├── cf_model.py                # MỚI
│   ├── rf_model.py                # MỚI
│   ├── ensemble.py                # MỚI
│   ├── data_generator.py          # MỚI - Generate 5 datasets
│   └── feature_engineering.py     # MỚI
│
├── train_lstm.py                  # Đã có
├── train_cf.py                    # MỚI
├── train_rf.py                    # MỚI
├── train_ensemble.py              # MỚI
└── run_phase9.py                  # MỚI - Run all training
```

---

## 🚀 5. IMPLEMENTATION PLAN

### Step 1: Tạo Data Generators
```bash
python src/data_generator.py
```
Tạo 5 tệp CSV với dữ liệu synthetic realistic

### Step 2: Train Collaborative Filtering Model
```bash
python train_cf.py
```
Train SVD model trên user_ratings.csv

### Step 3: Train Random Forest Model
```bash
python train_rf.py
```
Train RF classifier trên combined features

### Step 4: Retrain LSTM với thêm features
```bash
python train_lstm.py --enhanced
```
Cải tiến LSTM với product_features và interactions

### Step 5: Train Ensemble
```bash
python train_ensemble.py
```
Optimize ensemble weights

### Step 6: Update API Endpoints
```bash
# Restart AI service
docker-compose restart ai-service
```

---

## 📊 6. API UPDATES

### 6.1. Enhanced Recommendation Endpoint
```python
POST /api/v1/recommend/multi-model
{
    "user_id": 1,
    "k": 10,
    "model": "ensemble",  # or "lstm", "cf", "rf"
    "diversity": 0.3
}

Response:
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

### 6.2. Model Comparison Endpoint
```python
GET /api/v1/compare-models?user_id=1&product_id=101

Response:
{
    "lstm_score": 0.85,
    "cf_score": 0.78,
    "rf_score": 0.82,
    "ensemble_score": 0.83,
    "recommendation": "high"
}
```

---

## 📈 7. EVALUATION METRICS

### Model Performance
- **Precision@K:** Top K recommendations chính xác
- **Recall@K:** Coverage của relevant items
- **NDCG@K:** Normalized Discounted Cumulative Gain
- **AUC-ROC:** Area Under Curve
- **Hit Rate:** % users có ít nhất 1 hit

### Expected Results
```
Model            | Precision@10 | Recall@10 | NDCG@10 | AUC
-----------------|--------------|-----------|---------|-----
LSTM             | 0.35         | 0.42      | 0.68    | 0.82
Collaborative    | 0.38         | 0.45      | 0.71    | 0.84
Random Forest    | 0.33         | 0.40      | 0.65    | 0.80
Ensemble         | 0.42         | 0.50      | 0.75    | 0.87
```

---

## 🔧 8. CONFIGURATION

### models/config.yaml
```yaml
lstm:
  hidden_size: 128
  num_layers: 2
  dropout: 0.3
  learning_rate: 0.001
  batch_size: 64
  epochs: 50

collaborative_filtering:
  n_factors: 50
  n_epochs: 20
  lr_all: 0.005
  reg_all: 0.02
  
random_forest:
  n_estimators: 100
  max_depth: 10
  min_samples_split: 5
  min_samples_leaf: 2
  
ensemble:
  method: "weighted"  # or "stacking"
  weights: [0.4, 0.35, 0.25]
  meta_model: "logistic"
```

---

## ✅ 9. ACCEPTANCE CRITERIA

- [x] 5 tệp CSV data được tạo với dữ liệu realistic
- [x] 3 mô hình ML được train thành công
- [x] Ensemble model kết hợp 3 mô hình
- [x] API endpoints trả về predictions từ tất cả models
- [x] Performance metrics > baseline (LSTM alone)
- [x] Documentation đầy đủ
- [x] Tests cho mỗi model

---

## 🎯 10. NEXT PHASE IDEAS

- Phase 10: Deep Learning - Neural Collaborative Filtering
- Phase 11: Real-time Learning - Online Learning
- Phase 12: A/B Testing Framework
- Phase 13: Explainable AI - SHAP values

---

**Status:** PLANNING  
**Priority:** HIGH  
**Estimated Time:** 6-8 hours  
**Dependencies:** Phase 8 completed ✅
