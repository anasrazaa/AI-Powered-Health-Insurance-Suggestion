from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HealthCompare API",
    description="AI-powered health insurance comparison API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserProfile(BaseModel):
    age: int
    state: str
    zipCode: str
    familySize: str
    healthConditions: Optional[List[str]] = []
    prescriptionMeds: str
    income: str
    monthlyBudget: str
    deductiblePreference: str
    planType: str
    priority: str
    additionalNotes: Optional[str] = ""

class ComparisonRequest(BaseModel):
    userProfile: UserProfile
    question: Optional[str] = None

class PlanRecommendation(BaseModel):
    id: str
    name: str
    company: str
    type: str
    monthlyPremium: float
    deductible: float
    outOfPocketMax: float
    copay: float
    rating: float
    recommendation: str
    pros: List[str]
    cons: List[str]
    bestFor: str
    annualCost: float
    savings: float
    features: List[str]
    description: str

class ComparisonResponse(BaseModel):
    recommendations: List[PlanRecommendation]
    summary: str
    totalPlansAnalyzed: int
    processingTime: float
    userProfile: UserProfile

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "HealthCompare API is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "rag_system_loaded": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/plans/count")
async def get_plan_count():
    """Get the total number of plans in the system"""
    return {"total_plans": 17}

@app.get("/plans/list")
async def get_plans_list():
    """Get a list of all available plans"""
    plans = [
        {
            "id": "1",
            "name": "Blue Cross Blue Shield Gold PPO",
            "company": "Blue Cross Blue Shield",
            "type": "PPO",
            "monthly_premium": 450,
            "deductible": 1500,
            "out_of_pocket_max": 6500
        },
        {
            "id": "2", 
            "name": "Aetna Silver HMO",
            "company": "Aetna",
            "type": "HMO",
            "monthly_premium": 320,
            "deductible": 2500,
            "out_of_pocket_max": 8000
        }
    ]
    return {"plans": plans}

@app.post("/compare", response_model=ComparisonResponse)
async def compare_plans(request: ComparisonRequest):
    """Get personalized health insurance recommendations"""
    start_time = datetime.now()
    
    try:
        # Mock recommendations based on user profile
        recommendations = generate_mock_recommendations(request.userProfile)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        summary = f"Based on your profile (age {request.userProfile.age}, {request.userProfile.familySize} family members, {request.userProfile.income} income), we've found {len(recommendations)} plans that match your needs."
        
        return ComparisonResponse(
            recommendations=recommendations,
            summary=summary,
            totalPlansAnalyzed=17,
            processingTime=processing_time,
            userProfile=request.userProfile
        )
        
    except Exception as e:
        logger.error(f"Error in comparison: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@app.post("/query")
async def query_plans(request: ComparisonRequest):
    """Direct query to the system"""
    try:
        question = request.question or f"Recommend health insurance for {request.userProfile.age}-year-old in {request.userProfile.state}"
        
        return {
            "response": f"Based on your query: {question}, here are some recommendations...",
            "question": question,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    return {
        "total_plans": 17,
        "system_status": "operational",
        "last_updated": datetime.now().isoformat(),
        "api_version": "1.0.0"
    }

def generate_mock_recommendations(user_profile: UserProfile) -> List[PlanRecommendation]:
    """Generate mock recommendations based on user profile"""
    
    # Base plans
    base_plans = [
        {
            "id": "1",
            "name": "Blue Cross Blue Shield Gold PPO",
            "company": "Blue Cross Blue Shield",
            "type": "PPO",
            "monthlyPremium": 450.0,
            "deductible": 1500.0,
            "outOfPocketMax": 6500.0,
            "copay": 25.0,
            "rating": 4.8,
            "recommendation": "Best Overall",
            "pros": ["Excellent network coverage", "Low copays", "Great customer service"],
            "cons": ["Higher premium", "Limited HSA eligibility"],
            "bestFor": "Families with regular healthcare needs",
            "annualCost": 5400.0,
            "savings": 1200.0,
            "features": ["Prescription coverage", "Mental health", "Preventive care", "Emergency coverage"],
            "description": "Comprehensive PPO plan with excellent coverage and low out-of-pocket costs."
        },
        {
            "id": "2",
            "name": "Aetna Silver HMO",
            "company": "Aetna",
            "type": "HMO",
            "monthlyPremium": 320.0,
            "deductible": 2500.0,
            "outOfPocketMax": 8000.0,
            "copay": 35.0,
            "rating": 4.5,
            "recommendation": "Best Value",
            "pros": ["Affordable premium", "Good coverage", "HSA eligible"],
            "cons": ["Limited network", "Higher deductible"],
            "bestFor": "Healthy individuals on a budget",
            "annualCost": 3840.0,
            "savings": 800.0,
            "features": ["Prescription coverage", "Preventive care", "Emergency coverage"],
            "description": "Cost-effective HMO plan with good coverage for budget-conscious individuals."
        },
        {
            "id": "3",
            "name": "UnitedHealthcare Bronze HDHP",
            "company": "UnitedHealthcare",
            "type": "HDHP",
            "monthlyPremium": 280.0,
            "deductible": 4000.0,
            "outOfPocketMax": 7000.0,
            "copay": 0.0,
            "rating": 4.2,
            "recommendation": "Lowest Cost",
            "pros": ["Lowest premium", "HSA eligible", "Good for emergencies"],
            "cons": ["High deductible", "No copays", "Limited routine coverage"],
            "bestFor": "Young, healthy individuals",
            "annualCost": 3360.0,
            "savings": 1500.0,
            "features": ["HSA eligible", "Preventive care", "Emergency coverage"],
            "description": "High-deductible plan with the lowest premium, ideal for healthy individuals."
        }
    ]
    
    recommendations = []
    
    # Adjust recommendations based on user profile
    for plan in base_plans:
        adjusted_plan = plan.copy()
        
        # Adjust costs based on family size
        if user_profile.familySize != "1":
            family_multiplier = {"2": 1.8, "3": 2.5, "4": 3.0, "5": 3.5, "6+": 4.0}
            multiplier = family_multiplier.get(user_profile.familySize, 1.0)
            adjusted_plan["monthlyPremium"] *= multiplier
            adjusted_plan["annualCost"] = adjusted_plan["monthlyPremium"] * 12
        
        # Adjust based on health conditions
        if user_profile.healthConditions and "Diabetes" in user_profile.healthConditions:
            adjusted_plan["monthlyPremium"] *= 1.2
            adjusted_plan["annualCost"] = adjusted_plan["monthlyPremium"] * 12
        
        # Adjust based on age
        if user_profile.age > 50:
            adjusted_plan["monthlyPremium"] *= 1.3
            adjusted_plan["annualCost"] = adjusted_plan["monthlyPremium"] * 12
        
        recommendations.append(PlanRecommendation(**adjusted_plan))
    
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 