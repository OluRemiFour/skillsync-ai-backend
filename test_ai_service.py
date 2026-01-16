import sys
import os

# Add the backend directory to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.recommendation_service import recommendation_service

def test_service():
    print("Testing Recommendation Service...")
    try:
        results = recommendation_service.find_opportunities(
            course="Computer Science",
            skills="React, Node.js"
        )
        print("\nResults:")
        print(results)
        
        if isinstance(results, list) and len(results) > 0:
            print("\n✅ Service returned valid list of results.")
            first_item = results[0]
            required_keys = ["title", "details", "link", "location", "type", "deadline"]
            if all(key in first_item for key in required_keys):
                 print("✅ Results have correct structure.")
            else:
                 print("❌ Results missing required keys.")
        else:
            print("\n❌ Service returned empty results or invalid format.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_service()
