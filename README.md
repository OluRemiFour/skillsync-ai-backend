# SkillSync Backend

This is the Python/FastAPI backend for the SkillSync application. It handles data persistence, searching, matching, and web scraping for scholarships/internships.

## Setup

1.  **Prerequisites**: Python 3.10+, Chrome (for Selenium).
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Server**:
    ```bash
    uvicorn main:app --reload --port 8000
    ```

## Features

-   **FastAPI** for high-performance Async I/O.
-   **Selenium** for scraping scholarship data ("Predator" scraper).
-   **SQLModel** (Pydantic + SQLAlchemy) for database interactions.

## API Endpoints

-   `GET /api/scholarships/`: List all scholarships.
-   `POST /api/scholarships/scan`: Trigger a new scrape based on student profile.
