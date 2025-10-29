import redis
import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from api.app import crud, models, schemas, security
from .database import SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="A simple and efficient URL shortening service.",
    version="1.0.0"
)

# Connect to Redis using environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
cache = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)


# Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shorten", response_model=schemas.URLShortened, status_code=201)
def shorten_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    """
    Accepts a long URL and returns a unique 7-character short code.
    Validates that the input is a proper URL.
    """
    db_url = crud.create_short_url(db=db, url=url)
    return db_url

@app.get("/{short_code}", status_code=307)
def redirect_to_long_url(short_code: str, db: Session = Depends(get_db)):
    """
    Redirects to the original long URL.
    Implements a cache-aside strategy with Redis.
    Tracks the number of hits for each redirection.
    """
    # 1. First, check the Redis cache
    long_url = cache.get(short_code)
    long_url = None
    try:
        # 1. First, check the Redis cache
        long_url = cache.get(short_code)
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        
    if long_url:
        return RedirectResponse(url=str(long_url))

    # 2. Cache Miss: Fallback to PostgreSQL
    db_url = crud.get_url_by_short_code(db, short_code=short_code)
    
    if not db_url:
        logger.warning(f"Short code not found in database: {short_code}")
        raise HTTPException(status_code=404, detail="Short code not found")

    # 3. Increment hit count in the database
    crud.increment_hit_count(db, db_url)

    # 4. Populate Redis cache for future requests with a 24-hour TTL (Time-To-Live)
    try:
        cache.setex(short_code, 86400, str(db_url.long_url))
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        
    return RedirectResponse(url=str(db_url.long_url))

@app.get("/analytics/{short_code}", response_model=schemas.URLAnalytics)
def get_analytics(short_code: str, db: Session = Depends(get_db), api_key: str = Depends(security.get_api_key)):
    """
    Returns the hit count and original URL for a given short code.
    """
    db_url = crud.get_url_by_short_code(db, short_code=short_code)
    
    if not db_url:
        raise HTTPException(status_code=404, detail="Short code not found")
        
    return db_url