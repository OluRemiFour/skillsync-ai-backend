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

    async def find_opportunities(self, course: str, skills: str) -> list[dict]:
        """
        Search for scholarships and internships using Gemini 2.5 Flash with Google Search grounding.
        Note: response_mime_type is not supported when using tools like Google Search.
        """
        print(f"Starting AI search for {course} with skills: {skills}... 🔍")
        
        prompt = f"""
        Search for 5 current, real-world scholarships and internships for a student studying {course} with skills in {skills}.
        
        CRITICAL: Return ONLY a valid JSON array of objects.
        Each object MUST have these exact keys: 
        "title", "details", "link", "location", "type", "deadline".
        
        Deadline formatting:
        - If a specific date is found, use 'Month DD, YYYY' format.
        - If it's recurring or rolling, use 'Ongoing' or 'Rolling'.
        - Keep it as a concise string.
        
        Example structure:
        [
          {{"title": "...", "details": "...", "link": "...", "location": "...", "type": "...", "deadline": "..."}}
        ]
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                    # response_mime_type="application/json" is NOT supported with tools
                )
            )

            result_text = response.text.strip()
            
            # Extract JSON from potential markdown blocks or text response
            try:
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                data = json.loads(result_text)
                return data if isinstance(data, list) else []
            except (json.JSONDecodeError, IndexError):
                print(f"Failed to parse JSON directly. Attempting cleanup...")
                # Fallback: find the first '[' and last ']'
                start = result_text.find('[')
                end = result_text.rfind(']') + 1
                if start != -1 and end != 0:
                    data = json.loads(result_text[start:end])
                    return data if isinstance(data, list) else []
                return []

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
        Act as an elite career strategist and mentor. Generate a high-impact, personalized learning path for a candidate aiming to become a {goal}.
        Current Skills: {', '.join(skills)}.
        
        Guidelines for Content:
        - **Roadmap Overview**: A punchy, 2-sentence summary of the transformation journey.
        - **Milestones**: Provide 5 strategic phases.
        - **Descriptions**: Concise (max 3 sentences). Use **bolding** for key skills. 
        - **Resources**: Exactly 3 specific, recognized learning resources (e.g., "MDN Docs", "Advanced React Patterns on Frontend Masters").
        - **Icons**: Suggest a Lucide-React icon name for each phase (e.g., "Code", "Brain", "Layers", "Rocket", "Award").
        
        Return a JSON object with this exact structure:
        {{
            "roadmap": "A punchy summary.",
            "milestones": [
                {{
                    "title": "Phase Title",
                    "description": "Concise description with **bold** highlights.",
                    "resources": ["Resource 1", "Resource 2", "Resource 3"],
                    "estimated_time": "e.g., 2 weeks",
                    "icon": "IconName"
                }}
            ]
        }}
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            result_text = response.text.strip()
            
            # Robust JSON extraction
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
        Act as a technical recruiter and industry expert. Analyze the skill gap for a student majoring in {major} who is targeting a {target_role} role.
        Current Skills: {', '.join(current_skills)}.
        
        Requirements:
        1. **Missing Skills**: List 3-5 critical technical or soft skills currently lacking.
        2. **Action Plan**: Provide a numbered, step-by-step strategy to become job-ready. Each step should be one concise sentence.
        
        Formatting:
        - Use clean, professional language.
        - Ensure the output is ready for a high-end dashboard UI.
        
        Return a JSON object with this exact structure:
        {{
            "missing_skills": ["Skill Name 1", "Skill Name 2"],
            "action_plan": ["Step 1 description", "Step 2 description"]
        }}
        """

        try:
            response = await self.client.aio.models.generate_content(
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
