from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel

class URLBase(BaseModel):
    long_url: str
    expires_at: Optional[datetime] = datetime.now(timezone.utc) + timedelta(days=1)

class URLShortened(BaseModel):
    short_code: str
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class URLAnalytics(BaseModel):
    long_url: str
    short_code: str
    hits: int
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True