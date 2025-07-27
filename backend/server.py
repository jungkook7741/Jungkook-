from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# OpenAI configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Define Models
class CrimeReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    crime_type: str
    area: str
    location: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reported_by: Optional[str] = "Anonymous"

class CrimeReportCreate(BaseModel):
    crime_type: str
    area: str
    location: str
    description: str
    reported_by: Optional[str] = "Anonymous"

class PredictionRequest(BaseModel):
    area: Optional[str] = None

class PredictionResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    area: Optional[str] = None
    prediction_text: str
    insights: List[str]
    confidence: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Routes
@api_router.get("/")
async def root():
    return {"message": "Crime Reporting and Prediction Portal API"}

@api_router.post("/reports", response_model=CrimeReport)
async def create_crime_report(report: CrimeReportCreate):
    """Submit a new crime report"""
    report_dict = report.dict()
    crime_report = CrimeReport(**report_dict)
    await db.crime_reports.insert_one(crime_report.dict())
    return crime_report

@api_router.get("/reports", response_model=List[CrimeReport])
async def get_crime_reports(area: Optional[str] = None, limit: int = 50):
    """Get crime reports, optionally filtered by area"""
    query = {}
    if area:
        query["area"] = {"$regex": area, "$options": "i"}
    
    reports = await db.crime_reports.find(query).sort("timestamp", -1).limit(limit).to_list(limit)
    return [CrimeReport(**report) for report in reports]

@api_router.get("/reports/{report_id}", response_model=CrimeReport)
async def get_crime_report(report_id: str):
    """Get a specific crime report"""
    report = await db.crime_reports.find_one({"id": report_id})
    if not report:
        raise HTTPException(status_code=404, detail="Crime report not found")
    return CrimeReport(**report)

@api_router.post("/predict", response_model=PredictionResult)
async def predict_crime_patterns(request: PredictionRequest):
    """Generate AI-powered crime predictions for an area"""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Get recent crime data
    query = {}
    if request.area:
        query["area"] = {"$regex": request.area, "$options": "i"}
    
    recent_reports = await db.crime_reports.find(query).sort("timestamp", -1).limit(20).to_list(20)
    
    # Prepare data for AI analysis
    crime_data = []
    for report in recent_reports:
        crime_data.append({
            "type": report["crime_type"],
            "area": report["area"],
            "location": report["location"],
            "date": report["timestamp"].strftime("%Y-%m-%d %H:%M"),
            "description": report["description"][:100]  # Truncate for token efficiency
        })
    
    # Create AI analysis prompt
    area_filter = f" in {request.area}" if request.area else ""
    prompt = f"""
    Analyze the following crime data{area_filter} and provide predictions:

    Crime Reports:
    {crime_data}

    Please provide:
    1. Crime pattern analysis
    2. Potential hotspot areas
    3. Time-based patterns
    4. Risk assessment
    5. Preventive recommendations

    Format your response with clear insights and actionable recommendations.
    """

    try:
        # Initialize AI chat
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=f"crime_analysis_{str(uuid.uuid4())}",
            system_message="You are a crime analysis expert. Analyze crime data and provide detailed insights, predictions, and recommendations for law enforcement and community safety."
        ).with_model("openai", "gpt-4o")

        # Get AI prediction
        user_message = UserMessage(text=prompt)
        ai_response = await chat.send_message(user_message)
        
        # Parse insights from response (simple extraction)
        insights = []
        if "hotspot" in ai_response.lower():
            insights.append("Hotspot areas identified")
        if "pattern" in ai_response.lower():
            insights.append("Crime patterns detected")
        if "recommend" in ai_response.lower():
            insights.append("Preventive recommendations available")
        
        # Create prediction result
        prediction = PredictionResult(
            area=request.area,
            prediction_text=ai_response,
            insights=insights,
            confidence="High" if len(recent_reports) > 10 else "Medium"
        )
        
        # Store prediction
        await db.predictions.insert_one(prediction.dict())
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@api_router.get("/predictions", response_model=List[PredictionResult])
async def get_predictions(area: Optional[str] = None, limit: int = 10):
    """Get recent predictions"""
    query = {}
    if area:
        query["area"] = {"$regex": area, "$options": "i"}
    
    predictions = await db.predictions.find(query).sort("timestamp", -1).limit(limit).to_list(limit)
    return [PredictionResult(**pred) for pred in predictions]

@api_router.get("/stats")
async def get_crime_stats():
    """Get crime statistics by area and type"""
    # Area statistics
    area_pipeline = [
        {"$group": {"_id": "$area", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    area_stats = await db.crime_reports.aggregate(area_pipeline).to_list(10)
    
    # Crime type statistics
    type_pipeline = [
        {"$group": {"_id": "$crime_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    type_stats = await db.crime_reports.aggregate(type_pipeline).to_list(20)
    
    # Total count
    total_reports = await db.crime_reports.count_documents({})
    
    return {
        "total_reports": total_reports,
        "by_area": [{"area": stat["_id"], "count": stat["count"]} for stat in area_stats],
        "by_type": [{"type": stat["_id"], "count": stat["count"]} for stat in type_stats]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()