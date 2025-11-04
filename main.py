from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers import auth, user, food, health, recommendation
from backend.utils.logger import CustomLogger

LOGGER = CustomLogger()

app = FastAPI(
    title=settings.APP_NAME,
    description="A personalized food recommendation system based on health conditions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(food.router)
app.include_router(health.router)
app.include_router(recommendation.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Food Recommendation System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": settings.APP_NAME
    }


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    LOGGER.info(f"{settings.APP_NAME} started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    LOGGER.info(f"{settings.APP_NAME} shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )