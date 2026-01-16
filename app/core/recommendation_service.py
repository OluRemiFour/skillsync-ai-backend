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

    async def generate_learning_path(self, skills: list[str], goal: str) -> dict:
        """
        Generate a personalized learning path based on current skills and a career goal.
        """
        print(f"Generating learning path for goal: {goal} with current skills: {skills}... 🎓")
        
        prompt = f"""
        Act as an expert career counselor. Generate a detailed, personalized learning path for a student who wants to become a {goal}.
        Current skills: {', '.join(skills)}.
        
        The learning path should include:
        1. A brief roadmap overview.
        2. A list of 4-6 specific milestones or modules.
        3. For each milestone, provide:
           - "title": Name of the milestone.
           - "description": What to learn.
           - "resources": A list of 2-3 specific topics or skills to focus on.
           - "estimated_time": Approximate time to complete.
        
        Return a JSON object with this exact structure:
        {{
            "roadmap": "string",
            "milestones": [
                {{
                    "title": "string",
                    "description": "string",
                    "resources": ["string", "string"],
                    "estimated_time": "string"
                }}
            ]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            result_text = response.text.strip()
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            data = json.loads(result_text)
            return data

        except Exception as e:
            print(f"\n❌ --- GENERATION FAILED ---")
            print(f"Error Message: {str(e)}")
            return {"error": str(e), "roadmap": "Failed to generate roadmap", "milestones": []}

    async def analyze_skill_gap(self, current_skills: list[str], target_role: str, major: str) -> dict:
        """
        Analyze the gap between current skills and target role requirements.
        """
        print(f"Analyzing skill gap for {target_role} (Major: {major})... 📊")
        
        prompt = f"""
        Analyze the skill gap for a student majoring in {major} who wants to become a {target_role}.
        Current skills: {', '.join(current_skills)}.
        
        Identify:
        1. Missing skills required for the role.
        2. A step-by-step action plan to bridge the gap.
        
        Return a JSON object with this exact structure:
        {{
            "missing_skills": ["string", "string"],
            "action_plan": ["string", "string"]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            result_text = response.text.strip()
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            data = json.loads(result_text)
            return data

        except Exception as e:
            print(f"\n❌ --- ANALYSIS FAILED ---")
            print(f"Error Message: {str(e)}")
            return {"error": str(e), "missing_skills": [], "action_plan": []}

# Singleton instance
recommendation_service = RecommendationService()
