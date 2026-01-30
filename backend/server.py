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
import google.generativeai as genai


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
# MongoDB connection with proper SSL configuration for Render
client = AsyncIOMotorClient(
    mongo_url,
    tls=True,
    tlsAllowInvalidHostnames=True
)
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
    milestones: List[int] = []


class Milestone(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    count: int
    achieved_at: datetime
    men_at_milestone: int
    women_at_milestone: int


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
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""You are a knowledgeable historian analyzing inventions, products, and services.
When given an item, determine who created/invented it (man or woman), provide the creator's name, 
a category for the item, and a brief explanation.

Respond in this EXACT JSON format:
{{
    "result": "man" or "woman" or "natural",
    "creator_name": "Full name of the creator",
    "category": "Category (e.g., Technology, Medicine, Literature, Science, etc.)",
    "explanation": "Brief 1-2 sentence explanation"
}}

IMPORTANT: 
- If the item is a natural phenomenon, natural resource, plant, animal, mineral, element, or ANYTHING found in nature (not invented/created by humans), use "natural" for result. Examples: water, oxygen, trees, gold, diamonds, berries, sunlight, wind, etc.
- Only use "man" or "woman" for human-made inventions, products, or creations.
- If multiple people were involved, mention the primary inventor/creator and still use "man" or "woman" based on their gender.
- If the gender cannot be determined, default to "natural" if it's from nature, otherwise use the best guess based on historical records.

Who invented/created: {query.input_text}?

Respond ONLY with the JSON object, no other text."""
        
        response = model.generate_content(prompt)
        
        import json
        try:
            # Extract JSON from response
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            response_data = json.loads(response_text)
            result = response_data.get('result', 'unknown').lower()
            creator_name = response_data.get('creator_name', 'Unknown')
            category = response_data.get('category', 'General')
            explanation = response_data.get('explanation', '')
        except Exception as e:
            logging.error(f"Error parsing Gemini response: {e}")
            result = 'unknown'
            creator_name = 'Unknown'
            category = 'General'
            explanation = response.text if response.text else 'Unable to analyze'
        
        query_result = QueryResult(
            input_text=query.input_text,
            result=result,
            creator_name=creator_name,
            category=category,
            explanation=explanation
        )
        
        # Only save to database if it's an invention by man or woman (not natural things)
        if result in ['man', 'woman']:
            doc = query_result.model_dump()
            doc['timestamp'] = doc['timestamp'].isoformat()
            await db.queries.insert_one(doc)
            
            stats = await db.stats.find_one({"type": "global"}, {"_id": 0})
            if not stats:
                stats = {"type": "global", "total_queries": 0, "men_count": 0, "women_count": 0, "milestones": []}
            
            old_count = stats['total_queries']
            stats['total_queries'] += 1
            if result == 'man':
                stats['men_count'] += 1
            elif result == 'woman':
                stats['women_count'] += 1
            
            # Check if we've hit a milestone (every 100,000 queries)
            new_count = stats['total_queries']
            old_milestone = (old_count // 100000) * 100000
            new_milestone = (new_count // 100000) * 100000
            
            if new_milestone > old_milestone and new_milestone > 0:
                # We've hit a new milestone!
                milestone_doc = {
                    "count": new_milestone,
                    "achieved_at": datetime.now(timezone.utc).isoformat(),
                    "men_at_milestone": stats['men_count'],
                    "women_at_milestone": stats['women_count']
                }
                await db.milestones.insert_one(milestone_doc)
                if 'milestones' not in stats:
                    stats['milestones'] = []
                stats['milestones'].append(new_milestone)
            
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
        women_count=stats.get('women_count', 0),
        milestones=stats.get('milestones', [])
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
    # Use MongoDB aggregation pipeline for better performance
    pipeline = [
        {"$match": {"category": {"$exists": True}, "result": {"$in": ["man", "woman"]}}},
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1},
            "men_count": {"$sum": {"$cond": [{"$eq": ["$result", "man"]}, 1, 0]}},
            "women_count": {"$sum": {"$cond": [{"$eq": ["$result", "woman"]}, 1, 0]}}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    
    results = await db.queries.aggregate(pipeline).to_list(20)
    
    category_stats = [
        CategoryStats(
            category=result['_id'],
            count=result['count'],
            men_count=result['men_count'],
            women_count=result['women_count']
        )
        for result in results
    ]
    
    return category_stats


@api_router.get("/milestones", response_model=List[Milestone])
async def get_milestones():
    milestones = await db.milestones.find({}, {"_id": 0}).sort("count", -1).to_list(100)
    
    for milestone in milestones:
        if isinstance(milestone.get('achieved_at'), str):
            milestone['achieved_at'] = datetime.fromisoformat(milestone['achieved_at'])
    
    return milestones
    
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