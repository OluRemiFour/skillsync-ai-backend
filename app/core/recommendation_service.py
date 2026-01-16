import os
import json
from google import genai
from google.genai import types

class RecommendationService:
    def __init__(self):
        # In a real app, use os.getenv("GEMINI_API_KEY")
        # Using the provided key for now as requested
        self.api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCFlpwDlLCXZhBLiWmCVJwbP2FerIdysHE")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"

    def find_opportunities(self, course: str, skills: str) -> list[dict]:
        """
        Search for scholarships and internships using Gemini 2.5 Flash with Google Search grounding.
        """
        print(f"Starting AI search for {course} with skills: {skills}... 🔍")
        
        prompt = f"""
        Search for 5 current scholarships and internships for a student studying {course} 
        with skills in {skills}. 
        Return a JSON array of objects with these exact keys: 
        "title", "details", "link", "location", "type", "deadline".
        "type" must be either 'Remote', 'Onsite', or 'Hybrid'.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_mime_type="application/json"
                )
            )

            # Clean up the response text if necessary (usually not needed with response_mime_type)
            result_text = response.text.strip()
            
            # Allow for potential markdown code block wrapping
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            data = json.loads(result_text)
            return data

        except Exception as e:
            print(f"\n❌ --- SEARCH FAILED ---")
            print(f"Error Message: {str(e)}")
            return []

# Singleton instance
recommendation_service = RecommendationService()
