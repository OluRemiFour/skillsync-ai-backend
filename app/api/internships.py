from typing import List
from fastapi import APIRouter, HTTPException
from app.models.scholarship import Scholarship, ScholarshipCreate 
# Reusing Scholarship model for now as it has similar fields (title, provider, amount, url)
# In future refactor, we can create a generic Opportunity model.

from app.scrapers.scholarship_scraper import ScholarshipScraper

router = APIRouter()

# Mock DB for demo purpose
internships_db = []

@router.get("/", response_model=List[Scholarship])
async def get_internships():
    return internships_db

@router.post("/scan", response_model=List[ScholarshipCreate])
async def trigger_scan(profile: dict):
    """
    Triggers the scraper to find internships based on profile.
    Uses Gemini AI to construct an optimized search query.
    """
    from app.core.recommendation_service import recommendation_service
    
    try:
        skills = profile.get('skills', [])
        major = profile.get('major', '')
        
        # Call the recommendation service
        # Combine skills list into a string if needed, or pass as is if service handles it.
        # Service expects string: "React, Node.js"
        skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
        
        results_json = await recommendation_service.find_opportunities(course=major, skills=skills_str)
        
        # Convert JSON results to Scholarship/Internship objects
        results = []
        for item in results_json:
            # Map fields to our schema
            obj = ScholarshipCreate(
                title=item.get('title', 'Untitled Opportunity'),
                provider=item.get('location', 'Unknown Provider'),
                amount=item.get('type', 'N/A'), 
                url=item.get('link', '#'),
                description=f"{item.get('details', '')} | Deadline: {item.get('deadline', 'N/A')}",
                deadline=item.get('deadline'),
                match_score=85 
            )
            results.append(obj)
        
        # Save to DB
        for res in results:
             if not any(existing.url == res.url for existing in internships_db):
                db_item = Scholarship(**res.dict(), id=len(internships_db)+1)
                internships_db.append(db_item)
                
        return results

    except Exception as e:
        print(f"Error in scan: {e}") # Debug print
        raise HTTPException(status_code=500, detail=str(e))
