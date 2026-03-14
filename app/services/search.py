import asyncio

class MockSerpFetcher:
    """
    Mocks a search engine results page (SERP) API response.
    In a real-world scenario, you would integrate SerpApi, DataForSEO, etc. here.
    """
    @staticmethod
    async def fetch_top_10(topic: str) -> list[dict]:
        # Simulate network latency
        await asyncio.sleep(1.5)
        
        # We mock responses tailored to the provided topic simply by using the topic in the strings.
        # This provides a consistent, realistic structure for the Agent to process.
        capitalized_topic = topic.title()
        
        return [
            {
                "rank": 1,
                "url": "https://example.com/industry-leader",
                "title": f"The Ultimate Guide to {capitalized_topic} in 2025",
                "snippet": f"Discover the top strategies and tools for {topic}. We review the industry leaders and provide actionable tips for success."
            },
            {
                "rank": 2,
                "url": "https://competitor.com/blog",
                "title": f"15 Best Practices for {capitalized_topic}",
                "snippet": f"Looking for {topic}? Our team tested the market extensively. Here are the pros and cons you need to know before making a decision."
            },
            {
                "rank": 3,
                "url": "https://news.tech.com/analysis",
                "title": f"Why {capitalized_topic} is Changing the Industry",
                "snippet": f"An in-depth look at how {topic} influences bottom-line revenue. Trends predict widespread adoption by next year."
            },
            {
                "rank": 4,
                "url": "https://software-reviews.net/top",
                "title": f"Top 10 {capitalized_topic} Tools Compared",
                "snippet": f"Compare pricing, features, and user reviews for {topic}. Find out which solution fits your business size and budget."
            },
            {
                "rank": 5,
                "url": "https://academic.edu/research",
                "title": f"A Comprehensive Study on {capitalized_topic}",
                "snippet": f"Academic perspectives on {topic}. What does the data actually say? Read our peer-reviewed findings on efficacy and ROI."
            },
            {
                "rank": 6,
                "url": "https://quicktips.io/guides",
                "title": f"How to Get Started with {capitalized_topic}",
                "snippet": f"A beginner-friendly tutorial for {topic}. Step-by-step instructions to ensure you don't make common mistakes."
            },
            {
                "rank": 7,
                "url": "https://forum.community.net/discussion",
                "title": f"Community Consensus: {capitalized_topic}",
                "snippet": f"Real users share their experiences with {topic}. Is it worth the hype? Join the discussion to find out."
            },
            {
                "rank": 8,
                "url": "https://startup.com/our-journey",
                "title": f"How We Scaled Using {capitalized_topic}",
                "snippet": f"A case study on {topic}. See the exact frameworks we used to double our growth in just 6 months."
            },
            {
                "rank": 9,
                "url": "https://glossary.tech/definitions",
                "title": f"What is {capitalized_topic}? Definition & Examples",
                "snippet": f"Clear definitions and practical business examples for {topic}. Perfect for onboarding new team members."
            },
            {
                "rank": 10,
                "url": "https://video.hub.com/watch",
                "title": f"Video Tutorial: Mastering {capitalized_topic}",
                "snippet": f"Watch our experts break down {topic} into easy-to-understand concepts. Includes free templates and resources."
            }
        ]
