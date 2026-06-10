"""
RAG System for Product Recommendation
Uses sentence-transformers for embeddings and FAISS for vector search
"""
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import pickle
import json

class ProductRAG:
    """
    RAG System for product search and recommendation
    
    Components:
    - Sentence Transformer: Generate embeddings
    - FAISS: Vector similarity search
    - Product Database: Store product information
    """
    
    def __init__(
        self,
        model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2',
        embedding_dim: int = 384
    ):
        """
        Initialize RAG system
        
        Args:
            model_name: Sentence transformer model name
            embedding_dim: Embedding dimension
        """
        print(f"🔄 Loading sentence transformer: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = embedding_dim
        
        # FAISS index
        self.index = None
        
        # Product database
        self.products = []  # List of product dicts
        self.product_ids = []  # List of product IDs
        
        print(f"✅ RAG system initialized")
        print(f"   Model: {model_name}")
        print(f"   Embedding dim: {embedding_dim}")
    
    def generate_product_text(self, product: Dict) -> str:
        """
        Generate searchable text from product information
        
        Args:
            product: Product dictionary
            
        Returns:
            Concatenated text for embedding
        """
        # Combine product fields into searchable text
        text_parts = []
        
        if 'name' in product:
            text_parts.append(product['name'])
        
        if 'category' in product:
            text_parts.append(f"Danh mục: {product['category']}")
        
        if 'description' in product:
            text_parts.append(product['description'])
        
        if 'price' in product:
            text_parts.append(f"Giá: {product['price']} VNĐ")
        
        return " | ".join(text_parts)
    
    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            
        Returns:
            Embeddings array [N, embedding_dim]
        """
        print(f"\n🔄 Generating embeddings for {len(texts)} texts...")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        print(f"✅ Generated embeddings: {embeddings.shape}")
        
        return embeddings
    
    def build_index(
        self,
        products: List[Dict],
        use_gpu: bool = False
    ):
        """
        Build FAISS index from products
        
        Args:
            products: List of product dictionaries
            use_gpu: Use GPU for FAISS (if available)
        """
        print(f"\n🏗️  Building FAISS index...")
        print(f"   Products: {len(products)}")
        
        # Store products
        self.products = products
        self.product_ids = [p['product_id'] for p in products]
        
        # Generate texts
        texts = [self.generate_product_text(p) for p in products]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index
        if use_gpu and faiss.get_num_gpus() > 0:
            print("   Using GPU for FAISS")
            res = faiss.StandardGpuResources()
            self.index = faiss.GpuIndexFlatIP(res, self.embedding_dim)
        else:
            print("   Using CPU for FAISS")
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product (cosine similarity)
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        print(f"✅ FAISS index built")
        print(f"   Total vectors: {self.index.ntotal}")
    
    def search(
        self,
        query: str,
        k: int = 10
    ) -> List[Tuple[int, float, Dict]]:
        """
        Search for products using text query
        
        Args:
            query: Search query text
            k: Number of results
            
        Returns:
            List of (product_id, score, product_info) tuples
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Prepare results
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.products):
                product = self.products[idx]
                product_id = self.product_ids[idx]
                results.append((product_id, float(score), product))
        
        return results
    
    def recommend_by_product(
        self,
        product_id: int,
        k: int = 10,
        exclude_self: bool = True
    ) -> List[Tuple[int, float]]:
        """
        Recommend similar products based on a product
        
        Args:
            product_id: Product ID
            k: Number of recommendations
            exclude_self: Exclude the query product
            
        Returns:
            List of (product_id, score) tuples
        """
        # Find product index
        try:
            product_idx = self.product_ids.index(product_id)
        except ValueError:
            return []
        
        # Get product embedding
        product_embedding = self.index.reconstruct(product_idx).reshape(1, -1)
        
        # Search for similar products
        k_search = k + 1 if exclude_self else k
        scores, indices = self.index.search(product_embedding, k_search)
        
        # Prepare results
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.products):
                pid = self.product_ids[idx]
                
                # Exclude self if requested
                if exclude_self and pid == product_id:
                    continue
                
                results.append((pid, float(score)))
        
        return results[:k]
    
    def save(self, index_path: str = 'data/faiss_index.bin', metadata_path: str = 'data/rag_metadata.pkl'):
        """
        Save FAISS index and metadata
        
        Args:
            index_path: Path to save FAISS index
            metadata_path: Path to save metadata
        """
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save metadata
        metadata = {
            'products': self.products,
            'product_ids': self.product_ids,
            'embedding_dim': self.embedding_dim
        }
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"\n💾 Saved RAG system:")
        print(f"   Index: {index_path}")
        print(f"   Metadata: {metadata_path}")
    
    def load(self, index_path: str = 'data/faiss_index.bin', metadata_path: str = 'data/rag_metadata.pkl'):
        """
        Load FAISS index and metadata
        
        Args:
            index_path: Path to FAISS index
            metadata_path: Path to metadata
        """
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        self.products = metadata['products']
        self.product_ids = metadata['product_ids']
        self.embedding_dim = metadata['embedding_dim']
        
        print(f"\n✅ Loaded RAG system:")
        print(f"   Products: {len(self.products)}")
        print(f"   Vectors: {self.index.ntotal}")


class ProductChatbot:
    """
    Chatbot for product consultation using RAG
    """
    
    def __init__(self, rag: ProductRAG):
        """
        Initialize chatbot
        
        Args:
            rag: ProductRAG instance
        """
        self.rag = rag
        
        # Response templates
        self.templates = {
            'greeting': "Xin chào! Tôi có thể giúp bạn tìm sản phẩm. Bạn đang tìm gì?",
            'search_results': "Tôi tìm thấy {count} sản phẩm phù hợp:\n\n{products}",
            'no_results': "Xin lỗi, tôi không tìm thấy sản phẩm nào phù hợp với '{query}'. Bạn có thể thử từ khóa khác không?",
            'recommendation': "Dựa trên sản phẩm bạn quan tâm, tôi gợi ý:\n\n{products}",
            'product_detail': "📦 {name}\n💰 Giá: {price} VNĐ\n📁 Danh mục: {category}\n📝 {description}"
        }
    
    def format_product(self, product: Dict, rank: Optional[int] = None) -> str:
        """Format product for display"""
        prefix = f"{rank}. " if rank else ""
        return (
            f"{prefix}📦 {product.get('name', 'N/A')}\n"
            f"   💰 {product.get('price', 'N/A')} VNĐ\n"
            f"   📁 {product.get('category', 'N/A')}"
        )
    
    def search(self, query: str, k: int = 5) -> str:
        """
        Search for products and generate response
        
        Args:
            query: User query
            k: Number of results
            
        Returns:
            Response text
        """
        # Handle greetings
        greetings = ['xin chào', 'hello', 'hi', 'chào']
        if any(g in query.lower() for g in greetings):
            return self.templates['greeting']
        
        # Search products
        results = self.rag.search(query, k=k)
        
        if not results:
            return self.templates['no_results'].format(query=query)
        
        # Format results
        products_text = "\n\n".join([
            self.format_product(product, rank=i+1)
            for i, (_, _, product) in enumerate(results)
        ])
        
        response = self.templates['search_results'].format(
            count=len(results),
            products=products_text
        )
        
        return response
    
    def recommend(self, product_id: int, k: int = 5) -> str:
        """
        Recommend similar products
        
        Args:
            product_id: Product ID
            k: Number of recommendations
            
        Returns:
            Response text
        """
        recommendations = self.rag.recommend_by_product(product_id, k=k)
        
        if not recommendations:
            return "Xin lỗi, tôi không tìm thấy sản phẩm tương tự."
        
        # Get product details
        products_text = []
        for i, (pid, score) in enumerate(recommendations, 1):
            # Find product in database
            product = next((p for p in self.rag.products if p['product_id'] == pid), None)
            if product:
                products_text.append(self.format_product(product, rank=i))
        
        response = self.templates['recommendation'].format(
            products="\n\n".join(products_text)
        )
        
        return response
    
    def chat(self, message: str) -> str:
        """
        Process chat message
        
        Args:
            message: User message
            
        Returns:
            Bot response
        """
        # Simple intent detection
        message_lower = message.lower()
        
        # Check for recommendation intent
        if any(word in message_lower for word in ['gợi ý', 'tương tự', 'giống', 'recommend']):
            # Try to extract product ID
            import re
            match = re.search(r'product[_\s]?(\d+)', message_lower)
            if match:
                product_id = int(match.group(1))
                return self.recommend(product_id)
        
        # Default to search
        return self.search(message)


def load_products_from_csv(csv_path: str = 'data/user_behavior.csv') -> List[Dict]:
    """
    Load product information from CSV and create product database
    
    Args:
        csv_path: Path to user behavior CSV
        
    Returns:
        List of product dictionaries
    """
    import pandas as pd
    
    print(f"📂 Loading products from {csv_path}...")
    
    # Load CSV
    df = pd.read_csv(csv_path)
    
    # Get unique products
    unique_products = df['product_id'].unique()
    
    # Product information (matching our seeded data)
    product_info = {
        # Điện thoại & Tablet (1-5)
        1: {"name": "iPhone 15 Pro Max 256GB", "category": "Điện thoại & Tablet", "price": "29990000", "description": "iPhone 15 Pro Max với chip A17 Pro, camera 48MP, màn hình 6.7 inch"},
        2: {"name": "Samsung Galaxy S24 Ultra", "category": "Điện thoại & Tablet", "price": "27990000", "description": "Galaxy S24 Ultra với S Pen, camera 200MP, màn hình Dynamic AMOLED 6.8 inch"},
        3: {"name": "iPad Air M2 128GB", "category": "Điện thoại & Tablet", "price": "16990000", "description": "iPad Air với chip M2, màn hình Liquid Retina 10.9 inch"},
        4: {"name": "Xiaomi 14 Pro 512GB", "category": "Điện thoại & Tablet", "price": "19990000", "description": "Xiaomi 14 Pro với Snapdragon 8 Gen 3, camera Leica 50MP"},
        5: {"name": "OPPO Find X7 Ultra", "category": "Điện thoại & Tablet", "price": "24990000", "description": "OPPO Find X7 Ultra với camera Hasselblad, màn hình AMOLED 120Hz"},
        
        # Laptop & Máy tính (6-10)
        6: {"name": "MacBook Pro 14 M3 Pro", "category": "Laptop & Máy tính", "price": "52990000", "description": "MacBook Pro 14 inch với chip M3 Pro, RAM 18GB, SSD 512GB"},
        7: {"name": "Dell XPS 15 9530", "category": "Laptop & Máy tính", "price": "45990000", "description": "Dell XPS 15 với Intel Core i7-13700H, RTX 4060, màn hình 4K OLED"},
        8: {"name": "ASUS ROG Strix G16", "category": "Laptop & Máy tính", "price": "38990000", "description": "ASUS ROG gaming laptop với RTX 4070, Intel i9-13980HX, màn hình 240Hz"},
        9: {"name": "Lenovo ThinkPad X1 Carbon", "category": "Laptop & Máy tính", "price": "42990000", "description": "ThinkPad X1 Carbon Gen 11, Intel Core i7, RAM 32GB, siêu nhẹ 1.12kg"},
        10: {"name": "HP Pavilion 15", "category": "Laptop & Máy tính", "price": "18990000", "description": "HP Pavilion 15 với AMD Ryzen 7, RAM 16GB, SSD 512GB"},
        
        # Add more products (11-50) with basic info
    }
    
    # Fill in remaining products with generic info
    categories = [
        "Âm thanh & Phụ kiện", "Thời trang Nam", "Thời trang Nữ",
        "Đồ gia dụng", "Sách & Văn phòng phẩm", "Thể thao & Du lịch",
        "Mẹ & Bé", "Làm đẹp & Sức khỏe"
    ]
    
    for pid in range(11, 51):
        if pid not in product_info:
            cat_idx = (pid - 11) // 5
            category = categories[min(cat_idx, len(categories) - 1)]
            product_info[pid] = {
                "name": f"Sản phẩm {pid}",
                "category": category,
                "price": f"{(pid * 100000)}",
                "description": f"Mô tả sản phẩm {pid} thuộc danh mục {category}"
            }
    
    # Create product list
    products = []
    for pid in unique_products:
        if pid in product_info:
            product = product_info[pid].copy()
            product['product_id'] = int(pid)
            products.append(product)
    
    print(f"✅ Loaded {len(products)} products")
    
    return products


if __name__ == '__main__':
    # Test RAG system
    print("=" * 70)
    print("Testing RAG System")
    print("=" * 70)
    
    # Load products
    products = load_products_from_csv()
    
    # Initialize RAG
    rag = ProductRAG()
    
    # Build index
    rag.build_index(products)
    
    # Test search
    print("\n" + "=" * 70)
    print("Test 1: Search")
    print("=" * 70)
    
    queries = [
        "điện thoại iPhone",
        "laptop gaming",
        "tai nghe không dây"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = rag.search(query, k=3)
        for i, (pid, score, product) in enumerate(results, 1):
            print(f"   {i}. Product {pid}: {product['name']} (score: {score:.4f})")
    
    # Test recommendations
    print("\n" + "=" * 70)
    print("Test 2: Recommendations")
    print("=" * 70)
    
    test_product_id = 1
    print(f"\nSimilar to Product {test_product_id}:")
    recs = rag.recommend_by_product(test_product_id, k=5)
    for i, (pid, score) in enumerate(recs, 1):
        product = next((p for p in products if p['product_id'] == pid), None)
        if product:
            print(f"   {i}. Product {pid}: {product['name']} (score: {score:.4f})")
    
    # Test chatbot
    print("\n" + "=" * 70)
    print("Test 3: Chatbot")
    print("=" * 70)
    
    chatbot = ProductChatbot(rag)
    
    test_messages = [
        "Xin chào",
        "Tôi muốn mua laptop",
        "Điện thoại iPhone có không?"
    ]
    
    for message in test_messages:
        print(f"\nUser: {message}")
        response = chatbot.chat(message)
        print(f"Bot: {response}")
    
    # Save RAG system
    rag.save()
    
    print("\n✅ RAG system test complete!")
