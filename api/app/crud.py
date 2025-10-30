import hashlib
from sqlalchemy.orm import Session
from pydantic import HttpUrl
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, cast, Tuple
import logging

from . import models, schemas

logger = logging.getLogger(__name__)

def get_url_by_short_code(db: Session, short_code: str) -> Tuple[Optional[models.URL], bool]:
    """Retrieve a URL from the database by its short code."""
    db_url = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    is_expired = False
    if db_url:
        expires_at: Optional[datetime] = cast(Optional[datetime], db_url.expires_at)
        if expires_at and expires_at < datetime.now():
            is_expired = True
    return db_url, is_expired

def create_short_url(db: Session, url: schemas.URLBase):
    """Create a new short URL, handling potential hash collisions."""
    try:
        validated_url = HttpUrl(url.long_url)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format"
        )

    # Check if the long URL already exists
    existing_url = db.query(models.URL).filter(models.URL.long_url == str(validated_url)).first()
    if existing_url:
        return existing_url

    long_url_to_hash = str(validated_url)
    
    # Hashing and Collision Resolution
    while True:
        # 1. Generate hash from the long URL
        hash_object = hashlib.sha256(long_url_to_hash.encode())
        hex_digest = hash_object.hexdigest()
        short_code = hex_digest[:7] # Take the first 7 characters

        # 2. Check if the generated short_code already exists
        existing_short_code, _ = get_url_by_short_code(db, short_code) # Ignore is_expired here

        if not existing_short_code:
            # If it's unique, break the loop
            break
        
        # 3. If a collision occurs, append a salt and re-hash
        long_url_to_hash += "|collision"

    # Create the new database record
    logger.info(f"Creating new URL record with: long_url={str(validated_url)}, short_code={short_code}, hits=0, expires_at={url.expires_at}")
    db_url = models.URL(
        long_url=str(validated_url),
        short_code=short_code,
        hits=0,
        expires_at=url.expires_at
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def increment_hit_count(db: Session, db_url: models.URL):
    """Increment the hit counter for a given URL."""
    setattr(db_url, 'hits', (db_url.hits or 0) + 1)
    db.commit()
    db.refresh(db_url)
    return db_url