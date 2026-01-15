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
    from app.scrapers.scholarship_scraper import ScholarshipScraper
    from app.core.config import settings
    
    scraper = ScholarshipScraper()
    
    try:
        import anyio
        
        skills = profile.get('skills', [])
        major = profile.get('major', '')
        
        # Default simple query
        query = f"scholarships for {major} students"
        
        # Try to use Gemini for better query generation
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                
                skill_text = ", ".join(skills[:5]) if skills else "general"
                prompt = (
                    f"Create a specific, effective Google Search query to find current scholarships "
                    f"for a university student majoring in {major} with interests in {skill_text}. "
                    f"Return ONLY the raw query string. Do not use quotes."
                )
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp", 
                    contents=prompt
                )
                
                if response.text:
                    query = response.text.strip()
                    # Inject query into profile so scraper uses it
                    profile['ai_query'] = query
            except Exception as ai_error:
                print(f"Gemini query generation failed: {ai_error}")

        print(f"Scanning for scholarships with query: {query}")

        # Run scraper in a thread
        results = await anyio.to_thread.run_sync(scraper.run_predator_scan, profile)
        
        # Save to DB (mock)
        for res in results:
            if not any(existing.url == res.url for existing in scholarships_db):
                db_item = Scholarship(**res.dict(), id=len(scholarships_db)+1)
                scholarships_db.append(db_item)
            
        return results
    except Exception as e:
        print(f"Error in scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
