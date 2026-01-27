from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")


class QueryInput(BaseModel):
    input_text: str


class QueryResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    input_text: str
    result: str
    creator_name: Optional[str] = None
    category: Optional[str] = None
    explanation: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GlobalStats(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    total_queries: int = 0
    men_count: int = 0
    women_count: int = 0


class CategoryStats(BaseModel):
    category: str
    count: int
    men_count: int
    women_count: int


@api_router.get("/")
async def root():
    return {"message": "Inventor Gender Checker API"}


@api_router.post("/analyze", response_model=QueryResult)
async def analyze_invention(query: QueryInput):
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=str(uuid.uuid4()),
            system_message="""You are a knowledgeable historian analyzing inventions, products, and services.
            When given an item, determine who created/invented it (man or woman), provide the creator's name, 
            a category for the item, and a brief explanation.
            
            Respond in this EXACT JSON format:
            {
                "result": "man" or "woman" or "natural",
                "creator_name": "Full name of the creator",
                "category": "Category (e.g., Technology, Medicine, Literature, Science, etc.)",
                "explanation": "Brief 1-2 sentence explanation"
            }
            
            IMPORTANT: 
            - If the item is a natural phenomenon, natural resource, or something found in nature (not invented/created by humans), use "natural" for result.
            - If multiple people were involved, mention the primary inventor/creator.
            - If the gender cannot be determined or it's a collective work, use "unknown" for result."""
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(
            text=f"Who invented/created: {query.input_text}?"
        )
        
        response = await chat.send_message(user_message)
        
        import json
        try:
            response_data = json.loads(response)
            result = response_data.get('result', 'unknown').lower()
            creator_name = response_data.get('creator_name', 'Unknown')
            category = response_data.get('category', 'General')
            explanation = response_data.get('explanation', '')
        except:
            result = 'unknown'
            creator_name = 'Unknown'
            category = 'General'
            explanation = response
        
        query_result = QueryResult(
            input_text=query.input_text,
            result=result,
            creator_name=creator_name,
            category=category,
            explanation=explanation
        )
        
        doc = query_result.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.queries.insert_one(doc)
        
        if result in ['man', 'woman']:
            stats = await db.stats.find_one({"type": "global"}, {"_id": 0})
            if not stats:
                stats = {"type": "global", "total_queries": 0, "men_count": 0, "women_count": 0}
            
            stats['total_queries'] += 1
            if result == 'man':
                stats['men_count'] += 1
            elif result == 'woman':
                stats['women_count'] += 1
            
            await db.stats.update_one(
                {"type": "global"},
                {"$set": stats},
                upsert=True
            )
        
        return query_result
        
    except Exception as e:
        logging.error(f"Error analyzing invention: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/stats", response_model=GlobalStats)
async def get_stats():
    stats = await db.stats.find_one({"type": "global"}, {"_id": 0})
    if not stats:
        return GlobalStats()
    
    return GlobalStats(
        total_queries=stats.get('total_queries', 0),
        men_count=stats.get('men_count', 0),
        women_count=stats.get('women_count', 0)
    )


@api_router.get("/queries", response_model=List[QueryResult])
async def get_queries(limit: int = 50):
    queries = await db.queries.find(
        {}, 
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    for query in queries:
        if isinstance(query.get('timestamp'), str):
            query['timestamp'] = datetime.fromisoformat(query['timestamp'])
    
    return queries


@api_router.get("/categories", response_model=List[CategoryStats])
async def get_categories():
    queries = await db.queries.find({}, {"_id": 0, "category": 1, "result": 1}).to_list(1000)
    
    category_map = {}
    for query in queries:
        category = query.get('category', 'General')
        result = query.get('result', 'unknown')
        
        if category not in category_map:
            category_map[category] = {"count": 0, "men_count": 0, "women_count": 0}
        
        category_map[category]['count'] += 1
        if result == 'man':
            category_map[category]['men_count'] += 1
        elif result == 'woman':
            category_map[category]['women_count'] += 1
    
    category_stats = [
        CategoryStats(
            category=cat,
            count=stats['count'],
            men_count=stats['men_count'],
            women_count=stats['women_count']
        )
        for cat, stats in category_map.items()
    ]
    
    return sorted(category_stats, key=lambda x: x.count, reverse=True)


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()