#!/bin/bash

# Quick API Test Script
# Tests the main functionality of the e-commerce system

set -e

BASE_URL="http://localhost:8080"
INTERNAL_TOKEN="${SERVICE_INTERNAL_TOKEN:-change-me-internal-service-token}"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "E-commerce API Quick Test"
echo "=========================================="
echo ""

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health/)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ API Gateway is healthy${NC}"
else
    echo -e "${RED}✗ API Gateway health check failed${NC}"
    exit 1
fi
echo ""

# Test 2: List Products (Public)
echo -e "${BLUE}Test 2: List Products (Public)${NC}"
response=$(curl -s -w "\n%{http_code}" $BASE_URL/products/)
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Products listed successfully${NC}"
    product_count=$(echo "$response" | head -n-1 | grep -o '"id"' | wc -l)
    echo "  Found $product_count products"
else
    echo -e "${RED}✗ Failed to list products${NC}"
    exit 1
fi
echo ""

# Test 3: Register User
echo -e "${BLUE}Test 3: Register New User${NC}"
timestamp=$(date +%s)
email="test${timestamp}@example.com"
response=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/users/register/ \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$email\",
    \"password\": \"Test123!@#\",
    \"first_name\": \"Test\",
    \"last_name\": \"User\"
  }")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✓ User registered successfully${NC}"
    echo "  Email: $email"
else
    echo -e "${RED}✗ Failed to register user${NC}"
    echo "$response"
    exit 1
fi
echo ""

# Test 4: Login and Get Token
echo -e "${BLUE}Test 4: Login (Get JWT Token)${NC}"
response=$(curl -s -X POST $BASE_URL/users/token/ \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$email\",
    \"password\": \"Test123!@#\"
  }")

access_token=$(echo "$response" | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -n "$access_token" ]; then
    echo -e "${GREEN}✓ Login successful, token obtained${NC}"
else
    echo -e "${RED}✗ Failed to get access token${NC}"
    echo "$response"
    exit 1
fi
echo ""

# Test 5: Get User Profile
echo -e "${BLUE}Test 5: Get User Profile${NC}"
response=$(curl -s -w "\n%{http_code}" -X GET $BASE_URL/users/me/ \
  -H "Authorization: Bearer $access_token")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Profile retrieved successfully${NC}"
else
    echo -e "${RED}✗ Failed to get profile${NC}"
    exit 1
fi
echo ""

# Test 6: Check Stock
echo -e "${BLUE}Test 6: Check Product Stock${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/products/stock/check/ \
  -H "Content-Type: application/json" \
  -H "X-Service-Token: $INTERNAL_TOKEN" \
  -d '{
    "products": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ]
  }')
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Stock check successful${NC}"
    body=$(echo "$response" | head -n-1)
    available=$(echo "$body" | grep -o '"available":[^,}]*' | cut -d':' -f2)
    echo "  Stock available: $available"
else
    echo -e "${RED}✗ Failed to check stock${NC}"
    exit 1
fi
echo ""

# Test 7: Create Cart
echo -e "${BLUE}Test 7: Create Shopping Cart${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/cart/carts/ \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json" \
  -d '{}')
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✓ Cart created successfully${NC}"
    cart_id=$(echo "$response" | head -n-1 | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "  Cart ID: $cart_id"
else
    echo -e "${RED}✗ Failed to create cart${NC}"
    exit 1
fi
echo ""

# Test 8: Add Item to Cart
echo -e "${BLUE}Test 8: Add Item to Cart${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/cart/items/ \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json" \
  -d "{
    \"cart\": $cart_id,
    \"product_id\": 1,
    \"quantity\": 2
  }")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✓ Item added to cart${NC}"
else
    echo -e "${RED}✗ Failed to add item to cart${NC}"
    exit 1
fi
echo ""

# Test 9: Create Order
echo -e "${BLUE}Test 9: Create Order${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/orders/ \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "total_amount": "100.00",
    "shipping_address": "123 Test Street, Test City, Test Country",
    "status": "pending"
  }')
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✓ Order created successfully${NC}"
    order_id=$(echo "$response" | head -n-1 | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "  Order ID: $order_id"
else
    echo -e "${RED}✗ Failed to create order${NC}"
    exit 1
fi
echo ""

# Test 10: Create Payment
echo -e "${BLUE}Test 10: Create Payment${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/payments/ \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json" \
  -d "{
    \"order_id\": $order_id,
    \"amount\": \"100.00\",
    \"provider\": \"stripe\",
    \"transaction_id\": \"txn_test_${timestamp}\",
    \"status\": \"completed\"
  }")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✓ Payment created successfully${NC}"
else
    echo -e "${RED}✗ Failed to create payment${NC}"
    exit 1
fi
echo ""

# Test 11: Create Shipment
echo -e "${BLUE}Test 11: Create Shipment${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/shipping/ \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json" \
  -d "{
    \"order_id\": $order_id,
    \"address\": \"123 Test Street, Test City, Test Country\",
    \"carrier\": \"DHL\",
    \"tracking_number\": \"DHL_${timestamp}\",
    \"status\": \"pending\"
  }")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✓ Shipment created successfully${NC}"
else
    echo -e "${RED}✗ Failed to create shipment${NC}"
    exit 1
fi
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}All Tests Passed! ✓${NC}"
echo "=========================================="
echo ""
echo "The e-commerce system is working correctly!"
echo ""
echo "Test user credentials:"
echo "  Email: $email"
echo "  Password: Test123!@#"
echo "  Token: ${access_token:0:20}..."
echo ""
