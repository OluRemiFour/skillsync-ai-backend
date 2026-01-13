import logging
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.models.scholarship import ScholarshipCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class ScholarshipScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # In Docker/Render environments, we might NEED to specify the binary location
        import os
        chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
        if chrome_bin:
            chrome_options.binary_location = chrome_bin

        try:
            # Initialize Chrome with webdriver_manager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            # Ensure driver is None if initialization fails
            self.driver = None
        
    def scrape_scholarships_com(self, query: str = "computer science") -> List[ScholarshipCreate]:
        """
        Example scraper for a scholarship site.
        NOTE: This is a template. Real scraping requires robust selector handling and headers.
        """
        results = []
        try:
            if not self.driver:
                logger.error("Driver not initialized, skipping scrape")
                raise Exception("Driver not initialized")
                
            url = f"https://www.scholarships.com/financial-aid/college-scholarships/scholarship-directory/academic-major/{query}"
            logger.info(f"Scraping URL: {url}")
            self.driver.get(url)
            
            # Wait for content
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.scholarshiplist li"))
            )
            
            items = self.driver.find_elements(By.CSS_SELECTOR, "ul.scholarshiplist li")
            
            for item in items[:10]: # Limit to top 10 for now
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, "h3 a")
                    amount_elem = item.find_element(By.CSS_SELECTOR, ".scholarship-amount")
                    deadline_elem = item.find_element(By.CSS_SELECTOR, ".scholarship-deadline")
                    
                    title = title_elem.text
                    link = title_elem.get_attribute("href")
                    amount = amount_elem.text.strip()
                    # Parse deadline later, keep as text for now or verify format
                    
                    scholarship = ScholarshipCreate(
                        title=title,
                        provider="Scholarships.com",
                        amount=amount,
                        url=link,
                        tags=query,
                        match_score=85 
                    )
                    results.append(scholarship)
                except Exception as e:
                    logger.warning(f"Failed to parse item: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            # Fallback Mock Data if scraping fails (e.g. anti-bot or network issue)
            if not results:
                logger.info("Returning fallback data due to scrape failure")
                results.append(ScholarshipCreate(
                    title=f"Opportunity in {query}", 
                    provider="Manual Entry (Fallback)", 
                    amount="$5000 / $30hr", 
                    url="https://google.com/search?q=" + query, 
                    tags=query, 
                    match_score=80
                ))
        finally:
            if self.driver:
                self.driver.quit()
            
        return results

    def run_predator_scan(self, student_profile: dict) -> List[ScholarshipCreate]:
        """
        The 'Predator' scan - aggressively finds matches for a specific profile.
        """
        # In a real app, this would iterate through multiple sources
        # (Chegg, Fastweb, etc.) based on the student's major/GPA.
        logger.info(f"Starting Predator Scan for {student_profile.get('major')}")
        
        # 1. Scrape Source A
        results_a = self.scrape_scholarships_com(student_profile.get('major', 'computer-science'))
        
        # 2. Filter/Rank results (Mock logic)
        verified_results = []
        for s in results_a:
            # AI Logic would go here to verify eligibility
            if student_profile.get('gpa', 0) >= 3.0:
                s.match_score += 5
            verified_results.append(s)
            
        return verified_results
