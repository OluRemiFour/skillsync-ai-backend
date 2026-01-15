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
    """
    from app.scrapers.internship_scraper import InternshipScraper
    scraper = InternshipScraper()
    
    try:
        import anyio
        
        # Construct a better query
        skills = profile.get('skills', [])
        major = profile.get('major', '')
        query_terms = [major]
        if skills and isinstance(skills, list):
             query_terms.extend(skills[:2]) # Top 2 skills
        
        query = " ".join([q for q in query_terms if q])
        if not query: query = "software engineering"

        # Run scraper in a thread
        results = await anyio.to_thread.run_sync(
            scraper.scrape_internships, 
            query
        )
        
        # Save to DB (mock in-memory for now, real DB later)
        if not results:
             # Fallback if no results found
             return []

        for res in results:
            # Simple dedup check based on URL
            if not any(existing.url == res.url for existing in internships_db):
                db_item = Scholarship(**res.dict(), id=len(internships_db)+1)
                internships_db.append(db_item)
            
        return results
    except Exception as e:
        print(f"Error in scan: {e}") # Debug print
        raise HTTPException(status_code=500, detail=str(e))
