"""
SmartSort-AI FastAPI Backend
Handles image upload, classification, and recycling facility lookup
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai_model.classifier import PlasticClassifier
from backend.database import Database

# ============================================
# INITIALIZE APP
# ============================================

app = FastAPI(
    title="PlasticNet API",
    description="AI-Powered Plastic Waste Classification System",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize classifier and database
classifier = PlasticClassifier()
db = Database()

# ============================================
# MODELS
# ============================================

class PredictionResponse(BaseModel):
    success: bool
    predicted_class: str
    confidence: float
    confidence_percent: str
    full_name: str
    recycling_code: str
    recyclability: str
    common_items: List[str]
    value_per_kg: float
    curbside_accepted: bool
    instructions: str
    tips: List[str]
    color: str
    all_probabilities: dict
    timestamp: str
    nearest_facilities: Optional[List[dict]] = None

class FacilityQuery(BaseModel):
    latitude: float
    longitude: float
    radius_km: Optional[float] = 10.0
    plastic_type: Optional[str] = None

class HistoryItem(BaseModel):
    id: int
    plastic_type: str
    confidence: float
    timestamp: str
    image_name: Optional[str] = None

# ============================================
# STARTUP/SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting PlasticNet API...")
    
    # Load classifier model
    if classifier.load_model():
        print("✅ AI Model loaded successfully")
    else:
        print("⚠️  Failed to load model - using mock mode")
    
    # Initialize database
    db.initialize()
    print("✅ Database initialized")
    
    print("🎉 PlasticNet API ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down PlasticNet API...")
    db.close()

# ============================================
# ROUTES
# ============================================

@app.get("/")
async def root():
    """API health check"""
    return {
        "name": "PlasticNet API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "classify": "/classify",
            "facilities": "/facilities",
            "history": "/history",
            "stats": "/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    model_loaded = classifier.model is not None
    db_connected = db.conn is not None
    
    return {
        "status": "healthy" if (model_loaded and db_connected) else "degraded",
        "model_loaded": model_loaded,
        "database_connected": db_connected,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/classify", response_model=PredictionResponse)
async def classify_plastic(
    file: UploadFile = File(...),
    latitude: Optional[float] = Query(None, description="User latitude for facility lookup"),
    longitude: Optional[float] = Query(None, description="User longitude for facility lookup"),
    radius_km: Optional[float] = Query(10.0, description="Search radius in kilometers")
):
    """
    Classify plastic waste from uploaded image
    
    - **file**: Image file (JPG, PNG)
    - **latitude**: Optional user location for nearby facilities
    - **longitude**: Optional user location for nearby facilities
    - **radius_km**: Search radius for facilities (default 10km)
    """
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image data
        image_data = await file.read()
        
        # Classify image
        result = classifier.predict(image_data)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Classification failed'))
        
        # Add timestamp
        result['timestamp'] = datetime.now().isoformat()
        
        # Find nearby recycling facilities if location provided
        if latitude is not None and longitude is not None:
            facilities = db.get_nearby_facilities(
                latitude, 
                longitude, 
                result['predicted_class'],
                radius_km
            )
            result['nearest_facilities'] = facilities
        
        # Save to history
        db.add_classification_history(
            plastic_type=result['predicted_class'],
            confidence=result['confidence'],
            image_name=file.filename
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/facilities")
async def get_facilities(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    plastic_type: Optional[str] = Query(None, description="Filter by plastic type (PET, HDPE, OTHER)"),
    radius_km: float = Query(10.0, description="Search radius in kilometers")
):
    """
    Get nearby recycling facilities
    
    Returns list of facilities that accept the specified plastic type
    """
    facilities = db.get_nearby_facilities(latitude, longitude, plastic_type, radius_km)
    
    return {
        "success": True,
        "count": len(facilities),
        "radius_km": radius_km,
        "facilities": facilities
    }

@app.post("/facilities")
async def add_facility(
    name: str,
    latitude: float,
    longitude: float,
    address: str,
    accepts_pet: bool = True,
    accepts_hdpe: bool = True,
    accepts_other: bool = False,
    phone: Optional[str] = None,
    hours: Optional[str] = None,
    website: Optional[str] = None
):
    """
    Add a new recycling facility (admin function)
    """
    facility_id = db.add_facility(
        name=name,
        latitude=latitude,
        longitude=longitude,
        address=address,
        accepts_pet=accepts_pet,
        accepts_hdpe=accepts_hdpe,
        accepts_other=accepts_other,
        phone=phone,
        hours=hours,
        website=website
    )
    
    return {
        "success": True,
        "facility_id": facility_id,
        "message": "Facility added successfully"
    }

@app.get("/history")
async def get_history(
    limit: int = Query(50, description="Number of records to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """
    Get classification history
    
    Returns recent classification attempts
    """
    history = db.get_classification_history(limit, offset)
    
    return {
        "success": True,
        "count": len(history),
        "history": history
    }

@app.get("/stats")
async def get_statistics():
    """
    Get system statistics
    
    Returns classification counts, accuracy metrics, etc.
    """
    stats = db.get_statistics()
    
    return {
        "success": True,
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/plastic-info/{plastic_type}")
async def get_plastic_info(plastic_type: str):
    """
    Get detailed information about a plastic type
    
    - **plastic_type**: PET, HDPE, or OTHER
    """
    plastic_type = plastic_type.upper()
    
    if plastic_type not in classifier.MATERIAL_INFO:
        raise HTTPException(status_code=404, detail="Plastic type not found")
    
    info = classifier.MATERIAL_INFO[plastic_type]
    
    return {
        "success": True,
        "plastic_type": plastic_type,
        "info": info
    }

@app.delete("/history/{record_id}")
async def delete_history_record(record_id: int):
    """
    Delete a history record (admin function)
    """
    success = db.delete_history_record(record_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {
        "success": True,
        "message": "Record deleted successfully"
    }

@app.get("/market-prices")
async def get_market_prices():
    """
    Get current market prices for recycled plastics
    """
    prices = {
        "PET": {
            "price_per_kg": 0.12,
            "currency": "USD",
            "last_updated": "2025-10-10",
            "trend": "stable"
        },
        "HDPE": {
            "price_per_kg": 0.18,
            "currency": "USD",
            "last_updated": "2025-10-10",
            "trend": "increasing"
        },
        "OTHER": {
            "price_per_kg": 0.02,
            "currency": "USD",
            "last_updated": "2025-10-10",
            "trend": "stable"
        }
    }
    
    return {
        "success": True,
        "prices": prices,
        "disclaimer": "Prices vary by location and market conditions"
    }

# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║         PlasticNet FastAPI Backend               ║
    ║     AI-Powered Plastic Waste Classification       ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )