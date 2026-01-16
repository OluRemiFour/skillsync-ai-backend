from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.scholarship import Scholarship, ScholarshipCreate
from app.scrapers.scholarship_scraper import ScholarshipScraper

router = APIRouter()

# Mock DB for demo purpose
scholarships_db = []

@router.get("/", response_model=List[Scholarship])
async def get_scholarships():
    return scholarships_db

@router.post("/scan", response_model=List[ScholarshipCreate])
async def trigger_scan(profile: dict):
    """
    Triggers the scraper to find scholarships based on profile.
    Uses Gemini AI to construct an optimized search query.
    """
    from app.core.recommendation_service import recommendation_service
    
    try:
        skills = profile.get('skills', [])
        major = profile.get('major', '')
        
        # Call the recommendation service
        skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
        
        results_json = recommendation_service.find_opportunities(course=major, skills=skills_str)
        
        # Convert JSON results to Scholarship objects
        results = []
        for item in results_json:
            db_item = ScholarshipCreate(
                title=item.get('title', 'Unknown Scholarship'),
                provider=item.get('location', 'Various'), 
                amount=str(item.get('type', 'Varies')), 
                url=item.get('link', '#'),
                description=f"{item.get('details', '')} | Deadline: {item.get('deadline', 'N/A')}",
                deadline=item.get('deadline', 'Rolling'),
                match_score=90
            )
            results.append(db_item)

        # Save to DB
        for res in results:
            if not any(existing.url == res.url for existing in scholarships_db):
                db_item = Scholarship(**res.dict(), id=len(scholarships_db)+1)
                scholarships_db.append(db_item)

        return results
            
    except Exception as e:
        print(f"Error in scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
