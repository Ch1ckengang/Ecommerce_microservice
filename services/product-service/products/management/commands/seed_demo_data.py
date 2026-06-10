from django.core.management.base import BaseCommand
from products.models import Category, Product


class Command(BaseCommand):
    help = "Seed database with demo product data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # Create categories - 10 categories
        categories_data = [
            {"name": "Điện thoại & Tablet", "description": "Smartphone, tablet và phụ kiện"},
            {"name": "Laptop & Máy tính", "description": "Laptop, PC và linh kiện máy tính"},
            {"name": "Âm thanh & Phụ kiện", "description": "Tai nghe, loa và phụ kiện âm thanh"},
            {"name": "Thời trang Nam", "description": "Quần áo, giày dép nam"},
            {"name": "Thời trang Nữ", "description": "Quần áo, giày dép nữ"},
            {"name": "Đồ gia dụng", "description": "Đồ dùng nhà bếp và gia đình"},
            {"name": "Sách & Văn phòng phẩm", "description": "Sách, vở, dụng cụ văn phòng"},
            {"name": "Thể thao & Du lịch", "description": "Dụng cụ thể thao và đồ du lịch"},
            {"name": "Mẹ & Bé", "description": "Đồ dùng cho mẹ và bé"},
            {"name": "Làm đẹp & Sức khỏe", "description": "Mỹ phẩm và sản phẩm chăm sóc sức khỏe"},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={"description": cat_data["description"]}
            )
            categories[cat_data["name"]] = category
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Create products - 50 products across 10 categories
        products_data = [
            # Điện thoại & Tablet (5 products)
            {"name": "iPhone 15 Pro Max 256GB", "category": "Điện thoại & Tablet", "price": "29990000", "stock": 50, "sku": "PHONE-001", "description": "iPhone 15 Pro Max với chip A17 Pro, camera 48MP, màn hình 6.7 inch"},
            {"name": "Samsung Galaxy S24 Ultra", "category": "Điện thoại & Tablet", "price": "27990000", "stock": 45, "sku": "PHONE-002", "description": "Galaxy S24 Ultra với S Pen, camera 200MP, màn hình Dynamic AMOLED 6.8 inch"},
            {"name": "iPad Air M2 128GB", "category": "Điện thoại & Tablet", "price": "16990000", "stock": 30, "sku": "PHONE-003", "description": "iPad Air với chip M2, màn hình Liquid Retina 10.9 inch"},
            {"name": "Xiaomi 14 Pro 512GB", "category": "Điện thoại & Tablet", "price": "19990000", "stock": 60, "sku": "PHONE-004", "description": "Xiaomi 14 Pro với Snapdragon 8 Gen 3, camera Leica 50MP"},
            {"name": "OPPO Find X7 Ultra", "category": "Điện thoại & Tablet", "price": "24990000", "stock": 40, "sku": "PHONE-005", "description": "OPPO Find X7 Ultra với camera Hasselblad, màn hình AMOLED 120Hz"},
            
            # Laptop & Máy tính (5 products)
            {"name": "MacBook Pro 14 M3 Pro", "category": "Laptop & Máy tính", "price": "52990000", "stock": 25, "sku": "LAPTOP-001", "description": "MacBook Pro 14 inch với chip M3 Pro, RAM 18GB, SSD 512GB"},
            {"name": "Dell XPS 15 9530", "category": "Laptop & Máy tính", "price": "45990000", "stock": 30, "sku": "LAPTOP-002", "description": "Dell XPS 15 với Intel Core i7-13700H, RTX 4060, màn hình 4K OLED"},
            {"name": "ASUS ROG Strix G16", "category": "Laptop & Máy tính", "price": "38990000", "stock": 35, "sku": "LAPTOP-003", "description": "ASUS ROG gaming laptop với RTX 4070, Intel i9-13980HX, màn hình 240Hz"},
            {"name": "Lenovo ThinkPad X1 Carbon", "category": "Laptop & Máy tính", "price": "42990000", "stock": 20, "sku": "LAPTOP-004", "description": "ThinkPad X1 Carbon Gen 11, Intel Core i7, RAM 32GB, siêu nhẹ 1.12kg"},
            {"name": "HP Pavilion 15", "category": "Laptop & Máy tính", "price": "18990000", "stock": 50, "sku": "LAPTOP-005", "description": "HP Pavilion 15 với AMD Ryzen 7, RAM 16GB, SSD 512GB"},
            
            # Âm thanh & Phụ kiện (5 products)
            {"name": "AirPods Pro 2", "category": "Âm thanh & Phụ kiện", "price": "6490000", "stock": 100, "sku": "AUDIO-001", "description": "AirPods Pro thế hệ 2 với chip H2, chống ồn chủ động"},
            {"name": "Sony WH-1000XM5", "category": "Âm thanh & Phụ kiện", "price": "8990000", "stock": 80, "sku": "AUDIO-002", "description": "Tai nghe Sony cao cấp với chống ồn hàng đầu, pin 30 giờ"},
            {"name": "JBL Flip 6", "category": "Âm thanh & Phụ kiện", "price": "2990000", "stock": 120, "sku": "AUDIO-003", "description": "Loa Bluetooth JBL chống nước IP67, âm thanh mạnh mẽ"},
            {"name": "Logitech MX Master 3S", "category": "Âm thanh & Phụ kiện", "price": "2490000", "stock": 150, "sku": "AUDIO-004", "description": "Chuột không dây cao cấp với 8 nút lập trình, pin 70 ngày"},
            {"name": "Keychron K8 Pro", "category": "Âm thanh & Phụ kiện", "price": "3290000", "stock": 90, "sku": "AUDIO-005", "description": "Bàn phím cơ không dây, hot-swap, RGB"},
            
            # Thời trang Nam (5 products)
            {"name": "Áo Polo Nam Premium", "category": "Thời trang Nam", "price": "450000", "stock": 200, "sku": "MENFASH-001", "description": "Áo polo nam cotton cao cấp, form slim fit, nhiều màu"},
            {"name": "Quần Jean Nam Slim Fit", "category": "Thời trang Nam", "price": "650000", "stock": 180, "sku": "MENFASH-002", "description": "Quần jean nam co giãn nhẹ, form slim fit hiện đại"},
            {"name": "Giày Sneaker Nam", "category": "Thời trang Nam", "price": "1290000", "stock": 150, "sku": "MENFASH-003", "description": "Giày sneaker nam da thật, đế cao su êm ái"},
            {"name": "Áo Khoác Bomber Nam", "category": "Thời trang Nam", "price": "890000", "stock": 100, "sku": "MENFASH-004", "description": "Áo khoác bomber nam chống nước, nhiều túi tiện dụng"},
            {"name": "Balo Laptop Nam", "category": "Thời trang Nam", "price": "750000", "stock": 120, "sku": "MENFASH-005", "description": "Balo laptop 15.6 inch, chống nước, nhiều ngăn"},
            
            # Thời trang Nữ (5 products)
            {"name": "Váy Maxi Nữ", "category": "Thời trang Nữ", "price": "550000", "stock": 150, "sku": "WOMENFASH-001", "description": "Váy maxi nữ vải lụa mềm mại, họa tiết hoa nhẹ nhàng"},
            {"name": "Áo Sơ Mi Nữ", "category": "Thời trang Nữ", "price": "380000", "stock": 200, "sku": "WOMENFASH-002", "description": "Áo sơ mi nữ công sở, vải cotton thoáng mát"},
            {"name": "Giày Cao Gót 7cm", "category": "Thời trang Nữ", "price": "890000", "stock": 100, "sku": "WOMENFASH-003", "description": "Giày cao gót nữ da bóng, gót 7cm thanh lịch"},
            {"name": "Túi Xách Nữ", "category": "Thời trang Nữ", "price": "1250000", "stock": 80, "sku": "WOMENFASH-004", "description": "Túi xách nữ da PU cao cấp, nhiều ngăn tiện dụng"},
            {"name": "Đầm Công Sở", "category": "Thời trang Nữ", "price": "680000", "stock": 120, "sku": "WOMENFASH-005", "description": "Đầm công sở nữ form A thanh lịch, nhiều màu"},
            
            # Đồ gia dụng (5 products)
            {"name": "Nồi Cơm Điện Tử 1.8L", "category": "Đồ gia dụng", "price": "1890000", "stock": 60, "sku": "HOME-001", "description": "Nồi cơm điện tử Sharp 1.8L, 10 chức năng nấu"},
            {"name": "Máy Xay Sinh Tố", "category": "Đồ gia dụng", "price": "890000", "stock": 80, "sku": "HOME-002", "description": "Máy xay sinh tố công suất 600W, cối thủy tinh"},
            {"name": "Bộ Nồi Inox 5 Món", "category": "Đồ gia dụng", "price": "2490000", "stock": 50, "sku": "HOME-003", "description": "Bộ nồi inox 304 cao cấp, đáy 3 lớp, dùng bếp từ"},
            {"name": "Máy Hút Bụi Không Dây", "category": "Đồ gia dụng", "price": "3990000", "stock": 40, "sku": "HOME-004", "description": "Máy hút bụi cầm tay không dây, pin 60 phút"},
            {"name": "Bình Đun Siêu Tốc 1.7L", "category": "Đồ gia dụng", "price": "450000", "stock": 100, "sku": "HOME-005", "description": "Bình đun siêu tốc inox 1.7L, tự ngắt khi sôi"},
            
            # Sách & Văn phòng phẩm (5 products)
            {"name": "Sách Đắc Nhân Tâm", "category": "Sách & Văn phòng phẩm", "price": "89000", "stock": 300, "sku": "BOOK-001", "description": "Sách Đắc Nhân Tâm - Dale Carnegie, bìa cứng"},
            {"name": "Sách Nhà Giả Kim", "category": "Sách & Văn phòng phẩm", "price": "79000", "stock": 250, "sku": "BOOK-002", "description": "Nhà Giả Kim - Paulo Coelho, tái bản 2024"},
            {"name": "Bộ Bút Gel 10 Màu", "category": "Sách & Văn phòng phẩm", "price": "45000", "stock": 500, "sku": "BOOK-003", "description": "Bộ bút gel Thiên Long 10 màu, mực không lem"},
            {"name": "Vở Kẻ Ngang 200 Trang", "category": "Sách & Văn phòng phẩm", "price": "25000", "stock": 600, "sku": "BOOK-004", "description": "Vở kẻ ngang Campus 200 trang, giấy trắng mịn"},
            {"name": "Máy Tính Casio FX-580VN X", "category": "Sách & Văn phòng phẩm", "price": "650000", "stock": 150, "sku": "BOOK-005", "description": "Máy tính Casio khoa học, 552 chức năng"},
            
            # Thể thao & Du lịch (5 products)
            {"name": "Thảm Yoga TPE 8mm", "category": "Thể thao & Du lịch", "price": "350000", "stock": 200, "sku": "SPORT-001", "description": "Thảm yoga TPE 8mm chống trượt, kèm túi đựng"},
            {"name": "Bóng Đá Size 5", "category": "Thể thao & Du lịch", "price": "280000", "stock": 150, "sku": "SPORT-002", "description": "Bóng đá Động Lực size 5, da PU cao cấp"},
            {"name": "Vợt Cầu Lông Yonex", "category": "Thể thao & Du lịch", "price": "1890000", "stock": 80, "sku": "SPORT-003", "description": "Vợt cầu lông Yonex Nanoflare 800, khung carbon"},
            {"name": "Ba Lô Du Lịch 50L", "category": "Thể thao & Du lịch", "price": "890000", "stock": 100, "sku": "SPORT-004", "description": "Ba lô du lịch 50L chống nước, nhiều ngăn"},
            {"name": "Giày Chạy Bộ Nike", "category": "Thể thao & Du lịch", "price": "2490000", "stock": 120, "sku": "SPORT-005", "description": "Giày chạy bộ Nike Air Zoom, đế êm nhẹ"},
            
            # Mẹ & Bé (5 products)
            {"name": "Tã Bỉm Pampers Newborn", "category": "Mẹ & Bé", "price": "320000", "stock": 200, "sku": "BABY-001", "description": "Tã bỉm Pampers Newborn 84 miếng, siêu thấm"},
            {"name": "Bình Sữa Comotomo 250ml", "category": "Mẹ & Bé", "price": "450000", "stock": 150, "sku": "BABY-002", "description": "Bình sữa silicon Comotomo 250ml, chống sặc"},
            {"name": "Xe Đẩy Em Bé 2 Chiều", "category": "Mẹ & Bé", "price": "3990000", "stock": 50, "sku": "BABY-003", "description": "Xe đẩy em bé 2 chiều, gấp gọn, có mái che"},
            {"name": "Nôi Điện Tự Động", "category": "Mẹ & Bé", "price": "2890000", "stock": 40, "sku": "BABY-004", "description": "Nôi điện tự động ru, có nhạc và điều khiển"},
            {"name": "Bộ Đồ Chơi Xếp Hình", "category": "Mẹ & Bé", "price": "180000", "stock": 300, "sku": "BABY-005", "description": "Bộ đồ chơi xếp hình 100 chi tiết, an toàn"},
            
            # Làm đẹp & Sức khỏe (5 products)
            {"name": "Kem Chống Nắng Anessa", "category": "Làm đẹp & Sức khỏe", "price": "550000", "stock": 180, "sku": "BEAUTY-001", "description": "Kem chống nắng Anessa SPF50+ PA++++, chống nước"},
            {"name": "Serum Vitamin C", "category": "Làm đẹp & Sức khỏe", "price": "680000", "stock": 150, "sku": "BEAUTY-002", "description": "Serum Vitamin C 20%, làm sáng da, mờ thâm"},
            {"name": "Máy Massage Cầm Tay", "category": "Làm đẹp & Sức khỏe", "price": "890000", "stock": 100, "sku": "BEAUTY-003", "description": "Máy massage cầm tay 6 đầu, 20 cấp độ"},
            {"name": "Viên Uống Collagen", "category": "Làm đẹp & Sức khỏe", "price": "750000", "stock": 200, "sku": "BEAUTY-004", "description": "Viên uống Collagen Nhật Bản, hộp 30 viên"},
            {"name": "Máy Đo Huyết Áp Omron", "category": "Làm đẹp & Sức khỏe", "price": "1290000", "stock": 80, "sku": "BEAUTY-005", "description": "Máy đo huyết áp bắp tay Omron, chính xác cao"},
        ]

        for prod_data in products_data:
            category = categories[prod_data["category"]]
            product, created = Product.objects.get_or_create(
                sku=prod_data["sku"],
                defaults={
                    "name": prod_data["name"],
                    "category": category,
                    "price": prod_data["price"],
                    "stock": prod_data["stock"],
                    "description": prod_data["description"],
                    "is_active": True,
                }
            )
            if created:
                self.stdout.write(f"Created product: {product.name}")

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
