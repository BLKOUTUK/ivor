#!/bin/bash

echo "🧪 Testing IVOR Events Calendar Integration"
echo ""

# Function to test an endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="$3"
    
    echo -n "   Testing $name... "
    
    response=$(curl -s -w "%{http_code}" "$url" -o /tmp/response.json)
    status_code="${response: -3}"
    
    if [ "$status_code" = "$expected_status" ]; then
        echo "✅ SUCCESS ($status_code)"
        if [ -f /tmp/response.json ]; then
            # Show relevant data from response
            if command -v jq >/dev/null 2>&1; then
                case "$name" in
                    *"health"*)
                        jq -r '.status // "unknown"' /tmp/response.json 2>/dev/null | sed 's/^/      Status: /'
                        ;;
                    *"events"*)
                        total=$(jq -r '.total // 0' /tmp/response.json 2>/dev/null)
                        message=$(jq -r '.message // "No message"' /tmp/response.json 2>/dev/null)
                        echo "      Events: $total"
                        echo "      Message: $message"
                        ;;
                esac
            fi
        fi
    else
        echo "❌ FAILED ($status_code)"
        if [ -f /tmp/response.json ] && [ -s /tmp/response.json ]; then
            echo "      Response: $(head -c 100 /tmp/response.json)..."
        fi
    fi
    
    rm -f /tmp/response.json
}

# Test 1: Events Calendar API
echo "1️⃣ Testing Events Calendar API..."
test_endpoint "Health Check" "http://localhost:3001/api/health" "200"
test_endpoint "Upcoming Events" "http://localhost:3001/api/events/upcoming?limit=2" "200"
test_endpoint "Search Events" "http://localhost:3001/api/events/search?q=workshop" "200"

echo ""

# Test 2: IVOR Backend API
echo "2️⃣ Testing IVOR Backend API..."
test_endpoint "Health Check" "http://localhost:8000/health/" "200"
test_endpoint "Events Integration" "http://localhost:8000/events/upcoming?limit=2" "200"

echo ""

# Test 3: Integration Validation
echo "3️⃣ Testing Integration..."

# Get event from Calendar API
echo -n "   Fetching Calendar event... "
calendar_response=$(curl -s "http://localhost:3001/api/events/upcoming?limit=1")
if [ $? -eq 0 ]; then
    calendar_title=""
    if command -v jq >/dev/null 2>&1; then
        calendar_title=$(echo "$calendar_response" | jq -r '.events[0].title // "N/A"')
    fi
    echo "✅ Got: $calendar_title"
else
    echo "❌ Failed to fetch"
fi

# Get event from IVOR API
echo -n "   Fetching IVOR event... "
ivor_response=$(curl -s "http://localhost:8000/events/upcoming?limit=1")
if [ $? -eq 0 ]; then
    ivor_title=""
    if command -v jq >/dev/null 2>&1; then
        ivor_title=$(echo "$ivor_response" | jq -r '.events[0].title // "N/A"')
    fi
    echo "✅ Got: $ivor_title"
    
    # Compare titles
    if [ "$calendar_title" = "$ivor_title" ] && [ "$calendar_title" != "N/A" ]; then
        echo "   🔗 Integration: ✅ Events match! API integration successful"
    else
        echo "   ⚠️  Integration: Events differ (IVOR may be using fallback)"
    fi
else
    echo "❌ Failed to fetch"
fi

echo ""

# Test 4: Chat Integration
echo "4️⃣ Testing Chat Integration..."
echo -n "   Testing chat with events query... "

chat_response=$(curl -s -X POST "http://localhost:8000/chat/message" \
    -H "Content-Type: application/json" \
    -d '{"message": "What events are happening?", "session_id": "test"}')

if [ $? -eq 0 ]; then
    echo "✅ Chat responded"
    
    if command -v jq >/dev/null 2>&1; then
        message=$(echo "$chat_response" | jq -r '.message // "No message"')
        # Check if response contains event-related keywords
        if echo "$message" | grep -i -E "(event|workshop|community|celebration)" >/dev/null; then
            echo "   🔗 Chat mentions events: ✅ Integration working"
        else
            echo "   ⚠️  Chat response may not include event data"
        fi
        
        # Show first 100 chars of response
        echo "      Response preview: $(echo "$message" | head -c 100)..."
    fi
else
    echo "❌ Chat failed"
fi

echo ""
echo "🎯 Integration Test Complete!"
echo ""
echo "💡 Summary:"
echo "   • Events Calendar API provides event data"
echo "   • IVOR Backend consumes this data via HTTP API"
echo "   • Chat integration can reference events"
echo "   • Both systems remain independent"
echo ""
echo "🚀 Next Steps:"
echo "   1. Deploy Events Calendar API to production"
echo "   2. Configure IVOR to use production API URL"
echo "   3. Test frontend integration with BLKOUT website"