"""
Data Generator for Multi-Model AI System
Tạo 5 tệp dữ liệu realistic cho training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class DataGenerator:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.num_users = 500
        self.num_products = 100
        self.num_categories = 10
        self.num_interactions = 10000
        
        self.categories = [
            "Điện thoại & Tablet",
            "Laptop & Máy tính",
            "Âm thanh & Phụ kiện",
            "Thời trang Nam",
            "Thời trang Nữ",
            "Đồ gia dụng",
            "Sách & Văn phòng phẩm",
            "Thể thao & Du lịch",
            "Mẹ & Bé",
            "Làm đẹp & Sức khỏe"
        ]
        
        self.brands = {
            "Điện thoại & Tablet": ["Samsung", "Apple", "Xiaomi", "Oppo", "Vivo"],
            "Laptop & Máy tính": ["Dell", "HP", "Asus", "Lenovo", "Acer"],
            "Âm thanh & Phụ kiện": ["Sony", "JBL", "Bose", "Anker", "Logitech"],
            "Thời trang Nam": ["Nike", "Adidas", "Puma", "Uniqlo", "H&M"],
            "Thời trang Nữ": ["Zara", "H&M", "Forever21", "Mango", "Uniqlo"]
        }
        
        self.actions = ["view", "click", "add_to_cart", "purchase", "remove_from_cart"]
        self.devices = ["mobile", "desktop", "tablet"]
        
    def generate_product_features(self):
        """1. Tạo product_features.csv"""
        print("📊 Generating product_features.csv...")
        
        products = []
        for product_id in range(1, self.num_products + 1):
            category = random.choice(self.categories)
            brand = random.choice(self.brands.get(category, ["Generic"]))
            
            # Price ranges by category
            if category in ["Điện thoại & Tablet", "Laptop & Máy tính"]:
                price = random.randint(5000000, 30000000)
            elif category in ["Âm thanh & Phụ kiện"]:
                price = random.randint(500000, 5000000)
            else:
                price = random.randint(100000, 2000000)
            
            product = {
                "product_id": product_id,
                "category": category,
                "brand": brand,
                "price": price,
                "stock": random.randint(10, 200),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "num_reviews": random.randint(0, 500),
                "discount": round(random.uniform(0, 0.3), 2),
                "is_new": random.choice([0, 1]),
                "popularity_score": round(random.uniform(0.1, 1.0), 2)
            }
            products.append(product)
        
        df = pd.DataFrame(products)
        df.to_csv(self.data_dir / "product_features.csv", index=False)
        print(f"  ✅ Created: {len(df)} products")
        return df
    
    def generate_user_behavior(self, product_df):
        """2. Tạo user_behavior.csv (Enhanced)"""
        print("📊 Generating user_behavior.csv...")
        
        behaviors = []
        start_date = datetime.now() - timedelta(days=90)
        
        for _ in range(self.num_interactions):
            user_id = random.randint(1, self.num_users)
            product = product_df.sample(1).iloc[0]
            
            # Simulate user journey
            action_sequence = self._simulate_user_journey()
            
            for i, action in enumerate(action_sequence):
                timestamp = start_date + timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                behavior = {
                    "user_id": user_id,
                    "product_id": product["product_id"],
                    "action": action,
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "category": product["category"],
                    "price": product["price"],
                    "session_id": f"sess_{user_id}_{random.randint(1000, 9999)}"
                }
                behaviors.append(behavior)
        
        df = pd.DataFrame(behaviors)
        df = df.sort_values(["user_id", "timestamp"])
        df.to_csv(self.data_dir / "user_behavior.csv", index=False)
        print(f"  ✅ Created: {len(df)} behavior records")
        return df
    
    def _simulate_user_journey(self):
        """Simulate realistic user journey"""
        # 70% just view
        # 20% view -> click
        # 8% view -> click -> add_to_cart
        # 2% view -> click -> add_to_cart -> purchase
        
        rand = random.random()
        if rand < 0.70:
            return ["view"]
        elif rand < 0.90:
            return ["view", "click"]
        elif rand < 0.98:
            return ["view", "click", "add_to_cart"]
        else:
            return ["view", "click", "add_to_cart", "purchase"]
    
    def generate_user_ratings(self, product_df):
        """3. Tạo user_ratings.csv"""
        print("📊 Generating user_ratings.csv...")
        
        ratings = []
        num_ratings = 3000
        start_date = datetime.now() - timedelta(days=90)
        
        review_templates = [
            "Sản phẩm tuyệt vời!",
            "Chất lượng tốt, giá hợp lý",
            "Đáng đồng tiền",
            "Rất hài lòng",
            "Giao hàng nhanh",
            "Đóng gói cẩn thận",
            "Sản phẩm như mô tả",
            "Tạm được",
            "Không như mong đợi",
            "Cần cải thiện"
        ]
        
        for _ in range(num_ratings):
            user_id = random.randint(1, self.num_users)
            product = product_df.sample(1).iloc[0]
            
            # Rating correlates with product rating
            base_rating = product["rating"]
            rating = max(1, min(5, int(np.random.normal(base_rating, 0.5))))
            
            timestamp = start_date + timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23)
            )
            
            rating_record = {
                "user_id": user_id,
                "product_id": product["product_id"],
                "rating": rating,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "review_text": random.choice(review_templates)
            }
            ratings.append(rating_record)
        
        df = pd.DataFrame(ratings)
        df = df.sort_values(["user_id", "timestamp"])
        df.to_csv(self.data_dir / "user_ratings.csv", index=False)
        print(f"  ✅ Created: {len(df)} ratings")
        return df
    
    def generate_product_interactions(self, product_df):
        """4. Tạo product_interactions.csv"""
        print("📊 Generating product_interactions.csv...")
        
        interactions = []
        num_interactions = 15000
        start_date = datetime.now() - timedelta(days=90)
        
        interaction_types = [
            "view", "zoom", "scroll", "click_image", 
            "add_to_cart", "add_to_wishlist", "share", "compare"
        ]
        
        for _ in range(num_interactions):
            user_id = random.randint(1, self.num_users)
            product = product_df.sample(1).iloc[0]
            session_id = f"sess_{random.randint(10000, 99999)}"
            
            interaction = {
                "user_id": user_id,
                "product_id": product["product_id"],
                "interaction_type": random.choice(interaction_types),
                "duration_seconds": random.randint(5, 300),
                "session_id": session_id,
                "device": random.choice(self.devices),
                "timestamp": (start_date + timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )).strftime("%Y-%m-%d %H:%M:%S")
            }
            interactions.append(interaction)
        
        df = pd.DataFrame(interactions)
        df = df.sort_values(["user_id", "timestamp"])
        df.to_csv(self.data_dir / "product_interactions.csv", index=False)
        print(f"  ✅ Created: {len(df)} interactions")
        return df
    
    def generate_category_trends(self):
        """5. Tạo category_trends.csv"""
        print("📊 Generating category_trends.csv...")
        
        trends = []
        start_date = datetime.now() - timedelta(days=90)
        
        for day in range(90):
            date = start_date + timedelta(days=day)
            
            for category in self.categories:
                # Simulate trends with some randomness
                base_views = random.randint(500, 3000)
                base_purchases = int(base_views * random.uniform(0.05, 0.15))
                
                # Weekend boost
                if date.weekday() >= 5:
                    base_views = int(base_views * 1.3)
                    base_purchases = int(base_purchases * 1.2)
                
                # Category-specific avg price
                if category in ["Điện thoại & Tablet", "Laptop & Máy tính"]:
                    avg_price = random.randint(8000000, 20000000)
                elif category in ["Âm thanh & Phụ kiện"]:
                    avg_price = random.randint(1000000, 3000000)
                else:
                    avg_price = random.randint(300000, 1000000)
                
                trending_score = round(random.uniform(0.3, 1.0), 2)
                
                trend = {
                    "date": date.strftime("%Y-%m-%d"),
                    "category": category,
                    "view_count": base_views,
                    "purchase_count": base_purchases,
                    "avg_price": avg_price,
                    "trending_score": trending_score
                }
                trends.append(trend)
        
        df = pd.DataFrame(trends)
        df = df.sort_values(["date", "category"])
        df.to_csv(self.data_dir / "category_trends.csv", index=False)
        print(f"  ✅ Created: {len(df)} trend records")
        return df
    
    def generate_all(self):
        """Generate all 5 datasets"""
        print("\n" + "="*60)
        print("🚀 GENERATING 5 DATASETS FOR MULTI-MODEL AI")
        print("="*60 + "\n")
        
        # 1. Product Features (base data)
        product_df = self.generate_product_features()
        
        # 2. User Behavior (based on products)
        behavior_df = self.generate_user_behavior(product_df)
        
        # 3. User Ratings (based on products)
        ratings_df = self.generate_user_ratings(product_df)
        
        # 4. Product Interactions (based on products)
        interactions_df = self.generate_product_interactions(product_df)
        
        # 5. Category Trends (independent)
        trends_df = self.generate_category_trends()
        
        print("\n" + "="*60)
        print("✅ ALL DATASETS GENERATED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📁 Output directory: {self.data_dir}/")
        print(f"📊 Files created:")
        print(f"   1. product_features.csv     ({len(product_df)} records)")
        print(f"   2. user_behavior.csv        ({len(behavior_df)} records)")
        print(f"   3. user_ratings.csv         ({len(ratings_df)} records)")
        print(f"   4. product_interactions.csv ({len(interactions_df)} records)")
        print(f"   5. category_trends.csv      ({len(trends_df)} records)")
        print(f"\n💾 Total data points: {len(product_df) + len(behavior_df) + len(ratings_df) + len(interactions_df) + len(trends_df)}")
        
        return {
            "products": product_df,
            "behavior": behavior_df,
            "ratings": ratings_df,
            "interactions": interactions_df,
            "trends": trends_df
        }
    
    def print_statistics(self):
        """Print dataset statistics"""
        print("\n" + "="*60)
        print("📊 DATASET STATISTICS")
        print("="*60 + "\n")
        
        files = [
            "product_features.csv",
            "user_behavior.csv",
            "user_ratings.csv",
            "product_interactions.csv",
            "category_trends.csv"
        ]
        
        for file in files:
            filepath = self.data_dir / file
            if filepath.exists():
                df = pd.read_csv(filepath)
                print(f"📄 {file}")
                print(f"   Rows: {len(df)}")
                print(f"   Columns: {len(df.columns)}")
                print(f"   Size: {filepath.stat().st_size / 1024:.2f} KB")
                print()

if __name__ == "__main__":
    generator = DataGenerator(data_dir="data")
    datasets = generator.generate_all()
    generator.print_statistics()
