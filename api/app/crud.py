import hashlib
from sqlalchemy.orm import Session
from . import models, schemas

def get_url_by_short_code(db: Session, short_code: str):
    """Retrieve a URL from the database by its short code."""
    return db.query(models.URL).filter(models.URL.short_code == short_code).first()

def create_short_url(db: Session, url: schemas.URLBase):
    """Create a new short URL, handling potential hash collisions."""
    # Check if the long URL already exists
    existing_url = db.query(models.URL).filter(models.URL.long_url == url.long_url).first()
    if existing_url:
        return existing_url

    long_url_to_hash = url.long_url
    
    # Hashing and Collision Resolution
    while True:
        # 1. Generate hash from the long URL
        hash_object = hashlib.sha256(long_url_to_hash.encode())
        hex_digest = hash_object.hexdigest()
        short_code = hex_digest[:7] # Take the first 7 characters

        # 2. Check if the generated short_code already exists
        existing_short_code = get_url_by_short_code(db, short_code)

        if not existing_short_code:
            # If it's unique, break the loop
            break
        
        # 3. If a collision occurs, append a salt and re-hash
        long_url_to_hash += "|collision"

    # Create the new database record
    db_url = models.URL(
        long_url=url.long_url,
        short_code=short_code,
        hits=0
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