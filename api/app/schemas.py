from pydantic import BaseModel

# Schema for the request body of the /shorten endpoint
class URLBase(BaseModel):
    long_url: str

# Schema for the response body of the /shorten endpoint
class URLShortened(BaseModel):
    short_code: str

    class Config:
        from_attributes = True

# Schema for the response body of the /analytics endpoint
class URLAnalytics(BaseModel):
    long_url: str
    short_code: str
    hits: int

    class Config:
        from_attributes = True