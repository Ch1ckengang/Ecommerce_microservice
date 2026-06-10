# Giai đoạn 1: Chuẩn bị Dữ liệu ✅

## Tổng quan
Giai đoạn 1 chuẩn bị dữ liệu huấn luyện cho mô hình gợi ý LSTM bằng cách tạo dữ liệu hành vi người dùng tổng hợp và tiền xử lý thành các mẫu huấn luyện.

## Các nhiệm vụ đã hoàn thành

### ✅ Nhiệm vụ 1.1: Tạo tập dữ liệu
- **File**: `generate_data.py`
- **Đầu ra**: `data/user_behavior.csv`
- **Mô tả**: Tạo dữ liệu hành vi người dùng thực tế với:
  - 100 người dùng
  - 50 sản phẩm (khớp với dữ liệu đã seed)
  - 3 loại hành động: xem, thêm vào giỏ, mua hàng
  - Mẫu thực tế dựa trên sở thích người dùng theo danh mục
  - Dấu thời gian trải dài 3 tháng

**Định dạng CSV**:
```csv
user_id,product_id,action,timestamp
1,15,view,2024-01-28 10:15:30
1,15,add_to_cart,2024-01-28 10:45:12
1,23,view,2024-01-28 11:20:45
```

### ✅ Nhiệm vụ 1.2: Tiền xử lý dữ liệu
- **File**: `src/data_preprocessing.py`
- **Hàm**: `group_by_user()`
- **Mô tả**: 
  - Nhóm các tương tác theo user_id
  - Sắp xếp theo thời gian
  - Chuyển đổi product_ids thành chỉ số
  - Tạo từ điển ánh xạ sản phẩm

**Ví dụ**:
```python
User 1 → [15, 15, 23, 8, 12, 45, ...]
User 2 → [3, 7, 7, 9, 22, ...]
```

### ✅ Nhiệm vụ 1.3: Tạo mẫu huấn luyện
- **Hàm**: `create_training_samples()`
- **Mô tả**:
  - Chuyển đổi chuỗi thành các cặp đầu vào-đầu ra
  - Đầu vào: sequence[:-1]
  - Đầu ra: sản phẩm tiếp theo
  - Hỗ trợ độ dài chuỗi biến đổi (3-20)

**Ví dụ**:
```python
Chuỗi: [15, 15, 23, 8, 12]

Mẫu huấn luyện:
Đầu vào: [15, 15]        → Đầu ra: 23
Đầu vào: [15, 15, 23]    → Đầu ra: 8
Đầu vào: [15, 15, 23, 8] → Đầu ra: 12
```

## Các file được tạo

```
data/
├── user_behavior.csv    # Dữ liệu hành vi thô (~1500-3000 bản ghi)
├── mappings.pkl         # Ánh xạ Product ID ↔ Index
├── X_train.npy         # Chuỗi đầu vào đã padding (shape: [N, 20])
└── y_train.npy         # Sản phẩm mục tiêu (shape: [N])
```

## Cách chạy

### Yêu cầu
```bash
cd services/ai-service
pip install pandas numpy
```

### Thực thi Giai đoạn 1
```bash
python run_phase1.py
```

### Kết quả mong đợi
```
📌 GIAI ĐOẠN 1 — CHUẨN BỊ DỮ LIỆU
==================================================
Nhiệm vụ 1.1: Tạo tập dữ liệu
✅ Đã tạo 1847 bản ghi hành vi
✅ Đã lưu vào data/user_behavior.csv

📊 Thống kê:
   Tổng người dùng: 100
   Tổng sản phẩm: 50
   Tổng tương tác: 1847
   Phân loại hành động:
      view: 1108 (60.0%)
      add_to_cart: 554 (30.0%)
      purchase: 185 (10.0%)

Nhiệm vụ 1.2 & 1.3: Tiền xử lý dữ liệu
📂 Đang tải dữ liệu từ CSV...
   Đã tải 1847 bản ghi
🔢 Đang tạo ánh xạ sản phẩm...
   Tổng sản phẩm duy nhất: 50
   Kích thước từ vựng (với padding): 51
👥 Đang nhóm theo người dùng...
   Tổng người dùng: 100
🎯 Đang tạo mẫu huấn luyện...
   Đã tạo 1747 mẫu huấn luyện
📏 Đang padding chuỗi đến độ dài 20...
   Shape sau padding: (1747, 20)

✅ GIAI ĐOẠN 1 HOÀN THÀNH!
```

## Thống kê dữ liệu

- **Người dùng**: 100
- **Sản phẩm**: 50
- **Tương tác**: ~1500-3000 (thay đổi mỗi lần chạy)
- **Mẫu huấn luyện**: ~1500-2500
- **Độ dài chuỗi**: Tối đa 20 (đã padding)
- **Kích thước từ vựng**: 51 (50 sản phẩm + 1 padding)

## Bước tiếp theo

Giai đoạn 1 đã hoàn thành! Dữ liệu đã sẵn sàng cho:
- **Giai đoạn 2**: Huấn luyện mô hình LSTM
- Các mẫu huấn luyện đã được định dạng đúng
- Ánh xạ sản phẩm đã được lưu để suy luận
- Dữ liệu đã được chuẩn hóa và padding

## Cấu trúc code

```python
# Pipeline tiền xử lý chính
preprocessor = DataPreprocessor('data/user_behavior.csv')
preprocessor.load_data()
preprocessor.create_product_mapping()
preprocessor.group_by_user()
X, y = preprocessor.create_training_samples()
X_padded = preprocessor.pad_sequences(X)
preprocessor.save_mappings()
```

## Xác thực

Để xác minh Giai đoạn 1 đã hoàn thành:
```bash
ls -lh data/
# Nên hiển thị:
# - user_behavior.csv
# - mappings.pkl
# - X_train.npy
# - y_train.npy
```

---

**Trạng thái**: ✅ Hoàn thành và đã kiểm tra
**Sẵn sàng cho**: Giai đoạn 2 - Huấn luyện mô hình LSTM
