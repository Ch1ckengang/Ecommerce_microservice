#!/bin/bash

echo "🧪 TESTING FULL E-COMMERCE SYSTEM"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

test_endpoint() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $name (HTTP $response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $name (Expected $expected_code, Got $response)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

test_json_response() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    local name="$1"
    local url="$2"
    local check_field="$3"
    
    response=$(curl -s "$url" 2>/dev/null)
    
    if echo "$response" | grep -q "$check_field"; then
        echo -e "${GREEN}✅ PASS${NC}: $name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "$response"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $name (Field '$check_field' not found)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "📦 1. DOCKER CONTAINERS"
echo "----------------------"
docker ps --format "{{.Names}}" | grep -E "service|gateway|db|neo4j" | sort | while read container; do
    status=$(docker inspect --format='{{.State.Status}}' $container)
    if [ "$status" = "running" ]; then
        echo -e "${GREEN}✅${NC} $container"
    else
        echo -e "${RED}❌${NC} $container ($status)"
    fi
done
echo ""

echo "🏥 2. HEALTH ENDPOINTS"
echo "---------------------"
test_endpoint "Product Service" "http://localhost:8001/health/"
test_endpoint "User Service" "http://localhost:8002/health/"
test_endpoint "Cart Service" "http://localhost:8003/health/"
test_endpoint "Order Service" "http://localhost:8004/health/"
test_endpoint "Payment Service" "http://localhost:8005/health/"
test_endpoint "Shipping Service" "http://localhost:8006/health/"
test_endpoint "Frontend Service" "http://localhost:8007/"
test_endpoint "AI Service Health" "http://localhost:8008/api/v1/health"
echo ""

echo "📦 3. PRODUCT SERVICE"
echo "--------------------"
test_json_response "Get Products" "http://localhost:8001/products/" "success"
test_json_response "Get Categories" "http://localhost:8001/products/categories/" "success"
echo ""

echo "👤 4. USER SERVICE (Registration & Login)"
echo "-----------------------------------------"
# Register new user
USERNAME="testuser_$(date +%s)"
EMAIL="test_$(date +%s)@example.com"
PASSWORD="TestPass123"

REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8002/users/register/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"password_confirm\":\"$PASSWORD\"}")

if echo "$REGISTER_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✅ PASS${NC}: User Registration"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAIL${NC}: User Registration"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Login
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8002/users/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('access', ''))" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    echo -e "${GREEN}✅ PASS${NC}: User Login (Token obtained)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAIL${NC}: User Login"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

echo "🛒 5. CART SERVICE"
echo "-----------------"
if [ ! -z "$TOKEN" ]; then
    # Create cart
    CART_RESPONSE=$(curl -s -X POST http://localhost:8003/cart/carts/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json")
    
    CART_ID=$(echo "$CART_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('id', ''))" 2>/dev/null)
    
    if [ ! -z "$CART_ID" ]; then
        echo -e "${GREEN}✅ PASS${NC}: Create Cart (ID: $CART_ID)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Add item to cart
        ADD_ITEM_RESPONSE=$(curl -s -X POST http://localhost:8003/cart/items/ \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d "{\"cart\":$CART_ID,\"product_id\":1,\"quantity\":2,\"unit_price\":\"1000000\"}")
        
        if echo "$ADD_ITEM_RESPONSE" | grep -q "success\|product_id"; then
            echo -e "${GREEN}✅ PASS${NC}: Add Item to Cart"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}❌ FAIL${NC}: Add Item to Cart"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: Create Cart"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${YELLOW}⏭️  SKIP${NC}: Cart tests (No auth token)"
fi
echo ""

echo "📋 6. ORDER SERVICE"
echo "------------------"
if [ ! -z "$TOKEN" ]; then
    ORDER_RESPONSE=$(curl -s -X POST http://localhost:8004/orders/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"total_amount":"2000000","shipping_address":"123 Test St","status":"pending","order_items":[{"product_id":1,"quantity":2,"unit_price":"1000000"}]}')
    
    ORDER_ID=$(echo "$ORDER_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('id', ''))" 2>/dev/null)
    
    if [ ! -z "$ORDER_ID" ]; then
        echo -e "${GREEN}✅ PASS${NC}: Create Order (ID: $ORDER_ID)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: Create Order"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${YELLOW}⏭️  SKIP${NC}: Order tests (No auth token)"
fi
echo ""

echo "💳 7. PAYMENT SERVICE"
echo "--------------------"
if [ ! -z "$TOKEN" ] && [ ! -z "$ORDER_ID" ]; then
    PAYMENT_RESPONSE=$(curl -s -X POST http://localhost:8005/payments/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"order_id\":$ORDER_ID,\"amount\":\"2000000\",\"provider\":\"cod\",\"transaction_id\":\"TXN123\",\"status\":\"pending\"}")
    
    if echo "$PAYMENT_RESPONSE" | grep -q "success\|order_id"; then
        echo -e "${GREEN}✅ PASS${NC}: Create Payment"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: Create Payment"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${YELLOW}⏭️  SKIP${NC}: Payment tests (No auth token or order)"
fi
echo ""

echo "🚚 8. SHIPPING SERVICE"
echo "---------------------"
if [ ! -z "$TOKEN" ] && [ ! -z "$ORDER_ID" ]; then
    SHIPPING_RESPONSE=$(curl -s -X POST http://localhost:8006/shipping/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"order_id\":$ORDER_ID,\"address\":\"123 Test St\",\"carrier\":\"standard\",\"tracking_number\":\"TRK123\",\"status\":\"pending\"}")
    
    if echo "$SHIPPING_RESPONSE" | grep -q "success\|order_id"; then
        echo -e "${GREEN}✅ PASS${NC}: Create Shipment"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: Create Shipment"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${YELLOW}⏭️  SKIP${NC}: Shipping tests (No auth token or order)"
fi
echo ""

echo "🤖 9. AI SERVICE"
echo "---------------"
test_json_response "AI Health" "http://localhost:8008/api/v1/health" "status"
echo ""

echo "🌐 10. FRONTEND PAGES"
echo "--------------------"
test_endpoint "Home Page" "http://localhost:8007/"
test_endpoint "Products Page" "http://localhost:8007/products/"
test_endpoint "Login Page" "http://localhost:8007/login/"
test_endpoint "Register Page" "http://localhost:8007/register/"
echo ""

echo "🔍 11. CATEGORY FILTER"
echo "---------------------"
categories=("Laptop & Máy tính" "Điện thoại & Tablet" "Thời trang Nam")
for cat in "${categories[@]}"; do
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$cat'))")
    count=$(curl -s "http://localhost:8007/products/?category=$encoded" 2>&1 | grep -o "Tìm thấy [0-9]* sản phẩm" | grep -o "[0-9]*")
    if [ ! -z "$count" ] && [ "$count" -gt 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $cat ($count products)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $cat"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done
echo ""

echo "=================================="
echo "📊 TEST SUMMARY"
echo "=================================="
echo "Total Tests:  $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    exit 1
fi
