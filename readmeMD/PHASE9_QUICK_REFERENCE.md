# Phase 9 Quick Reference Guide

**Quick access to Phase 9 AI Service features**

---

## 🚀 Quick Test

```bash
# Test Phase 9 system
./test_phase9.sh

# Get Phase 9 health status
curl http://localhost:8008/api/v1/phase9/health | jq

# Get recommendations
curl -X POST http://localhost:8008/api/v1/phase9/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "k": 5}' | jq
```

---

## 📊 Phase 9 Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/phase9/health` | GET | Check system health |
| `/api/v1/phase9/stats` | GET | Get system statistics |
| `/api/v1/phase9/recommend` | POST | Get multi-model recommendations |
| `/api/v1/phase9/compare` | POST | Compare model predictions |

---

## 🎯 Key Features

### 3 ML Models
- **LSTM**: Sequential pattern recognition
- **Collaborative Filtering**: User-item similarity (500 users × 100 items × 50 factors)
- **Random Forest**: Feature-based prediction (100 trees, 25 features)

### 5 Datasets (33,231 records)
- `user_behavior.csv` - 14,231 user actions
- `product_features.csv` - 100 products
- `product_interactions.csv` - 15,000 interactions
- `user_ratings.csv` - 3,000 ratings
- `category_trends.csv` - 900 trend records

### Ensemble System
- **Method**: Weighted averaging
- **Weights**: LSTM=0.40, CF=0.35, RF=0.25
- **Confidence**: Based on model agreement

---

## 📝 Example Requests

### 1. Get Recommendations
```bash
curl -X POST http://localhost:8008/api/v1/phase9/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "k": 10,
    "weights": {
      "lstm": 0.40,
      "cf": 0.35,
      "rf": 0.25
    },
    "filter_available": true
  }'
```

### 2. Compare Models
```bash
curl -X POST http://localhost:8008/api/v1/phase9/compare \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "product_id": 10
  }'
```

### 3. Health Check
```bash
curl http://localhost:8008/api/v1/phase9/health
```

---

## 🔧 Model Training

### Train Individual Models
```bash
# Collaborative Filtering
docker exec ai-service python3 train_cf.py

# Random Forest
docker exec ai-service python3 train_rf.py

# Ensemble
docker exec ai-service python3 train_ensemble.py
```

### Generate New Data
```bash
docker exec ai-service python3 generate_data.py
```

---

## 📂 Important Files

### Documentation
- `services/ai-service/README_PHASE9.md` - Full Phase 9 guide
- `services/ai-service/PHASE9_QUICK_START.md` - Quick start guide
- `services/ai-service/PHASE9_TEST_RESULTS.md` - Test results
- `kiro_md/PHASE9_COMPLETION_SUMMARY.md` - Implementation summary

### Code
- `services/ai-service/routers/phase9_recommend.py` - API endpoints
- `services/ai-service/src/cf_model.py` - Collaborative Filtering
- `services/ai-service/src/rf_model.py` - Random Forest
- `services/ai-service/src/ensemble.py` - Ensemble system

### Models
- `services/ai-service/models/cf_model.pkl` - Trained CF model
- `services/ai-service/models/rf_model.pkl` - Trained RF model
- `services/ai-service/models/ensemble_weights.pkl` - Ensemble config

### Data
- `services/ai-service/data/*.csv` - 5 training datasets

---

## ✅ Verification Checklist

- [x] All 3 models trained successfully
- [x] All 5 datasets generated (33,231 records)
- [x] All Phase 9 endpoints working
- [x] All existing endpoints still working (backward compatible)
- [x] All Docker containers healthy (8 services)
- [x] Comprehensive tests passing (7/7)
- [x] Documentation complete

---

## 🔄 Backward Compatibility

**Original AI endpoints remain unchanged:**
- `/api/v1/recommend` - LSTM+Graph+RAG hybrid
- `/api/v1/chatbot` - Chatbot system
- `/api/v1/smart_recommend` - Smart recommendations
- `/api/v1/health` - System health

**Phase 9 is completely isolated** - uses separate namespace `/phase9/`

---

## 📊 Test Results Summary

```
✅ PASSED: 7/7 tests
   ✅ Phase 9 Health Check
   ✅ Phase 9 Recommendations
   ✅ Phase 9 Model Comparison
   ✅ Existing: Health Check
   ✅ Existing: User-based Recommendations
   ✅ Existing: Query-based Recommendations
   ✅ Existing: Similar Products

🎉 ALL TESTS PASSED!
✅ Phase 9 system is operational
✅ Backward compatibility verified
✅ No breaking changes detected
```

---

## 🌐 API Documentation

**Interactive Swagger UI**: http://localhost:8008/docs

Look for the **"Phase 9 - Multi-Model"** section in the Swagger UI.

---

## 🎓 Quick Stats

| Metric | Value |
|--------|-------|
| **Models Trained** | 3 (LSTM, CF, RF) |
| **Datasets** | 5 files, 33,231 records |
| **New Endpoints** | 4 Phase 9 endpoints |
| **Test Coverage** | 7/7 tests passed |
| **Breaking Changes** | 0 |
| **Deployment Status** | ✅ Production Ready |

---

**Last Updated**: June 9, 2026  
**Status**: ✅ Complete and Operational
