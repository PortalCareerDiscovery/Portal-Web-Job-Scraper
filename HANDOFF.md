# Service Handoff: Portal Web Job Scraper

## Overview

The Portal Web Job Scraper is a Python-based microservice designed to aggregate internship listings from LinkedIn. It functions as an automated ETL (Extract, Transform, Load) pipeline that runs on a daily schedule. The service scrapes job data, normalizes it, generates vector embeddings for semantic search, and stores the processed records in a MongoDB database.

This service supports the "Application Optimization" feature of the Portal platform, enabling candidates to find relevant opportunities through vector-based semantic matching.

## Architecture

### Core Components

1.  **Scraper (`data/scraper.py`)**:
    *   Leverages the `jobspy` library to interface with LinkedIn's job search.
    *   configured to target internships within the United States.
    *   Fetches job metadata including title, company, location, description, and direct URLs.

2.  **Normalization & Embedding (`data/normalize.py`)**:
    *   **Normalization**: Standardizes raw scraping output into a consistent schema. Filters out incomplete records (missing ID, title, company, or description).
    *   **Embedding**: Uses `sentence-transformers` (model: `all-MiniLM-L6-v2`) to generate vector embeddings from job descriptions.
    *   **Lazy Loading**: The heavy transformer model is lazy-loaded (instantiated only upon first use) to optimize startup time and resource usage.
    *   **Timestamps**: Adds UTC timestamps (`created_at`, `updated_at`) for audit trails.

3.  **Database Layer (`data/db.py`)**:
    *   **Connection**: Connects to MongoDB Atlas using `pymongo`.
    *   **Security**: Uses `certifi` to ensure robust SSL/TLS certificate verification across different environments (local vs. containerized).
    *   **Schema Enforcement**: Creates a unique index on `job_id` to prevent duplicate entries.
    *   **Data Lifecycle**: Implements a TTL (Time-To-Live) index on `created_at` (30 days) to automatically expire old listings.
    *   **Batch Operations**: Uses `insert_many` with `ordered=False` to maximize throughput, allowing non-duplicate records to be inserted even if some in the batch fail due to unique constraints.

4.  **Entry Point (`app/main.py`)**:
    *   Orchestrates the execution flow: Initialize Logging -> Ensure DB Indexes -> Run Scrape/Normalize/Load Pipeline.
    *   Designed as a "run-to-completion" script, making it suitable for serverless job runners (e.g., Google Cloud Run Jobs).

## Data Flow

1.  **Trigger**: The service starts via a scheduled trigger (e.g., Cloud Scheduler).
2.  **Extract**: `scrape_linkedin()` requests a defined count of jobs (env: `RESULT_COUNT`).
3.  **Transform**:
    *   Raw jobs are iterated.
    *   Valid jobs are selected.
    *   Text descriptions are converted to vector embeddings.
4.  **Load**:
    *   The service attempts to insert the batch into the `job_embeddings` collection.
    *   Existing `job_id`s result in a harmless write error (caught and logged), while new jobs are successfully persisted.
5.  **Exit**: The process logs the result summary and terminates.

## Configuration & Environment Variables

The service relies on environment variables for configuration. Ensure these are set in the deployment environment (e.g., GCP Secrets Manager).

| Variable | Description | Default |
| :--- | :--- | :--- |
| `MONGODB_URI` | **Required**. Connection string for MongoDB Atlas. | N/A |
| `DATABASE_NAME` | **Required**. Name of the target database. | `portal_application_optimization` |
| `RESULT_COUNT` | Number of jobs to scrape per run. | `100` |
| `EMBEDDING_MODEL` | HuggingFace model name for embeddings. | `all-MiniLM-L6-v2` |

## Deployment Strategy

### Google Cloud Platform (Recommended)

This service is optimized for **Google Cloud Run Jobs** rather than a continuously running service.

1.  **Containerization**: Build the Docker image using the provided `Dockerfile`.
    *   Ensure `requirements.txt` is up-to-date (`uv pip compile pyproject.toml -o requirements.txt`) before building.
2.  **Execution**: Deploy as a Cloud Run Job.
3.  **Scheduling**: Use Google Cloud Scheduler to trigger the job daily (e.g., at midnight UTC).

### Local Development

1.  **Dependency Management**: Uses `uv` for fast package management.
    *   Install: `uv sync`
2.  **Running Locally**:
    *   Create a `.env` file with the required variables.
    *   Execute: `python -m app.main`

## Developer Notes

*   **SSL Verification**: The `certifi` package is critical for the MongoDB connection. If you encounter `[SSL: CERTIFICATE_VERIFY_FAILED]`, ensure `certifi` is installed and `tlsCAFile=certifi.where()` is present in `data/db.py`.
*   **Memory Usage**: The `SentenceTransformer` model requires significant memory (approx. 400MB-1GB depending on the model). Ensure the deployment container has at least 2GB of RAM to prevent OOM kills.
*   **JobSpy Stability**: The `jobspy` library scrapes public endpoints. It is subject to breakage if LinkedIn changes their DOM or API. Monitor logs (`portal_job_scraper.log`) for scraping failures.
*   **Duplicate Handling**: The service is designed to be idempotent. Re-running it multiple times a day is safe; it will only add new jobs that haven't been seen before.
