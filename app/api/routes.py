from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.schemas import GenerationRequest, JobResponse, JobDetailResponse
from app.services.job_manager import JobManager
import json

router = APIRouter()

@router.post("/jobs", response_model=JobResponse, status_code=202)
async def create_generation_job(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    job = JobManager.create_job(
        db=db,
        topic=request.topic,
        target_word_count=request.word_count,
        language=request.language
    )
    
    # Kick off background process
    background_tasks.add_task(JobManager.process_job_background, job.id)
    
    return JobResponse(
        id=job.id,
        topic=job.topic,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at
    )

@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = JobManager.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    result_dict = None
    if job.result:
        try:
            result_dict = json.loads(job.result)
        except:
            pass
            
    return JobDetailResponse(
        id=job.id,
        topic=job.topic,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
        error_message=job.error_message,
        result=result_dict
    )
