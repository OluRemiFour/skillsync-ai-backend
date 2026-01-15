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
        
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                
                prompt = (
                    f"Search for 5 current scholarships due soon for a student studying {major} "
                    f"with interests in {', '.join(skills)}. "
                    f"Return a JSON list of objects with these exact keys: "
                    f"'title', 'provider', 'amount', 'link', 'deadline', 'description'. "
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
                    
                    # Convert JSON to Scholarship objects
                    results = []
                    for item in results_json:
                        db_item = ScholarshipCreate(
                            title=item.get('title', 'Unknown Scholarship'),
                            provider=item.get('provider', 'Various'),
                            amount=str(item.get('amount', 'Varies')),
                            url=item.get('link', '#'),
                            description=item.get('description', ''),
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

            except Exception as ai_error:
                print(f"Gemini scholarship scan failed: {ai_error}")

        return []
    except Exception as e:
        print(f"Error in scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
