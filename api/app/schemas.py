from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel

# Schema for the request body of the /shorten endpoint
class URLBase(BaseModel):
    long_url: str
    expires_at: Optional[datetime] = datetime.now(timezone.utc) + timedelta(days=1)

# Schema for the response body of the /shorten endpoint
class URLShortened(BaseModel):
    short_code: str
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema for the response body of the /analytics endpoint
class URLAnalytics(BaseModel):
    long_url: str
    short_code: str
    hits: int
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True