#!/bin/bash
# Quick API Test Script
# Usage: bash test_api.sh

API_URL="http://localhost:8000/chatbot_query"

echo "🧪 Testing Stock Chatbot API"
echo "================================"

# Test 1: Basic price query
echo -e "\n1️⃣ Testing: Basic Price Query"
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"user_query": "What is the price of TCS?"}' \
  | jq '.'

# Test 2: Company info
echo -e "\n2️⃣ Testing: Company Information"
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Tell me about Reliance"}' \
  | jq '.'

# Test 3: Market overview
echo -e "\n3️⃣ Testing: Market Overview"
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"user_query": "What is the market overview?"}' \
  | jq '.'

# Test 4: Health check
echo -e "\n4️⃣ Testing: Health Check"
curl -X GET http://localhost:8000/health | jq '.'

echo -e "\n✅ Tests completed!"

