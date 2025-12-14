# OVERVIEW

This is a job scraper that CURRENTLY only scrapes from LinkedIn. It scrapes, normalizes, creates and embedding, and inserts each job listing into MongoDB to go along with the Application Optimization service. It refreshes by adding new jobs everyday at midnight (depends on local time of system).

Currently, the service just looks for all types of INTERNSHIPS. 

# Dependencies 

This service uses uv as a package manager. 

Additonally, it uses the [JobSpy](https://github.com/speedyapply/JobSpy?tab=readme-ov-file) library. 

The environment vars are:
```
#MONGODB URI
MONGODB_URI: str (contact Anthony for now)

#MONGODB JOB DB NAME
DATABASE_NAME = "portal_application_optimization"

#EMBEDDING MODEL
EMBEDDING_MODEL="all-MiniLM-L6-v2"

#NUMBER OF JOBS
RESULT_COUNT = 500
```
