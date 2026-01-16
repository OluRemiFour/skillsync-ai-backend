import os
import json
from google import genai
from google.genai import types

class RecommendationService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.0-flash"

    def find_opportunities(self, course: str, skills: str) -> list[dict]:
        """
        Search for scholarships and internships using Gemini 2.0 Flash with Google Search grounding.
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

            # Clean up the response text if necessary
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

    async def generate_learning_path(self, skills: list[str], goal: str) -> dict:
        """
        Generate a personalized learning path based on skills and goal.
        """
        print(f"Generating learning path for goal: {goal}... 🚀")
        
        prompt = f"""
        Generate a personalized learning path for a student with these skills: {', '.join(skills)}.
        The goal is: {goal}.
        Return a JSON object with these exact keys:
        "title": A catchy title for the path.
        "description": A brief overview.
        "steps": A list of objects with "title", "description", and "resources" (list of strings).
        "estimated_duration": e.g., "6 weeks".
        """

        try:
            # We use synchronous call for now as the SDK might not be async-first in this version
            # or we can wrap it if needed. For now, matching the existing find_opportunities pattern.
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            return json.loads(result_text)

        except Exception as e:
            print(f"\n❌ --- LEARNING PATH GENERATION FAILED ---")
            print(f"Error Message: {str(e)}")
            return {"error": str(e)}

# Singleton instance
recommendation_service = RecommendationService()
