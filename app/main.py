import logging
import sys
from data.db import save_job_to_db, create_indexes

logging.basicConfig(
    filename="portal_job_scraper.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a'
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Job started via Cloud Run")
    create_indexes()
    save_job_to_db()
    logger.info("Job finished. Container exiting.")
    
if __name__ == "__main__":
    main()
