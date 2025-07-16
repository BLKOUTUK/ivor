#!/usr/bin/env python3
"""
BLKOUT Community Data System - Startup Script
Initializes database and starts the IVOR backend
"""

import asyncio
import os
import sys
import subprocess
import logging
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import init_db
from core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemRunner:
    """Handles system startup and initialization"""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        
    async def setup_database(self):
        """Initialize database and create tables"""
        
        print("📊 Setting up database...")
        
        try:
            # Initialize database
            await init_db()
            print("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Database setup failed: {str(e)}")
            return False
    
    def check_requirements(self):
        """Check if all required dependencies are installed"""
        
        print("🔍 Checking requirements...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "psycopg2-binary",
            "redis",
            "httpx",
            "python-dotenv",
            "pydantic"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing required packages: {', '.join(missing_packages)}")
            print("Install them with: pip install " + " ".join(missing_packages))
            return False
        
        print("✅ All requirements satisfied")
        return True
    
    def check_environment(self):
        """Check environment variables and configuration"""
        
        print("🔧 Checking environment configuration...")
        
        required_env_vars = [
            "DATABASE_URL",
            "REDIS_URL"
        ]
        
        missing_vars = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print("Please set them in your .env file or environment")
            return False
        
        print("✅ Environment configuration is valid")
        return True
    
    def start_server(self):
        """Start the FastAPI server"""
        
        print("🚀 Starting IVOR backend server...")
        
        try:
            # Start uvicorn server
            subprocess.run([
                "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload",
                "--log-level", "info"
            ], cwd=self.backend_dir)
            
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
        except Exception as e:
            print(f"❌ Server startup failed: {str(e)}")
    
    async def run(self):
        """Run the complete system startup"""
        
        print("🌟 BLKOUT Community Data System - Starting Up")
        print("=" * 60)
        
        # Check requirements
        if not self.check_requirements():
            sys.exit(1)
        
        # Check environment
        if not self.check_environment():
            sys.exit(1)
        
        # Setup database
        if not await self.setup_database():
            sys.exit(1)
        
        print("\n✅ System initialization complete!")
        print("🚀 Starting server on http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔧 Health Check: http://localhost:8000/health")
        print("\nPress Ctrl+C to stop the server\n")
        
        # Start server
        self.start_server()

def main():
    """Main entry point"""
    
    runner = SystemRunner()
    asyncio.run(runner.run())

if __name__ == "__main__":
    main()