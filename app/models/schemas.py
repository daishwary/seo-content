from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- Request/Response API Schemas ---
class GenerationRequest(BaseModel):
    topic: str
    word_count: int = Field(default=1500, gt=0)
    language: str = Field(default="English")

class JobResponse(BaseModel):
    id: str
    topic: str
    status: str
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None

class JobDetailResponse(JobResponse):
    result: Optional[dict] = None

# --- Internal & Agent Output Schemas ---
class SEOMetadata(BaseModel):
    title_tag: str = Field(description="SEO title tag for the article (50-60 chars)")
    meta_description: str = Field(description="Meta description optimized for CTR (150-160 chars)")
    primary_keyword: str = Field(description="The main target keyword")
    secondary_keywords: List[str] = Field(description="List of secondary/LSI keywords")

class LinkSuggestion(BaseModel):
    anchor_text: str = Field(description="The text to hyperlink")
    target_topic_or_url: str = Field(description="Suggested internal topic/page or external reference URL")
    context: str = Field(description="Brief explanation of where this link belongs in the article")

class ArticleFAQ(BaseModel):
    question: str
    answer: str

class ArticleOutput(BaseModel):
    title: str = Field(description="The H1 title of the article")
    content_markdown: str = Field(description="The full article body in markdown, including H2/H3 headers. Should read naturally.")
    metadata: SEOMetadata
    structured_data_schema: str = Field(description="A valid JSON string representation of the article/FAQ schema markup (JSON-LD)")
    internal_links: List[LinkSuggestion] = Field(description="3-5 internal link suggestions")
    external_links: List[LinkSuggestion] = Field(description="2-4 external reference suggestions")
    faq: List[ArticleFAQ] = Field(description="FAQ section addressing common queries")

class ContentScore(BaseModel):
    seo_score: int = Field(description="Score from 0-100 evaluating keyword usage, header structure, and search intent.")
    readability_score: int = Field(description="Score from 0-100 evaluating human-like reading quality, avoiding robotic phrasing.")
    feedback: str = Field(description="Specific feedback on what needs improvement.")
    needs_revision: bool = Field(description="True if the content falls below a quality threshold and requires rewriting.")
