import logging
import schedule
import time
from data.db import save_job_to_db, create_indexes

logging.basicConfig(
    filename="portal_job_scraper.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a'
)

logger = logging.getLogger(__name__)

def run_scheduled_job():
    save_job_to_db()

def main():
    logger.info("Application started")
    create_indexes()
    schedule.every().day.at("00:00").do(run_scheduled_job)

    while True:
        schedule.run_pending()
        time.sleep(1)
    
if __name__ == "__main__":
    main()
