import logging
import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from pymongo.server_api import ServerApi
from data.normalize import normalize_jobs

load_dotenv()

uri = os.getenv("MONGODB_URI", "")
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
DATABASE_NAME = os.getenv("DATABASE_NAME", "")

logger = logging.getLogger(__name__)

def create_indexes():
    try:
        db = client[DATABASE_NAME]
        collection = db.job_embeddings
        collection.create_index("created_at", expireAfterSeconds=2592000)
        collection.create_index("job_id", unique=True)
        logger.info("Indexes created")
    except Exception as e:
        logger.error(f"Index creation failed: {str(e)}")

def save_job_to_db():
    try:
        db = client[DATABASE_NAME]
        collection = db.job_embeddings

        jobs_list = normalize_jobs()
        if not jobs_list:
            logger.info("No jobs to insert")
            return []
        
        result = collection.insert_many(jobs_list, ordered=False)
        logger.info(f"Successfully saved {len(result.inserted_ids)} jobs")
        return result.inserted_ids

    except BulkWriteError as e:
        n_inserted = (e.details or {}).get("nInserted", 0)
        logger.info(f"Inserted {n_inserted} jobs; skipped duplicates")
        return []

    except Exception as e:
        logger.error(f"Database save failed: {str(e)}")
        raise
