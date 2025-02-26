import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from typing import List, Dict, Any
import asyncio
import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Get MongoDB URL from environment variable or use default
mongodb_url = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")

try:
    client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)
    # Verify the connection works
    client.server_info()
    db = client.voice_assistant
    logger.info(f"Successfully connected to MongoDB at {mongodb_url}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    # Provide a fallback mechanism
    db = None

# In-memory storage
interactions: List[Dict[str, Any]] = []

# Lock for thread safety
lock = asyncio.Lock()

async def save_interaction(text: str, intent: str, response_data: Dict[str, Any] = None):
    """
    Save the interaction to the database with enhanced data
    """
    interaction_data = {
        "text": text,
        "intent": intent,
        "timestamp": datetime.datetime.utcnow(),
        "response": response_data
    }
    
    if db is None:
        logger.warning("MongoDB not available, using in-memory storage")
        async with lock:
            interactions.append(interaction_data)
        return
    
    try:
        await db.interactions.insert_one(interaction_data)
        logger.info(f"Saved interaction: {text} - {intent}")
    except Exception as e:
        logger.error(f"Error saving to MongoDB: {e}")
        # Use in-memory storage as fallback
        async with lock:
            interactions.append(interaction_data)

async def get_recent_interactions(limit: int = 10):
    """
    Get recent interactions from the database
    """
    if db is None:
        logger.warning("MongoDB not available, using in-memory storage")
        return sorted(interactions, key=lambda x: x.get("timestamp", datetime.datetime.min), reverse=True)[:limit]
    
    try:
        cursor = db.interactions.find().sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    except Exception as e:
        logger.error(f"Error retrieving from MongoDB: {e}")
        return sorted(interactions, key=lambda x: x.get("timestamp", datetime.datetime.min), reverse=True)[:limit]