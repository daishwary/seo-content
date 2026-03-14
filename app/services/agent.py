import json
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from app.models.db_models import Job, JobStatus
from app.models.schemas import ArticleOutput, ContentScore
from app.services.search import MockSerpFetcher
import os

logger = logging.getLogger(__name__)

class SEOAgent:
    def __init__(self, db: Session, job: Job):
        self.db = db
        self.job = job
        client_key = os.getenv("OPENAI_API_KEY", "")
        self.client = AsyncOpenAI(api_key=client_key) if client_key else None
        
    async def run(self):
        """Main execution workflow with durability checks to resume gracefully"""
        try:
            if not self.client:
                raise ValueError("OPENAI_API_KEY missing from environment.")

            # Step 1: SERP Data Collection
            if not self.job.serp_data:
                logger.info(f"Fetching SERP data for job {self.job.id}")
                serp_results = await MockSerpFetcher.fetch_top_10(self.job.topic)
                self.job.serp_data = json.dumps(serp_results)
                self.db.commit()
            
            # Step 2: Outline & FAQ generation
            if not self.job.outline:
                logger.info(f"Generating Outline for job {self.job.id}")
                outline = await self._generate_outline(json.loads(self.job.serp_data))
                self.job.outline = outline
                self.db.commit()
                
            # Step 3: Full Article Generation
            if not self.job.result:
                logger.info(f"Drafting content for job {self.job.id}")
                article = await self._draft_content()
                
                # Step 4: Bonus - Content Scorer and Revision
                self.job.status = JobStatus.SCORED_REVISING
                self.db.commit()
                
                logger.info(f"Scoring content for job {self.job.id}")
                score = await self._score_content(article)
                
                if score.needs_revision:
                    logger.info(f"Content needs revision. Feedback: {score.feedback}")
                    article = await self._revise_content(article, score.feedback)
                
                # Finalize Result
                self.job.result = article.model_dump_json()
                self.job.status = JobStatus.COMPLETED
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Agent failed for job {self.job.id}: {str(e)}")
            self.job.status = JobStatus.FAILED
            self.job.error_message = str(e)
            self.db.commit()

    async def _generate_outline(self, serp_data: List[Dict[str, Any]]) -> str:
        """Analyzes SERP data to extract themes and generate an outline."""
        prompt = f"""
        You are an expert SEO Content Strategist. Your goal is to analyze the top 10 search results for the topic: '{self.job.topic}'
        and produce a detailed structural outline for an article targeting {self.job.target_word_count} words in {self.job.language}.

        Here is the SERP data:
        {json.dumps(serp_data, indent=2)}

        Provide a structured markdown outline including H1, H2, and H3 headers. 
        Ensure you cover the main intent shown in the search results and identify common themes.
        """
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content

    async def _draft_content(self) -> ArticleOutput:
        """Generates the full article content based on the outline, targeting structured Pydantic output."""
        prompt = f"""
        You are a senior content writer and SEO expert. Write an exhaustive, engaging, and highly readable article 
        about '{self.job.topic}' in {self.job.language}. It should be approximately {self.job.target_word_count} words long.
        
        Follow this outline precisely:
        {self.job.outline}
        
        You must output the result strictly according to the provided JSON schema. Ensure:
        - Natural phrasing that doesn't sound robotic
        - Proper markdown in the output field
        - A dedicated FAQ section based on common implied questions
        - High quality metadata and keywords
        - Internal link mapping to generic related SEO concepts
        - External link recommendations to authoritative sites
        """
        
        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a specialized SEO content generation engine."},
                {"role": "user", "content": prompt}
            ],
            response_format=ArticleOutput,
            temperature=0.7
        )
        return response.choices[0].message.parsed
        
    async def _score_content(self, article: ArticleOutput) -> ContentScore:
        """Acts as an Editor agent evaluating the quality of the content."""
        prompt = f"""
        You are a strict SEO Editor. Review the following generated article about '{self.job.topic}'.
        
        Evaluate it based on:
        1. SEO Optimization: Are the keywords used naturally? Is the H1/H2 structure sound?
        2. Readability: Does it sound like a human wrote it? Is it engaging?
        
        Title: {article.title}
        Content Snippet (First 500 chars): {article.content_markdown[:500]}...
        Metadata: {article.metadata.model_dump_json()}
        
        Output a score according to the JSON schema. If either score < 75, set 'needs_revision' to true and provide clear feedback.
        """
        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format=ContentScore,
            temperature=0.1
        )
        return response.choices[0].message.parsed
        
    async def _revise_content(self, original: ArticleOutput, feedback: str) -> ArticleOutput:
        """Revises the article based on editor feedback."""
        prompt = f"""
        You are revising an article about '{self.job.topic}' based on editor feedback.
        
        Editor Feedback: {feedback}
        
        Original Content constraints: Maintain the schema, improve the flow, and fix the specific issues raised by the editor.
        """
        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format=ArticleOutput,
            temperature=0.7
        )
        return response.choices[0].message.parsed
