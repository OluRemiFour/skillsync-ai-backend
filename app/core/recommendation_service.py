import google.generativeai as genai
from app.core.config import settings

class RecommendationService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    async def generate_learning_path(self, skills: list[str], goal: str):
        if not self.model:
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
            response = await self.model.generate_content_async(prompt)
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return {"raw_response": clean_text} # Frontend will parse this
        except Exception as e:
            return {"error": str(e)}

recommendation_service = RecommendationService()
