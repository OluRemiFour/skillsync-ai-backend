import random
from google import genai
from google.genai import types
from app.core.config import settings

class RecommendationService:
    def __init__(self):
        # Collect all available API keys
        self.api_keys = []
        if settings.GEMINI_API_KEY:
            self.api_keys.append(settings.GEMINI_API_KEY)
        
        # Check for additional keys
        for key_attr in ['GEMINI_API_KEY_1', 'GEMINI_API_KEY_2', 'GEMINI_API_KEY_3', 'GEMINI_API_KEY_4']:
            val = getattr(settings, key_attr, None)
            if val:
                self.api_keys.append(val)
        
        # Remove duplicates and empty strings
        self.api_keys = list(set([k for k in self.api_keys if k]))
        
        self.current_key_index = 0
        self.model_id = 'gemini-2.0-flash'
        self.client = self._get_client()

    def _get_client(self):
        if not self.api_keys:
            return None
        return genai.Client(api_key=self.api_keys[self.current_key_index])

    def _rotate_key(self):
        if not self.api_keys or len(self.api_keys) <= 1:
            return False
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"Switching to API Key index: {self.current_key_index}")
        self.client = self._get_client()
        return True

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
        
        max_retries = len(self.api_keys)
        attempts = 0
        
        while attempts < max_retries:
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt
                )
                clean_text = response.text.replace('```json', '').replace('```', '').strip()
                return {"raw_response": clean_text}
            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limit or quota errors (429 or 403 sometimes implies quota)
                if "429" in error_str or "resource exhausted" in error_str or "quota" in error_str:
                    print(f"API Key Exhausted (Attempt {attempts+1}/{max_retries}): {e}")
                    if self._rotate_key():
                        attempts += 1
                        continue
                    else:
                        return {"error": "All API keys exhausted."}
                
                # For other errors, return immediately
                return {"error": str(e)}
        
        return {"error": "Failed to generate content after retries."}

recommendation_service = RecommendationService()
