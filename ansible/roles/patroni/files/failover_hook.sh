#!/bin/bash

echo "Calling..."

# Lấy hostname của máy
hostname=$(hostname)

# Đặt URL của endpoint API
api_url="https://4cab-2402-800-578c-333f-d67f-2a47-28f5-f664.ngrok-free.app/failover-hook"

# Đặt JSON data với hostname
data=$(cat <<EOF
{
  "hostname": "$hostname"
}
EOF
)

# Gọi API với curl
response=$(curl -X POST "$api_url" \
  -H "Content-Type: application/json" \
  -d "$data")

# In ra response từ API
echo "Response from API: $response"
