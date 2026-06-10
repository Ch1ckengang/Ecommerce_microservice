#!/bin/bash

echo "🔍 KIỂM TRA BỘ LỌC DANH MỤC"
echo "================================"
echo ""

# Test các danh mục khác nhau
categories=(
  "Laptop & Máy tính"
  "Điện thoại & Tablet"
  "Thời trang Nam"
  "Thời trang Nữ"
  "Âm thanh & Phụ kiện"
)

echo "📊 Kiểm tra từng danh mục:"
echo ""

for category in "${categories[@]}"; do
  # URL encode category
  encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$category'))")
  
  # Get product count from HTML
  count=$(curl -s "http://localhost:8007/products/?category=$encoded" 2>/dev/null | grep -o "Tìm thấy [0-9]* sản phẩm" | grep -o "[0-9]*")
  
  # Get actual product cards
  cards=$(curl -s "http://localhost:8007/products/?category=$encoded" 2>/dev/null | grep -o 'class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition product-card"' | wc -l)
  
  if [ "$count" = "$cards" ] && [ "$count" -gt 0 ]; then
    echo "✅ $category: $count sản phẩm (khớp với $cards cards)"
  elif [ "$count" = "$cards" ]; then
    echo "⚠️  $category: 0 sản phẩm (có thể chưa có data)"
  else
    echo "❌ $category: KHÔNG KHỚP (count=$count, cards=$cards)"
  fi
done

echo ""
echo "================================"
echo "✅ Kiểm tra hoàn tất!"
