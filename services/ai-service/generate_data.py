"""
Generate synthetic user behavior data for AI training
This script creates realistic user interaction patterns
"""
import csv
import random
from datetime import datetime, timedelta

# Configuration
NUM_USERS = 100
NUM_PRODUCTS = 50  # We have 50 products from seed data
ACTIONS = ['view', 'add_to_cart', 'purchase']
ACTION_WEIGHTS = [0.6, 0.3, 0.1]  # view > add_to_cart > purchase

# Product IDs from our seeded data (1-50)
PRODUCT_IDS = list(range(1, NUM_PRODUCTS + 1))

# Categories mapping (for realistic behavior patterns)
CATEGORIES = {
    'Điện thoại & Tablet': list(range(1, 6)),
    'Laptop & Máy tính': list(range(6, 11)),
    'Âm thanh & Phụ kiện': list(range(11, 16)),
    'Thời trang Nam': list(range(16, 21)),
    'Thời trang Nữ': list(range(21, 26)),
    'Đồ gia dụng': list(range(26, 31)),
    'Sách & Văn phòng phẩm': list(range(31, 36)),
    'Thể thao & Du lịch': list(range(36, 41)),
    'Mẹ & Bé': list(range(41, 46)),
    'Làm đẹp & Sức khỏe': list(range(46, 51)),
}

def generate_user_behavior():
    """Generate realistic user behavior data"""
    behaviors = []
    
    # Start date: 3 months ago
    start_date = datetime.now() - timedelta(days=90)
    
    for user_id in range(1, NUM_USERS + 1):
        # Each user has interest in 1-3 categories
        interested_categories = random.sample(list(CATEGORIES.keys()), k=random.randint(1, 3))
        interested_products = []
        for cat in interested_categories:
            interested_products.extend(CATEGORIES[cat])
        
        # Generate 5-30 interactions per user
        num_interactions = random.randint(5, 30)
        
        # User's current timestamp
        user_time = start_date + timedelta(days=random.randint(0, 60))
        
        for _ in range(num_interactions):
            # 70% chance to interact with interested products, 30% random
            if random.random() < 0.7 and interested_products:
                product_id = random.choice(interested_products)
            else:
                product_id = random.choice(PRODUCT_IDS)
            
            # Choose action based on weights
            action = random.choices(ACTIONS, weights=ACTION_WEIGHTS)[0]
            
            # Add timestamp (increment by 1-60 minutes)
            user_time += timedelta(minutes=random.randint(1, 60))
            
            behaviors.append({
                'user_id': user_id,
                'product_id': product_id,
                'action': action,
                'timestamp': user_time.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Sort by timestamp
    behaviors.sort(key=lambda x: x['timestamp'])
    
    return behaviors

def save_to_csv(behaviors, filename='data/user_behavior.csv'):
    """Save behaviors to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['user_id', 'product_id', 'action', 'timestamp'])
        writer.writeheader()
        writer.writerows(behaviors)
    
    print(f"✅ Generated {len(behaviors)} behavior records")
    print(f"✅ Saved to {filename}")

if __name__ == '__main__':
    print("🔄 Generating user behavior data...")
    behaviors = generate_user_behavior()
    save_to_csv(behaviors)
    
    # Print statistics
    print("\n📊 Statistics:")
    print(f"   Total users: {NUM_USERS}")
    print(f"   Total products: {NUM_PRODUCTS}")
    print(f"   Total interactions: {len(behaviors)}")
    
    action_counts = {}
    for b in behaviors:
        action_counts[b['action']] = action_counts.get(b['action'], 0) + 1
    
    print(f"   Actions breakdown:")
    for action, count in action_counts.items():
        print(f"      {action}: {count} ({count/len(behaviors)*100:.1f}%)")
