# AI SERVICE IMPLEMENTATION PLAN
**Hệ thống AI gợi ý sản phẩm và Chatbot tư vấn cho E-Commerce**

> **Updated:** 2026-06-02  
> **Status:** Planning Phase  
> **Docker-based Deployment**

---

## 📋 TỔNG QUAN

### Mục tiêu
Xây dựng AI Service hoàn chỉnh với:
- ✅ **Recommendation Engine**: Gợi ý sản phẩm dựa trên hành vi người dùng
- ✅ **Chatbot**: Tư vấn sản phẩm thông minh
- ✅ **Semantic Search**: Tìm kiếm ngữ nghĩa
- ✅ **Knowledge Graph**: Quan hệ sản phẩm-người dùng

### Kế hoạch Training Model
**3 Models sẽ được train và so sánh:**
1. **RNN** (Recurrent Neural Network) - Baseline
2. **LSTM** (Long Short-Term Memory) - Standard
3. **BiLSTM** (Bidirectional LSTM) - Advanced

**3 Datasets sẽ được tạo và test:**
1. **Dataset Original** (36k behaviors) - Dữ liệu thực tế
2. **Dataset Balanced** (40k behaviors) - Cân bằng distribution
3. **Dataset Extended** (100k+ behaviors) - Scale test

**Total Experiments:** 3 models × 3 datasets = **9 training runs**

### Deployment Architecture
```
Docker Environment:
├── ai-service          (Port 8007) - FastAPI
├── neo4j               (Port 7474, 7687) - Knowledge Graph
├── redis               (Port 6379) - Cache
├── product-service     (Port 8002) - Product API
├── user-service        (Port 8001) - User API
└── postgresql/mysql    - Databases
```

### Output cuối cùng
- ✅ Model tối ưu nhất (accuracy, inference time, memory)
- ✅ Docker Compose configuration
- ✅ API endpoints hoàn chỉnh
- ✅ Documentation đầy đủ
- ✅ Deployment guide

---

## ✅ PROGRESS CHECKLIST

### 📊 Data Preparation
- [ ] Dataset 1: Original (36k) - Already exists
- [ ] Dataset 2: Balanced (40k) 
- [ ] Dataset 3: Extended (100k+)
- [ ] Data preprocessing pipeline
- [ ] Train/Val/Test splits ready

### 🧠 Model Training (9 experiments total)
- [ ] RNN + Dataset Original
- [ ] RNN + Dataset Balanced  
- [ ] RNN + Dataset Extended
- [ ] LSTM + Dataset Original
- [ ] LSTM + Dataset Balanced
- [ ] LSTM + Dataset Extended
- [ ] BiLSTM + Dataset Original
- [ ] BiLSTM + Dataset Balanced
- [ ] BiLSTM + Dataset Extended

### 📈 Model Evaluation
- [ ] Performance comparison report
- [ ] Best model selection
- [ ] Model optimization
- [ ] Export production weights

### 🐳 Docker Setup
- [ ] Dockerfile for AI Service
- [ ] Docker Compose configuration
- [ ] Neo4j container setup
- [ ] Redis container setup
- [ ] Network configuration
- [ ] Volume persistence

### 🔌 API Implementation
- [ ] FastAPI app structure
- [ ] /api/ai/health endpoint
- [ ] /api/ai/recommend endpoint
- [ ] /api/ai/recommend/trending endpoint
- [ ] /api/ai/chat endpoint
- [ ] /api/ai/search endpoint
- [ ] /api/ai/behavior endpoint
- [ ] JWT authentication middleware
- [ ] Request logging

### 🕸️ Knowledge Graph
- [ ] Neo4j schema design
- [ ] Import data to Neo4j
- [ ] Product similarity computation
- [ ] Graph query optimization
- [ ] Neo4j Python client

### 🔍 Vector Search
- [ ] Product embeddings generation
- [ ] FAISS index building
- [ ] Semantic search API
- [ ] Embedding service wrapper

### 🤖 Services Implementation
- [ ] Recommendation Service (Hybrid)
- [ ] Chatbot Service (RAG)
- [ ] Search Service
- [ ] Behavior Logging Service
- [ ] Model Loader Service
- [ ] Cache Service

### 🧪 Testing
- [ ] Unit tests (models)
- [ ] Unit tests (services)
- [ ] API integration tests
- [ ] Load testing
- [ ] End-to-end tests

### 📚 Documentation
- [ ] API documentation (OpenAPI)
- [ ] Model training guide
- [ ] Deployment guide
- [ ] User manual
- [ ] Troubleshooting guide

---

## 🎯 PHASE 1: FOUNDATION & DATA PREPARATION (Tuần 1)

### 1.1. Cấu trúc Project
```
ai-service/
├── main.py                    # FastAPI app
├── requirements.txt           # Dependencies
├── config.py                  # Configuration
├── .env                       # Environment variables
│
├── models/                    # AI Models
│   ├── __init__.py
│   ├── rnn_model.py          # RNN implementation
│   ├── lstm_model.py         # LSTM implementation
│   ├── bilstm_model.py       # BiLSTM implementation
│   ├── model_loader.py       # Load trained models
│   └── embeddings.py         # Text embeddings
│
├── data/                      # Data & Datasets
│   ├── raw/
│   │   ├── data36k.csv          # Dataset 1: Original (36k)
│   │   ├── dataset_balanced.csv # Dataset 2: Balanced (40k)
│   │   └── dataset_extended.csv # Dataset 3: Extended (100k+)
│   ├── processed/               # Preprocessed data
│   │   ├── dataset1_train.npz
│   │   ├── dataset1_val.npz
│   │   ├── dataset1_test.npz
│   │   └── ...
│   ├── embeddings/              # Product embeddings
│   │   ├── products_index.faiss
│   │   └── products_meta.pkl
│   └── generators/
│       ├── balance_generator.py
│       └── extend_generator.py
│
├── training/                  # Training scripts
│   ├── train_rnn.py
│   ├── train_lstm.py
│   ├── train_bilstm.py
│   ├── compare_models.py     # Benchmark & compare
│   └── utils.py              # Training utilities
│
├── weights/                   # Trained model weights
│   ├── rnn/
│   │   ├── original_best.weights.h5
│   │   ├── balanced_best.weights.h5
│   │   └── extended_best.weights.h5
│   ├── lstm/
│   │   ├── original_best.weights.h5
│   │   ├── balanced_best.weights.h5
│   │   └── extended_best.weights.h5
│   └── bilstm/
│       ├── original_best.weights.h5
│       ├── balanced_best.weights.h5
│       └── extended_best.weights.h5
│
├── services/                  # Business logic
│   ├── __init__.py
│   ├── recommendation_service.py
│   ├── chatbot_service.py
│   ├── search_service.py
│   └── behavior_service.py
│
├── api/                       # API endpoints
│   ├── __init__.py
│   ├── recommendation.py
│   ├── chatbot.py
│   ├── search.py
│   └── health.py
│
├── middleware/                # Middleware
│   ├── __init__.py
│   ├── auth.py               # JWT validation
│   └── logging.py            # Request logging
│
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── http_client.py        # Call other services
│   ├── cache.py              # Redis cache
│   ├── preprocessor.py       # Data preprocessing
│   └── metrics.py            # Evaluation metrics
│
├── graph/                     # Knowledge Graph
│   ├── __init__.py
│   ├── neo4j_client.py
│   └── queries.py
│
├── notebooks/                 # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_rnn.ipynb
│   ├── 03_model_lstm.ipynb
│   ├── 04_model_bilstm.ipynb
│   └── 05_model_comparison.ipynb
│
├── docker/                    # Docker configurations
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   └── entrypoint.sh
│
└── tests/                     # Tests
    ├── test_models.py
    ├── test_api.py
    └── test_services.py
```

---

## 🐳 DOCKER CONFIGURATION

### Deployment với Docker Compose hiện tại

AI Service đã được tích hợp vào `docker-compose.yml` chính với config sau:

**File:** `tieuluan1/docker-compose.yml` (đã có trong project)

```yaml
# AI Service configuration (đã được thêm vào)
ai-service:
  build: ./services/ai-service
  container_name: ai-service
  ports:
    - "8007:8007"
  env_file: .env
  environment:
    - NEO4J_URI=bolt://neo4j:7687
    - NEO4J_USER=neo4j
    - NEO4J_PASSWORD=dkstore123
    - REDIS_URL=redis://redis:6379
    - PRODUCT_SERVICE_URL=http://product-service:8002
    - USER_SERVICE_URL=http://user-service:8001
    - ORDER_SERVICE_URL=http://order-service:8004
  volumes:
    - ./services/ai-service/weights:/app/weights:ro
    - ./services/ai-service/data/embeddings:/app/data/embeddings:ro
    - ./services/ai-service/logs:/app/logs
  depends_on:
    neo4j:
      condition: service_healthy
    redis:
      condition: service_healthy
    product-service:
      condition: service_started
    user-service:
      condition: service_started
  extra_hosts:
    - "host.docker.internal:host-gateway"
  restart: unless-stopped
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:8007/api/ai/health || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s

# Neo4j - Knowledge Graph
neo4j:
  image: neo4j:5.18
  container_name: neo4j
  ports:
    - "7474:7474"   # Neo4j Browser (HTTP)
    - "7687:7687"   # Bolt protocol
  environment:
    - NEO4J_AUTH=neo4j/dkstore123
    - NEO4J_PLUGINS=["apoc"]
    - NEO4J_dbms_security_procedures_unrestricted=apoc.*
    - NEO4J_server_memory_heap_initial__size=512m
    - NEO4J_server_memory_heap_max__size=2G
    - NEO4J_server_memory_pagecache_size=1G
  volumes:
    - neo4j_data:/data
    - neo4j_logs:/logs
    - neo4j_import:/var/lib/neo4j/import
  restart: unless-stopped
  healthcheck:
    test: ["CMD-SHELL", "cypher-shell -u neo4j -p dkstore123 'RETURN 1' || exit 1"]
    interval: 10s
    timeout: 10s
    retries: 5
    start_period: 30s

# Redis - Cache for AI Service
redis:
  image: redis:7-alpine
  container_name: redis
  ports:
    - "6379:6379"
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru --appendonly yes
  volumes:
    - redis_data:/data
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 3
    start_period: 10s

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:
  redis_data:
```

**Lưu ý:**
- AI Service kết nối với các services khác qua Docker network
- Volume mounts cho weights, embeddings và logs
- Health checks đảm bảo dependencies ready trước khi start
- Redis có persistence với AOF enabled


### Dockerfile for AI Service

**File:** `services/ai-service/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data/embeddings weights

# Expose port
EXPOSE 8007

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8007/api/ai/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007"]
```

### .dockerignore

**File:** `services/ai-service/.dockerignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/

# Data (large files - mount as volumes instead)
data/raw/*.csv
weights/*.h5
weights/*.weights.h5
data/embeddings/*.faiss
data/embeddings/*.pkl

# Jupyter
.ipynb_checkpoints/
*.ipynb

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Tests
.pytest_cache/
.coverage
htmlcov/

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# Training outputs
results/
training_logs/
```
```


### 1.2. Setup Dependencies

**requirements.txt**
```txt
# FastAPI & Server
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.18
pydantic==2.10.0
pydantic-settings==2.6.0

# Machine Learning
tensorflow==2.18.0
# hoặc: torch==2.5.0 torchvision torchaudio
scikit-learn==1.6.0
numpy==2.0.2
pandas==2.2.3

# NLP & Embeddings
sentence-transformers==3.3.1
transformers==4.47.0

# Vector DB & Graph
faiss-cpu==1.9.0.post1
# hoặc: chromadb==0.5.23
neo4j==5.27.0

# Cache & Storage
redis==5.2.0
hiredis==3.0.0

# HTTP Client
httpx==0.28.0
aiohttp==3.11.9

# JWT & Auth
python-jose[cryptography]==3.3.0
pyjwt==2.10.1

# Utils
python-dotenv==1.0.1
python-json-logger==3.2.1
tqdm==4.67.1

# Testing & Development
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
black==24.10.0
flake8==7.1.1

# Monitoring
prometheus-client==0.21.0
```

### 1.3. Data Generation Scripts

#### ✅ **Task 1.3.1: Dataset 1 - Original (Đã có)**
- File: `data36k.csv` (36,000 behaviors)
- Status: ✅ Ready

#### 📝 **Task 1.3.2: Dataset 2 - Balanced Data**
**Mục đích:** Cân bằng distribution của các actions để model học tốt hơn

**Script:** `data/generators/balance_generator.py`
```python
"""
Balanced Dataset Generator

Điều chỉnh distribution:
- view: 30%           (thay vì 50%+ trong original)
- add_to_cart: 25%    (thay vì 20%)
- purchase: 20%       (thay vì 5%)
- wishlist: 10%
- remove_from_cart: 8%
- search_click: 5%
- share: 1%
- review: 1%

Output: dataset_balanced.csv (40k records)
"""
```

#### 📝 **Task 1.3.3: Dataset 3 - Extended Data**
**Mục đích:** Scale up để test performance với large-scale data

**Script:** `data/generators/extend_generator.py`
```python
"""
Extended Dataset Generator

Mở rộng:
- 1000 users (thay vì 500)
- 200 products (thay vì 100)
- 100k-150k behaviors
- Longer sequences (15-20 actions/user)
- Realistic temporal patterns
- Seasonal trends

Output: dataset_extended.csv (100k+ records)
"""
```

### 1.4. Data Preprocessing Pipeline

**Script:** `utils/preprocessor.py`
```python
class BehaviorDataPreprocessor:
    """
    - Load CSV
    - Clean data (remove nulls, duplicates)
    - Encode actions → integers
    - Encode product_ids → integers
    - Normalize price, stock
    - Create sequences (sliding window)
    - Train/val/test split (70/15/15)
    """
```

**Output format:**
```python
X_train: (N, SEQ_LEN, NUM_FEATURES)  # e.g., (20000, 10, 5)
y_train: (N,)                         # product_id encoded
```

---

## 🧠 PHASE 2: MODEL DEVELOPMENT (Tuần 2-3)

### 2.1. Model Architecture Design

#### 📝 **Model 1: RNN (Vanilla Recurrent Neural Network)**

**File:** `models/rnn_model.py`

```python
import tensorflow as tf
from tensorflow.keras import layers, Model

class RNNRecommendationModel(Model):
    """
    Simple RNN for baseline comparison
    
    Architecture:
    - Embedding layer (product_id → vector)
    - SimpleRNN layer (64 units)
    - Dropout (0.3)
    - Dense output (NUM_PRODUCTS, softmax)
    """
    
    def __init__(self, num_products, embedding_dim=50, rnn_units=64):
        super().__init__()
        self.embedding = layers.Embedding(num_products+1, embedding_dim)
        self.rnn = layers.SimpleRNN(rnn_units, return_sequences=False)
        self.dropout = layers.Dropout(0.3)
        self.dense = layers.Dense(num_products, activation='softmax')
    
    def call(self, inputs, training=False):
        x = self.embedding(inputs)
        x = self.rnn(x)
        x = self.dropout(x, training=training)
        return self.dense(x)
```

**Ưu điểm:**
- Đơn giản, nhanh
- Baseline để so sánh

**Nhược điểm:**
- Vanishing gradient với sequences dài
- Khó học long-term dependencies


#### 📝 **Model 2: LSTM (Long Short-Term Memory)**

**File:** `models/lstm_model.py`

```python
class LSTMRecommendationModel(Model):
    """
    LSTM with 2 layers for better sequence learning
    
    Architecture:
    - Embedding layer (50d)
    - LSTM layer 1 (128 units, return_sequences=True)
    - Dropout (0.3)
    - LSTM layer 2 (64 units)
    - Dropout (0.3)
    - Dense output (NUM_PRODUCTS, softmax)
    """
    
    def __init__(self, num_products, embedding_dim=50):
        super().__init__()
        self.embedding = layers.Embedding(num_products+1, embedding_dim)
        self.lstm1 = layers.LSTM(128, return_sequences=True)
        self.dropout1 = layers.Dropout(0.3)
        self.lstm2 = layers.LSTM(64)
        self.dropout2 = layers.Dropout(0.3)
        self.dense = layers.Dense(num_products, activation='softmax')
    
    def call(self, inputs, training=False):
        x = self.embedding(inputs)
        x = self.lstm1(x)
        x = self.dropout1(x, training=training)
        x = self.lstm2(x)
        x = self.dropout2(x, training=training)
        return self.dense(x)
```

**Ưu điểm:**
- Học được long-term dependencies
- Giải quyết vanishing gradient
- Phù hợp cho sequence prediction

**Nhược điểm:**
- Chậm hơn RNN
- Nhiều parameters hơn

#### 📝 **Model 3: BiLSTM (Bidirectional LSTM)**

**File:** `models/bilstm_model.py`

```python
class BiLSTMRecommendationModel(Model):
    """
    Bidirectional LSTM - học cả forward & backward context
    
    Architecture:
    - Embedding layer (50d)
    - Bidirectional LSTM 1 (128 units each direction)
    - Dropout (0.3)
    - Bidirectional LSTM 2 (64 units each direction)
    - Dropout (0.3)
    - Dense output (NUM_PRODUCTS, softmax)
    """
    
    def __init__(self, num_products, embedding_dim=50):
        super().__init__()
        self.embedding = layers.Embedding(num_products+1, embedding_dim)
        self.bilstm1 = layers.Bidirectional(
            layers.LSTM(128, return_sequences=True)
        )
        self.dropout1 = layers.Dropout(0.3)
        self.bilstm2 = layers.Bidirectional(layers.LSTM(64))
        self.dropout2 = layers.Dropout(0.3)
        self.dense = layers.Dense(num_products, activation='softmax')
    
    def call(self, inputs, training=False):
        x = self.embedding(inputs)
        x = self.bilstm1(x)
        x = self.dropout1(x, training=training)
        x = self.bilstm2(x)
        x = self.dropout2(x, training=training)
        return self.dense(x)
```

**Ưu điểm:**
- Học được context từ cả 2 chiều
- Accuracy tốt nhất (typically)
- Hiểu được pattern phức tạp

**Nhược điểm:**
- Chậm nhất (2x parameters)
- Memory intensive
- Overkill cho simple sequences


### 2.2. Training Pipeline

#### 📝 **Training Script Template**

**File:** `training/train_rnn.py` (tương tự cho LSTM, BiLSTM)

```python
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, TensorBoard
)
from models.rnn_model import RNNRecommendationModel
from utils.preprocessor import BehaviorDataPreprocessor
from utils.metrics import evaluate_model

def train_on_dataset(dataset_name, model_type='rnn'):
    """
    Train model on specific dataset
    
    Args:
        dataset_name: 'original', 'balanced', 'extended'
        model_type: 'rnn', 'lstm', 'bilstm'
    """
    
    print(f"Training {model_type.upper()} on {dataset_name} dataset...")
    
    # 1. Load & preprocess data
    data_path = f"data/raw/dataset_{dataset_name}.csv"
    preprocessor = BehaviorDataPreprocessor(seq_len=10)
    X_train, y_train, X_val, y_val, X_test, y_test = \
        preprocessor.load_and_split(data_path)
    
    # 2. Initialize model
    num_products = preprocessor.num_products
    if model_type == 'rnn':
        model = RNNRecommendationModel(num_products)
    elif model_type == 'lstm':
        model = LSTMRecommendationModel(num_products)
    else:  # bilstm
        model = BiLSTMRecommendationModel(num_products)
    
    # 3. Compile
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy', 'top_k_categorical_accuracy']
    )
    
    # 4. Callbacks
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    weight_path = f"weights/{model_type}/{dataset_name}_best.weights.h5"
    
    callbacks = [
        ModelCheckpoint(
            weight_path, 
            monitor='val_loss',
            save_best_only=True,
            save_weights_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        ),
        TensorBoard(log_dir=f'logs/{model_type}/{dataset_name}_{timestamp}')
    ]
    
    # 5. Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=50,
        batch_size=256,
        callbacks=callbacks,
        verbose=1
    )
    
    # 6. Evaluate
    results = evaluate_model(model, X_test, y_test, preprocessor)
    
    # 7. Save results
    save_training_results(model_type, dataset_name, history, results)
    
    return model, results

def save_training_results(model_type, dataset_name, history, results):
    """Save training metrics to JSON"""
    output = {
        'model': model_type,
        'dataset': dataset_name,
        'timestamp': datetime.now().isoformat(),
        'final_metrics': results,
        'history': {
            'loss': [float(x) for x in history.history['loss']],
            'val_loss': [float(x) for x in history.history['val_loss']],
            'accuracy': [float(x) for x in history.history['accuracy']],
            'val_accuracy': [float(x) for x in history.history['val_accuracy']]
        }
    }
    
    os.makedirs(f'results/{model_type}', exist_ok=True)
    with open(f'results/{model_type}/{dataset_name}_results.json', 'w') as f:
        json.dump(output, f, indent=2)

if __name__ == '__main__':
    datasets = ['original', 'balanced', 'extended']
    for dataset in datasets:
        train_on_dataset(dataset, model_type='rnn')
```


### 2.3. Model Comparison & Benchmarking

#### 📝 **Comparison Script**

**File:** `training/compare_models.py`

```python
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

def load_all_results():
    """Load all training results from JSON files"""
    models = ['rnn', 'lstm', 'bilstm']
    datasets = ['original', 'balanced', 'extended']
    
    results = []
    for model in models:
        for dataset in datasets:
            try:
                with open(f'results/{model}/{dataset}_results.json') as f:
                    data = json.load(f)
                    results.append({
                        'Model': model.upper(),
                        'Dataset': dataset,
                        'Test Accuracy': data['final_metrics']['test_accuracy'],
                        'Top-5 Accuracy': data['final_metrics']['top5_accuracy'],
                        'Test Loss': data['final_metrics']['test_loss'],
                        'Inference Time (ms)': data['final_metrics']['inference_time_ms'],
                        'Model Size (MB)': data['final_metrics']['model_size_mb'],
                        'Training Time (min)': data['final_metrics']['training_time_min']
                    })
            except FileNotFoundError:
                continue
    
    return pd.DataFrame(results)

def generate_comparison_report():
    """Generate comprehensive comparison report"""
    df = load_all_results()
    
    # 1. Overall best model per metric
    print("=" * 80)
    print("BEST MODELS BY METRIC")
    print("=" * 80)
    
    metrics = ['Test Accuracy', 'Top-5 Accuracy', 'Inference Time (ms)']
    for metric in metrics:
        best = df.loc[df[metric].idxmax() if 'Time' not in metric else df[metric].idxmin()]
        print(f"\n{metric}:")
        print(f"  Model: {best['Model']} | Dataset: {best['Dataset']} | Value: {best[metric]:.4f}")
    
    # 2. Average performance by model
    print("\n" + "=" * 80)
    print("AVERAGE PERFORMANCE BY MODEL")
    print("=" * 80)
    avg_by_model = df.groupby('Model').mean()
    print(tabulate(avg_by_model, headers='keys', tablefmt='grid', floatfmt='.4f'))
    
    # 3. Best dataset per model
    print("\n" + "=" * 80)
    print("BEST DATASET PER MODEL")
    print("=" * 80)
    for model in df['Model'].unique():
        model_df = df[df['Model'] == model]
        best = model_df.loc[model_df['Test Accuracy'].idxmax()]
        print(f"\n{model}:")
        print(f"  Best Dataset: {best['Dataset']}")
        print(f"  Test Accuracy: {best['Test Accuracy']:.4f}")
        print(f"  Top-5 Accuracy: {best['Top-5 Accuracy']:.4f}")
    
    # 4. Recommendation
    print("\n" + "=" * 80)
    print("FINAL RECOMMENDATION")
    print("=" * 80)
    
    # Weighted score: 50% accuracy, 30% top5, 20% speed
    df['Score'] = (
        df['Test Accuracy'] * 0.5 + 
        df['Top-5 Accuracy'] * 0.3 - 
        (df['Inference Time (ms)'] / 1000) * 0.2
    )
    
    best_overall = df.loc[df['Score'].idxmax()]
    print(f"\n🏆 WINNER: {best_overall['Model']} on {best_overall['Dataset']} dataset")
    print(f"   Test Accuracy: {best_overall['Test Accuracy']:.4f}")
    print(f"   Top-5 Accuracy: {best_overall['Top-5 Accuracy']:.4f}")
    print(f"   Inference Time: {best_overall['Inference Time (ms)']:.2f} ms")
    print(f"   Model Size: {best_overall['Model Size (MB)']:.2f} MB")
    
    # 5. Save plots
    plot_comparison_charts(df)
    
    return df, best_overall

def plot_comparison_charts(df):
    """Generate visualization plots"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Accuracy comparison
    pivot = df.pivot(index='Dataset', columns='Model', values='Test Accuracy')
    pivot.plot(kind='bar', ax=axes[0, 0])
    axes[0, 0].set_title('Test Accuracy by Model & Dataset')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].legend(title='Model')
    
    # 2. Inference time comparison
    pivot = df.pivot(index='Dataset', columns='Model', values='Inference Time (ms)')
    pivot.plot(kind='bar', ax=axes[0, 1])
    axes[0, 1].set_title('Inference Time by Model & Dataset')
    axes[0, 1].set_ylabel('Time (ms)')
    
    # 3. Top-5 accuracy
    pivot = df.pivot(index='Dataset', columns='Model', values='Top-5 Accuracy')
    pivot.plot(kind='bar', ax=axes[1, 0])
    axes[1, 0].set_title('Top-5 Accuracy by Model & Dataset')
    axes[1, 0].set_ylabel('Top-5 Accuracy')
    
    # 4. Model size
    avg_size = df.groupby('Model')['Model Size (MB)'].mean()
    avg_size.plot(kind='bar', ax=axes[1, 1])
    axes[1, 1].set_title('Average Model Size')
    axes[1, 1].set_ylabel('Size (MB)')
    
    plt.tight_layout()
    plt.savefig('results/model_comparison.png', dpi=300)
    print("\n📊 Comparison charts saved to: results/model_comparison.png")

if __name__ == '__main__':
    df, best = generate_comparison_report()
```


### 2.4. Evaluation Metrics

**File:** `utils/metrics.py`

```python
import time
import numpy as np
from sklearn.metrics import accuracy_score, top_k_accuracy_score

def evaluate_model(model, X_test, y_test, preprocessor):
    """Comprehensive model evaluation"""
    
    # 1. Test accuracy
    test_loss, test_acc, top5_acc = model.evaluate(X_test, y_test, verbose=0)
    
    # 2. Inference time
    start = time.time()
    predictions = model.predict(X_test[:100], verbose=0)
    inference_time = (time.time() - start) / 100 * 1000  # ms per sample
    
    # 3. Top-K accuracy
    y_pred = model.predict(X_test, verbose=0)
    top1_acc = accuracy_score(y_test, np.argmax(y_pred, axis=1))
    top3_acc = top_k_accuracy_score(y_test, y_pred, k=3)
    top5_acc = top_k_accuracy_score(y_test, y_pred, k=5)
    top10_acc = top_k_accuracy_score(y_test, y_pred, k=10)
    
    # 4. Model size
    model.save_weights('temp_weights.h5')
    import os
    model_size_mb = os.path.getsize('temp_weights.h5') / (1024 * 1024)
    os.remove('temp_weights.h5')
    
    # 5. Recommendations quality (diversity, coverage)
    diversity = calculate_diversity(y_pred, top_k=10)
    coverage = calculate_coverage(y_pred, preprocessor.num_products, top_k=10)
    
    return {
        'test_loss': float(test_loss),
        'test_accuracy': float(test_acc),
        'top1_accuracy': float(top1_acc),
        'top3_accuracy': float(top3_acc),
        'top5_accuracy': float(top5_acc),
        'top10_accuracy': float(top10_acc),
        'inference_time_ms': float(inference_time),
        'model_size_mb': float(model_size_mb),
        'diversity': float(diversity),
        'coverage': float(coverage)
    }

def calculate_diversity(predictions, top_k=10):
    """Average pairwise distance between top-K recommendations"""
    diversities = []
    for pred in predictions:
        top_items = np.argsort(pred)[-top_k:]
        # Jaccard distance or embedding distance
        diversity = len(set(top_items)) / top_k
        diversities.append(diversity)
    return np.mean(diversities)

def calculate_coverage(predictions, num_products, top_k=10):
    """Percentage of products that appear in top-K recommendations"""
    recommended_products = set()
    for pred in predictions:
        top_items = np.argsort(pred)[-top_k:]
        recommended_products.update(top_items)
    return len(recommended_products) / num_products
```

---

## 🚀 PHASE 3: KNOWLEDGE GRAPH & RAG (Tuần 4)

### 3.1. Neo4j Knowledge Graph

#### 📝 **Graph Schema**
```cypher
// Nodes
(:User {user_id, username, email, role})
(:Product {product_id, name, price, category_name})
(:Category {name})

// Relationships
(User)-[:VIEW {count, last_at}]->(Product)
(User)-[:PURCHASE {count, last_at}]->(Product)
(User)-[:ADD_TO_CART {count, last_at}]->(Product)
(User)-[:WISHLIST {count, last_at}]->(Product)
(User)-[:SEARCH_CLICK {count, last_at}]->(Product)
(User)-[:REMOVE_FROM_CART {count, last_at}]->(Product)
(User)-[:SHARE {count, last_at}]->(Product)
(User)-[:REVIEW {count, last_at}]->(Product)
(Product)-[:IN_CATEGORY]->(Category)
(Product)-[:SIMILAR_TO {score}]->(Product)
```

#### 📝 **Neo4j Client**

**File:** `graph/neo4j_client.py`

```python
from neo4j import GraphDatabase
from typing import List, Dict

class Neo4jClient:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def get_user_recommendations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Graph-based recommendations:
        1. Products similar to user's purchases
        2. Products bought by similar users
        """
        query = """
        MATCH (u:User {user_id: $user_id})-[:PURCHASE]->(p1:Product)
        MATCH (p1)-[:SIMILAR_TO]->(rec:Product)
        WHERE NOT (u)-[:PURCHASE]->(rec)
        RETURN rec.product_id AS product_id, 
               rec.name AS name,
               COUNT(*) AS score
        ORDER BY score DESC
        LIMIT $limit
        
        UNION
        
        MATCH (u:User {user_id: $user_id})-[:PURCHASE]->(p:Product)
              <-[:PURCHASE]-(similar_user:User)
              -[:PURCHASE]->(rec:Product)
        WHERE NOT (u)-[:PURCHASE]->(rec)
        RETURN rec.product_id AS product_id,
               rec.name AS name,
               COUNT(DISTINCT similar_user) AS score
        ORDER BY score DESC
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query, user_id=user_id, limit=limit)
            return [dict(record) for record in result]
```


    def compute_product_similarity(self):
        """Compute product similarity based on co-purchase patterns"""
        query = """
        MATCH (p1:Product)<-[:PURCHASE]-(u:User)-[:PURCHASE]->(p2:Product)
        WHERE p1.product_id < p2.product_id
        WITH p1, p2, COUNT(DISTINCT u) AS co_purchases
        WHERE co_purchases >= 3
        MERGE (p1)-[s:SIMILAR_TO]->(p2)
        SET s.score = co_purchases
        MERGE (p2)-[s2:SIMILAR_TO]->(p1)
        SET s2.score = co_purchases
        RETURN COUNT(*) AS relationships_created
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return result.single()['relationships_created']
```

### 3.2. Vector Database & Semantic Search

#### 📝 **Text Embeddings**

**File:** `models/embeddings.py`

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

class ProductEmbeddingService:
    """Generate and search product embeddings for semantic search"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.product_ids = []
        self.product_texts = {}
    
    def generate_embeddings(self, products: List[Dict]):
        """
        Generate embeddings for all products
        
        Args:
            products: [{product_id, name, description, category_name, ...}]
        """
        self.product_ids = [p['product_id'] for p in products]
        
        # Create rich text representation
        texts = []
        for p in products:
            text = f"{p['name']} {p.get('description', '')} {p['category_name']}"
            texts.append(text)
            self.product_texts[p['product_id']] = text
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine sim)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        print(f"✓ Generated embeddings for {len(products)} products")
        return embeddings
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Semantic search for products
        
        Args:
            query: Natural language query
            top_k: Number of results
        
        Returns:
            [{product_id, name, score}, ...]
        """
        if self.index is None:
            raise ValueError("Index not built. Call generate_embeddings first.")
        
        # Encode query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.product_ids):
                results.append({
                    'product_id': self.product_ids[idx],
                    'score': float(score),
                    'text': self.product_texts[self.product_ids[idx]]
                })
        
        return results
    
    def save(self, path_prefix: str):
        """Save index and metadata"""
        faiss.write_index(self.index, f"{path_prefix}_index.faiss")
        with open(f"{path_prefix}_meta.pkl", 'wb') as f:
            pickle.dump({
                'product_ids': self.product_ids,
                'product_texts': self.product_texts
            }, f)
    
    def load(self, path_prefix: str):
        """Load index and metadata"""
        self.index = faiss.read_index(f"{path_prefix}_index.faiss")
        with open(f"{path_prefix}_meta.pkl", 'rb') as f:
            meta = pickle.load(f)
            self.product_ids = meta['product_ids']
            self.product_texts = meta['product_texts']
```


### 3.3. RAG (Retrieval-Augmented Generation) for Chatbot

#### 📝 **Chatbot Service with RAG**

**File:** `services/chatbot_service.py`

```python
from typing import Dict, List
import httpx
from models.embeddings import ProductEmbeddingService

class ChatbotService:
    """
    RAG-based chatbot for product consultation
    
    Pipeline:
    1. Intent detection (rule-based or classifier)
    2. Retrieve relevant products (vector search)
    3. Generate response (template or LLM)
    """
    
    def __init__(self, embedding_service: ProductEmbeddingService):
        self.embedding_service = embedding_service
        self.sessions = {}  # session_id -> conversation history
    
    async def chat(self, 
                   user_id: int, 
                   message: str, 
                   session_id: str = None) -> Dict:
        """
        Process chat message
        
        Returns:
            {
                'session_id': str,
                'reply': str,
                'intent': str,
                'suggested_products': [...]
            }
        """
        # 1. Detect intent
        intent = self._detect_intent(message)
        
        # 2. Retrieve relevant products
        products = await self._retrieve_products(message, intent, user_id)
        
        # 3. Generate response
        reply = self._generate_response(intent, message, products)
        
        # 4. Store conversation history
        if session_id:
            self._update_session(session_id, message, reply)
        
        return {
            'session_id': session_id or self._create_session_id(),
            'reply': reply,
            'intent': intent,
            'suggested_products': products[:5],
            'confidence': 0.85
        }
    
    def _detect_intent(self, message: str) -> str:
        """
        Simple rule-based intent detection
        
        Intents:
        - product_search: "tìm", "cần", "laptop", "điện thoại"
        - price_inquiry: "giá", "bao nhiêu", "rẻ"
        - recommendation: "gợi ý", "đề xuất", "nên mua"
        - comparison: "so sánh", "khác nhau"
        - order_status: "đơn hàng", "ship"
        - complaint: "khiếu nại", "không hài lòng"
        """
        message_lower = message.lower()
        
        if any(kw in message_lower for kw in ['đơn hàng', 'ship', 'giao', 'vận chuyển']):
            return 'order_status'
        elif any(kw in message_lower for kw in ['so sánh', 'khác nhau', 'vs', 'hay']):
            return 'comparison'
        elif any(kw in message_lower for kw in ['giá', 'bao nhiêu', 'rẻ', 'đắt']):
            return 'price_inquiry'
        elif any(kw in message_lower for kw in ['gợi ý', 'đề xuất', 'nên mua', 'recommend']):
            return 'recommendation'
        elif any(kw in message_lower for kw in ['khiếu nại', 'không hài lòng', 'tệ']):
            return 'complaint'
        else:
            return 'product_search'
    
    async def _retrieve_products(self, 
                                  message: str, 
                                  intent: str, 
                                  user_id: int) -> List[Dict]:
        """Retrieve relevant products based on intent"""
        
        if intent in ['product_search', 'price_inquiry', 'comparison']:
            # Semantic search
            results = self.embedding_service.search(message, top_k=10)
            
            # Get full product info from Product Service
            product_ids = [r['product_id'] for r in results]
            products = await self._fetch_products(product_ids)
            
            # Add similarity scores
            for prod, res in zip(products, results):
                prod['relevance_score'] = res['score']
            
            return products
        
        elif intent == 'recommendation':
            # Get personalized recommendations
            # (will be implemented in recommendation_service)
            return []
        
        return []
    
    async def _fetch_products(self, product_ids: List[int]) -> List[Dict]:
        """Fetch product details from Product Service"""
        async with httpx.AsyncClient() as client:
            products = []
            for pid in product_ids:
                try:
                    resp = await client.get(
                        f"http://product-service:8002/api/products/{pid}",
                        timeout=2.0
                    )
                    if resp.status_code == 200:
                        products.append(resp.json())
                except:
                    continue
            return products
    
    def _generate_response(self, 
                          intent: str, 
                          message: str, 
                          products: List[Dict]) -> str:
        """Generate response based on intent and products"""
        
        if intent == 'product_search' and products:
            top3 = products[:3]
            product_list = "\n".join([
                f"• {p['name']} - {p['price']:,.0f}đ" 
                for p in top3
            ])
            return (
                f"Tôi tìm thấy {len(products)} sản phẩm phù hợp với yêu cầu của bạn:\n\n"
                f"{product_list}\n\n"
                "Bạn muốn xem chi tiết sản phẩm nào?"
            )
        
        elif intent == 'price_inquiry' and products:
            cheapest = min(products, key=lambda x: x['price'])
            return (
                f"Sản phẩm rẻ nhất tôi tìm được là:\n"
                f"• {cheapest['name']}\n"
                f"• Giá: {cheapest['price']:,.0f}đ\n"
                f"• Còn {cheapest['stock']} sản phẩm trong kho"
            )
        
        elif intent == 'recommendation':
            return (
                "Dựa trên lịch sử mua hàng của bạn, tôi gợi ý một số sản phẩm "
                "mà bạn có thể quan tâm. Bạn muốn xem gợi ý về loại sản phẩm nào?"
            )
        
        elif intent == 'order_status':
            return (
                "Để kiểm tra trạng thái đơn hàng, bạn có thể vào mục "
                "'Đơn hàng của tôi' hoặc cung cấp mã đơn hàng để tôi tra cứu."
            )
        
        else:
            return (
                "Xin lỗi, tôi chưa hiểu rõ yêu cầu của bạn. "
                "Bạn có thể nói rõ hơn được không?"
            )
```

---

## 🔌 PHASE 4: API IMPLEMENTATION (Tuần 5)

### 4.1. FastAPI Application Structure

**File:** `main.py`

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from api import recommendation, chatbot, search, health
from middleware.logging import setup_logging
from models.model_loader import ModelLoader
from models.embeddings import ProductEmbeddingService
from graph.neo4j_client import Neo4jClient
from utils.cache import RedisCache

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global services
model_loader = None
embedding_service = None
neo4j_client = None
redis_cache = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global model_loader, embedding_service, neo4j_client, redis_cache
    
    logger.info("🚀 Starting AI Service...")
    
    # Load best model
    logger.info("Loading trained model...")
    model_loader = ModelLoader()
    model_loader.load_best_model()  # From comparison results
    
    # Load embeddings
    logger.info("Loading product embeddings...")
    embedding_service = ProductEmbeddingService()
    embedding_service.load('data/embeddings/products')
    
    # Connect to Neo4j
    logger.info("Connecting to Neo4j...")
    neo4j_client = Neo4jClient(
        uri=settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    
    # Connect to Redis
    logger.info("Connecting to Redis...")
    redis_cache = RedisCache(settings.REDIS_URL)
    await redis_cache.connect()
    
    logger.info("✅ AI Service ready!")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    neo4j_client.close()
    await redis_cache.close()

app = FastAPI(
    title='AI Service',
    description='Product Recommendation & Chatbot Service',
    version='1.0.0',
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix='/api/ai', tags=['Health'])
app.include_router(recommendation.router, prefix='/api/ai', tags=['Recommendation'])
app.include_router(chatbot.router, prefix='/api/ai', tags=['Chatbot'])
app.include_router(search.router, prefix='/api/ai', tags=['Search'])

# Dependency injection
def get_model_loader():
    return model_loader

def get_embedding_service():
    return embedding_service

def get_neo4j_client():
    return neo4j_client

def get_cache():
    return redis_cache
```


### 4.2. Recommendation API

**File:** `api/recommendation.py`

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from services.recommendation_service import RecommendationService
from middleware.auth import get_current_user

router = APIRouter()

class RecommendRequest(BaseModel):
    product_id: Optional[int] = None
    user_id: Optional[int] = None
    context: str = 'homepage'  # homepage, product_detail, cart, checkout
    limit: int = 10

class ProductSummary(BaseModel):
    product_id: int
    name: str
    price: float
    image_url: Optional[str]
    score: float

class RecommendResponse(BaseModel):
    products: List[ProductSummary]
    strategy: str

@router.post('/recommend', response_model=RecommendResponse)
async def get_recommendations(
    request: RecommendRequest,
    current_user = Depends(get_current_user),
    rec_service: RecommendationService = Depends()
):
    """
    Get product recommendations
    
    Strategies:
    - Personalized (based on user history + LSTM)
    - Similar products (based on product_id + Graph)
    - Trending (popular products)
    - Hybrid (weighted combination)
    """
    user_id = request.user_id or current_user.get('user_id')
    
    recommendations = await rec_service.get_recommendations(
        user_id=user_id,
        product_id=request.product_id,
        context=request.context,
        limit=request.limit
    )
    
    return recommendations

@router.get('/recommend/trending', response_model=RecommendResponse)
async def get_trending(
    limit: int = Query(10, le=50),
    category_id: Optional[int] = None,
    rec_service: RecommendationService = Depends()
):
    """Get trending products"""
    
    trending = await rec_service.get_trending(
        category_id=category_id,
        limit=limit
    )
    
    return trending

@router.post('/behavior')
async def log_behavior(
    event: dict,
    current_user = Depends(get_current_user)
):
    """
    Log user behavior event
    
    Body:
    {
        "event_type": "view" | "add_to_cart" | "purchase" | ...,
        "product_id": 123,
        "metadata": {...}
    }
    """
    # Store in database for future training
    # Also update real-time cache for instant personalization
    
    return {"status": "accepted"}
```


### 4.3. Hybrid Recommendation Service

**File:** `services/recommendation_service.py`

```python
import numpy as np
from typing import List, Dict, Optional
import httpx

class RecommendationService:
    """
    Hybrid recommendation system combining:
    - LSTM model (sequence-based)
    - Knowledge Graph (relationship-based)
    - Vector search (content-based)
    """
    
    def __init__(self, 
                 model_loader, 
                 neo4j_client, 
                 embedding_service, 
                 cache):
        self.model_loader = model_loader
        self.neo4j = neo4j_client
        self.embeddings = embedding_service
        self.cache = cache
    
    async def get_recommendations(self,
                                   user_id: int,
                                   product_id: Optional[int] = None,
                                   context: str = 'homepage',
                                   limit: int = 10) -> Dict:
        """
        Main recommendation method
        
        Strategy selection based on context:
        - homepage: personalized (LSTM + Graph)
        - product_detail: similar products (Graph + Embeddings)
        - cart: complementary products
        - checkout: upselling
        """
        
        # Check cache first
        cache_key = f"rec:{user_id}:{product_id}:{context}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Get recommendations from different sources
        if context == 'product_detail' and product_id:
            # Similar products
            products = await self._similar_products(product_id, limit * 2)
            strategy = 'similar_products'
        
        elif context in ['homepage', 'cart']:
            # Personalized recommendations
            lstm_recs = await self._lstm_recommendations(user_id, limit)
            graph_recs = await self._graph_recommendations(user_id, limit)
            
            # Combine and re-rank
            products = self._hybrid_merge(lstm_recs, graph_recs, limit)
            strategy = 'hybrid_personalized'
        
        else:
            # Fallback to trending
            products = await self.get_trending(limit=limit)
            strategy = 'trending'
        
        result = {
            'products': products[:limit],
            'strategy': strategy
        }
        
        # Cache for 1 hour
        await self.cache.set(cache_key, result, ttl=3600)
        
        return result
    
    async def _lstm_recommendations(self, user_id: int, limit: int) -> List[Dict]:
        """Get recommendations from LSTM model"""
        
        # 1. Get user's recent behavior sequence
        sequence = await self._get_user_sequence(user_id, seq_len=10)
        
        if not sequence:
            return []
        
        # 2. Predict next products
        predictions = self.model_loader.predict(sequence)
        
        # 3. Get top-K product_ids
        top_indices = np.argsort(predictions[0])[::-1][:limit]
        product_ids = self.model_loader.decode_product_ids(top_indices)
        scores = predictions[0][top_indices]
        
        # 4. Fetch product details
        products = await self._fetch_products(product_ids)
        
        # 5. Add scores
        for prod, score in zip(products, scores):
            prod['score'] = float(score)
        
        return products
    
    async def _graph_recommendations(self, user_id: int, limit: int) -> List[Dict]:
        """Get recommendations from Knowledge Graph"""
        
        graph_results = self.neo4j.get_user_recommendations(user_id, limit)
        
        # Fetch full product details
        product_ids = [r['product_id'] for r in graph_results]
        products = await self._fetch_products(product_ids)
        
        # Add graph scores
        score_map = {r['product_id']: r['score'] for r in graph_results}
        for prod in products:
            prod['score'] = float(score_map.get(prod['product_id'], 0))
        
        return products
    
    async def _similar_products(self, product_id: int, limit: int) -> List[Dict]:
        """Get similar products using Graph + Embeddings"""
        
        # 1. From Knowledge Graph (co-purchase similarity)
        graph_similar = self.neo4j.get_similar_products(product_id, limit // 2)
        
        # 2. From Vector embeddings (content similarity)
        product = await self._fetch_products([product_id])
        if product:
            query_text = f"{product[0]['name']} {product[0]['category_name']}"
            embedding_similar = self.embeddings.search(query_text, limit // 2)
            
            # Merge
            all_similar = graph_similar + embedding_similar
            # Remove duplicates and sort by score
            seen = set()
            unique = []
            for item in sorted(all_similar, key=lambda x: x['score'], reverse=True):
                if item['product_id'] not in seen and item['product_id'] != product_id:
                    seen.add(item['product_id'])
                    unique.append(item)
            
            return unique[:limit]
        
        return graph_similar
    
    def _hybrid_merge(self, 
                      lstm_recs: List[Dict], 
                      graph_recs: List[Dict], 
                      limit: int) -> List[Dict]:
        """
        Merge recommendations with weighted scoring
        
        Score = 0.6 * lstm_score + 0.4 * graph_score
        """
        # Create score maps
        lstm_map = {p['product_id']: p['score'] for p in lstm_recs}
        graph_map = {p['product_id']: p['score'] for p in graph_recs}
        
        # All unique product IDs
        all_ids = set(lstm_map.keys()) | set(graph_map.keys())
        
        # Compute hybrid scores
        hybrid_scores = []
        for pid in all_ids:
            lstm_score = lstm_map.get(pid, 0)
            graph_score = graph_map.get(pid, 0)
            
            # Weighted combination
            final_score = 0.6 * lstm_score + 0.4 * graph_score
            
            hybrid_scores.append({
                'product_id': pid,
                'score': final_score
            })
        
        # Sort by score
        hybrid_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Fetch product details for top-K
        top_ids = [h['product_id'] for h in hybrid_scores[:limit]]
        products = await self._fetch_products(top_ids)
        
        # Add final scores
        score_map = {h['product_id']: h['score'] for h in hybrid_scores}
        for prod in products:
            prod['score'] = score_map[prod['product_id']]
        
        return products
    
    async def get_trending(self, 
                           category_id: Optional[int] = None, 
                           limit: int = 10) -> Dict:
        """
        Get trending products based on recent behaviors
        
        Algorithm: Time-weighted popularity score
        Score = views * 0.3 + add_to_cart * 0.5 + purchase * 1.0
        Recent behaviors (7 days) weighted higher
        """
        # Query from database
        # For now, mock implementation
        
        trending = await self._fetch_trending_from_db(category_id, limit)
        
        return {
            'products': trending,
            'strategy': 'trending'
        }
    
    async def _get_user_sequence(self, user_id: int, seq_len: int) -> np.ndarray:
        """Get user's recent behavior sequence"""
        # Query from database
        # Return encoded product_ids as numpy array
        pass
    
    async def _fetch_products(self, product_ids: List[int]) -> List[Dict]:
        """Fetch product details from Product Service"""
        async with httpx.AsyncClient() as client:
            products = []
            for pid in product_ids:
                try:
                    resp = await client.get(
                        f"http://localhost:8002/api/products/{pid}",
                        timeout=2.0
                    )
                    if resp.status_code == 200:
                        products.append(resp.json())
                except:
                    continue
            return products
    
    async def _fetch_trending_from_db(self, category_id, limit):
        """Query trending products from database"""
        # Implementation
        pass
```

---

## 📊 PHASE 5: TESTING & EVALUATION (Tuần 6)

### 5.1. Testing Matrix

| Test Type | Coverage | Tools |
|-----------|----------|-------|
| Unit Tests | Models, Utils | pytest |
| Integration Tests | API endpoints | pytest + httpx |
| Load Tests | Performance | locust |
| Model Tests | Accuracy, Inference time | custom scripts |

### 5.2. Acceptance Criteria

✅ **Model Performance:**
- Test accuracy > 5% (better than random)
- Top-5 accuracy > 20%
- Top-10 accuracy > 35%
- Inference time < 50ms per request

✅ **API Performance:**
- Response time < 200ms (p95)
- Throughput > 100 req/s
- Availability > 99%

✅ **Recommendation Quality:**
- Diversity score > 0.7
- Coverage > 60% of products
- User CTR > 5% (A/B test)

---

## 📅 IMPLEMENTATION TIMELINE

### **Week 1: Data & Foundation**
- [ ] Day 1: Setup project structure & Docker
- [ ] Day 2: Generate Dataset 2 (Balanced)
- [ ] Day 3: Generate Dataset 3 (Extended)
- [ ] Day 4: Data preprocessing pipeline
- [ ] Day 5-7: Exploratory data analysis & validation

### **Week 2: Model Training - RNN & LSTM**
- [ ] Day 8: Train RNN + Dataset Original
- [ ] Day 9: Train RNN + Dataset Balanced
- [ ] Day 10: Train RNN + Dataset Extended
- [ ] Day 11: Train LSTM + Dataset Original
- [ ] Day 12: Train LSTM + Dataset Balanced
- [ ] Day 13: Train LSTM + Dataset Extended
- [ ] Day 14: Review & optimize hyperparameters

### **Week 3: Model Training - BiLSTM & Comparison**
- [ ] Day 15: Train BiLSTM + Dataset Original
- [ ] Day 16: Train BiLSTM + Dataset Balanced
- [ ] Day 17: Train BiLSTM + Dataset Extended
- [ ] Day 18-19: Comprehensive model comparison
- [ ] Day 20-21: Select & optimize best model

### **Week 4: Graph & RAG**
- [ ] Day 22: Setup Neo4j Docker & import data
- [ ] Day 23: Build Knowledge Graph schema
- [ ] Day 24: Implement graph queries
- [ ] Day 25: Generate product embeddings
- [ ] Day 26: Build FAISS vector index
- [ ] Day 27: Implement semantic search
- [ ] Day 28: RAG pipeline for chatbot

### **Week 5: API Implementation**
- [ ] Day 29: FastAPI app structure
- [ ] Day 30: Recommendation endpoints
- [ ] Day 31: Chatbot endpoints
- [ ] Day 32: Search & behavior endpoints
- [ ] Day 33: JWT middleware & HTTP clients
- [ ] Day 34: Redis caching layer
- [ ] Day 35: Integration testing

### **Week 6: Testing & Deployment**
- [ ] Day 36: Unit tests (models & services)
- [ ] Day 37: API integration tests
- [ ] Day 38: Load testing & optimization
- [ ] Day 39: Docker deployment testing
- [ ] Day 40: API documentation (OpenAPI)
- [ ] Day 41: User manual & guides
- [ ] Day 42: Final review & deployment

---

## 🎯 SUCCESS METRICS

### Model Comparison Matrix
```
Total Experiments: 3 models × 3 datasets = 9 training runs

┌──────────┬────────────┬──────────┬───────────┬────────────┬─────────────┐
│ Model    │ Dataset    │ Accuracy │ Top-5 Acc │ Inf. Time  │ Model Size  │
├──────────┼────────────┼──────────┼───────────┼────────────┼─────────────┤
│ RNN      │ Original   │ ?        │ ?         │ ?          │ ?           │
│ RNN      │ Balanced   │ ?        │ ?         │ ?          │ ?           │
│ RNN      │ Extended   │ ?        │ ?         │ ?          │ ?           │
│ LSTM     │ Original   │ 1.1%     │ ?         │ ?          │ ?           │
│ LSTM     │ Balanced   │ ?        │ ?         │ ?          │ ?           │
│ LSTM     │ Extended   │ ?        │ ?         │ ?          │ ?           │
│ BiLSTM   │ Original   │ ?        │ ?         │ ?          │ ?           │
│ BiLSTM   │ Balanced   │ ?        │ ?         │ ?          │ ?           │
│ BiLSTM   │ Extended   │ ?        │ ?         │ ?          │ ?           │
└──────────┴────────────┴──────────┴───────────┴────────────┴─────────────┘

🏆 WINNER: [To be determined after training]
```

### Performance Targets
- **Test Accuracy:** > 5% (baseline)
- **Top-5 Accuracy:** > 20%
- **Top-10 Accuracy:** > 35%
- **Inference Time:** < 50ms per request
- **API Response Time:** < 200ms (p95)
- **Throughput:** > 100 req/s
- **Recommendation Diversity:** > 0.7
- **Product Coverage:** > 60%

### Final Deliverables
- ✅ 3 trained models (RNN, LSTM, BiLSTM) - 9 weight files
- ✅ 3 datasets for comparison
- ✅ Comprehensive comparison report with charts
- ✅ Production-ready AI Service in Docker
- ✅ Complete API documentation (OpenAPI/Swagger)
- ✅ Testing suite (Unit + Integration + Load)
- ✅ Docker Compose for full stack deployment
- ✅ Deployment guide & troubleshooting
- ✅ User manual

---

## 📦 DEPLOYMENT COMMANDS

### Build & Run with Docker Compose

```bash
# Navigate to project root
cd d:\ky2nam4\kttkpm\code_tieuluan1\tieuluan1

# Start Neo4j and Redis first (đợi health check pass)
docker-compose up -d neo4j redis

# Wait for services to be healthy (khoảng 30-40 giây)
docker-compose ps

# Check Neo4j logs
docker-compose logs neo4j

# Check Redis logs  
docker-compose logs redis

# Import data to Neo4j (chạy script Python từ host)
python build_knowledge_graph.py

# Start all services (bao gồm AI service)
docker-compose up -d

# Hoặc chỉ start AI service
docker-compose up -d ai-service

# Check AI service logs
docker-compose logs -f ai-service

# View all services status
docker-compose ps

# Test AI Service health
curl http://localhost:8007/api/ai/health

# Stop specific service
docker-compose stop ai-service

# Stop all services
docker-compose down

# Stop và xóa volumes (CAREFUL - mất data!)
docker-compose down -v
```

### Development Mode (Local - không dùng Docker)

```bash
# Navigate to AI service folder
cd d:\ky2nam4\kttkpm\code_tieuluan1\tieuluan1\services\ai-service

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Neo4j via Docker (nếu chưa có)
docker run -d --name neo4j ^
  -p 7474:7474 -p 7687:7687 ^
  -e NEO4J_AUTH=neo4j/dkstore123 ^
  neo4j:5.18

# Start Redis via Docker (nếu chưa có)
docker run -d --name redis ^
  -p 6379:6379 ^
  redis:7-alpine

# Set environment variables (Windows PowerShell)
$env:NEO4J_URI="bolt://localhost:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="dkstore123"
$env:REDIS_URL="redis://localhost:6379"
$env:PRODUCT_SERVICE_URL="http://localhost:8002"
$env:USER_SERVICE_URL="http://localhost:8001"

# Or use .env file
# Copy .env.example to .env and edit values

# Run AI Service
uvicorn main:app --reload --port 8007

# In another terminal - Test API
curl http://localhost:8007/api/ai/health
```

### Troubleshooting

```bash
# Check if Neo4j is running
docker ps | findstr neo4j

# Check Neo4j Browser
# Open: http://localhost:7474
# Login: neo4j / dkstore123

# Check Redis
docker exec -it redis redis-cli ping
# Should return: PONG

# View AI service logs
docker-compose logs --tail=100 -f ai-service

# Restart AI service
docker-compose restart ai-service

# Rebuild AI service image
docker-compose build ai-service
docker-compose up -d ai-service

# Check network connectivity
docker exec -it ai-service ping neo4j
docker exec -it ai-service ping redis
docker exec -it ai-service ping product-service

# Check volumes
docker volume ls | findstr neo4j
docker volume ls | findstr redis
```

### Useful Commands

```bash
# Export Neo4j data
docker exec neo4j neo4j-admin database dump neo4j --to-path=/data/dumps

# Import Neo4j data
docker exec neo4j neo4j-admin database load neo4j --from-path=/data/dumps

# Redis CLI
docker exec -it redis redis-cli

# Check Redis keys
docker exec redis redis-cli KEYS "rec:*"

# Clear Redis cache
docker exec redis redis-cli FLUSHALL

# Monitor Redis
docker exec redis redis-cli MONITOR
```

---

## 📚 REFERENCES & RESOURCES

### Papers & Articles
- LSTM: "Long Short-Term Memory" (Hochreiter & Schmidhuber, 1997)
- BiLSTM: "Bidirectional LSTM-CRF Models"
- RAG: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"

### Libraries & Tools
- TensorFlow/Keras: Model training
- FAISS: Vector similarity search
- Neo4j: Graph database
- FastAPI: API framework
- Redis: Caching

### Tutorials
- [TensorFlow LSTM Tutorial](https://www.tensorflow.org/guide/keras/rnn)
- [FAISS Getting Started](https://github.com/facebookresearch/faiss/wiki)
- [Neo4j Recommendation](https://neo4j.com/use-cases/real-time-recommendation-engine/)

---

## 🎓 CONCLUSION

This implementation plan provides a comprehensive roadmap for building a production-ready AI Service with:

1. **Rigorous model comparison** (3 models × 5 datasets = 15 experiments)
2. **Hybrid recommendation** (LSTM + Graph + Embeddings)
3. **Intelligent chatbot** (RAG-based)
4. **Scalable architecture** (FastAPI + Redis + Neo4j)
5. **Complete testing** (Unit + Integration + Load tests)

**Expected Outcome:** A high-performance AI service that significantly improves user experience through personalized recommendations and intelligent consultation.

---

**Author:** AI Service Team  
**Version:** 1.0  
**Last Updated:** 2026-06-02
