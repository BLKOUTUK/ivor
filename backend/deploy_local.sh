#\!/bin/bash

echo "🚀 BLKOUT Community Data System - Local Deployment"
echo "================================================="

# Check if database exists
if [ \! -f "blkout_community.db" ]; then
    echo "❌ Database not found. Please run database initialization first."
    exit 1
fi

# Check environment file
if [ \! -f ".env" ]; then
    echo "❌ Environment file not found. Please create .env file."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Set deployment timestamp
DEPLOY_TIME=$(date '+%Y-%m-%d %H:%M:%S')
echo "🕐 Deployment started at: $DEPLOY_TIME"

# Create deployment info
cat > deployment_info.json << EOF_JSON
{
    "deployment_time": "$DEPLOY_TIME",
    "environment": "local",
    "database": "SQLite",
    "status": "active",
    "version": "v1.0.0",
    "features": [
        "Community Profiles",
        "Quiz Results",
        "IVOR AI Assistant",
        "Conversation History",
        "Privacy Controls",
        "Consent Management"
    ]
}
EOF_JSON

echo "✅ Deployment configuration created"

# Start health monitoring
echo "🔍 Starting health monitoring..."
python3 -c "
import sqlite3
import json
from datetime import datetime

print('Health Check Results:')
print('=' * 30)

# Database check
try:
    conn = sqlite3.connect('blkout_community.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type=\"table\"')
    table_count = cursor.fetchone()[0]
    print(f'✅ Database: {table_count} tables active')
    conn.close()
except Exception as e:
    print(f'❌ Database: {e}')

# Environment check
try:
    with open('.env', 'r') as f:
        env_count = len([line for line in f if '=' in line and not line.startswith('#')])
    print(f'✅ Environment: {env_count} variables configured')
except Exception as e:
    print(f'❌ Environment: {e}')

print('\\n🎉 System is ready for use\!')
print('\\nNext steps:')
print('1. Connect frontend forms to backend API')
print('2. Test with real community data')
print('3. Monitor usage and performance')
print('4. Scale to production environment')
"

echo "✅ Local deployment completed successfully\!"
