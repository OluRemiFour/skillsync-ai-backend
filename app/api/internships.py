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
        
        # Try to use Gemini for better query generation
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                
                skill_text = ", ".join(skills[:5]) if skills else "general skills"
                prompt = (
                    f"Create a specific, effective Google Search query to find current internship openings "
                    f"for a university student majoring in {major} with skills in {skill_text}. "
                    f"Return ONLY the raw query string (e.g. 'Software Engineering internships python remote'). "
                    f"Do not use quotes or explanations."
                )
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp", 
                    contents=prompt
                )
                
                if response.text:
                    query = response.text.strip()
            except Exception as ai_error:
                print(f"Gemini query generation failed: {ai_error}, falling back to simple query.")
                # Fallback logic
                query_terms = [major, "internship"]
                if skills and isinstance(skills, list):
                    query_terms.extend(skills[:2])
                query = " ".join([str(q) for q in query_terms if q])

        print(f"Scraping with query: {query}")

        # Run scraper in a thread
        results = await anyio.to_thread.run_sync(
            scraper.scrape_internships, 
            query
        )
        
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
