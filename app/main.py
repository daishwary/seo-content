import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from app.api import routes
from app.db.session import init_db

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

def get_app() -> FastAPI:
    app = FastAPI(
        title="SEO Content Generator Agent API",
        description="A backend service that generates SEO-optimized articles based on search engine results.",
        version="1.0.0"
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.on_event("startup")
    async def startup_event():
        init_db()

    # Include the main router
    app.include_router(routes.router, prefix="/api")

    @app.get("/")
    async def root():
        return RedirectResponse(url="/static/index.html")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = get_app()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
