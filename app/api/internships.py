from typing import List
from fastapi import APIRouter, HTTPException
from app.models.scholarship import Scholarship, ScholarshipCreate 
# Reusing Scholarship model for now as it has similar fields (title, provider, amount, url)
# In future refactor, we can create a generic Opportunity model.

from app.scrapers.scholarship_scraper import ScholarshipScraper

router = APIRouter()

@router.get("/", response_model=List[Scholarship])
async def get_internships():
    # Fetch from DB engine when implemented
    return []

@router.post("/scan", response_model=List[ScholarshipCreate])
async def trigger_scan(profile: dict):
    """
    Triggers the scraper to find internships.
    """
    scraper = ScholarshipScraper()
    try:
        # Run scraper (Reuse scholarship scraper logic but with internship keywords)
        results = scraper.scrape_scholarships_com(query=f"{profile.get('major', 'software')} internship")
        
        # Save to DB (mock)
        for res in results:
            # Convert to DB model with ID
            db_item = Scholarship(**res.dict(), id=len(internships_db)+1)
            internships_db.append(db_item)
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
