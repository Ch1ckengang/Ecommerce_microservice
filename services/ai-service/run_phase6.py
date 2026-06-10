"""
Run Phase 6: FastAPI Service
This script tests the FastAPI service
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "=" * 70)
    print("Test 1: Health Check")
    print("=" * 70)
    
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.status_code == 200

def test_stats():
    """Test stats endpoint"""
    print("\n" + "=" * 70)
    print("Test 2: Statistics")
    print("=" * 70)
    
    response = requests.get(f"{BASE_URL}/api/v1/stats")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.status_code == 200

def test_recommend_user_based():
    """Test user-based recommendation"""
    print("\n" + "=" * 70)
    print("Test 3: User-based Recommendation")
    print("=" * 70)
    
    payload = {
        "user_id": 1,
        "user_sequence": [1, 2, 3, 4, 5],
        "k": 5,
        "exclude_seen": True
    }
    
    print(f"Request: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/v1/recommend", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Recommendation Type: {data['recommendation_type']}")
        print(f"Total: {data['total']}")
        print(f"Weights: {data['weights_used']}")
        print(f"\nTop-5 Recommendations:")
        for i, rec in enumerate(data['recommendations'][:5], 1):
            print(f"  {i}. Product {rec['product_id']}: {rec['score']:.4f}")
            print(f"     LSTM: {rec['breakdown']['lstm']:.4f} | "
                  f"Graph: {rec['breakdown']['graph']:.4f} | "
                  f"RAG: {rec['breakdown']['rag']:.4f}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_recommend_query_based():
    """Test query-based recommendation"""
    print("\n" + "=" * 70)
    print("Test 4: Query-based Recommendation")
    print("=" * 70)
    
    payload = {
        "query": "laptop gaming mạnh mẽ",
        "k": 5
    }
    
    print(f"Request: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/v1/recommend", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Recommendation Type: {data['recommendation_type']}")
        print(f"Total: {data['total']}")
        print(f"\nTop-5 Recommendations:")
        for i, rec in enumerate(data['recommendations'][:5], 1):
            print(f"  {i}. Product {rec['product_id']}: {rec['score']:.4f}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_similar_products():
    """Test similar products endpoint"""
    print("\n" + "=" * 70)
    print("Test 5: Similar Products")
    print("=" * 70)
    
    product_id = 1
    k = 5
    
    print(f"Request: product_id={product_id}, k={k}")
    
    response = requests.get(f"{BASE_URL}/api/v1/similar/{product_id}?k={k}")
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data['total']}")
        print(f"\nTop-5 Similar Products:")
        for i, rec in enumerate(data['recommendations'][:5], 1):
            print(f"  {i}. Product {rec['product_id']}: {rec['score']:.4f}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_chatbot():
    """Test chatbot endpoint"""
    print("\n" + "=" * 70)
    print("Test 6: Chatbot")
    print("=" * 70)
    
    messages = [
        "Xin chào",
        "Tôi muốn mua laptop gaming",
        "Điện thoại iPhone có không?"
    ]
    
    for message in messages:
        print(f"\nUser: {message}")
        
        payload = {
            "message": message,
            "user_id": 1
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/chatbot", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Bot: {data['response'][:200]}...")  # First 200 chars
        else:
            print(f"Error: {response.text}")
            return False
        
        time.sleep(0.5)  # Small delay between messages
    
    return True

def test_hybrid_recommendation():
    """Test hybrid recommendation with custom weights"""
    print("\n" + "=" * 70)
    print("Test 7: Hybrid Recommendation with Custom Weights")
    print("=" * 70)
    
    payload = {
        "user_sequence": [1, 2, 3],
        "query": "tai nghe bluetooth",
        "k": 5,
        "weights": {
            "lstm": 0.2,
            "graph": 0.2,
            "rag": 0.6
        }
    }
    
    print(f"Request: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/v1/recommend", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Recommendation Type: {data['recommendation_type']}")
        print(f"Weights Used: {data['weights_used']}")
        print(f"\nTop-5 Recommendations:")
        for i, rec in enumerate(data['recommendations'][:5], 1):
            print(f"  {i}. Product {rec['product_id']}: {rec['score']:.4f}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def main():
    """Run all tests"""
    print("=" * 70)
    print("📌 GIAI ĐOẠN 6 — KIỂM THỬ FASTAPI SERVICE")
    print("=" * 70)
    print("\n⚠️  Đảm bảo FastAPI service đang chạy:")
    print("   uvicorn main:app --reload")
    print("\nĐợi 3 giây...")
    time.sleep(3)
    
    tests = [
        ("Health Check", test_health),
        ("Statistics", test_stats),
        ("User-based Recommendation", test_recommend_user_based),
        ("Query-based Recommendation", test_recommend_query_based),
        ("Similar Products", test_similar_products),
        ("Chatbot", test_chatbot),
        ("Hybrid Recommendation", test_hybrid_recommendation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Không thể kết nối đến {BASE_URL}")
            print("   Đảm bảo FastAPI service đang chạy:")
            print("   uvicorn main:app --reload")
            return
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 KẾT QUẢ KIỂM THỬ")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTổng kết: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n✅ GIAI ĐOẠN 6 HOÀN THÀNH!")
        print("\nFastAPI Service cung cấp:")
        print("   ✅ Health check và statistics")
        print("   ✅ Gợi ý dựa trên người dùng")
        print("   ✅ Gợi ý dựa trên truy vấn")
        print("   ✅ Tìm sản phẩm tương tự")
        print("   ✅ Chatbot tư vấn")
        print("   ✅ Trọng số tùy chỉnh")
        print("\nAPI Documentation: http://localhost:8000/docs")
        print("\nSẵn sàng cho:")
        print("   - Giai đoạn 7: Tích hợp với microservices")
        print("   - Giai đoạn 8: Deployment")
    else:
        print("\n⚠️  Một số tests thất bại. Kiểm tra lại!")

if __name__ == "__main__":
    main()
