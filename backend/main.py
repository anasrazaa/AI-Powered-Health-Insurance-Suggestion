from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import asyncio
import logging
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import the RAG system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the optimized RAG system
from app_optimized import OptimizedHealthInsuranceRAG

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
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "http://localhost:3002", 
        "http://127.0.0.1:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the RAG system
rag_system = None

class UserProfile(BaseModel):
    age: Optional[int] = None
    familySize: Optional[str] = None
    healthConditions: Optional[List[str]] = []
    prescriptionMeds: Optional[str] = None
    income: str  # Required
    priority: Optional[str] = None
    additionalNotes: Optional[str] = ""

    def get_completeness_score(self) -> float:
        """Calculate how complete the user profile is (0-1)"""
        # Financial fields are now required
        required_fields = ['income']
        # Other fields are optional but improve recommendations
        optional_fields = ['age', 'familySize', 'prescriptionMeds', 'priority']
        
        required_filled = sum(1 for field in required_fields if getattr(self, field) is not None and getattr(self, field) != "")
        optional_filled = sum(1 for field in optional_fields if getattr(self, field) is not None and getattr(self, field) != "")
        
        # Must have all required fields to be considered complete
        if required_filled < len(required_fields):
            return required_filled / len(required_fields) * 0.6  # Max 60% without required fields
        
        # Add optional fields to reach 100%
        return 0.6 + (optional_filled / len(optional_fields)) * 0.4

    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields"""
        required_fields = {
            'income': 'Annual Household Income'
        }
        optional_fields = {
            'age': 'Age',
            'familySize': 'Family Size',
            'prescriptionMeds': 'Prescription Medications',
            'priority': 'Priority'
        }
        missing = []
        
        # Check required fields first
        for field, display_name in required_fields.items():
            value = getattr(self, field)
            if value is None or value == "":
                missing.append(display_name)
        
        # Check optional fields
        for field, display_name in optional_fields.items():
            value = getattr(self, field)
            if value is None or value == "":
                missing.append(f"{display_name} (optional)")
        
        return missing

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

class AIAdviceResponse(BaseModel):
    advice: str
    keyPoints: List[str]
    riskFactors: List[str]
    recommendations: List[str]

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    global rag_system
    try:
        logger.info("Initializing Health Insurance RAG system...")
        
        # Get OpenAI API key from environment
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key or openai_key == "sk-proj-your-api-key-here":
            logger.warning("OPENAI_API_KEY not set or invalid. Using mock mode for testing.")
            
            # Create a mock RAG system that doesn't require API key
            class MockRAGSystem:
                def __init__(self):
                    # Try to load real data first
                    markdown_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_plan.md")
                    
                    if os.path.exists(markdown_file):
                        logger.info(f"Mock system: Found sample_plan.md, loading real data...")
                        with open(markdown_file, "r", encoding="utf-8") as f:
                            md_content = f.read()
                        
                        # Use the real parsing logic from the optimized RAG system
                        try:
                            from app_optimized import OptimizedHealthInsuranceRAG
                            temp_rag = OptimizedHealthInsuranceRAG("dummy-key")
                            self.plans = temp_rag.parse_insurance_plans(md_content)
                            logger.info(f"Mock system: Parsed {len(self.plans)} real insurance plans")
                        except Exception as e:
                            logger.warning(f"Mock system: Failed to parse real data: {e}")
                            self.plans = self._get_default_plans()
                    else:
                        logger.warning(f"Mock system: sample_plan.md not found, using default plans")
                        self.plans = self._get_default_plans()
                
                def _get_default_plans(self):
                    return [
                        {
                            "plan_name": "Blue Cross Blue Shield Gold PPO",
                            "carrier": "Blue Cross Blue Shield",
                            "plan_type": "PPO",
                            "monthly_premium": "450",
                            "deductible": "1500",
                            "max_out_of_pocket": "6500",
                            "hsa_eligible": False,
                            "content": "Comprehensive PPO plan with excellent coverage."
                        },
                        {
                            "plan_name": "Aetna Silver HMO",
                            "carrier": "Aetna",
                            "plan_type": "HMO",
                            "monthly_premium": "320",
                            "deductible": "2500",
                            "max_out_of_pocket": "8000",
                            "hsa_eligible": True,
                            "content": "Cost-effective HMO plan with good coverage."
                        },
                        {
                            "plan_name": "UnitedHealthcare Bronze HDHP",
                            "carrier": "UnitedHealthcare",
                            "plan_type": "HDHP",
                            "monthly_premium": "280",
                            "deductible": "4000",
                            "max_out_of_pocket": "7000",
                            "hsa_eligible": True,
                            "content": "High-deductible plan with lowest premium."
                        }
                    ]
                
                def query_plans(self, question):
                    return {"result": f"Mock AI analysis for: {question}. Based on your profile, I recommend considering the available plans based on your specific needs and budget."}
                
                def parse_insurance_plans(self, content):
                    return self.plans
                
                def create_optimized_documents(self, plans):
                    return []
                
                def setup_vectorstore(self, documents):
                    pass
            
            rag_system = MockRAGSystem()
            logger.info("Mock RAG system initialized successfully")
            return
        
        # Initialize real RAG system with valid API key
        rag_system = OptimizedHealthInsuranceRAG(openai_key)
        
        # Load and parse markdown content
        logger.info("Loading and parsing insurance plans...")
        markdown_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_plan.md")
        
        logger.info(f"Looking for sample_plan.md at: {markdown_file}")
        
        if os.path.exists(markdown_file):
            logger.info(f"Found sample_plan.md, loading real data...")
            with open(markdown_file, "r", encoding="utf-8") as f:
                md_content = f.read()
            
            # Parse plans into structured data
            plans = rag_system.parse_insurance_plans(md_content)
            logger.info(f"Parsed {len(plans)} insurance plans from real data")
            
            # Create optimized documents
            documents = rag_system.create_optimized_documents(plans)
            
            # Setup vector store (will use cached version if available)
            rag_system.setup_vectorstore(documents)
            
            # Store plans for later use
            rag_system.plans = plans
        else:
            logger.warning(f"sample_plan.md not found at {markdown_file}. Using mock data.")
            # Create mock plans for testing
            rag_system.plans = [
                {
                    "plan_name": "Blue Cross Blue Shield Gold PPO",
                    "carrier": "Blue Cross Blue Shield",
                    "plan_type": "PPO",
                    "monthly_premium": "450",
                    "deductible": "1500",
                    "max_out_of_pocket": "6500",
                    "hsa_eligible": False,
                    "content": "Comprehensive PPO plan with excellent coverage."
                },
                {
                    "plan_name": "Aetna Silver HMO",
                    "carrier": "Aetna",
                    "plan_type": "HMO",
                    "monthly_premium": "320",
                    "deductible": "2500",
                    "max_out_of_pocket": "8000",
                    "hsa_eligible": True,
                    "content": "Cost-effective HMO plan with good coverage."
                }
            ]
        
        logger.info("RAG system initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        logger.info("Falling back to mock mode...")
        # Create a minimal mock system
        rag_system = type('MockRAG', (), {
            'plans': [
                {
                    "plan_name": "Blue Cross Blue Shield Gold PPO",
                    "carrier": "Blue Cross Blue Shield",
                    "plan_type": "PPO",
                    "monthly_premium": "450",
                    "deductible": "1500",
                    "max_out_of_pocket": "6500",
                    "hsa_eligible": False,
                    "content": "Comprehensive PPO plan with excellent coverage."
                }
            ]
        })()
        rag_system.query_plans = lambda question: {"result": f"Mock response for: {question}"}

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
        "rag_system_loaded": rag_system is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/plans/count")
async def get_plan_count():
    """Get the total number of plans in the system"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        count = len(rag_system.plans) if hasattr(rag_system, 'plans') else 0
        return {"total_plans": count}
    except Exception as e:
        logger.error(f"Error getting plan count: {e}")
        raise HTTPException(status_code=500, detail="Failed to get plan count")

@app.get("/plans/list")
async def get_plans_list():
    """Get a list of all available plans"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        plans = []
        if hasattr(rag_system, 'plans'):
            for plan in rag_system.plans:
                # Handle missing or invalid values gracefully
                monthly_premium = plan.get("monthly_premium", 0)
                deductible = plan.get("deductible", 0)
                max_out_of_pocket = plan.get("max_out_of_pocket", 0)
                
                # Convert to float and handle invalid values
                try:
                    monthly_premium = float(monthly_premium) if monthly_premium else 0
                except (ValueError, TypeError):
                    monthly_premium = 0
                
                try:
                    deductible = float(deductible) if deductible else 0
                except (ValueError, TypeError):
                    deductible = 0
                
                try:
                    max_out_of_pocket = float(max_out_of_pocket) if max_out_of_pocket else 0
                except (ValueError, TypeError):
                    max_out_of_pocket = 0
                
                plan_data = {
                    "id": plan.get("plan_name", "Unknown Plan"),
                    "name": plan.get("plan_name", "Unknown Plan"),
                    "company": plan.get("carrier", "Unknown Carrier"),
                    "type": plan.get("plan_type", "Unknown"),
                    "monthly_premium": monthly_premium,
                    "deductible": deductible,
                    "out_of_pocket_max": max_out_of_pocket
                }
                print(f"[DEBUG] API Response for {plan.get('plan_name', 'Unknown')[:30]}: deductible=${deductible}, max_oop=${max_out_of_pocket}")
                plans.append(plan_data)
        return {"plans": plans}
    except Exception as e:
        logger.error(f"Error getting plans list: {e}")
        raise HTTPException(status_code=500, detail="Failed to get plans list")

@app.get("/plans/detail/{plan_name}")
async def get_plan_detail(plan_name: str):
    """Get detailed information for a specific plan"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        if hasattr(rag_system, 'plans'):
            # Find the plan by name (case-insensitive)
            plan = None
            for p in rag_system.plans:
                if p.get("plan_name", "").lower() == plan_name.lower():
                    plan = p
                    break
            
            if not plan:
                raise HTTPException(status_code=404, detail="Plan not found")
            
            # Return detailed plan information
            return {
                "plan_name": plan.get("plan_name"),
                "carrier": plan.get("carrier"),
                "plan_type": plan.get("plan_type"),
                "monthly_premium": plan.get("monthly_premium"),
                "deductible": plan.get("deductible"),
                "max_out_of_pocket": plan.get("max_out_of_pocket"),
                "hsa_eligible": plan.get("hsa_eligible"),
                "content": plan.get("content", ""),
                "effective_date": "August 01, 2025",
                "plan_year": "2025"
            }
        else:
            raise HTTPException(status_code=404, detail="No plans available")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to get plan details")

@app.post("/compare", response_model=ComparisonResponse)
async def compare_plans(request: ComparisonRequest):
    """Get personalized health insurance recommendations"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    start_time = datetime.now()
    
    try:
        # Check profile completeness
        completeness_score = request.userProfile.get_completeness_score()
        missing_fields = request.userProfile.get_missing_fields()
        
        # Build the question based on user profile
        question = build_question_from_profile(request.userProfile)
        
        # Get recommendations from RAG system
        result = rag_system.query_plans(question)
        rag_response = result["result"]
        
        # Parse and structure the response using RAG recommendations
        recommendations = parse_rag_response_with_ai_recommendations(rag_response, request.userProfile)
        
        # Add profile completeness information to response
        if completeness_score < 1.0:
            rag_response += f"\n\nNote: Your profile is {completeness_score*100:.0f}% complete. "
            if missing_fields:
                required_missing = [field for field in missing_fields if "(optional)" not in field]
                optional_missing = [field.replace(" (optional)", "") for field in missing_fields if "(optional)" in field]
                
                if required_missing:
                    rag_response += f"Required information missing: {', '.join(required_missing)}. "
                if optional_missing:
                    rag_response += f"Optional information that would improve recommendations: {', '.join(optional_missing)}. "
            rag_response += "Consider providing more details for more personalized recommendations."
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ComparisonResponse(
            recommendations=recommendations,
            summary=rag_response,
            totalPlansAnalyzed=len(rag_system.plans) if hasattr(rag_system, 'plans') else 0,
            processingTime=processing_time,
            userProfile=request.userProfile
        )
        
    except Exception as e:
        logger.error(f"Error in comparison: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@app.post("/query")
async def query_plans(request: ComparisonRequest):
    """Direct query to the RAG system"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        question = request.question or build_question_from_profile(request.userProfile)
        result = rag_system.query_plans(question)
        
        return {
            "response": result["result"],
            "question": question,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

def build_question_from_profile(profile: UserProfile) -> str:
    """Build a comprehensive question from user profile with graceful handling of missing data"""
    question_parts = []
    
    # Basic demographics (handle missing data gracefully)
    if profile.age:
        question_parts.append(f"I am a {profile.age}-year-old person")
    else:
        question_parts.append("I am looking for health insurance")
    
    question_parts.append("living in the United States")
    
    if profile.familySize:
        question_parts.append(f"with a family size of {profile.familySize}")
    else:
        question_parts.append("seeking individual or family coverage")
    
    # Financial information (now required)
    question_parts.append(f"with an income range of {profile.income}")
    
    # Health conditions
    if profile.healthConditions and profile.healthConditions != ['None']:
        conditions = ", ".join([c for c in profile.healthConditions if c != 'None'])
        if conditions:
            question_parts.append(f"I have the following health conditions: {conditions}")
    
    # Prescription medications
    if profile.prescriptionMeds == "yes":
        question_parts.append("I take prescription medications regularly")
    elif profile.prescriptionMeds == "no":
        question_parts.append("I do not take prescription medications regularly")
    

    
    if profile.priority:
        question_parts.append(f"and my priority is {profile.priority}")
    
    # Additional notes
    if profile.additionalNotes and profile.additionalNotes.strip():
        question_parts.append(f"Additional notes: {profile.additionalNotes}")
    
    # Final request
    question_parts.append("Please recommend the best health insurance plans for my situation, including detailed comparisons of costs, coverage, and benefits.")
    
    return " ".join(question_parts)

def parse_rag_response_with_ai_recommendations(response: str, user_profile: UserProfile) -> List[PlanRecommendation]:
    """Parse the RAG response and use AI recommendations to select relevant plans"""
    recommendations = []
    
    # Use the real RAG system to get actual plan data
    if hasattr(rag_system, 'plans') and rag_system.plans:
        all_plans = rag_system.plans
        
        # Select plans based on user preferences and AI recommendations
        selected_plans = select_relevant_plans(all_plans, user_profile, response)
        
        for i, plan in enumerate(selected_plans):
            # Use exact values from sample_plan.md without modifications
            monthly_premium = float(plan.get('monthly_premium', 0))
            deductible = float(plan.get('deductible', 0))
            max_out_of_pocket = float(plan.get('max_out_of_pocket', 0))
            
            # Calculate annual cost using exact values
            annual_cost = monthly_premium * 12
            
            # Determine recommendation based on plan characteristics and user preferences
            recommendation, rating = determine_recommendation(plan, user_profile)
            
            # Create recommendation object (pros and cons will be generated by frontend)
            recommendation_obj = PlanRecommendation(
                id=str(i + 1),
                name=plan.get('plan_name', 'Unknown Plan'),
                company=plan.get('carrier', 'Unknown Carrier'),
                type=plan.get('plan_type', 'Unknown'),
                monthlyPremium=monthly_premium,
                deductible=deductible,
                outOfPocketMax=max_out_of_pocket,
                copay=25.0,  # Default copay
                rating=rating,
                recommendation=recommendation,
                pros=[],  # Will be generated by frontend
                cons=[],  # Will be generated by frontend
                bestFor=f"{user_profile.priority.replace('-', ' ').title() if user_profile.priority else 'General'} seekers",
                annualCost=annual_cost,
                savings=1200.0,  # Estimated savings
                features=["Prescription coverage", "Preventive care", "Emergency coverage"],
                description=f"Comprehensive {plan.get('plan_type', 'health')} plan with {recommendation.lower()} focus."
            )
            
            recommendations.append(recommendation_obj)
    
    return recommendations

def select_relevant_plans(all_plans: List[Dict], user_profile: UserProfile, ai_response: str) -> List[Dict]:
    """Select the most relevant plans based on user preferences and AI recommendations"""
    # Extract plan names mentioned in AI response
    mentioned_plans = []
    for plan in all_plans:
        plan_name = plan.get('plan_name', '')
        if plan_name and plan_name.lower() in ai_response.lower():
            mentioned_plans.append(plan)
    
    # If AI mentioned specific plans, use those
    if mentioned_plans:
        return mentioned_plans[:3]  # Return up to 3 mentioned plans
    
    # Otherwise, filter based on user preferences
    filtered_plans = []
    
    for plan in all_plans:
        filtered_plans.append(plan)
    
    # Sort by user priority
    if user_profile.priority == "lowest-cost":
        filtered_plans.sort(key=lambda x: float(x.get('monthly_premium', 0)))
    elif user_profile.priority == "lowest-deductible":
        filtered_plans.sort(key=lambda x: float(x.get('deductible', 0)))
    elif user_profile.priority == "best-coverage":
        # Sort by lowest out-of-pocket max (better coverage)
        filtered_plans.sort(key=lambda x: float(x.get('max_out_of_pocket', 0)))
    else:
        # Balanced approach - sort by total annual cost
        filtered_plans.sort(key=lambda x: float(x.get('monthly_premium', 0)) * 12 + float(x.get('deductible', 0)))
    
    return filtered_plans[:3]  # Return top 3 filtered plans

def determine_recommendation(plan: Dict, user_profile: UserProfile) -> tuple:
    """Determine recommendation and rating based on plan characteristics and user preferences"""
    monthly_premium = float(plan.get('monthly_premium', 0))
    deductible = float(plan.get('deductible', 0))
    
    if user_profile.priority == "lowest-cost":
        return "Lowest Cost", 4.0
    elif user_profile.priority == "best-coverage":
        return "Best Coverage", 4.8
    elif user_profile.priority == "lowest-deductible":
        return "Lowest Deductible", 4.5
    else:
        # Default recommendation based on plan characteristics
        if monthly_premium < 300:
            return "Lowest Cost", 4.0
        elif deductible < 1500:
            return "Lowest Deductible", 4.5
        else:
            return "Best Value", 4.3

def generate_pros_cons(plan: Dict) -> tuple:
    """Generate pros and cons based on plan characteristics"""
    pros = []
    cons = []
    
    monthly_premium = float(plan.get('monthly_premium', 0))
    deductible = float(plan.get('deductible', 0))
    plan_type = plan.get('plan_type', '')
    
    if plan.get('hsa_eligible'):
        pros.append("HSA eligible for tax benefits")
    else:
        cons.append("Not HSA eligible")
    
    if plan_type == 'PPO':
        pros.append("Flexible provider network")
    elif plan_type == 'HMO':
        pros.append("Lower premiums")
        cons.append("Limited provider network")
    
    if deductible < 2000:
        pros.append("Low deductible")
    else:
        cons.append("High deductible")
    
    if monthly_premium < 400:
        pros.append("Affordable premium")
    else:
        cons.append("Higher premium")
    
    return pros, cons

def build_ai_advice_question(profile: UserProfile) -> str:
    """Build a question specifically for generating personalized AI advice"""
    question_parts = []
    
    # Basic profile information
    if profile.age:
        question_parts.append(f"I am {profile.age} years old")
    else:
        question_parts.append("I am seeking health insurance advice")
    
    if profile.familySize:
        question_parts.append(f"with a family size of {profile.familySize}")
    
    question_parts.append(f"and my income range is {profile.income}")
    
    # Health information
    if profile.healthConditions and profile.healthConditions != ['None']:
        conditions = ", ".join([c for c in profile.healthConditions if c != 'None'])
        if conditions:
            question_parts.append(f"I have health conditions: {conditions}")
    
    if profile.prescriptionMeds == "yes":
        question_parts.append("I take prescription medications regularly")
    
    if profile.priority:
        question_parts.append(f"My priority is {profile.priority}")
    
    # Request for personalized advice
    question_parts.append("Based on my profile, please provide personalized advice about:")
    question_parts.append("1. What type of health insurance plan would be best for me")
    question_parts.append("2. Key factors I should consider")
    question_parts.append("3. Potential risks or concerns")
    question_parts.append("4. Specific recommendations for my situation")
    question_parts.append("Please provide clear, actionable advice that I can use to make an informed decision.")
    
    return " ".join(question_parts)

def parse_ai_advice_response(ai_response: str, user_profile: UserProfile) -> AIAdviceResponse:
    """Parse the AI response into structured advice"""
    try:
        # For now, create structured advice from the AI response
        # In a more sophisticated implementation, you could use AI to parse this
        
        # Split the response into sections
        lines = ai_response.split('\n')
        
        # Extract key points (look for bullet points or numbered lists)
        key_points = []
        risk_factors = []
        recommendations = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                if any(word in line.lower() for word in ['risk', 'concern', 'warning', 'caution']):
                    risk_factors.append(line.lstrip('•-*123456789. '))
                elif any(word in line.lower() for word in ['recommend', 'suggest', 'consider', 'choose']):
                    recommendations.append(line.lstrip('•-*123456789. '))
                else:
                    key_points.append(line.lstrip('•-*123456789. '))
        
        # If no structured points found, create them from the text
        if not key_points:
            key_points = [
                "Consider your healthcare usage patterns",
                "Evaluate provider network coverage",
                "Compare total annual costs including deductibles"
            ]
        
        if not risk_factors:
            risk_factors = [
                "High deductibles may be challenging if you have frequent healthcare needs",
                "Limited networks may restrict access to preferred providers"
            ]
        
        if not recommendations:
            recommendations = [
                "Review plan networks before enrolling",
                "Consider your expected healthcare usage for the year",
                "Compare total costs, not just monthly premiums"
            ]
        
        return AIAdviceResponse(
            advice=ai_response,
            keyPoints=key_points,
            riskFactors=risk_factors,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error parsing AI advice response: {e}")
        # Return fallback advice
        return AIAdviceResponse(
            advice="Based on your profile, I recommend focusing on plans that match your healthcare needs and budget. Consider factors like deductibles, provider networks, and prescription coverage when making your decision.",
            keyPoints=["Consider total annual costs", "Evaluate provider networks", "Review prescription coverage"],
            riskFactors=["High deductibles may be challenging", "Limited networks may restrict access"],
            recommendations=["Review plan details carefully", "Compare multiple options", "Consider your healthcare usage"]
        )

@app.post("/ai-advice", response_model=AIAdviceResponse)
async def get_ai_advice(request: ComparisonRequest):
    """Generate personalized AI advice based on user profile"""
    try:
        if rag_system is None:
            return JSONResponse(
                status_code=503,
                content={"error": "RAG system not initialized"}
            )
        
        # Build a comprehensive question for AI advice
        advice_question = build_ai_advice_question(request.userProfile)
        
        # Get AI response using the RAG system
        ai_response = await rag_system.aquery(advice_question)
        
        # Parse the AI response into structured advice
        structured_advice = parse_ai_advice_response(ai_response, request.userProfile)
        
        return structured_advice
        
    except Exception as e:
        logger.error(f"Error generating AI advice: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate AI advice: {str(e)}"}
        )

@app.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        total_plans = len(rag_system.plans) if hasattr(rag_system, 'plans') else 0
        return {
            "total_plans": total_plans,
            "system_status": "operational",
            "last_updated": datetime.now().isoformat(),
            "api_version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system stats")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 