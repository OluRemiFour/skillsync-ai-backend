import logging
from typing import List
from app.models.scholarship import ScholarshipCreate
# Fallback to pure search if Selenium is too heavy or blocked
try:
    from googlesearch import search
except ImportError:
    search = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InternshipScraper:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def scrape_internships(self, query: str = "software engineer internship") -> List[ScholarshipCreate]:
        """
        Scrapes internships using Google Search as a resilient fallback.
        Real scraping of LinkedIn/Indeed often requires paid APIs or complex proxies.
        This provides 'real' links found via Google.
        """
        results = []
        full_query = f"{query} internship 2025 apply"
        logger.info(f"Searching for: {full_query}")

        try:
            if search:
                # Get top 10 results
                i = 0
                for url in search(full_query, num_results=10, advanced=True):
                    # advanced=True yields SearchResult objects with title, desc, url
                    if i >= 10: break
                    
                    try:
                        title = url.title if hasattr(url, 'title') else "Internship Opportunity"
                        description = url.description if hasattr(url, 'description') else "Click to view details."
                        link = url.url if hasattr(url, 'url') else str(url)
                        
                        # Basic filtering
                        if "linkedin" in link or "indeed" in link or "glassdoor" in link or "careers" in link or "jobs" in link:
                             item = ScholarshipCreate(
                                title=title,
                                provider="Web Search", 
                                amount="Competitive", # improved from "Unknown"
                                url=link,
                                tags=query,
                                match_score=80
                            )
                             results.append(item)
                             i += 1
                    except Exception as e:
                        logger.warning(f"Error parsing search result: {e}")
                        continue
            else:
                logger.warning("googlesearch-python not installed. Returning fallback.")
                # Fallback if library missing
                return []

        except Exception as e:
             logger.error(f"Internship scrape failed: {e}")
        
        return results
