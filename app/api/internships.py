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
    from app.scrapers.internship_scraper import InternshipScraper
    from app.core.config import settings
    
    scraper = InternshipScraper()
    
    try:
        import anyio
        
        skills = profile.get('skills', [])
        major = profile.get('major', '')
        
        # Default simple query
        query = f"internships for {major} students"
        
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                
                prompt = (
                    f"Search for 5 current scholarships and internships for a student studying {major} "
                    f"with skills in {', '.join(skills)}. "
                    f"Return a JSON list of objects with these exact keys: "
                    f"'title', 'details', 'link', 'location', 'type', 'deadline'. "
                    f"'type' must be either 'Remote', 'Onsite', or 'Hybrid'."
                )
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        response_mime_type="application/json"
                    )
                )
                
                if response.text:
                    import json
                    results_json = json.loads(response.text)
                    
                    # Convert JSON results to Scholarship/Internship objects
                    results = []
                    for item in results_json:
                        # Map fields to our schema
                        obj = ScholarshipCreate(
                            title=item.get('title', 'Untitled Opportunity'),
                            provider=item.get('location', 'Unknown Provider'),
                            amount=item.get('type', 'N/A'), # Using amount field for Type temporarily
                            url=item.get('link', '#'),
                            description=f"{item.get('details', '')} | Deadline: {item.get('deadline', 'N/A')}",
                            deadline=item.get('deadline'), # Assuming model has this field
                            match_score=85 # Default high score for AI matches
                        )
                        results.append(obj)
                    
                    # Save to DB
                    for res in results:
                         if not any(existing.url == res.url for existing in internships_db):
                            db_item = Scholarship(**res.dict(), id=len(internships_db)+1)
                            internships_db.append(db_item)
                            
                    return results

            except Exception as ai_error:
                print(f"Gemini scan failed: {ai_error}")
                # Fallback to empty list or basic search if needed
                pass

        # Old scraper fallback if AI fails or returns nothing (optional, removed for now per request)
        # results = await anyio.to_thread.run_sync(scraper.scrape_internships, query)
        
        return []
        
        # Save to DB (mock in-memory for now, real DB later)
        if not results:
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
