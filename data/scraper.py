import logging
from jobspy import scrape_jobs
from typing import Dict, List

logger = logging.getLogger(__name__)

def scrape_linkedin(result_count:int) -> List[Dict]:
    logger.info(f"Starting to scrape {result_count} jobs from LinkedIn...")
    try:
        jobs = scrape_jobs(
        site_name=["linkedin"],
        hours_old=24,
        linkedin_fetch_description=True,
        location="United States",
        results_wanted=int(result_count),
        job_type= "internship"
        )

    except Exception as e:
        logger.exception(f"Error scraping LinkedIn: {e}")
        raise
    
    if jobs.empty:
        logger.warning("jobs dataframe is empty")
        return []

    jobs_dict = jobs.to_dict('records')
    logger.info("Converted jobs dataframe into list of dictionaries. Returning...")
    
    return jobs_dict
