from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.scholarship import Scholarship, ScholarshipCreate
from app.scrapers.scholarship_scraper import ScholarshipScraper

router = APIRouter()

# In-memory mock DB for demo
scholarships_db = []

@router.get("/", response_model=List[Scholarship])
async def get_scholarships():
    return scholarships_db

@router.post("/scan", response_model=List[ScholarshipCreate])
async def trigger_scan(profile: dict):
    """
    Triggers the 'Predator' scraper to find scholarships for the given profile.
    """
    scraper = ScholarshipScraper()
    try:
        # Run scraper (synchronously for now for demo, should be async/background)
        results = scraper.run_predator_scan(profile)
        
        # Save to DB (mock)
        for res in results:
            # Convert to DB model with ID
            db_item = Scholarship(**res.dict(), id=len(scholarships_db)+1)
            scholarships_db.append(db_item)
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
