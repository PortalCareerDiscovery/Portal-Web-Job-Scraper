import os
import logging
import datetime
from data.scraper import scrape_linkedin
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

logger = logging.getLogger(__name__)

RESULT_COUNT = int(os.getenv("RESULT_COUNT", "5"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

_model = None

def normalize_jobs():

    raw_jobs = scrape_linkedin(RESULT_COUNT)

    if not raw_jobs:
        return []
    
    normalized_list = []
    for job in raw_jobs:

        job_id = job.get("id")
        job_url = job.get("job_url_direct") or job.get("job_url")
        job_title = job.get("title")
        job_company = job.get("company")
        job_location = job.get("location")
        job_date_posted = job.get("date_posted")
        job_remote = job.get("is_remote")
        job_function = job.get("job_function")
        job_description = job.get("description")

        if not job_id or not job_title or not job_description or not job_company:
            logger.warning(f"Skipping job due to missing required fields (id, title, description, or company). ID: {job_id}")
            continue

        try:
            embedding = create_job_embedding(job_description)
        except Exception as e:
            logger.error(f"Failed to create embedding for job {job_id}: {e}")
            continue

        normalized_list.append({
            "job_id": job_id,
            "title": job_title,
            "description": job_description,
            "type": job_function,
            "company": job_company,
            "location": job_location,
            "salary": None,
            "job_url": job_url,
            "remote": job_remote,
            "date_posted": job_date_posted,
            "embedding": embedding,
            "embedding_model": EMBEDDING_MODEL,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
            "deleted": False
        })
    
    return normalized_list

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def create_job_embedding(job_description: str):
    try:
        model = get_model()
        embedding = model.encode(job_description)
        return embedding.tolist()

    except Exception as e:
        raise e
