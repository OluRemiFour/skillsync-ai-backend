from google import genai
from app.core.config import settings

class RecommendationService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.model_id = 'gemini-1.5-flash'
        else:
            self.client = None

    async def generate_learning_path(self, skills: list[str], goal: str):
        if not self.client:
            return {
                "error": "AI Service not configured",
                "path": []
            }
        
        prompt = f"""
        Act as a career counselor. 
        Create a learning path for a student with these skills: {', '.join(skills)}.
        Their goal is: {goal}.
        
        Return a valid JSON array of objects. Do not include any markdown formatting or code blocks.
        Each step should have: 
        - title
        - description
        - priority (High/Medium)
        - estimated_weeks
        - resource_link (a valid URL to a reputable course like Coursera, Udemy, or documentation)
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return {"raw_response": clean_text}
        except Exception as e:
            return {"error": str(e)}

recommendation_service = RecommendationService()
