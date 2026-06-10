#!/bin/bash
# ================================================================
# E-Commerce Microservices — Full End-to-End Test Script
# Tests the complete purchase flow + AI services
# ================================================================
set -e

BASE="http://localhost:8080"
ts=$(date +%s)
PASSED=0
FAILED=0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { PASSED=$((PASSED + 1)); echo -e "${GREEN}✓ $1${NC}"; }
fail() { FAILED=$((FAILED + 1)); echo -e "${RED}✗ $1${NC}"; }

echo "=========================================="
echo "  E-Commerce Full End-to-End Test"
echo "  $(date)"
echo "=========================================="
echo ""

# ---- Health Checks ----
echo -e "${YELLOW}--- Service Health Checks ---${NC}"
for svc in user-service product-service cart-service order-service payment-service shipping-service; do
    port=$(echo $svc | sed 's/user-service/8002/;s/product-service/8001/;s/cart-service/8003/;s/order-service/8004/;s/payment-service/8005/;s/shipping-service/8006/')
    resp=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/health/")
    if [ "$resp" = "200" ]; then pass "$svc healthy"; else fail "$svc unhealthy ($resp)"; fi
done
# AI service
resp=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8008/api/v1/health")
if [ "$resp" = "200" ]; then pass "ai-service healthy"; else fail "ai-service unhealthy"; fi
# Gateway
resp=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/health/")
if [ "$resp" = "200" ]; then pass "api-gateway healthy"; else fail "api-gateway unhealthy"; fi
echo ""

# ---- 1. Register ----
echo -e "${YELLOW}--- 1. User Registration ---${NC}"
reg_resp=$(curl -s -X POST "$BASE/users/register/" -H "Content-Type: application/json" \
  -d "{\"username\":\"testfull$ts\",\"email\":\"full${ts}@test.com\",\"password\":\"TestPass123!@#\",\"password_confirm\":\"TestPass123!@#\"}")
reg_ok=$(echo "$reg_resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success',False))" 2>/dev/null)
if [ "$reg_ok" = "True" ]; then pass "User registered"; else fail "Registration failed: $reg_resp"; fi

# ---- 2. Login ----
echo -e "${YELLOW}--- 2. User Login (JWT) ---${NC}"
token_resp=$(curl -s -X POST "$BASE/users/token/" -H "Content-Type: application/json" \
  -d "{\"username\":\"testfull$ts\",\"password\":\"TestPass123!@#\"}")
access=$(echo "$token_resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access'])" 2>/dev/null)
if [ -n "$access" ] && [ "$access" != "None" ]; then pass "Login successful (token obtained)"; else fail "Login failed"; exit 1; fi

# ---- 3. Get Profile ----
echo -e "${YELLOW}--- 3. User Profile ---${NC}"
profile=$(curl -s "$BASE/users/me/" -H "Authorization: Bearer $access")
profile_ok=$(echo "$profile" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',d).get('username',''))" 2>/dev/null)
if [ "$profile_ok" = "testfull$ts" ]; then pass "Profile fetched correctly"; else fail "Profile mismatch: $profile_ok"; fi

# ---- 4. Product Listing ----
echo -e "${YELLOW}--- 4. Product Listing (Public) ---${NC}"
products=$(curl -s "$BASE/products/?page_size=5")
count=$(echo "$products" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('data',d.get('results',[]))))" 2>/dev/null)
if [ "$count" -gt "0" ] 2>/dev/null; then pass "Product listing: $count products returned"; else fail "No products returned"; fi

# ---- 5. Stock Check ----
echo -e "${YELLOW}--- 5. Stock Validation ---${NC}"
stock=$(curl -s -X POST "$BASE/products/stock/check/" -H "Content-Type: application/json" \
  -d '{"products": [{"product_id": 1, "quantity": 1}]}')
avail=$(echo "$stock" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['available'])" 2>/dev/null)
if [ "$avail" = "True" ]; then pass "Stock check: available"; else fail "Stock check failed"; fi

# ---- 6. Create Cart ----
echo -e "${YELLOW}--- 6. Cart Creation ---${NC}"
cart_resp=$(curl -s -X POST "$BASE/cart/carts/" -H "Content-Type: application/json" \
  -H "Authorization: Bearer $access" -d '{}')
cart_id=$(echo "$cart_resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
if [ -n "$cart_id" ] && [ "$cart_id" != "None" ]; then pass "Cart created (ID: $cart_id)"; else fail "Cart creation failed"; fi

# ---- 7. Add Item to Cart ----
echo -e "${YELLOW}--- 7. Add to Cart ---${NC}"
add_resp=$(curl -s -X POST "$BASE/cart/items/" -H "Content-Type: application/json" \
  -H "Authorization: Bearer $access" \
  -d "{\"cart\":$cart_id,\"product_id\":1,\"quantity\":2,\"unit_price\":\"79.99\"}")
add_ok=$(echo "$add_resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success',False))" 2>/dev/null)
if [ "$add_ok" = "True" ]; then pass "Item added to cart"; else fail "Add to cart failed: $add_resp"; fi

# ---- 8. Create Order with Items ----
echo -e "${YELLOW}--- 8. Create Order (with stock validation) ---${NC}"
order_resp=$(curl -s -X POST "$BASE/orders/" -H "Content-Type: application/json" \
  -H "Authorization: Bearer $access" \
  -d '{"total_amount":"159.98","shipping_address":"123 Demo Street, HCM","status":"pending","order_items":[{"product_id":1,"quantity":2,"unit_price":"79.99"}]}')
order_id=$(echo "$order_resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
if [ -n "$order_id" ] && [ "$order_id" != "None" ]; then pass "Order created (ID: $order_id)"; else fail "Order creation failed"; fi

# ---- 9. Create Payment ----
echo -e "${YELLOW}--- 9. Payment ---${NC}"
pay_resp=$(curl -s -X POST "$BASE/payments/" -H "Content-Type: application/json" \
  -H "Authorization: Bearer $access" \
  -d "{\"order_id\":$order_id,\"amount\":\"159.98\",\"provider\":\"cod\",\"transaction_id\":\"PAY-FULL-$ts\",\"status\":\"pending\"}")
pay_ok=$(echo "$pay_resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success',False))" 2>/dev/null)
if [ "$pay_ok" = "True" ]; then pass "Payment created"; else fail "Payment failed: $pay_resp"; fi

# ---- 10. Create Shipment ----
echo -e "${YELLOW}--- 10. Shipment ---${NC}"
ship_resp=$(curl -s -X POST "$BASE/shipping/" -H "Content-Type: application/json" \
  -H "Authorization: Bearer $access" \
  -d "{\"order_id\":$order_id,\"address\":\"123 Demo Street, HCM\",\"carrier\":\"standard\",\"tracking_number\":\"TRK-FULL-$ts\",\"status\":\"pending\"}")
ship_ok=$(echo "$ship_resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success',False))" 2>/dev/null)
if [ "$ship_ok" = "True" ]; then pass "Shipment created"; else fail "Shipment failed: $ship_resp"; fi

# ---- 11. AI Chatbot ----
echo -e "${YELLOW}--- 11. AI Chatbot ---${NC}"
chat_resp=$(curl -s -X POST "$BASE/ai/chatbot" -H "Content-Type: application/json" \
  -d '{"message":"tư vấn laptop gaming giá rẻ"}' 2>/dev/null)
chat_ok=$(echo "$chat_resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print('response' in d)" 2>/dev/null)
if [ "$chat_ok" = "True" ]; then pass "AI Chatbot responded"; else fail "Chatbot failed"; fi

# ---- 12. AI Recommendations ----
echo -e "${YELLOW}--- 12. AI Recommendations ---${NC}"
rec_resp=$(curl -s -X POST "$BASE/ai/recommend" -H "Content-Type: application/json" \
  -d '{"user_id":1,"k":3}' 2>/dev/null)
rec_ok=$(echo "$rec_resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print('recommendations' in d or 'product_ids' in d or 'data' in d)" 2>/dev/null)
if [ "$rec_ok" = "True" ]; then pass "AI Recommendations returned"; else fail "Recommendations failed"; fi

# ---- Summary ----
echo ""
echo "=========================================="
echo "  TEST RESULTS"
echo "=========================================="
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
total=$((PASSED + FAILED))
echo "  Total:  $total"
echo ""

if [ "$FAILED" -eq "0" ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "   Full flow verified: Register → Login → Cart → Order → Payment → Shipping → AI"
    exit 0
else
    echo -e "${RED}⚠ Some tests failed. See details above.${NC}"
    exit 1
fi
