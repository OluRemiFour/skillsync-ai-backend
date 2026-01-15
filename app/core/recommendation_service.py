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
        Create a detailed learning path for a student with these skills: {', '.join(skills)}.
        Their goal is: {goal}.
        
        Return a JSON array of objects.
        Each object MUST have: 
        - title (string): Name of the step
        - description (string): What to learn
        - priority (string): "High" or "Medium"
        - estimated_weeks (number): Duration
        - resource_link (string): A valid URL to a reputable course (Coursera, Udemy, etc.)
        """
        
        max_retries = len(self.api_keys) * 2 # Allow more retries if we have multiple keys
        attempts = 0
        
        while attempts < max_retries:
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return {"raw_response": response.text}
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
    
    async def analyze_skill_gap(self, current_skills: list[str], target_role: str, major: str):
        if not self.client:
            return {
                "missing_skills": [],
                "action_plan": ["Configure AI Service to see recommendations"]
            }
        
        prompt = f"""
        Analyze the skill gap for a student with these skills: {', '.join(current_skills)}.
        They are a {major} major targeting the role: {target_role}.
        
        Return a JSON object with:
        - missing_skills (list of strings): Critical technical skills they likely lack.
        - action_plan (list of strings): 3-5 high-level steps to bridge the gap.
        
        Return valid JSON only.
        """
        
        max_retries = len(self.api_keys) * 2
        attempts = 0
        
        while attempts < max_retries:
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                import json
                return json.loads(response.text)
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "resource exhausted" in error_str or "quota" in error_str:
                    if self._rotate_key():
                        attempts += 1
                        continue
                return {"error": str(e), "missing_skills": [], "action_plan": []}
        
        return {"error": "Failed to analyze skills", "missing_skills": [], "action_plan": []}

recommendation_service = RecommendationService()
