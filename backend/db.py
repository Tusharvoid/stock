import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is not set")

client = AsyncIOMotorClient(MONGODB_URI)
db = client["stock_app"]
users_collection = db["users"]

# Test connection function
async def test_connection():
    try:
        # Test the connection
        await client.admin.command('ping')
        print("MongoDB connection successful!")
        
        # Create index on email field for faster queries and uniqueness
        await users_collection.create_index("email", unique=True)
        print("Database indexes created successfully!")
        
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False
