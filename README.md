# SEO Content Generator Agent

This is a backend service designed to act as an intelligent agent for generating SEO-optimized articles based on search engine results. It uses FastAPI, Pydantic, SQLAlchemy (SQLite), and OpenAI Structured Outputs.

## Features Included
- **Core Agent**: Analyzes mock SERP data, outlines a structure, and drafts content with metadata, FAQs, and link suggestions.
- **Job Management**: Submits jobs asynchronously (`pending` -> `running` -> `scored_revising` -> `completed` -> `failed`).
- **Durability**: Saves intermediate steps (SERP data, outline) to a SQLite db (`jobs.db`) so the agent can resume if the process restarts mid-execution.
- **Content Quality Scorer (Bonus)**: Uses a secondary prompt to score the first draft for SEO and Readability. If the text scores poorly, it triggers a revision prompt.
- **FAQ Section (Bonus)**: Extrapolates common topics from SERPs into question-and-answer pairs.
- **RESTful Endpoints**: Simple POST / GET polling model.

## Setup Instructions

This project was built to be run inside a Conda environment.

1. Create and activate a conda environment:
   ```bash
   conda create -n seo_agent python=3.12
   conda activate seo_agent
   ```
2. Install the necessary packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key in the environment or an `.env` file in the root directory:
   ```bash
   export OPENAI_API_KEY="your-sk-key"
   # On windows:
   $env:OPENAI_API_KEY="your-sk-key"
   ```
4. Start the application. The system uses Uvicorn embedded inside `app/main.py`!
   ```bash
   python -m app.main
   ```

## API Usage

**Start Job:**
```bash
curl -X POST http://localhost:8000/api/jobs \
     -H "Content-Type: application/json" \
     -d '{"topic": "best productivity tools for remote teams", "word_count": 1000}'
```

**Check Status:** (Replace the ID with the one returned from the previous POST call)
```bash
curl http://localhost:8000/api/jobs/{JOB_ID}
```

## Running Tests
Run basic API and schema constraints checks.
```bash
pytest tests/
```
