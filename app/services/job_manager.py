import uuid
import asyncio
from sqlalchemy.orm import Session
from app.models.db_models import Job, JobStatus
from app.db.session import SessionLocal

class JobManager:
    @staticmethod
    def create_job(db: Session, topic: str, target_word_count: int, language: str) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            topic=topic,
            target_word_count=target_word_count,
            language=language,
            status=JobStatus.PENDING
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_job(db: Session, job_id: str) -> Job:
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    async def process_job_background(job_id: str):
        # We need a new session per thread/background task
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            db.close()
            return

        try:
            job.status = JobStatus.RUNNING
            db.commit()

            from app.services.agent import SEOAgent
            agent = SEOAgent(db, job)
            # await agent.run() handles its own status updates to COMPLETED or FAILED
            await agent.run()
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
        finally:
            db.close()
