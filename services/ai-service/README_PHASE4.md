# Giai đoạn 4: Hệ thống RAG - HOÀN THÀNH ✅

## Tổng quan
Giai đoạn 4 triển khai hệ thống RAG (Retrieval-Augmented Generation) cho tìm kiếm sản phẩm ngữ nghĩa và tư vấn chatbot sử dụng sentence transformers và cơ sở dữ liệu vector FAISS.

## Kiến trúc

### Các thành phần
1. **Sentence Transformer**: Mô hình embedding đa ngôn ngữ
2. **FAISS**: Công cụ tìm kiếm độ tương đồng vector
3. **Product Database**: Thông tin sản phẩm có cấu trúc
4. **Chatbot**: Giao diện hội thoại để tư vấn sản phẩm

### Chi tiết mô hình
- **Mô hình**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Chiều embedding**: 384
- **Cơ sở dữ liệu vector**: FAISS (phiên bản CPU)
- **Độ đo tương đồng**: Cosine similarity (Inner Product)

## Triển khai

### Nhiệm vụ 4.1: Tạo Embeddings ✅
- Đã tải 50 sản phẩm từ dữ liệu hành vi người dùng
- Đã tạo embeddings đa ngôn ngữ sử dụng sentence-transformers
- Chiều embedding: 384
- Mô hình hỗ trợ văn bản tiếng Việt và tiếng Anh

### Nhiệm vụ 4.2: Cài đặt cơ sở dữ liệu Vector ✅
- Đã khởi tạo FAISS IndexFlatIP (Inner Product cho cosine similarity)
- Sử dụng triển khai CPU (có thể nâng cấp lên GPU)
- Tổng số vectors đã lập chỉ mục: 50

### Nhiệm vụ 4.3: Lưu trữ Product Embeddings ✅
- Đã tạo văn bản có thể tìm kiếm từ thông tin sản phẩm:
  - Tên sản phẩm
  - Danh mục
  - Mô tả
  - Giá
- Đã chuẩn hóa embeddings cho cosine similarity
- Đã lưu trữ trong chỉ mục FAISS

### Nhiệm vụ 4.4: Truy xuất ✅
Đã triển khai hai phương thức truy xuất:

#### 1. Tìm kiếm dựa trên văn bản
Ví dụ truy vấn và kết quả:
- **"điện thoại iPhone cao cấp"** → iPhone 15 Pro Max (điểm: 0.6425)
- **"laptop gaming mạnh mẽ"** → ASUS ROG Strix G16 (điểm: 0.5314)
- **"tai nghe không dây chống ồn"** → Sản phẩm âm thanh (điểm: 0.3761)

#### 2. Gợi ý dựa trên sản phẩm
Gợi ý sản phẩm tương tự:
- **iPhone 15 Pro Max** → iPad Air M2 (0.7289), Xiaomi 14 Pro (0.6964)
- **MacBook Pro 14** → Dell XPS 15 (0.6628), HP Pavilion (0.6243)

### Nhiệm vụ 4.5: Tạo phản hồi (Chatbot) ✅
Đã triển khai ProductChatbot với:
- **Phát hiện ý định**: Chào hỏi, tìm kiếm, gợi ý
- **Mẫu phản hồi**: Hỗ trợ tiếng Việt
- **Luồng hội thoại**: Tư vấn sản phẩm tự nhiên

#### Tính năng Chatbot
1. **Xử lý chào hỏi**
   - User: "Xin chào"
   - Bot: "Xin chào! Tôi có thể giúp bạn tìm sản phẩm. Bạn đang tìm gì?"

2. **Tìm kiếm sản phẩm**
   - User: "Tôi muốn mua điện thoại iPhone"
   - Bot: Trả về top 5 sản phẩm phù hợp với chi tiết

3. **Gợi ý**
   - User: "Gợi ý sản phẩm tương tự product 1"
   - Bot: Trả về 5 sản phẩm tương tự dựa trên embeddings

## Các file được tạo

### File dữ liệu
```
data/
├── faiss_index.bin      # Chỉ mục vector FAISS (76KB)
└── rag_metadata.pkl     # Metadata sản phẩm (6.0KB)
```

### File source
```
src/
└── rag.py              # Triển khai RAG
    ├── ProductRAG      # Lớp RAG chính
    ├── ProductChatbot  # Giao diện chatbot
    └── load_products_from_csv()  # Trình tải dữ liệu
```

## Chỉ số hiệu suất

### Chất lượng tìm kiếm
- **Độ liên quan cao**: Truy vấn iPhone → Sản phẩm iPhone (điểm 0.64)
- **Khớp danh mục**: Laptop gaming → Laptop gaming (điểm 0.53)
- **Đa danh mục**: Sản phẩm được nhóm đúng theo danh mục

### Chất lượng gợi ý
- **Điểm tương đồng**: Phạm vi 0.5-0.9 cho sản phẩm liên quan
- **Tính nhất quán danh mục**: Sản phẩm tương tự từ cùng/danh mục liên quan
- **Đa dạng**: Gợi ý trải rộng nhiều loại sản phẩm

## Tài liệu tham khảo API

### Lớp ProductRAG

#### Phương thức
```python
# Khởi tạo hệ thống RAG
rag = ProductRAG(
    model_name='paraphrase-multilingual-MiniLM-L12-v2',
    embedding_dim=384
)

# Xây dựng chỉ mục FAISS
rag.build_index(products, use_gpu=False)

# Tìm kiếm dựa trên văn bản
results = rag.search(query="điện thoại iPhone", k=10)
# Trả về: List[(product_id, score, product_dict)]

# Gợi ý dựa trên sản phẩm
recs = rag.recommend_by_product(product_id=1, k=10)
# Trả về: List[(product_id, score)]

# Lưu/Tải
rag.save(index_path='data/faiss_index.bin', metadata_path='data/rag_metadata.pkl')
rag.load(index_path='data/faiss_index.bin', metadata_path='data/rag_metadata.pkl')
```

### Lớp ProductChatbot

#### Phương thức
```python
# Khởi tạo chatbot
chatbot = ProductChatbot(rag)

# Xử lý tin nhắn người dùng
response = chatbot.chat("Tôi muốn mua laptop")
# Trả về: Chuỗi phản hồi đã định dạng

# Tìm kiếm trực tiếp
response = chatbot.search("điện thoại", k=5)

# Gợi ý trực tiếp
response = chatbot.recommend(product_id=1, k=5)
```

## Ví dụ sử dụng

### Ví dụ 1: Tìm kiếm ngữ nghĩa
```python
from src.rag import ProductRAG, load_products_from_csv

# Tải sản phẩm
products = load_products_from_csv('data/user_behavior.csv')

# Khởi tạo và xây dựng chỉ mục
rag = ProductRAG()
rag.build_index(products)

# Tìm kiếm
results = rag.search("laptop gaming", k=5)
for pid, score, product in results:
    print(f"{product['name']}: {score:.4f}")
```

### Ví dụ 2: Tư vấn Chatbot
```python
from src.rag import ProductRAG, ProductChatbot, load_products_from_csv

# Cài đặt
products = load_products_from_csv('data/user_behavior.csv')
rag = ProductRAG()
rag.build_index(products)
chatbot = ProductChatbot(rag)

# Chat
response = chatbot.chat("Tôi muốn mua điện thoại iPhone")
print(response)
```

### Ví dụ 3: Tải chỉ mục đã lưu
```python
from src.rag import ProductRAG

# Tải chỉ mục đã xây dựng
rag = ProductRAG()
rag.load(
    index_path='data/faiss_index.bin',
    metadata_path='data/rag_metadata.pkl'
)

# Sử dụng ngay lập tức
results = rag.search("laptop", k=5)
```

## Kiểm thử

### Chạy Giai đoạn 4
```bash
cd services/ai-service
python run_phase4.py
```

### Kết quả mong đợi
- ✅ Tải 50 sản phẩm
- ✅ Tạo embeddings (50 x 384)
- ✅ Xây dựng chỉ mục FAISS
- ✅ Kiểm tra 5 truy vấn tìm kiếm
- ✅ Kiểm tra gợi ý sản phẩm
- ✅ Kiểm tra hội thoại chatbot
- ✅ Lưu chỉ mục và metadata

## Chi tiết kỹ thuật

### Tạo Embedding
- **Batch size**: 32
- **Chuẩn hóa**: Chuẩn hóa L2 cho cosine similarity
- **Thời gian xử lý**: ~2 giây cho 50 sản phẩm

### Cấu hình FAISS
- **Loại chỉ mục**: IndexFlatIP (tìm kiếm chính xác)
- **Độ đo khoảng cách**: Inner product (cosine similarity sau chuẩn hóa)
- **Sử dụng bộ nhớ**: ~76KB cho 50 sản phẩm

### Định dạng văn bản sản phẩm
```
{product_name} | Danh mục: {category} | {description} | Giá: {price} VNĐ
```

## Ưu điểm

### 1. Hiểu ngữ nghĩa
- Hiểu truy vấn tiếng Việt một cách tự nhiên
- Khớp ý định, không chỉ từ khóa
- Ví dụ: "điện thoại cao cấp" → Điện thoại cao cấp

### 2. Hỗ trợ đa ngôn ngữ
- Truy vấn tiếng Việt và tiếng Anh
- Khớp sản phẩm đa ngôn ngữ
- Công thức truy vấn linh hoạt

### 3. Truy xuất nhanh
- FAISS cung cấp tìm kiếm mức mili giây
- Có thể mở rộng đến hàng triệu sản phẩm
- Sử dụng bộ nhớ hiệu quả

### 4. Giao diện hội thoại
- Tương tác ngôn ngữ tự nhiên
- Phản hồi nhận biết ngữ cảnh
- Khám phá sản phẩm thân thiện với người dùng

## Hạn chế & Cải tiến tương lai

### Hạn chế hiện tại
1. **Embeddings tĩnh**: Sản phẩm phải được lập chỉ mục lại khi cập nhật
2. **Không mở rộng truy vấn**: Diễn giải truy vấn đơn
3. **Phát hiện ý định đơn giản**: Dựa trên quy tắc, không phải ML
4. **Không có lịch sử hội thoại**: Chatbot không trạng thái

### Cải tiến đã lên kế hoạch (Giai đoạn 5+)
1. **Chấm điểm kết hợp**: Kết hợp với gợi ý LSTM và Graph
2. **Mở rộng truy vấn**: Sử dụng từ đồng nghĩa và thuật ngữ liên quan
3. **NLU nâng cao**: Phân loại ý định dựa trên ML
4. **Bộ nhớ hội thoại**: Hỗ trợ đối thoại nhiều lượt
5. **Cập nhật thời gian thực**: Cập nhật chỉ mục tăng dần

## Điểm tích hợp

### Cho Giai đoạn 5 (Gợi ý kết hợp)
```python
# RAG cung cấp điểm tương đồng ngữ nghĩa
rag_scores = rag.search(query, k=20)

# Kết hợp với điểm LSTM và Graph
final_scores = combine_scores(
    lstm_scores=lstm_predictions,
    graph_scores=graph_recommendations,
    rag_scores=rag_scores,
    weights=[0.3, 0.3, 0.4]
)
```

### Cho Giai đoạn 6 (Dịch vụ FastAPI)
```python
# Endpoint: /search
@app.post("/search")
async def search_products(query: str):
    results = rag.search(query, k=10)
    return {"products": results}

# Endpoint: /chatbot
@app.post("/chatbot")
async def chatbot_query(message: str):
    response = chatbot.chat(message)
    return {"response": response}
```

## Dependencies
```
sentence-transformers==2.2.2  # Mô hình embedding
faiss-cpu==1.7.4              # Tìm kiếm vector
transformers==4.36.2          # Mô hình transformer
numpy==1.26.2                 # Thao tác mảng
pandas==2.1.4                 # Xử lý dữ liệu
```

## Kết luận

Giai đoạn 4 đã triển khai thành công hệ thống RAG sẵn sàng production với:
- ✅ Tìm kiếm sản phẩm ngữ nghĩa
- ✅ Gợi ý độ tương đồng vector
- ✅ Giao diện chatbot hội thoại
- ✅ Hỗ trợ tiếng Việt
- ✅ Truy xuất nhanh dựa trên FAISS

**Trạng thái**: HOÀN THÀNH ✅  
**Giai đoạn tiếp theo**: Giai đoạn 5 - Hệ thống gợi ý kết hợp

---

**Được tạo**: 2026-04-28  
**Mô hình**: paraphrase-multilingual-MiniLM-L12-v2  
**Cơ sở dữ liệu Vector**: FAISS  
**Sản phẩm đã lập chỉ mục**: 50  
**Chiều Embedding**: 384
